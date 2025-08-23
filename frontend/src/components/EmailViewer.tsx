import React from 'react';
import { 
  ArrowLeftIcon, 
  StarIcon, 
  TrashIcon, 
  ArrowUturnLeftIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';
import type { Email } from '../types/email';

interface EmailViewerProps {
  email: Email | null;
  onBack: () => void;
  onReply: (email: Email) => void;
  onToggleStar: (emailId: string) => void;
  onDelete: (emailId: string) => void;
}

const EmailViewer: React.FC<EmailViewerProps> = ({ 
  email, 
  onBack, 
  onReply, 
  onToggleStar, 
  onDelete 
}) => {
  if (!email) {
    return (
      <div className="flex-1 bg-transparent flex items-center justify-center">
        <div className="text-center text-white">
          <div className="text-4xl mb-4">📧</div>
          <h3 className="text-lg font-medium mb-2">Select an email</h3>
          <p className="text-white/70">Choose an email from the list to view its contents.</p>
        </div>
      </div>
    );
  }

  const formatDateTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const formatEmailList = (recipients: { email: string; name: string }[]) => {
    return recipients.map(r => `${r.name} <${r.email}>`).join(', ');
  };

  return (
    <div className="flex-1 bg-black flex flex-col">
      {/* Header */}
      <div className="border-b border-white/20 p-4 bg-white/10 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={onBack}
            className="p-2 hover:bg-white/10 rounded-lg text-white"
          >
            <ArrowLeftIcon className="w-5 h-5 text-black" color="black" overlineThickness="24px"/>
          </button>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => onToggleStar(email.id)}
              className="p-2 hover:bg-white/10 rounded-lg"
            >
              {email.isStarred ? (
                <StarIconSolid className="w-5 h-5 text-yellow-400" />
              ) : (
                <StarIcon className="w-5 h-5 text-white/70" />
              )}
            </button>
            
            <button
              onClick={() => onDelete(email.id)}
              className="p-2 hover:bg-white/10 rounded-lg text-red-400"
            >
              <TrashIcon className="w-5 h-5" />
            </button>
            
            <button className="p-2 hover:bg-white/10 rounded-lg text-white/70">
              <EllipsisVerticalIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Subject */}
        <h1 className="text-2xl font-bold text-white mb-4">
          {email.subject}
        </h1>

        {/* Email details */}
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-medium">
              {email.from.name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-white">
                    {email.from.name}
                  </div>
                  <div className="text-sm text-white">
                    {email.from.email}
                  </div>
                </div>
                <div className="text-sm text-white">
                  {formatDateTime(email.timestamp)}
                </div>
              </div>
              
              <div className="mt-2 text-sm text-white">
                <div>
                  <strong>To:</strong> {formatEmailList(email.to)}
                </div>
                {email.cc && email.cc.length > 0 && (
                  <div>
                    <strong>CC:</strong> {formatEmailList(email.cc)}
                  </div>
                )}
                {email.bcc && email.bcc.length > 0 && (
                  <div>
                    <strong>BCC:</strong> {formatEmailList(email.bcc)}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Email body */}
      <div className="flex-1 p-6 overflow-y-auto bg-white/5 backdrop-blur-sm">
        <div className="prose max-w-none">
          <div style={{ whiteSpace: 'pre-wrap' }} className="text-white leading-relaxed">
            {email.body}
          </div>
        </div>

        {/* Attachments */}
        {email.attachments && email.attachments.length > 0 && (
          <div className="mt-6 border-t border-white/20 pt-4">
            <h3 className="text-sm font-medium text-white mb-3">
              Attachments ({email.attachments.length})
            </h3>
            <div className="space-y-2">
              {email.attachments.map((attachment) => (
                <div 
                  key={attachment.id}
                  className="flex items-center gap-3 p-3 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20"
                >
                  <div className="w-8 h-8 bg-blue-400/20 rounded flex items-center justify-center">
                    📎
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-sm text-white">{attachment.name}</div>
                    <div className="text-xs text-white/70">
                      {(attachment.size / 1024 / 1024).toFixed(2)} MB
                    </div>
                  </div>
                  <button className="text-blue-300 hover:text-blue-100 text-sm font-medium">
                    Download
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="border-t border-white/20 p-4 bg-white/10 backdrop-blur-sm">
        <div className="flex gap-3">
          <button
            onClick={() => onReply(email)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500/80 text-black rounded-lg hover:bg-blue-500 transition-colors backdrop-blur-sm"
          >
            <ArrowUturnLeftIcon className="w-4 h-4" />
            Reply
          </button>
          
          <button
            onClick={() => onReply(email)}
            className="flex items-center gap-2 px-4 py-2 border border-white/30 text-black rounded-lg hover:bg-white/20 hover:text-white transition-colors backdrop-blur-sm bg-white/5"
          >
            Reply All
          </button>
          
          <button
            onClick={() => onReply(email)}
            className="flex items-center gap-2 px-4 py-2 border border-white/30 text-black rounded-lg hover:bg-white/20 hover:text-white transition-colors backdrop-blur-sm bg-white/5"
          >
            Forward
          </button>
        </div>
      </div>
    </div>
  );
};

export default EmailViewer;
