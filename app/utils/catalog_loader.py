"""
Domain Catalog Manager - Class-based approach for managing domain catalogs
Handles loading, saving, adding, updating, deleting domain catalog information from JSON file
"""

import json
from typing import Dict, Optional
from pathlib import Path
from app.core.logger.logger_config import setup_logger
from app.constants import ErrorMessage


# Initialize logger for tracking operations
logger = setup_logger(__name__)


# Define the path to the domain catalogs JSON file (path resolves to: app/data/domain_catalogs.json)
CATALOG_FILE = Path(__file__).parent.parent / "data" / "domain_catalogs.json"


class DomainCatalogManager:
    """
    Manager class for domain catalog operations.
    Provides separate methods for add, update, delete, and retrieve operations.
    Uses singleton pattern for shared access across the application.
    """
    
    def __init__(self, catalog_file: Path = CATALOG_FILE):
        """
        Initialize the domain catalog manager.
        Called once when creating the singleton instance.
        
        Args:
            catalog_file (Path): Path to the JSON file storing domain catalogs
        """
        # Store the file path for later use
        self.catalog_file = catalog_file
        
        # Log initialization for debugging purposes
        logger.info(f"DomainCatalogManager initialized with file: {catalog_file}")
    

    def _load_catalogs(self) -> Dict:
        """
        Load all domain catalogs from JSON file (private method).
        This method is called internally by other methods to read data.
        
        Returns:
            Dict: Dictionary with 'users' key containing array of user objects
                  Returns empty structure if file doesn't exist or has errors
        
        Example return structure:
            {
                "users": [
                    {
                        "user_id": "demo_user",
                        "domains": {
                            "travel": "TripJack API description...",
                            "healthcare": "Medical records description..."
                        }
                    }
                ]
            }
        """
        try:
            # Check if the JSON file exists on disk
            if self.catalog_file.exists():
                # Open file in read mode with UTF-8 encoding
                with open(self.catalog_file, 'r', encoding='utf-8') as f:
                    # Parse JSON and return as dictionary
                    return json.load(f)
            
            # File doesn't exist, return empty structure
            return {"users": []}
        
        except json.JSONDecodeError:
            # JSON file is malformed or corrupted
            logger.error("Invalid JSON in catalog file")
            return {"users": []}
        
        except Exception as e:
            # Catch any other errors (permissions, disk issues, etc.)
            logger.error(f"Error loading domain catalogs: {str(e)}")
            return {"users": []}
    

    def _save_catalogs(self, catalogs: Dict) -> None:
        """
        Save domain catalogs to JSON file (private method).
        This method is called internally after any data modification.
        
        Args:
            catalogs (Dict): Dictionary with 'users' key containing array of user objects
            
        Raises:
            Exception: If unable to write to file (permissions, disk space, etc.)
        """
        try:
            # Create the data directory if it doesn't exist (parents=True creates parent directories, exist_ok=True doesn't error if exists)
            self.catalog_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Open file in write mode with UTF-8 encoding (this will overwrite existing content)
            with open(self.catalog_file, 'w', encoding='utf-8') as f:
                # Write dictionary as formatted JSON (indent=2 for readable formatting, ensure_ascii=False to preserve non-ASCII characters)
                json.dump(catalogs, f, indent=2, ensure_ascii=False)
            
            # Log successful save operation
            logger.info("Catalogs saved successfully")
        
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error saving domain catalogs: {str(e)}")
            # Re-raise as generic exception with context
            raise Exception(f"Error saving domain catalogs: {str(e)}")
    

    def _find_user(self, catalogs: Dict, user_id: str) -> Optional[Dict]:
        """
        Find a user in the catalogs (private helper method).
        Searches through the users array to locate a specific user.
        
        Args:
            catalogs (Dict): Catalogs dictionary containing users array
            user_id (str): User ID to find
            
        Returns:
            Optional[Dict]: User dictionary if found, None if not found
            
        Example return:
            {"user_id": "demo_user", "domains": {...}}
        """
        # Loop through all users in the catalog
        for user in catalogs.get("users", []):
            # Check if this user's ID matches the search ID
            if user.get("user_id") == user_id:
                # Found the user, return their data
                return user
        
        # User not found, return None
        return None

    def add_domain(self, user_id: str, domain_name: str, catalog: str) -> Dict:
        """
        Add a NEW domain catalog for a user for endpoint - POST /domain/catalog.
        Does NOT update if domain already exists - raises exception instead.
        This enforces the separation between add and update operations.
        
        Args:
            user_id (str): User ID who owns the catalog
            domain_name (str): Domain name (will be normalized to lowercase)
            catalog (str): Catalog description text
            
        Returns:
            Dict: Result dictionary with success status and message
            Example: {"success": True, "domain_name": "travel", "message": "..."}
            
        Raises:
            ValueError: If domain already exists for this user
        """
        # Load current catalogs from JSON file
        catalogs = self._load_catalogs()
        
        # Normalize domain name to lowercase and trim whitespace (this ensures consistent storage, Travel -> travel)
        normalized_domain = domain_name.strip().lower()
        
        # Try to find existing user
        user = self._find_user(catalogs, user_id)
        
        if user:
            # User already exists in the system
            
            # Get user's existing domains dictionary
            domains = user.get("domains", {})
            
            # Check if this domain already exists
            if normalized_domain in domains:
                # Domain exists, log warning
                logger.warning(f"Domain '{normalized_domain}' already exists for user '{user_id}'")
                # Raise error to prevent duplicate domains (caller should use update_domain instead)
                raise ValueError(ErrorMessage.DOMAIN_ALREADY_EXISTS.value.format(domain_name=normalized_domain))
            
            # Domain doesn't exist, safe to add (add new domain to existing domains dictionary)
            domains[normalized_domain] = catalog
            
            # Update user's domains
            user["domains"] = domains
        
        else:
            # User doesn't exist, create new user with domain (append new user object to users array)
            catalogs["users"].append({
                "user_id": user_id,
                "domains": {
                    normalized_domain: catalog
                }
            })
        
        # Save updated catalogs back to JSON file
        self._save_catalogs(catalogs)
        
        # Log successful addition
        logger.info(f"Added domain '{normalized_domain}' for user '{user_id}'")
        
        # Return success result
        return {
            "success": True,
            "domain_name": normalized_domain,
            "message": f"Domain '{normalized_domain}' successfully added"
        }
    

    def update_domain(self, user_id: str, domain_name: str, catalog: str) -> Dict:
        """
        Update an EXISTING domain catalog for a user for endpoint - PUT /domain/catalog.
        Does NOT create if domain doesn't exist - raises exception instead.
        This enforces the separation between add and update operations.
        
        Args:
            user_id (str): User ID who owns the catalog
            domain_name (str): Domain name (will be normalized to lowercase)
            catalog (str): New catalog description text
            
        Returns:
            Dict: Result dictionary with success status and message
            Example: {"success": True, "domain_name": "travel", "message": "..."}
            
        Raises:
            ValueError: If domain or user doesn't exist
        """
        # Load current catalogs from JSON file
        catalogs = self._load_catalogs()
        
        # Normalize domain name to lowercase and trim whitespace
        normalized_domain = domain_name.strip().lower()
        
        # Try to find the user
        user = self._find_user(catalogs, user_id)
        
        if not user:
            # User doesn't exist, cannot update
            logger.warning(f"User '{user_id}' not found")
            # Raise error to indicate user not found
            raise ValueError(ErrorMessage.USER_NOT_FOUND.value.format(user_id=user_id))
        
        # User exists, get their domains dictionary
        domains = user.get("domains", {})
        
        # Check if domain exists
        if normalized_domain not in domains:
            # Domain doesn't exist, cannot update
            logger.warning(f"Domain '{normalized_domain}' not found for user '{user_id}'")
            # Raise error to indicate domain not found (caller should use add_domain instead)
            raise ValueError(ErrorMessage.DOMAIN_NOT_FOUND.value.format(domain_name=normalized_domain))
        
        # Domain exists, safe to update (replace old catalog with new catalog)
        domains[normalized_domain] = catalog
        
        # Save updated catalogs back to JSON file
        self._save_catalogs(catalogs)
        
        # Log successful update
        logger.info(f"Updated domain '{normalized_domain}' for user '{user_id}'")
        
        # Return success result
        return {
            "success": True,
            "domain_name": normalized_domain,
            "message": f"Domain '{normalized_domain}' successfully updated"
        }
    

    def delete_domain(self, user_id: str, domain_name: str) -> Dict:
        """
        Delete a domain catalog for a user for endpoint - DELETE /domain/catalog.
        Removes the domain from user's domains dictionary.
        
        Args:
            user_id (str): User ID who owns the catalog
            domain_name (str): Domain name to delete (will be normalized to lowercase)
            
        Returns:
            Dict: Result dictionary with success status and message
            Example: {"success": True, "domain_name": "travel", "message": "..."}
            
        Raises:
            ValueError: If domain or user doesn't exist
        """
        # Load current catalogs from JSON file
        catalogs = self._load_catalogs()
        
        # Normalize domain name to lowercase and trim whitespace
        normalized_domain = domain_name.strip().lower()
        
        # Try to find the user
        user = self._find_user(catalogs, user_id)
        
        if not user:
            # User doesn't exist, cannot delete
            logger.warning(f"User '{user_id}' not found")
            # Raise error to indicate user not found
            raise ValueError(ErrorMessage.USER_NOT_FOUND.value.format(user_id=user_id))
        
        # User exists, get their domains dictionary
        domains = user.get("domains", {})
        
        # Check if domain exists
        if normalized_domain not in domains:
            # Domain doesn't exist, cannot delete
            logger.warning(f"Domain '{normalized_domain}' not found for user '{user_id}'")
            # Raise error to indicate domain not found
            raise ValueError(ErrorMessage.DOMAIN_NOT_FOUND.value.format(domain_name=normalized_domain))
        
        # Domain exists, safe to delete (remove domain from dictionary using del keyword)
        del domains[normalized_domain]
        
        # Save updated catalogs back to JSON file
        self._save_catalogs(catalogs)
        
        # Log successful deletion
        logger.info(f"Deleted domain '{normalized_domain}' for user '{user_id}'")
        
        # Return success result
        return {
            "success": True,
            "domain_name": normalized_domain,
            "message": f"Domain '{normalized_domain}' successfully deleted"
        }
    

    def get_all_user_catalogs(self, user_id: str) -> Optional[str]:
        """
        Get ALL catalog descriptions for a user, concatenated together for memory_prompt.py.
        Used to include all catalogs in the AI system prompt for context-aware responses.
        
        Args:
            user_id (str): User ID who owns the catalogs
            
        Returns:
            Optional[str]: All catalog descriptions concatenated with labels, 
                          or None if user has no catalogs
            
        Example return:
            "**TRAVEL DOMAIN:**
            TripJack API offers...
            
            **HEALTHCARE DOMAIN:**
            Medical records..."
        """
        # Load current catalogs from JSON file
        catalogs = self._load_catalogs()
        
        # Try to find the user
        user = self._find_user(catalogs, user_id)
        
        if not user:
            # User doesn't exist, return None
            return None
        
        # User exists, get their domains dictionary
        user_domains = user.get("domains", {})
        
        if not user_domains:
            # User has no domains, return None
            return None
        
        # User has domains, concatenate them with labels
        # Create empty list to store formatted catalog strings
        catalog_parts = []
        
        # Loop through each domain and its catalog content
        for domain_name, catalog_content in user_domains.items():
            # Format each domain with uppercase label and content
            catalog_parts.append(f"**{domain_name.upper()} DOMAIN:**\n{catalog_content}")
        
        # Join all catalog parts with double newline separator (this creates readable separation between different domains)
        return "\n\n".join(catalog_parts)
    

    def get_user_domain_names(self, user_id: str) -> list:
        """
        Get list of all domain names for a user for endpoint - /domain/user/{user_id} fro UI purpose.
        Used by the frontend to display "Previously Added Domains" list.
        
        Args:
            user_id (str): User ID who owns the catalogs
            
        Returns:
            list: List of domain names (empty list if no domains)
            Example: ["travel", "healthcare", "finance"]
        """
        # Load current catalogs from JSON file
        catalogs = self._load_catalogs()
        
        # Try to find the user
        user = self._find_user(catalogs, user_id)
        
        if not user:
            # User doesn't exist, return empty list
            return []
        
        # User exists, get their domains dictionary (extract only the keys domain names and convert to list)
        return list(user.get("domains", {}).keys())


# Create a singleton instance for use in endpoints (this single instance is shared across the entire application, import and use this: from app.utils.catalog_loader import catalog_manager)
catalog_manager = DomainCatalogManager()


# Backward compatibility function for memory_prompt.py (provides simple function wrapper for code that doesn't need the class)
def get_all_user_catalogs(user_id: str) -> Optional[str]:
    """
    Get ALL catalog descriptions for a user (backward compatibility wrapper).
    Delegates to DomainCatalogManager instance.
    
    Args:
        user_id (str): User ID who owns the catalogs
        
    Returns:
        Optional[str]: All catalog descriptions concatenated, or None
    """
    # Delegate to singleton instance method
    return catalog_manager.get_all_user_catalogs(user_id)
