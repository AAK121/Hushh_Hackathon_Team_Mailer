import React from 'react';
import MailerPandaUI from './MailerPandaUI';

interface MailerPandaAgentProps {
  onBack: () => void;
}

const MailerPandaAgent: React.FC<MailerPandaAgentProps> = ({ onBack }) => {
  return <MailerPandaUI onBack={onBack} />;
};

export default MailerPandaAgent;
