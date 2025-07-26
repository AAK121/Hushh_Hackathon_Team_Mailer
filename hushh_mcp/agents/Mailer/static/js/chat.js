// Global variables
let sessionId = null;
let conversationId = null;
let currentCampaignId = null;
let isWaitingForResponse = false;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    // Generate session ID if not exists
    sessionId = sessionStorage.getItem('sessionId') || generateSessionId();
    sessionStorage.setItem('sessionId', sessionId);
    
    // Auto-resize textarea
    const messageInput = document.getElementById('messageInput');
    messageInput.addEventListener('input', autoResizeTextarea);
}

function setupEventListeners() {
    // File upload
    const excelFile = document.getElementById('excelFile');
    excelFile.addEventListener('change', handleFileUpload);
    
    // Drag and drop
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('drop', handleFileDrop);
    uploadArea.addEventListener('click', () => excelFile.click());
    
    // Modal close events
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('uploadModal');
        if (event.target === modal) {
            closeUploadModal();
        }
    });
}

function generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
}

function autoResizeTextarea() {
    const textarea = document.getElementById('messageInput');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message || isWaitingForResponse) return;
    
    // Clear input and show user message
    messageInput.value = '';
    autoResizeTextarea();
    
    displayMessage(message, 'user');
    showTypingIndicator();
    
    isWaitingForResponse = true;
    
    try {
        const response = await fetch('/api/send-message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            hideTypingIndicator();
            displayMessage(data.response, 'assistant');
            
            sessionId = data.session_id;
            conversationId = data.conversation_id;
            
            // Check if we should show action buttons
            updateActionButtons(data.response);
        } else {
            hideTypingIndicator();
            displayMessage('Sorry, I encountered an error: ' + data.error, 'assistant');
        }
    } catch (error) {
        hideTypingIndicator();
        displayMessage('Sorry, I encountered a network error. Please try again.', 'assistant');
        console.error('Error:', error);
    } finally {
        isWaitingForResponse = false;
    }
}

function displayMessage(content, type) {
    const messagesContainer = document.getElementById('messagesContainer');
    
    // Hide welcome message if it exists
    const welcomeMessage = messagesContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? 'U' : 'AI';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Format content (preserve line breaks and add basic formatting)
    const formattedContent = formatMessageContent(content);
    messageContent.innerHTML = formattedContent;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function formatMessageContent(content) {
    // Convert line breaks to <br>
    let formatted = content.replace(/\n/g, '<br>');
    
    // Make **text** bold
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Make URLs clickable
    formatted = formatted.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    
    return formatted;
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('messagesContainer');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'AI';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(messageContent);
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function updateActionButtons(response) {
    const uploadBtn = document.querySelector('.btn-upload');
    const sendEmailsBtn = document.querySelector('.btn-send-emails');
    
    if (response.toLowerCase().includes('approve') || response.toLowerCase().includes('upload an excel')) {
        uploadBtn.style.display = 'inline-flex';
    }
    
    if (response.toLowerCase().includes('ready to send emails') || response.toLowerCase().includes('send emails')) {
        sendEmailsBtn.style.display = 'inline-flex';
    }
}

function showUploadModal() {
    document.getElementById('uploadModal').style.display = 'block';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
    // Reset file input
    document.getElementById('excelFile').value = '';
}

function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    event.target.style.borderColor = '#10a37f';
    event.target.style.backgroundColor = '#f0fff4';
}

function handleFileDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
            document.getElementById('excelFile').files = files;
            handleFileUpload();
        } else {
            alert('Please upload an Excel file (.xlsx or .xls)');
        }
    }
}

async function handleFileUpload() {
    const fileInput = document.getElementById('excelFile');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    if (!sessionId) {
        alert('Please start a conversation first');
        return;
    }
    
    closeUploadModal();
    showLoading('Uploading and processing Excel file...');
    
    const formData = new FormData();
    formData.append('excel_file', file);
    formData.append('session_id', sessionId);
    
    try {
        const response = await fetch('/api/upload-excel/', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (response.ok) {
            displayMessage(`📁 Excel file uploaded successfully! Found ${data.contacts_count} contacts.`, 'assistant');
            currentCampaignId = data.campaign_id;
            
            // Show preview of contacts
            if (data.preview_contacts && data.preview_contacts.length > 0) {
                let previewText = '\n📋 Preview of contacts:\n';
                data.preview_contacts.forEach((contact, index) => {
                    previewText += `${index + 1}. ${contact.name || 'N/A'} - ${contact.email}\n`;
                });
                displayMessage(previewText, 'assistant');
            }
            
            // Show send emails button
            document.querySelector('.btn-send-emails').style.display = 'inline-flex';
        } else {
            displayMessage('❌ Error uploading file: ' + data.error, 'assistant');
        }
    } catch (error) {
        hideLoading();
        displayMessage('❌ Network error while uploading file. Please try again.', 'assistant');
        console.error('Upload error:', error);
    }
}

async function sendEmails() {
    if (!currentCampaignId || !sessionId) {
        alert('Please upload an Excel file first');
        return;
    }
    
    const confirmation = confirm('Are you sure you want to send emails to all contacts in your list?');
    if (!confirmation) return;
    
    showLoading('Sending emails... This may take a while.');
    
    try {
        const response = await fetch('/api/send-emails/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                campaign_id: currentCampaignId
            })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (response.ok) {
            displayMessage(`🎉 Email campaign completed!\\n✅ ${data.sent_count} emails sent successfully\\n❌ ${data.failed_count} emails failed`, 'assistant');
            
            // Hide send emails button after completion
            document.querySelector('.btn-send-emails').style.display = 'none';
            currentCampaignId = null;
        } else {
            displayMessage('❌ Error sending emails: ' + data.error, 'assistant');
        }
    } catch (error) {
        hideLoading();
        displayMessage('❌ Network error while sending emails. Please try again.', 'assistant');
        console.error('Send emails error:', error);
    }
}

function showLoading(text = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    loadingText.textContent = text;
    overlay.style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function startNewChat() {
    // Clear current session
    sessionId = generateSessionId();
    sessionStorage.setItem('sessionId', sessionId);
    conversationId = null;
    currentCampaignId = null;
    
    // Clear messages
    const messagesContainer = document.getElementById('messagesContainer');
    messagesContainer.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-content">
                <h1>Welcome to Hushh Mailer Agent</h1>
                <p>I'm your AI-powered email campaign assistant. I can help you:</p>
                <ul>
                    <li><i class="fas fa-edit"></i> Create professional email templates</li>
                    <li><i class="fas fa-file-excel"></i> Process Excel contact lists</li>
                    <li><i class="fas fa-paper-plane"></i> Send bulk emails via Mailjet</li>
                    <li><i class="fas fa-chart-line"></i> Track email campaign results</li>
                </ul>
                <p class="start-prompt">To get started, describe the type of email you'd like to create!</p>
            </div>
        </div>
    `;
    
    // Hide action buttons
    document.querySelector('.btn-upload').style.display = 'none';
    document.querySelector('.btn-send-emails').style.display = 'none';
    
    // Close any open modals
    closeUploadModal();
    hideLoading();
}

// Add CSS for typing indicator
const style = document.createElement('style');
style.textContent = `
    .typing-dots {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .typing-dots span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #8e8ea0;
        animation: typing 1.4s ease-in-out infinite;
    }
    
    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% { opacity: 0.3; }
        30% { opacity: 1; }
    }
`;
document.head.appendChild(style);
