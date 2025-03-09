let currentChannelId;
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const chatMessages = document.getElementById('chat-messages');
const loadingIndicator = document.getElementById('loading-indicator');
let loadingInterval;

// Add event listeners
chatForm.addEventListener('submit', handleSubmit);
messageInput.addEventListener('input', adjustTextareaHeight);
messageInput.addEventListener('keydown', handleKeydown);

// Add keyboard shortcut handlers
document.addEventListener('keydown', (e) => {
    if (e.target === messageInput) {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key.toLowerCase()) {
                case 'a':
                    e.preventDefault();
                    messageInput.select();
                    break;
                case 'c':
                    // Default copy behavior is fine
                    break;
                case 'v':
                    // Default paste behavior is fine
                    break;
                case 'x':
                    // Default cut behavior is fine
                    break;
            }
        }
    }
});

function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
}

function adjustTextareaHeight() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 192) + 'px';
}

async function handleSubmit(e) {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;

    addMessageToUI(message, 'User');
    messageInput.value = '';
    adjustTextareaHeight();
    startLoadingAnimation();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                channel_id: currentChannelId
            })
        });

        const data = await response.json();
        clearInterval(loadingInterval);
        loadingIndicator.remove();
        addMessageToUI(data.response, 'Athena');
    } catch (error) {
        console.error('Error sending message:', error);
        clearInterval(loadingInterval);
        loadingIndicator.remove();
    }
}

function startLoadingAnimation() {
    loadingIndicator.className = 'mb-4 text-left';
    const contentDiv = document.createElement('div');
    contentDiv.className = 'inline-block p-4 rounded-lg bg-gray-800 text-gray-200';
    let dots = 0;
    loadingIndicator.innerHTML = '';
    loadingIndicator.appendChild(contentDiv);
    chatMessages.appendChild(loadingIndicator);
    
    loadingInterval = setInterval(() => {
        dots = (dots + 1) % 4;
        contentDiv.textContent = 'Athena is thinking' + '.'.repeat(dots);
    }, 500);
}

function addMessageToUI(message, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `mb-4 ${role === 'User' ? 'text-right' : 'text-left'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = `inline-block p-4 rounded-lg ${role === 'User' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-200'}`;
    
    contentDiv.innerHTML = marked.parse(message);
    
    const links = contentDiv.getElementsByTagName('a');
    for (let link of links) {
        link.className = 'text-blue-400 underline';
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    window.scrollTo(0, document.body.scrollHeight);
}

// Initialize the chat
async function initializeChat() {
    try {
        const response = await fetch('/api/new-channel', {
            method: 'POST'
        });
        const data = await response.json();
        currentChannelId = data.channel_id;

        // Load initial messages
        const messagesResponse = await fetch(`/api/messages/${currentChannelId}`);
        const messagesData = await messagesResponse.json();
        messagesData.messages.forEach(msg => {
            addMessageToUI(msg.content, msg.role);
        });
    } catch (error) {
        console.error('Error initializing chat:', error);
    }
}

initializeChat();