"""
Neo4j Connection Tester
Simple Neo4j connection testing with logging
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from neo4j import GraphDatabase
from app.config.config import NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD
from app.logger.logger_config import setup_logger


# Initialize logger
logger = setup_logger(__name__)


class Neo4jTester:
    """Test Neo4j database connection"""
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize Neo4j tester
        
        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.username = username
        self.password = password
    
    def test_connection(self) -> bool:
        """
        Test Neo4j connection
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            driver.verify_connectivity()
            driver.close()
            logger.info("Neo4j connection successful")
            return True
        except Exception as e:
            logger.error(f"Neo4j connection failed: {str(e)}")
            return False


def test_neo4j_connection_from_config():
    """Test Neo4j connection using config file"""
    tester = Neo4jTester(NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD)
    return tester.test_connection()

if __name__ == "__main__":
    success = test_neo4j_connection_from_config()
    if success:
        print("Neo4j connection successful!")
    else:
        print("Neo4j connection failed!")