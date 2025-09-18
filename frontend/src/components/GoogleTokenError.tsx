import React from 'react';
import styled from 'styled-components';

interface GoogleTokenErrorProps {
  error: string;
  onReauthenticate?: () => void;
  onRetry?: () => void;
}

const ErrorContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  border-radius: 12px;
  color: white;
  margin: 1rem 0;
  text-align: center;
`;

const ErrorIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
`;

const ErrorTitle = styled.h3`
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
  font-weight: 600;
`;

const ErrorMessage = styled.p`
  margin: 0 0 1.5rem 0;
  font-size: 1rem;
  line-height: 1.5;
  opacity: 0.9;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
`;

const ActionButton = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  ${props => props.variant === 'primary' ? `
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
    
    &:hover {
      background: rgba(255, 255, 255, 0.3);
      border-color: rgba(255, 255, 255, 0.5);
    }
  ` : `
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.2);
    
    &:hover {
      background: rgba(255, 255, 255, 0.2);
    }
  `}
`;

const GoogleTokenError: React.FC<GoogleTokenErrorProps> = ({ 
  error, 
  onReauthenticate, 
  onRetry 
}) => {
  const isAuthError = error.includes('sign in') || error.includes('expired') || error.includes('authentication');
  
  const handleReauth = () => {
    // Clear any stored tokens
    sessionStorage.removeItem('google_access_token');
    sessionStorage.removeItem('google_token_expiry');
    
    if (onReauthenticate) {
      onReauthenticate();
    } else {
      // Refresh the page to restart the auth flow
      window.location.reload();
    }
  };

  return (
    <ErrorContainer>
      <ErrorIcon>❌</ErrorIcon>
      <ErrorTitle>Google Authentication Error</ErrorTitle>
      <ErrorMessage>{error}</ErrorMessage>
      
      <ButtonGroup>
        {isAuthError ? (
          <ActionButton variant="primary" onClick={handleReauth}>
            Sign In with Google Again
          </ActionButton>
        ) : (
          <ActionButton variant="primary" onClick={onRetry}>
            Try Again
          </ActionButton>
        )}
        
        <ActionButton variant="secondary" onClick={() => window.location.reload()}>
          Refresh Page
        </ActionButton>
      </ButtonGroup>
    </ErrorContainer>
  );
};

export default GoogleTokenError;
