export interface Email {
  id: string;
  from: {
    email: string;
    name: string;
  };
  to: {
    email: string;
    name: string;
  }[];
  cc?: {
    email: string;
    name: string;
  }[];
  bcc?: {
    email: string;
    name: string;
  }[];
  subject: string;
  body: string;
  timestamp: string;
  isRead: boolean;
  isStarred: boolean;
  labels: string[];
  attachments?: {
    id: string;
    name: string;
    size: number;
    type: string;
  }[];
}

export interface AIGeneratedEmail {
  subject: string;
  body: string;
  reasoning: string;
}
