document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const loadingIndicator = document.getElementById('loading-indicator');
    const loadingDots = document.getElementById('loading-dots');

    let currentChannelId = null;
    let loadingInterval;

    // Function to animate loading dots
    function startLoadingAnimation() {
        let dots = 1;
        loadingIndicator.classList.remove('hidden');
        loadingInterval = setInterval(() => {
            loadingDots.textContent = '.'.repeat(dots);
            dots = dots === 3 ? 1 : dots + 1;
        }, 500);
    }

    function stopLoadingAnimation() {
        loadingIndicator.classList.add('hidden');
        clearInterval(loadingInterval);
    }

    // Function to add a message to the UI
    function addMessageToUI(message, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-4 ${role === 'User' ? 'text-right' : 'text-left'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = `inline-block p-3 rounded-lg ${role === 'User' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800'}`;
        // Parse markdown and sanitize HTML
        contentDiv.innerHTML = marked.parse(message);
        
        messageDiv.appendChild(contentDiv);
        
        if (role === 'Assistant') {
            // Replace loading indicator with the actual message
            loadingIndicator.parentNode.insertBefore(messageDiv, loadingIndicator);
            loadingIndicator.classList.add('hidden');
        } else {
            chatMessages.appendChild(messageDiv);
        }
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to show loading indicator in message flow
    function startLoadingAnimation() {
        let dots = 1;
        loadingIndicator.classList.remove('hidden');
        chatMessages.appendChild(loadingIndicator);
        loadingInterval = setInterval(() => {
            loadingDots.textContent = '.'.repeat(dots);
            dots = dots === 3 ? 1 : dots + 1;
        }, 500);
    }

    // Create initial chat channel
    async function initializeChat() {
        try {
            const response = await fetch('/api/new-channel', { method: 'POST' });
            const data = await response.json();
            currentChannelId = data.channel_id;
        } catch (error) {
            console.error('Error creating chat:', error);
        }
    }

    // Initialize chat when page loads
    initializeChat();

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;

        // Clear input
        messageInput.value = '';

        // Add user message to UI
        addMessageToUI(message, 'User');

        // Show loading indicator
        startLoadingAnimation();

        try {
            // Send message to server
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    channel_id: currentChannelId
                })
            });

            const data = await response.json();
            
            // Hide loading indicator
            stopLoadingAnimation();
            
            // Add assistant's response to UI
            addMessageToUI(data.response, 'Assistant');
        } catch (error) {
            // Hide loading indicator
            stopLoadingAnimation();
            
            console.error('Error sending message:', error);
            addMessageToUI('Error: Could not send message', 'System');
        }
    });
});