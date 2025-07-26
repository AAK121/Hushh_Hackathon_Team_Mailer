class MailerAgent {
    constructor() {
        this.conversations = [];
        this.currentConversation = null;
        this.currentEmailTemplate = '';
        this.messageInput = document.getElementById('messageInput');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.sendBtn = document.getElementById('sendBtn');
        this.emailModal = document.getElementById('emailModal');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        this.initializeEventListeners();
        this.autoResizeTextarea();
    }

    initializeEventListeners() {
        // Auto-resize textarea
        this.messageInput.addEventListener('input', this.autoResizeTextarea.bind(this));
        
        // Click outside modal to close
        this.emailModal.addEventListener('click', (e) => {
            if (e.target === this.emailModal) {
                this.closeModal();
            }
        });
        
        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.emailModal.style.display === 'flex') {
                this.closeModal();
            }
        });
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 200) + 'px';
        
        // Enable/disable send button
        this.sendBtn.disabled = !this.messageInput.value.trim();
    }

    startNewConversation() {
        this.currentConversation = {
            id: Date.now(),
            title: 'New Email Draft',
            messages: []
        };
        
        this.clearMessages();
        this.showWelcomeMessage();
        this.updateConversationList();
    }

    clearMessages() {
        this.messagesContainer.innerHTML = '';
    }

    showWelcomeMessage() {
        this.messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <i class="fas fa-envelope-open"></i>
                </div>
                <h2>Welcome to Hushh Mailer Agent</h2>
                <p>I'm here to help you create professional emails. Just describe what you want to write, and I'll draft it for you.</p>
                
                <div class="example-prompts">
                    <h3>Try these examples:</h3>
                    <div class="prompt-examples">
                        <button class="example-btn" onclick="mailerAgent.useExample('I want to send a welcome email to new interns joining next week')">
                            <i class="fas fa-handshake"></i>
                            Welcome email for new interns
                        </button>
                        <button class="example-btn" onclick="mailerAgent.useExample('Create a follow-up email for a job interview')">
                            <i class="fas fa-briefcase"></i>
                            Follow-up interview email
                        </button>
                        <button class="example-btn" onclick="mailerAgent.useExample('Draft a professional meeting invitation')">
                            <i class="fas fa-calendar"></i>
                            Meeting invitation
                        </button>
                        <button class="example-btn" onclick="mailerAgent.useExample('Write a thank you email to clients')">
                            <i class="fas fa-heart"></i>
                            Thank you email
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    useExample(text) {
        this.messageInput.value = text;
        this.autoResizeTextarea();
        this.sendMessage();
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Clear welcome message if it's the first message
        if (this.messagesContainer.querySelector('.welcome-message')) {
            this.clearMessages();
        }

        // Add user message
        this.addMessage('user', message);
        
        // Clear input
        this.messageInput.value = '';
        this.autoResizeTextarea();

        // Show loading
        this.showLoading();

        try {
            // Check if this is a revision request
            if (this.revisionMode && this.revisionTemplate) {
                const emailContent = await this.generateEmail(message, message, this.revisionTemplate);
                this.revisionMode = false;
                this.revisionTemplate = null;
                
                // Hide loading
                this.hideLoading();
                
                // Add AI response
                this.addMessage('ai', `I've updated the email based on your feedback. Here's the revised version:`);
                
                // Show updated email preview
                setTimeout(() => {
                    this.showEmailPreview(emailContent);
                }, 500);
            } else {
                // Generate new email
                const emailContent = await this.generateEmail(message);
                
                // Hide loading
                this.hideLoading();
                
                // Add AI response
                this.addMessage('ai', `I've generated an email draft based on your request. Would you like to review it?`);
                
                // Show email preview modal
                setTimeout(() => {
                    this.showEmailPreview(emailContent);
                }, 500);
            }
            
        } catch (error) {
            this.hideLoading();
            this.addMessage('ai', 'Sorry, I encountered an error while generating the email. Please try again.');
        }
    }

    async generateEmail(userInput, feedback = null, currentTemplate = null) {
        try {
            const response = await fetch('/api/generate-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_input: userInput,
                    feedback: feedback,
                    current_template: currentTemplate
                })
            });

            const data = await response.json();
            
            if (data.success) {
                return data.email_template;
            } else {
                throw new Error(data.error || 'Failed to generate email');
            }
        } catch (error) {
            console.error('Error generating email:', error);
            // Fallback to mock data if API fails
            return this.getMockTemplate(userInput);
        }
    }

    getMockTemplate(userInput) {
        // Fallback mock templates in case API is not available
        const templates = {
            'welcome': `Dear {name},

Welcome to our team! We're excited to have you join us as a new intern.

Your first day will be on {start_date}, and you'll be working with the {department} team. We've prepared an orientation program to help you get started and familiarize yourself with our company culture and processes.

Please bring the following items on your first day:
- Photo ID
- Signed offer letter
- Any required documentation

If you have any questions before your start date, please don't hesitate to reach out to me or our HR team.

Looking forward to working with you!

Best regards,
{sender_name}
{title}
{company_name}`,

            'follow-up': `Dear {name},

Thank you for taking the time to interview for the {position} role at {company_name}. I enjoyed our conversation and was impressed by your experience and enthusiasm.

I wanted to follow up on our discussion and reiterate my strong interest in this position. After learning more about the role and your team's goals, I'm even more excited about the opportunity to contribute to {company_name}.

If you need any additional information from me, please don't hesitate to ask. I look forward to hearing about the next steps in the process.

Thank you again for your time and consideration.

Best regards,
{your_name}`,

            'default': `Dear {name},

I hope this email finds you well.

{message_body}

Thank you for your time and attention.

Best regards,
{sender_name}`
        };

        const input = userInput.toLowerCase();
        if (input.includes('welcome') || input.includes('intern') || input.includes('new')) {
            return templates['welcome'];
        } else if (input.includes('follow') || input.includes('interview')) {
            return templates['follow-up'];
        } else {
            return templates['default'];
        }
    }

    addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = `message-avatar ${sender}-avatar`;
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `<div class="message-text">${content}</div>`;
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;

        // Update conversation
        if (this.currentConversation) {
            this.currentConversation.messages.push({ sender, content, timestamp: Date.now() });
            this.updateConversationTitle();
        }
    }

    updateConversationTitle() {
        if (this.currentConversation && this.currentConversation.messages.length > 0) {
            const firstUserMessage = this.currentConversation.messages.find(m => m.sender === 'user');
            if (firstUserMessage) {
                this.currentConversation.title = firstUserMessage.content.slice(0, 30) + '...';
                this.updateConversationList();
            }
        }
    }

    updateConversationList() {
        const conversationList = document.getElementById('conversationList');
        conversationList.innerHTML = '';

        this.conversations.forEach(conv => {
            const item = document.createElement('div');
            item.className = `conversation-item ${conv.id === this.currentConversation?.id ? 'active' : ''}`;
            item.innerHTML = `
                <i class="fas fa-envelope"></i>
                ${conv.title}
            `;
            item.onclick = () => this.loadConversation(conv.id);
            conversationList.appendChild(item);
        });

        // Add current conversation if not in list
        if (this.currentConversation && !this.conversations.find(c => c.id === this.currentConversation.id)) {
            this.conversations.unshift(this.currentConversation);
            this.updateConversationList();
        }
    }

    loadConversation(conversationId) {
        const conversation = this.conversations.find(c => c.id === conversationId);
        if (conversation) {
            this.currentConversation = conversation;
            this.clearMessages();
            
            conversation.messages.forEach(msg => {
                this.addMessage(msg.sender, msg.content);
            });
            
            this.updateConversationList();
        }
    }

    showEmailPreview(content) {
        const emailPreview = document.getElementById('emailPreview');
        emailPreview.textContent = content;
        this.currentEmailTemplate = content;
        this.emailModal.style.display = 'flex';
    }

    closeModal() {
        this.emailModal.style.display = 'none';
    }

    requestRevision() {
        this.closeModal();
        
        // Add AI message asking for feedback
        this.addMessage('ai', 'What changes would you like me to make to the email? Please describe the revisions you need.');
        
        // Set flag for revision mode
        this.revisionMode = true;
        this.revisionTemplate = this.currentEmailTemplate;
        
        // Focus on input
        this.messageInput.focus();
    }

    approveEmail() {
        this.closeModal();
        
        // Add success message
        this.addMessage('ai', '✅ Email approved! The email template is ready to be sent to your recipients. You can now upload your contact list or send it manually.');
        
        // Show success actions
        setTimeout(() => {
            this.showSuccessActions();
        }, 1000);
    }

    showSuccessActions() {
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'success-actions';
        actionsDiv.innerHTML = `
            <div style="background-color: #40414f; border-radius: 8px; padding: 20px; margin: 16px 0; border-left: 4px solid #10a37f;">
                <h3 style="color: #10a37f; margin-bottom: 12px;"><i class="fas fa-check-circle"></i> Email Ready!</h3>
                <p style="margin-bottom: 16px; color: #d1d5db;">Your email is approved and ready to send. What would you like to do next?</p>
                <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="mailerAgent.handleUploadContacts()">
                        <i class="fas fa-upload"></i> Upload Contact List
                    </button>
                    <button class="btn btn-secondary" onclick="mailerAgent.handleSendManually()">
                        <i class="fas fa-paper-plane"></i> Send Manually
                    </button>
                    <button class="btn btn-secondary" onclick="mailerAgent.handleCopyTemplate()">
                        <i class="fas fa-copy"></i> Copy Template
                    </button>
                </div>
            </div>
        `;
        
        this.messagesContainer.appendChild(actionsDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    handleUploadContacts() {
        // Create file input element
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.xlsx,.xls';
        fileInput.style.display = 'none';
        
        fileInput.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                this.showLoading();
                try {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/api/process-excel', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    this.hideLoading();
                    
                    if (data.success) {
                        this.addMessage('ai', `✅ Successfully processed ${data.count} recipients from your Excel file. Columns found: ${data.columns.join(', ')}`);
                        
                        // Show send confirmation
                        setTimeout(() => {
                            this.showSendConfirmation(data.recipients);
                        }, 1000);
                    } else {
                        this.addMessage('ai', `❌ Error processing file: ${data.error}`);
                    }
                } catch (error) {
                    this.hideLoading();
                    this.addMessage('ai', `❌ Error uploading file: ${error.message}`);
                }
            }
        };
        
        document.body.appendChild(fileInput);
        fileInput.click();
        document.body.removeChild(fileInput);
    }

    showSendConfirmation(recipients) {
        const confirmDiv = document.createElement('div');
        confirmDiv.className = 'send-confirmation';
        confirmDiv.innerHTML = `
            <div style="background-color: #40414f; border-radius: 8px; padding: 20px; margin: 16px 0; border-left: 4px solid #f39c12;">
                <h3 style="color: #f39c12; margin-bottom: 12px;"><i class="fas fa-exclamation-triangle"></i> Ready to Send</h3>
                <p style="margin-bottom: 16px; color: #d1d5db;">You're about to send emails to ${recipients.length} recipients. This action cannot be undone.</p>
                <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="mailerAgent.confirmSendEmails(${JSON.stringify(recipients).replace(/"/g, '&quot;')})">
                        <i class="fas fa-paper-plane"></i> Send All Emails
                    </button>
                    <button class="btn btn-secondary" onclick="mailerAgent.cancelSend()">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                </div>
            </div>
        `;
        
        this.messagesContainer.appendChild(confirmDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    async confirmSendEmails(recipients) {
        this.showLoading();
        
        try {
            const response = await fetch('/api/send-emails', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email_template: this.currentEmailTemplate,
                    recipients: recipients,
                    subject: 'Important Message'
                })
            });
            
            const data = await response.json();
            this.hideLoading();
            
            if (data.success) {
                this.addMessage('ai', `📧 ${data.message}`);
                
                // Show detailed results
                const successCount = data.results.filter(r => r.success).length;
                const failCount = data.results.length - successCount;
                
                if (failCount > 0) {
                    const failedEmails = data.results.filter(r => !r.success).map(r => r.email).join(', ');
                    this.addMessage('ai', `⚠️ ${failCount} emails failed to send: ${failedEmails}`);
                }
            } else {
                this.addMessage('ai', `❌ Error sending emails: ${data.error}`);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage('ai', `❌ Error sending emails: ${error.message}`);
        }
    }

    cancelSend() {
        this.addMessage('ai', 'Email sending cancelled. You can upload a different file or modify the template if needed.');
    }

    handleSendManually() {
        this.addMessage('ai', 'For manual sending, you can copy the email template and customize it for each recipient. Would you like me to help you create variations for specific recipients?');
    }

    handleCopyTemplate() {
        // Get the current email template
        const emailContent = this.currentEmailTemplate || document.getElementById('emailPreview').textContent;
        navigator.clipboard.writeText(emailContent).then(() => {
            this.addMessage('ai', '📋 Email template copied to clipboard! You can now paste it into your email client.');
        }).catch(() => {
            this.addMessage('ai', 'Unable to copy to clipboard. Please manually select and copy the email content from the preview.');
        });
    }

    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }

    handleKeyDown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }
}

// Global functions for HTML onclick events
function startNewConversation() {
    mailerAgent.startNewConversation();
}

function useExample(text) {
    mailerAgent.useExample(text);
}

function sendMessage() {
    mailerAgent.sendMessage();
}

function closeModal() {
    mailerAgent.closeModal();
}

function requestRevision() {
    mailerAgent.requestRevision();
}

function approveEmail() {
    mailerAgent.approveEmail();
}

function handleKeyDown(event) {
    mailerAgent.handleKeyDown(event);
}

// Initialize the application
const mailerAgent = new MailerAgent();

// Initialize with welcome screen
document.addEventListener('DOMContentLoaded', () => {
    mailerAgent.startNewConversation();
});
