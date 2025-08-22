// API Types for Research Agent Frontend

export interface ArxivPaper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  arxiv_id: string;
  published: string;
  updated: string;
  pdf_url: string;
  summary_url: string;
}

export interface ArxivSearchRequest {
  query: string;
  max_results?: number;
}

export interface ArxivSearchResponse {
  papers: ArxivPaper[];
  total_results: number;
  query: string;
}

export interface PaperUploadResponse {
  paper_id: string;
  filename: string;
  title?: string;
  status: string;
  message: string;
}

export interface PaperSummaryResponse {
  paper_id: string;
  summary: string;
  status: string;
  processing_time: number;
}

export interface SnippetProcessRequest {
  text: string;
  instruction: string;
}

export interface SnippetProcessResponse {
  result: string;
  instruction: string;
  original_text: string;
  processing_time: number;
}

export interface SaveNotesRequest {
  paper_id: string;
  editor_id: string;
  content: string;
}

export interface SaveNotesResponse {
  success: boolean;
  message: string;
  editor_id: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// Frontend State Types

export interface PdfHighlight {
  text: string;
  page: number;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface NotebookEditor {
  id: string;
  name: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  paper_id?: string;
  snippet?: string;
}

export interface AppState {
  currentPaper: ArxivPaper | null;
  searchResults: ArxivPaper[];
  isSearching: boolean;
  isLoadingPaper: boolean;
  isProcessingSnippet: boolean;
  chatMessages: ChatMessage[];
  notebooks: NotebookEditor[];
  selectedText: string;
  currentPage: number;
  showUploadModal: boolean;
  error: string | null;
}

export interface PanelSizes {
  pdfPanel: number;
  chatPanel: number;
  notebookPanel: number;
}

// Component Props Types

export interface PdfViewerProps {
  pdfUrl: string;
  onTextSelect: (text: string) => void;
  currentPage: number;
  onPageChange: (page: number) => void;
}

export interface ChatPanelProps {
  messages: ChatMessage[];
  searchResults: ArxivPaper[];
  isSearching: boolean;
  onSearch: (query: string) => void;
  onPaperSelect: (paper: ArxivPaper) => void;
  onSnippetProcess: (text: string, instruction: string) => void;
  selectedText: string;
}

export interface NotebookPanelProps {
  notebooks: NotebookEditor[];
  onCreateNotebook: (name: string) => void;
  onUpdateNotebook: (id: string, content: string) => void;
  onDeleteNotebook: (id: string) => void;
  onSaveNotes: (editorId: string, content: string) => void;
}

export interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

export interface FileUploadProps {
  onFileUpload: (file: File) => void;
  isUploading: boolean;
  acceptedTypes?: string[];
}
