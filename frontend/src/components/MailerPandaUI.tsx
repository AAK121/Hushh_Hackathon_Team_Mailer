import React, { useState } from 'react';
import './MailerPandaUI.css';
import { useAuth } from '../contexts/AuthContext';
import { hushMcpApi } from '../services/hushMcpApi';

// Interface definitions for backend integration
interface GeneratedEmail {
  subject: string;
  content: string;
}

interface CampaignResponse {
  campaign_id?: string;
  status: string;
  email_template?: {
    subject: string;
    body: string;
  };
  recipient_count?: number;
  approval_status?: string;
  requires_approval?: boolean;
  errors?: string[];
  message?: string;
  processing_time?: number;
  emails_sent?: number;
  recipients_processed?: number;
  results?: any; // For flexible response handling
  [key: string]: any; // Allow additional dynamic properties
}

interface MailerPandaUIProps {
  onBack?: () => void;
}

// --- Main MailerPanda UI Component ---
function MailerPandaUI({ onBack }: MailerPandaUIProps) {
  // Auth context for user information and token generation
  const { user } = useAuth();
  
  // State to manage the overall flow of the UI
  // 'INITIAL' -> 'DRAFT_REVIEW' -> 'SUGGESTING_CHANGES' OR 'FINAL_CONFIRMATION' -> 'SENT'
  const [uiState, setUiState] = useState('INITIAL');
  
  // State for user inputs
  const [userInput, setUserInput] = useState('');
  const [excelFile, setExcelFile] = useState<File | null>(null);
  const [suggestion, setSuggestion] = useState('');
  const [useContextPersonalization, setUseContextPersonalization] = useState(false);

  // State to hold the response from the backend
  const [generatedEmail, setGeneratedEmail] = useState<GeneratedEmail>({ subject: '', content: '' });

  // State for loading indicators
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // --- Handlers for User Actions ---

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setExcelFile(file);
    }
  };

  const handleGenerateClick = async () => {
    if (!userInput) {
      alert('Please enter a command for the mailing agent.');
      return;
    }

    if (!user?.id) {
      alert('User not authenticated. Please log in.');
      return;
    }

    console.log("Sending to backend:", { command: userInput, file: excelFile?.name });
    setIsLoading(true);
    setError(''); // Clear any previous errors

    try {
      // Generate fresh consent tokens using the same pattern as AIAgentChat
      console.log("Generating fresh consent tokens for user:", user.id);
      let consentTokens;
      try {
        consentTokens = await hushMcpApi.createMailerPandaTokens(user.id);
        console.log("Generated consent tokens:", consentTokens);
      } catch (tokenError) {
        console.error("Failed to generate consent tokens:", tokenError);
        setError('Failed to generate authentication tokens. Please try again.');
        setIsLoading(false);
        return;
      }

      // Use hushMcpApi to send request with proper API configuration
      // Include sample recipient emails if no Excel file is provided
      const recipientEmails = excelFile ? undefined : [
        'test1@example.com',
        'test2@example.com'
      ];
      
      const data: CampaignResponse = await hushMcpApi.executeMailerPanda({
        user_id: user.id,
        user_input: `Please generate an email template with subject and body for: ${userInput}. 
                     Requirements: 
                     - Return email_template with subject and body fields
                     - Excel file: ${excelFile ? excelFile.name : 'none provided'}
                     - Personalization: ${useContextPersonalization ? 'enabled' : 'disabled'}
                     - This is for review approval, not immediate sending
                     - Ensure the response includes email_template.subject and email_template.body`,
        mode: 'interactive',
        consent_tokens: consentTokens,
        sender_email: user.email || 'test@example.com',
        recipient_emails: recipientEmails,
        require_approval: true,
        use_ai_generation: true,
        
        // Personalization settings (matching backend expectations)
        enable_description_personalization: useContextPersonalization,
        excel_file_path: excelFile ? excelFile.name : undefined,
        personalization_mode: 'smart',
        
        // API keys (get from environment or use fallback)
        google_api_key: import.meta.env.VITE_GOOGLE_API_KEY || import.meta.env.VITE_OPENAI_API_KEY || 'AIzaSyCyTIMomAZ-EtebfSToII2gwLo8pInVXwY',
        mailjet_api_key: 'cca56ed08f5272f813370d7fc5a34a24',
        mailjet_api_secret: '60fb43675233e2ac775f1c6cb8fe455c'
      });

      console.log("Backend response:", data);
      console.log("Response status:", data.status);
      console.log("Email template:", data.email_template);
      console.log("Emails sent:", data.emails_sent);
      console.log("Full response JSON:", JSON.stringify(data, null, 2));

      // Simple, strict handling - no fallbacks at all
      if (data.status === 'completed' && data.emails_sent !== undefined && data.emails_sent > 0) {
        // Emails were sent directly
        setUiState('SENT');
      } else if (data.email_template && data.email_template.subject && data.email_template.body) {
        // Valid email template received
        setGeneratedEmail({
          subject: data.email_template.subject,
          content: data.email_template.body
        });
        setUiState('DRAFT_REVIEW');
      } else {
        // Any other case is an error - show exactly what happened
        throw new Error(`Backend Error - Status: ${data.status} | Email Template: ${data.email_template ? 'Present but incomplete' : 'Missing'} | Full Response: ${JSON.stringify(data)}`);
      }
      
    } catch (error) {
      console.error('Error calling backend:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(`Error generating email: ${errorMessage}`);
      setUiState('INITIAL'); // Return to initial state on error
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleApprove = () => {
    setUiState('FINAL_CONFIRMATION');
  };

  const handleSuggestChanges = () => {
    setUiState('SUGGESTING_CHANGES');
  };

  const handleSubmitSuggestion = async () => {
    if (!suggestion) {
        alert('Please enter your suggestions.');
        return;
    }
    
    console.log("Sending suggestions to backend:", suggestion);
    setIsLoading(true);

    try {
      // Send approval request with modification feedback using hushMcpApi
      const data = await hushMcpApi.executeMailerPanda({
        user_id: user?.id || 'frontend_user_123',
        user_input: `Modify email with feedback: ${suggestion}. Please regenerate the email template based on this feedback and return email_template with subject and body fields.`,
        mode: 'interactive',
        consent_tokens: {},
        require_approval: true,
        use_ai_generation: true
      });

      console.log("Modification response:", data);

      // Check if we got a new email template
      if (data.email_template && (data.status === 'awaiting_approval' || data.status === 'completed')) {
        // Update the generated email content with the modified version
        setGeneratedEmail({
          subject: data.email_template.subject || 'Modified Email',
          content: data.email_template.body || 'No content generated'
        });
        
        // Clear the suggestion and go back to review state
        setSuggestion('');
        setUiState('DRAFT_REVIEW');
        
        console.log("Modified email template received:", data.email_template);
      } else {
        throw new Error(`Modification failed: ${data.status}`);
      }
      
    } catch (error) {
      console.error('Error submitting suggestions:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(`Error submitting suggestions: ${errorMessage}`);
      setUiState('SUGGESTING_CHANGES'); // Stay in the suggestion state to allow retry
    } finally {
      setIsLoading(false);
    }
  };

  const handleFinalSend = async () => {
    console.log("Final approval received! Sending emails now.");
    setIsLoading(true);

    try {
      // Send final approval using hushMcpApi
      const data = await hushMcpApi.executeMailerPanda({
        user_id: user?.id || 'frontend_user_123',
        user_input: 'Final approval - send emails',
        mode: 'batch',
        consent_tokens: {},
        require_approval: false
      });

      console.log("Final approval response:", data);

      setUiState('SENT');
      
    } catch (error) {
      console.error('Error sending final approval:', error);
      alert('Error sending emails. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelSend = () => {
    setUiState('DRAFT_REVIEW'); // Go back to the review screen
  };

  const handleReset = () => {
    setUiState('INITIAL');
    setUserInput('');
    setExcelFile(null);
    setSuggestion('');
    setGeneratedEmail({ subject: '', content: '' });
  };

  // --- Render Functions for each UI State ---

  const renderInitialState = () => (
    <div className="card">
      <h2>MailerPanda Assistant</h2>
      <p>Upload a contact sheet (optional) and tell me what to do.</p>
      
      <div className="file-input-wrapper">
        <button className="btn-file">
          {excelFile ? `✔️ ${excelFile.name}` : 'Upload Excel Sheet'}
        </button>
        <input 
          type="file" 
          accept=".xlsx, .xls, .csv"
          onChange={handleFileChange} 
        />
      </div>

      <div className="checkbox-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={useContextPersonalization}
            onChange={(e) => setUseContextPersonalization(e.target.checked)}
          />
          <span className="checkmark"></span>
          Use context personalization from description column in Excel sheet
        </label>
      </div>

      <div className="input-group">
        <input
          type="text"
          className="main-input"
          placeholder="e.g., 'Draft an email to clients about our new pricing...'"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleGenerateClick()}
        />
        <button onClick={handleGenerateClick} disabled={isLoading}>
          {isLoading ? 'Generating...' : '➤'}
        </button>
      </div>

      {onBack && (
        <button className="btn-back" onClick={onBack}>
          ← Back to Agents
        </button>
      )}
    </div>
  );

  const renderDraftReviewState = () => (
    <div className="card">
      <h2>Review Generated Draft</h2>
      <div className="email-display">
        <p><strong>Subject:</strong> {generatedEmail.subject}</p>
        <div className="email-content">
          <p>{generatedEmail.content}</p>
        </div>
      </div>
      <div className="button-group">
        <button className="btn-approve" onClick={handleApprove}>Approve Content</button>
        <button className="btn-suggest" onClick={handleSuggestChanges}>Suggest Changes</button>
      </div>
    </div>
  );

  const renderSuggestChangesState = () => (
    <div className="card">
        <h2>Suggest Changes</h2>
        <p>Your suggestions will be used to generate a new draft.</p>
        <textarea
            className="suggestion-box"
            placeholder="e.g., 'Make the tone more casual', 'Mention the 20% discount for early birds...'"
            value={suggestion}
            onChange={(e) => setSuggestion(e.target.value)}
        />
        <div className="button-group">
            <button onClick={handleSubmitSuggestion} disabled={isLoading}>
              {isLoading ? 'Submitting...' : 'Submit Suggestions'}
            </button>
            <button className="btn-secondary" onClick={() => setUiState('DRAFT_REVIEW')}>Back to Review</button>
        </div>
    </div>
  );

  const renderFinalConfirmationState = () => (
    <div className="card confirmation-card">
      <h2>Final Confirmation</h2>
      <p>Are you sure you want to send this email to all contacts in the provided list?</p>
      <div className="button-group">
        <button className="btn-danger" onClick={handleFinalSend} disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Yes, Send Mail'}
        </button>
        <button className="btn-secondary" onClick={handleCancelSend}>No, Go Back</button>
      </div>
    </div>
  );

  const renderSentState = () => (
    <div className="card">
        <h2>✅ Success!</h2>
        <p>The emails have been queued for sending.</p>
        <button onClick={handleReset}>Start a New Task</button>
    </div>
  );

  // --- Main Render Logic ---
  const renderCurrentState = () => {
    // Show error message if there's an error
    if (error) {
      return (
        <div className="card">
          <h2>❌ Error</h2>
          <div className="error-message" style={{ 
            backgroundColor: '#fee', 
            border: '1px solid #fcc', 
            padding: '10px', 
            borderRadius: '5px',
            marginBottom: '20px',
            color: '#900'
          }}>
            {error}
          </div>
          <button 
            className="btn-primary" 
            onClick={() => setError('')}
          >
            Try Again
          </button>
          <button 
            className="btn-secondary" 
            onClick={handleReset}
            style={{ marginLeft: '10px' }}
          >
            Reset
          </button>
        </div>
      );
    }

    if (isLoading && (uiState === 'FINAL_CONFIRMATION' || uiState === 'SENT')) {
      return (
        <div className="card">
          <h2>Sending Emails...</h2>
          <p>This may take a moment.</p>
        </div>
      );
    }

    switch (uiState) {
      case 'DRAFT_REVIEW':
        return renderDraftReviewState();
      case 'SUGGESTING_CHANGES':
        return renderSuggestChangesState();
      case 'FINAL_CONFIRMATION':
        return renderFinalConfirmationState();
      case 'SENT':
        return renderSentState();
      case 'INITIAL':
      default:
        return renderInitialState();
    }
  };

  return (
    <div className="app-container">
      {renderCurrentState()}
    </div>
  );
}

export default MailerPandaUI;
