// Chat functionality

// Converts markdown to HTML using marked.js library for full markdown support
function parseMarkdown(text) {
    if (!text) return '';
    
    // Configure marked.js with optimal settings for chat rendering
    marked.setOptions({
        breaks: true,        // Convert single line breaks to <br>
        gfm: true,          // Enable GitHub Flavored Markdown (tables, strikethrough, etc.)
        headerIds: false,   // Disable auto-generated header IDs for cleaner HTML
        mangle: false,      // Don't obfuscate email addresses
        sanitize: false     // Modern marked handles XSS safely without sanitize
    });
    
    // Parse markdown text to HTML
    return marked.parse(text);
}

// Retrieves the current user ID from input field or returns default
function getUserId() {
    return document.getElementById('userId').value || 'demo_user';
}

// Gets the domain name context from the Domain Catalog input field
function getDomainName() {
    // Get domain name from Domain Catalog section's domain name input field
    const domainInput = document.getElementById('domainName');
    const domain = domainInput ? domainInput.value.trim().toLowerCase() : '';
    
    // Return normalized domain name (lowercase, trimmed) or null if empty
    return domain || null;
}

// Displays a message in the chat container with optional response time
function addMessage(content, role, responseTime = null) {
    const messagesContainer = document.getElementById('messages');
    
    // Remove welcome message if exists
    const welcomeMsg = messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    
    const contentWrapper = document.createElement('div');
    contentWrapper.style.display = 'flex';
    contentWrapper.style.flexDirection = 'column';
    contentWrapper.style.gap = '0.25rem';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    // Use innerHTML with markdown parsing for assistant messages, plain text for user
    if (role === 'assistant') {
        contentDiv.innerHTML = parseMarkdown(content);
    } else {
        contentDiv.textContent = content;
    }
    
    contentWrapper.appendChild(contentDiv);
    
    // Add response time for assistant messages
    if (role === 'assistant' && responseTime !== null) {
        const timeDiv = document.createElement('div');
        timeDiv.className = 'response-time';
        
        // Format time
        const seconds = (responseTime / 1000).toFixed(1);
        const minutes = Math.floor(responseTime / 60000);
        const remainingSeconds = ((responseTime % 60000) / 1000).toFixed(1);
        
        if (minutes > 0) {
            timeDiv.textContent = `${minutes}m ${remainingSeconds}s`;
        } else {
            timeDiv.textContent = `${seconds}s`;
        }
        
        contentWrapper.appendChild(timeDiv);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentWrapper);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showThinkingIndicator() {
    const messagesContainer = document.getElementById('messages');
    
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'thinking-indicator';
    thinkingDiv.id = 'thinking-indicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const thinkingContent = document.createElement('div');
    thinkingContent.className = 'thinking-content';
    
    const thinkingText = document.createElement('span');
    thinkingText.textContent = 'Thinking';
    thinkingText.style.color = 'var(--text-secondary)';
    thinkingText.style.fontSize = '0.9rem';
    
    const dotsContainer = document.createElement('div');
    dotsContainer.className = 'thinking-dots';
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        dotsContainer.appendChild(dot);
    }
    
    thinkingContent.appendChild(thinkingText);
    thinkingContent.appendChild(dotsContainer);
    thinkingDiv.appendChild(avatar);
    thinkingDiv.appendChild(thinkingContent);
    
    messagesContainer.appendChild(thinkingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeThinkingIndicator() {
    const thinking = document.getElementById('thinking-indicator');
    if (thinking) {
        thinking.remove();
    }
}

function setLoading(isLoading) {
    const sendButton = document.querySelector('.send-button');
    const userInput = document.getElementById('userInput');
    
    sendButton.disabled = isLoading;
    userInput.disabled = isLoading;
}

async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Start timer
    const startTime = Date.now();
    
    // Show loading
    setLoading(true);
    showThinkingIndicator();
    
    try {
        // Ensure session_id is always a string
        const sessionId = String(getSessionId());
        const userId = String(getUserId());
        const domainName = getDomainName();  // Get optional domain context
        
        console.log('Sending message with:', { message, userId, sessionId, domainName }); // Debug log
        
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: userId,
                session_id: sessionId,
                domain_name: domainName  // Include domain context if provided
            })
        });
        
        const data = await response.json();
        
        // Calculate response time
        const responseTime = Date.now() - startTime;
        
        // Remove thinking indicator
        removeThinkingIndicator();
        
        if (response.ok) {
            addMessage(data.response, 'assistant', responseTime);
        } else {
            addMessage(`Error: ${data.error}`, 'assistant', responseTime);
        }
    } catch (error) {
        const responseTime = Date.now() - startTime;
        removeThinkingIndicator();
        addMessage(`Error: ${error.message}`, 'assistant', responseTime);
    } finally {
        setLoading(false);
    }
}

async function viewMemories() {
    const memoryList = document.getElementById('memoryList');
    memoryList.innerHTML = '<div style="text-align: center; padding: 1rem;">Loading...</div>';
    
    try {
        const response = await fetch(`/memories?user_id=${getUserId()}&session_id=${getSessionId()}`);
        const data = await response.json();
        
        if (response.ok && data.memories.length > 0) {
            memoryList.innerHTML = '<h4 style="margin-bottom: 0.5rem; font-size: 0.875rem; position: sticky; top: 0; background: var(--bg-dark); z-index: 10; padding: 0.25rem 0;">Stored Memories (' + data.memories.length + '):</h4>';
            
            // Show ALL memories (removed slice limit)
            data.memories.forEach((mem, index) => {
                const memDiv = document.createElement('div');
                memDiv.className = 'memory-item';
                const memText = mem.memory || mem;
                const displayText = typeof memText === 'string' ? memText : JSON.stringify(memText);
                // Show more characters for better readability
                const truncatedText = displayText.length > 80 ? displayText.substring(0, 80) + '...' : displayText;
                memDiv.textContent = `${index + 1}. ${truncatedText}`;
                memoryList.appendChild(memDiv);
            });
        } else {
            memoryList.innerHTML = '<div style="text-align: center; padding: 1rem; color: var(--text-secondary);">No memories yet</div>';
        }
    } catch (error) {
        memoryList.innerHTML = `<div style="text-align: center; padding: 1rem; color: var(--danger-color);">Error: ${error.message}</div>`;
    }
}

async function clearMemories() {
    if (!confirm('Are you sure you want to clear all long-term memories (LTM)? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/memories/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: getUserId()
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`Successfully cleared ${data.deleted_count} memories!`);
            document.getElementById('memoryList').innerHTML = '';
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function clearSession() {
    if (!confirm('Are you sure you want to clear session history (STM) for this session? This will remove conversation context from Redis.')) {
        return;
    }
    
    try {
        const response = await fetch('/session/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: getSessionId()
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`Success: ${data.message}`);
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

function clearChat() {
    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = `
        <div class="welcome-message">
            <h2>How can I help you today?</h2>
        </div>
    `;
}

// Toggle Domain Catalog collapsible section
function toggleDomainCatalog() {
    const content = document.getElementById('domainCatalogContent');
    const icon = document.getElementById('domainCatalogIcon');
    
    // Toggle expanded class
    content.classList.toggle('expanded');
    icon.classList.toggle('rotated');
    
    // Save state to localStorage
    const isExpanded = content.classList.contains('expanded');
    localStorage.setItem('domainCatalogExpanded', isExpanded);
}

// Initialize Domain Catalog collapse state on page load
function initializeDomainCatalog() {
    const savedState = localStorage.getItem('domainCatalogExpanded');
    // Default is collapsed (false)
    if (savedState === 'true') {
        const content = document.getElementById('domainCatalogContent');
        const icon = document.getElementById('domainCatalogIcon');
        content.classList.add('expanded');
        icon.classList.add('rotated');
    }
}

// Loads and displays all domains previously added by the current user
async function loadUserDomains() {
    const userId = getUserId();
    
    try {
        const response = await fetch(`/domain/user?user_id=${userId}`);
        const data = await response.json();
        
        if (response.ok && data.domains && data.domains.length > 0) {
            // Show the section
            document.getElementById('previouslyAddedDomainsSection').style.display = 'block';
            
            // Display the domains
            const domainsList = document.getElementById('previouslyAddedDomainsList');
            domainsList.innerHTML = '';
            
            data.domains.forEach(domain => {
                const domainItem = document.createElement('div');
                domainItem.className = 'added-domain-item';
                
                const checkmark = document.createElement('span');
                checkmark.className = 'checkmark';
                checkmark.textContent = '✅';
                
                const domainName = document.createElement('span');
                domainName.className = 'domain-name';
                domainName.textContent = domain;
                
                domainItem.appendChild(checkmark);
                domainItem.appendChild(domainName);
                domainsList.appendChild(domainItem);
            });
        } else {
            // Hide the section if no domains
            document.getElementById('previouslyAddedDomainsSection').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading user domains:', error);
        // Hide the section on error
        document.getElementById('previouslyAddedDomainsSection').style.display = 'none';
    }
}

async function addDomainCatalog() {
    const domainNameInput = document.getElementById('domainName');
    const domainCatalogInput = document.getElementById('domainCatalog');
    
    // Normalize domain name (lowercase and trim) for consistent storage
    const domainName = domainNameInput.value.trim().toLowerCase();
    const domainCatalog = domainCatalogInput.value.trim();
    const userId = getUserId();  // Get current user ID
    
    // Validate inputs
    if (!domainName) {
        alert('Please enter a domain name');
        return;
    }
    
    if (!domainCatalog) {
        alert('Please enter a domain catalog/description');
        return;
    }
    
    try {
        const response = await fetch('/domain/catalog', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,  // Include user ID
                domain_name: domainName,
                domain_catalog: domainCatalog
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`✅ ${data.message}`);
            // Clear inputs after successful submission
            domainNameInput.value = '';
            domainCatalogInput.value = '';
            
            // Reload the user's domains list to show the newly added domain
            await loadUserDomains();
        } else {
            alert(`❌ Error: ${data.detail || 'Failed to add domain'}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Generate or get session ID - ALWAYS returns a string
function getSessionId() {
    const sessionIdInput = document.getElementById('sessionId');
    if (sessionIdInput && sessionIdInput.value.trim()) {
        // User has entered a custom session ID - ensure it's a string
        return String(sessionIdInput.value.trim());
    }
    
    // Otherwise, generate one
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId || sessionId === 'null' || sessionId === 'undefined') {
        // Generate unique session ID: timestamp + random string
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem('sessionId', sessionId);
    }
    // Ensure we always return a string
    return String(sessionId);
}

// Initialize session ID and Domain Catalog on page load
window.addEventListener('DOMContentLoaded', function() {
    const sessionIdInput = document.getElementById('sessionId');
    if (sessionIdInput) {
        // Auto-populate with generated ID
        sessionIdInput.value = getSessionId();
    }
    
    // Initialize Domain Catalog collapse state
    initializeDomainCatalog();
    
    // Load user's previously added domains
    loadUserDomains();
});

// Reload domains when user ID changes
document.addEventListener('DOMContentLoaded', function() {
    const userIdInput = document.getElementById('userId');
    if (userIdInput) {
        userIdInput.addEventListener('change', function() {
            loadUserDomains();
        });
    }
});

// Auto-resize textarea
document.getElementById('userInput').addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});


// ========================================
// Modal Close on Outside Click
// ========================================

/**
 * Close modal when clicking outside the modal container.
 * Adds event listeners to all modal overlays.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get all modal overlays
    const addModal = document.getElementById('addDomainModal');
    const updateModal = document.getElementById('updateDomainModal');
    const deleteModal = document.getElementById('deleteDomainModal');
    
    // Add click event listener to close modal when clicking on overlay
    addModal.addEventListener('click', function(event) {
        // Check if the click was on the overlay (not the modal container)
        if (event.target === addModal) {
            closeAddDomainModal();
        }
    });
    
    updateModal.addEventListener('click', function(event) {
        // Check if the click was on the overlay (not the modal container)
        if (event.target === updateModal) {
            closeUpdateDomainModal();
        }
    });
    
    deleteModal.addEventListener('click', function(event) {
        // Check if the click was on the overlay (not the modal container)
        if (event.target === deleteModal) {
            closeDeleteDomainModal();
        }
    });
});

// ========================================
// Domain Catalog Modal Functions
// ========================================

/**
 * Open modal to add a new domain catalog.
 * Displays a modal with input fields for domain name and catalog description.
 */
function openAddDomainModal() {
    // Get the modal element
    const modal = document.getElementById('addDomainModal');
    
    // Clear previous input values
    document.getElementById('addDomainName').value = '';
    document.getElementById('addDomainCatalog').value = '';
    
    // Show the modal by adding 'active' class
    modal.classList.add('active');
}


/**
 * Close the add domain modal.
 * Hides the modal and clears input fields.
 */
function closeAddDomainModal() {
    // Get the modal element
    const modal = document.getElementById('addDomainModal');
    
    // Hide the modal by removing 'active' class
    modal.classList.remove('active');
}


/**
 * Submit the add domain form.
 * Validates inputs and calls the API to add the domain.
 */
function submitAddDomain() {
    // Get input values
    const domainName = document.getElementById('addDomainName').value.trim();
    const domainCatalog = document.getElementById('addDomainCatalog').value.trim();
    
    // Validate inputs
    if (!domainName) {
        alert('Please enter a domain name');
        return;
    }
    
    if (!domainCatalog) {
        alert('Please enter a domain catalog description');
        return;
    }
    
    // Close the modal
    closeAddDomainModal();
    
    // Call the add function with the provided values
    addDomainViaModal(domainName, domainCatalog);
}


/**
 * Open modal to update an existing domain catalog.
 * Displays a modal with input fields for domain name and new catalog description.
 */
function openUpdateDomainModal() {
    // Get the modal element
    const modal = document.getElementById('updateDomainModal');
    
    // Clear previous input values
    document.getElementById('updateDomainName').value = '';
    document.getElementById('updateDomainCatalog').value = '';
    
    // Show the modal by adding 'active' class
    modal.classList.add('active');
}


/**
 * Close the update domain modal.
 * Hides the modal and clears input fields.
 */
function closeUpdateDomainModal() {
    // Get the modal element
    const modal = document.getElementById('updateDomainModal');
    
    // Hide the modal by removing 'active' class
    modal.classList.remove('active');
}


/**
 * Submit the update domain form.
 * Validates inputs and calls the API to update the domain.
 */
function submitUpdateDomain() {
    // Get input values
    const domainName = document.getElementById('updateDomainName').value.trim();
    const domainCatalog = document.getElementById('updateDomainCatalog').value.trim();
    
    // Validate inputs
    if (!domainName) {
        alert('Please enter a domain name');
        return;
    }
    
    if (!domainCatalog) {
        alert('Please enter a new domain catalog description');
        return;
    }
    
    // Close the modal
    closeUpdateDomainModal();
    
    // Call the update function with the provided values
    updateDomainViaModal(domainName, domainCatalog);
}


/**
 * Open modal to delete a domain catalog.
 * Displays a modal with input field for domain name.
 */
function openDeleteDomainModal() {
    // Get the modal element
    const modal = document.getElementById('deleteDomainModal');
    
    // Clear previous input value
    document.getElementById('deleteDomainName').value = '';
    
    // Show the modal by adding 'active' class
    modal.classList.add('active');
}


/**
 * Close the delete domain modal.
 * Hides the modal and clears input field.
 */
function closeDeleteDomainModal() {
    // Get the modal element
    const modal = document.getElementById('deleteDomainModal');
    
    // Hide the modal by removing 'active' class
    modal.classList.remove('active');
}


/**
 * Submit the delete domain form.
 * Validates input and calls the API to delete the domain.
 */
function submitDeleteDomain() {
    // Get input value
    const domainName = document.getElementById('deleteDomainName').value.trim();
    
    // Validate input
    if (!domainName) {
        alert('Please enter a domain name');
        return;
    }
    
    // Close the modal
    closeDeleteDomainModal();
    
    // Call the delete function with the provided value
    deleteDomainViaModal(domainName);
}

/**
 * Add a new domain catalog via API.
 * Makes a POST request to /domain/catalog endpoint.
 * 
 * @param {string} domainName - Name of the domain to add
 * @param {string} domainCatalog - Catalog description for the domain
 */
async function addDomainViaModal(domainName, domainCatalog) {
    const userId = getUserId();
    
    try {
        // Make POST request to add domain catalog
        const response = await fetch('/domain/catalog', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                domain_name: domainName.toLowerCase(),
                domain_catalog: domainCatalog
            })
        });
        
        // Parse response JSON
        const data = await response.json();
        
        // Handle success or error response
        if (response.ok) {
            alert(`Success: ${data.message}`);
            
            // Reload the user's domains list to show the newly added domain
            await loadUserDomains();
        } else {
            alert(`Error: ${data.detail || 'Failed to add domain'}`);
        }
    } catch (error) {
        // Handle network or other errors
        alert(`Error: ${error.message}`);
    }
}

/**
 * Update an existing domain catalog via API.
 * Uses PUT method following REST conventions.
 * 
 * @param {string} domainName - Name of the domain to update
 * @param {string} domainCatalog - New catalog description for the domain
 */
async function updateDomainViaModal(domainName, domainCatalog) {
    const userId = getUserId();
    
    try {
        // Make PUT request to update domain catalog
        const response = await fetch('/domain/catalog', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                domain_name: domainName.toLowerCase(),
                domain_catalog: domainCatalog
            })
        });
        
        // Parse response JSON
        const data = await response.json();
        
        // Handle success or error response
        if (response.ok) {
            alert(`Success: ${data.message}`);
            
            // Reload the user's domains list to reflect changes
            await loadUserDomains();
        } else {
            alert(`Error: ${data.detail || 'Failed to update domain'}`);
        }
    } catch (error) {
        // Handle network or other errors
        alert(`Error: ${error.message}`);
    }
}

/**
 * Delete a domain catalog via API.
 * Makes a DELETE request to /domain/catalog endpoint.
 * 
 * @param {string} domainName - Name of the domain to delete
 */
async function deleteDomainViaModal(domainName) {
    const userId = getUserId();
    
    try {
        // Make DELETE request to remove domain catalog
        // Pass user_id and domain_name as query parameters
        const response = await fetch(
            `/domain/catalog?user_id=${encodeURIComponent(userId)}&domain_name=${encodeURIComponent(domainName.toLowerCase())}`,
            {
                method: 'DELETE'
            }
        );
        
        // Parse response JSON
        const data = await response.json();
        
        // Handle success or error response
        if (response.ok) {
            alert(`Success: ${data.message}`);
            
            // Reload the user's domains list to reflect deletion
            await loadUserDomains();
        } else {
            alert(`Error: ${data.detail || 'Failed to delete domain'}`);
        }
    } catch (error) {
        // Handle network or other errors
        alert(`Error: ${error.message}`);
    }
}
