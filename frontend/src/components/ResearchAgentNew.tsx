import React, { useRef, useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeHighlight from 'rehype-highlight';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import './ResearchAgentNew.css';
import './force-cache-refresh.css';
import './scrollbar-override.css';
import { researchAgentApi, Paper } from '../services/ResearchAgentApi';

// Chat message interface
interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'ai' | 'system';
  timestamp: Date;
}

const ResearchAgentNew: React.FC = () => {
  const [leftPanelWidth, setLeftPanelWidth] = useState(55); // Initial width as percentage
  const [isResizing, setIsResizing] = useState(false);
  const [activeView, setActiveView] = useState<'abstract' | 'pdf'>('abstract');
  
  // Chat-related state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [originalChatMessages, setOriginalChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  
  // Research-related state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Paper[]>([]);
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected'>('disconnected');
  
  // Modal and notes state
  const [showNotesModal, setShowNotesModal] = useState(false);
  const [showEditNotesModal, setShowEditNotesModal] = useState(false);
  const [showNotesListModal, setShowNotesListModal] = useState(false);
  const [showNoteSelectionModal, setShowNoteSelectionModal] = useState(false);
  const [pendingAiResponse, setPendingAiResponse] = useState<string>('');
  const [notesFileName, setNotesFileName] = useState('');
  const [currentNotes, setCurrentNotes] = useState('');
  const [editingNotesName, setEditingNotesName] = useState('');
  const [editingNotesContent, setEditingNotesContent] = useState('');
  const [savedNotes, setSavedNotes] = useState<Record<string, string>>({});
  const [selectedNotesName, setSelectedNotesName] = useState<string>('current');
  const [currentNoteMessageId, setCurrentNoteMessageId] = useState<string | null>(null);
  
  // Upload-related state
  const [uploadedPaper, setUploadedPaper] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedPaperData, setUploadedPaperData] = useState<Paper | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing || !containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      
      // Constrain the width between 20% and 80%
      const constrainedWidth = Math.min(Math.max(newLeftWidth, 20), 80);
      setLeftPanelWidth(constrainedWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const handleMouseDown = () => {
    setIsResizing(true);
  };

  const handleViewChange = (view: 'abstract' | 'pdf') => {
    setActiveView(view);
  };

  // Chat functionality
  const addChatMessage = (message: ChatMessage) => {
    setChatMessages(prev => [...prev, message]);
  };

  const generateId = () => {
    return Math.random().toString(36).substr(2, 9);
  };

  const handleSendMessage = async () => {
    const message = chatInput.trim();
    if (!message || isSendingMessage) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: generateId(),
      content: message,
      role: 'user',
      timestamp: new Date()
    };
    addChatMessage(userMessage);
    setChatInput('');
    setIsSendingMessage(true);

    try {
      // Enhanced message with paper context if available
      let enhancedMessage = message;
      if (selectedPaper) {
        enhancedMessage = `Context: I'm discussing the paper "${selectedPaper.title}" by ${selectedPaper.authors.join(', ')}. 

Paper Summary: ${selectedPaper.summary}

Paper ID: ${selectedPaper.arxiv_id}
Categories: ${selectedPaper.categories.join(', ')}

User Question: ${message}`;
      }

      // Send message to research agent API
      const response = await researchAgentApi.sendChatMessage(enhancedMessage, selectedPaper?.id);
      
      const aiMessage: ChatMessage = {
        id: generateId(),
        content: response.message,
        role: 'ai',
        timestamp: new Date()
      };
      addChatMessage(aiMessage);
      // Remove automatic note saving - user will choose manually using save button
      
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Display error message to user
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: `Sorry, I couldn't process your request. The research agent appears to be unavailable. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        role: 'ai',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
    } finally {
      setIsSendingMessage(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Search functionality
  const handleSearch = async () => {
    const query = searchQuery.trim();
    if (!query || isSearching) return;

    setIsSearching(true);
    
    try {
      const response = await researchAgentApi.searchPapers(query, 20);
      setSearchResults(response.papers);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: `Search failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
    } finally {
      setIsSearching(false);
    }
  };

  const handlePaperSelect = (paper: Paper) => {
    setSelectedPaper(paper);
    
    // Remove paper selection notification - user can see it's selected in the UI
    /*
    const systemMessage: ChatMessage = {
      id: generateId(),
      content: `Selected paper: "${paper.title}" by ${paper.authors.join(', ')}. You can now ask questions about this paper.`,
      role: 'system',
      timestamp: new Date()
    };
    addChatMessage(systemMessage);
    */
  };

  // Handle paper upload
  const handlePaperUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file only.');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB.');
      return;
    }

    setIsUploading(true);
    setUploadedPaper(file);

    try {
      // Upload to backend for processing
      const uploadResult = await researchAgentApi.uploadPDF(file);

      // Create a Paper object from the upload result
      const uploadedPaperObj: Paper = {
        id: uploadResult.paper_id,
        title: file.name.replace('.pdf', ''),
        authors: ['Uploaded Document'],
        published: new Date().toISOString().split('T')[0],
        arxiv_id: uploadResult.paper_id,
        categories: ['uploaded'],
        summary: `Uploaded PDF document with ${uploadResult.text_length} characters extracted`,
        pdf_url: URL.createObjectURL(file)
      };

      setUploadedPaperData(uploadedPaperObj);
      setSelectedPaper(uploadedPaperObj);

      // Add system message about successful upload
      const systemMessage: ChatMessage = {
        id: generateId(),
        content: `📄 Successfully uploaded and processed "${file.name}". 

✅ **PDF Analysis Ready**: ${uploadResult.text_length} characters extracted
✅ **AI Chat Available**: Ask questions about this document
✅ **Note Saving**: Save responses to your notes
✅ **Backend Processed**: Full document analysis available

You can now ask detailed questions about the content of this document!`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(systemMessage);

      // Clear search results since we're now working with uploaded paper
      setSearchResults([]);
      setSearchQuery('');

    } catch (error) {
      console.error('Error uploading paper:', error);
      alert(`Failed to upload paper: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsUploading(false);
      // Clear the input so the same file can be uploaded again if needed
      event.target.value = '';
    }
  };

  // Notes functionality
  const handleNotesModalOpen = () => {
    setShowNotesModal(true);
  };

  // Create a new blank note directly
  const handleCreateNewNote = async () => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
    const defaultName = `Note_${timestamp}_${Math.random().toString(36).substr(2, 4)}`;
    
    const noteName = prompt('Enter a name for your new note:', defaultName);
    if (!noteName || !noteName.trim()) {
      return; // User cancelled or entered empty name
    }

    const finalNoteName = noteName.trim();
    
    // Check if note name already exists
    if (savedNotes[finalNoteName]) {
      alert('A note with this name already exists. Please choose a different name.');
      return;
    }

    try {
      // Create blank note using updateNote (which saves exactly what we give it)
      await researchAgentApi.updateNote(finalNoteName, '');
      
      // Update local state
      setSavedNotes(prev => ({
        ...prev,
        [finalNoteName]: ''
      }));
      
      // Add success message
      const successMessage: ChatMessage = {
        id: generateId(),
        content: `✅ Created new blank note: "${finalNoteName}"`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(successMessage);
      
      // Reload notes to update UI
      await loadNotesFromVault();
      
    } catch (error) {
      console.error('Failed to create new note:', error);
      alert(`Failed to create note: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleCreateNotes = async () => {
    if (!notesFileName.trim()) {
      alert('Please enter a notes file name');
      return;
    }

    // Check if note name already exists
    if (savedNotes[notesFileName]) {
      alert('A note with this name already exists. Please choose a different name.');
      return;
    }

    const fileName = notesFileName; // Remove timestamp to use clean name
    const contentToSave = currentNotes.trim() || ''; // Always create blank notes

    await saveNotesToVault(fileName, contentToSave);
    setCurrentNotes('');
    setNotesFileName('');
    setSelectedNotesName('current'); // Reset dropdown to current session
    setShowNotesModal(false);

    // If there's a pending AI response, go back to the note selection modal
    if (pendingAiResponse) {
      // Refresh notes to include the newly created note
      await loadNotesFromVault();
      setTimeout(() => {
        setShowNoteSelectionModal(true);
      }, 100);
    }
  };

  const handleEditNotes = async (notesName: string) => {
    console.log('✏️ handleEditNotes called for:', notesName);

    try {
      setEditingNotesName(notesName);
      
      // Load the note content from the vault
      console.log('Loading note content from vault...');
      const content = await researchAgentApi.getNote(notesName);
      console.log('Note content loaded:', {
        noteName: notesName,
        contentLength: content?.length || 0,
        isEmpty: !content || content.trim() === ''
      });
      
      setEditingNotesContent(content || savedNotes[notesName] || '');
      
      setShowEditNotesModal(true);
      setShowNotesListModal(false);
      
      console.log('Edit modal opened successfully');
      
    } catch (error) {
      console.error('Failed to load note for editing:', error);
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: `Failed to load note "${notesName}": ${error instanceof Error ? error.message : 'Unknown error'}`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
    }
  };

  const handleShowNotesListForEdit = () => {
    const notesNames = Object.keys(savedNotes);
    if (notesNames.length > 0) {
      setShowNotesListModal(true);
    } else {
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: 'No saved notes to edit. Please create notes first.',
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
    }
  };

  const handleSaveEditedNotes = async () => {
    console.log('🔧 handleSaveEditedNotes called:', {
      editingNotesName,
      editingNotesContentLength: editingNotesContent.length,
      isEmpty: editingNotesContent.trim() === ''
    });

    if (!editingNotesName.trim()) {
      console.warn('Save aborted: missing notes name', {
        editingNotesName
      });
      alert('Please make sure you have a valid note name.');
      return;
    }
    
    try {
      console.log('Saving edited notes:', {
        noteName: editingNotesName,
        contentLength: editingNotesContent.length,
        isEmpty: editingNotesContent.trim() === ''
      });
      
      // Allow saving empty content (user might want to clear the note)
      const contentToSave = editingNotesContent; // Don't trim, preserve user's intent
      
      // Update the note using the API
      console.log('🔄 Calling API updateNote...');
      await researchAgentApi.updateNote(editingNotesName, contentToSave);
      console.log('✅ API updateNote completed successfully');
      
      // Update local state
      setSavedNotes(prev => ({
        ...prev,
        [editingNotesName]: contentToSave
      }));
      console.log('✅ Local state updated');

      // Reload notes from vault to ensure consistency
      console.log('🔄 Reloading notes from vault...');
      await loadNotesFromVault();
      console.log('✅ Notes reloaded from vault');
      
      setShowEditNotesModal(false);
      setEditingNotesName('');
      setEditingNotesContent('');
      
      // Add success message to show user the save worked
      const successMessage: ChatMessage = {
        id: generateId(),
        content: contentToSave.trim() === '' ? 
          `✅ Notes "${editingNotesName}" cleared successfully!` :
          `✅ Notes "${editingNotesName}" updated successfully!`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(successMessage);
      
      console.log('✅ Save operation completed successfully');
      
    } catch (error) {
      console.error('❌ Failed to save edited notes:', error);
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: `❌ Failed to update notes: ${error instanceof Error ? error.message : 'Unknown error'}`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
      
      // Also show an alert for immediate feedback
      alert(`Failed to save notes: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Save specific AI response to selected notes (called from message action button)
  const saveSpecificResponseToNotes = async (messageContent: string, messageId: string) => {
    try {
      console.log('🔄 Preparing to save AI response to notes...');
      
      // First refresh notes to get all current notes (including newly created ones)
      await loadNotesFromVault();
      console.log('✅ Notes refreshed from vault');
      
      // Create note entry with just the response content and separator
      const noteEntry = `${messageContent}\n--- Response ---\n`;
      
      // Store the response for note selection modal
      setPendingAiResponse(noteEntry);
      setCurrentNoteMessageId(messageId);
      setShowNoteSelectionModal(true);
      
      console.log('✅ Note selection modal opened');
      
    } catch (error) {
      console.error('❌ Failed to prepare AI response for saving:', error);
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: `❌ Failed to load notes. Please try again.`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
      
      alert('Failed to load notes. Please try again.');
    }
  };

  // Function to save AI response to selected note(s)
  const saveAiResponseToSelectedNotes = async (selectedNoteNames: string[]) => {
    try {
      console.log('🔄 Starting to save AI response to notes:', selectedNoteNames);
      console.log('📝 Pending AI response preview:', pendingAiResponse.substring(0, 100) + '...');
      
      // Always save to "AI Responses" first
      console.log('🔄 Getting existing AI Responses notes...');
      const existingAiNotes = await researchAgentApi.getNote('AI Responses') || '';
      console.log('📋 Existing AI notes length:', existingAiNotes.length);
      
      const updatedAiNotes = existingAiNotes + pendingAiResponse;
      console.log('🔄 Updating AI Responses notes with total length:', updatedAiNotes.length);
      await researchAgentApi.updateNote('AI Responses', updatedAiNotes);
      console.log('✅ Saved to AI Responses successfully');
      
      // Also save to user-selected notes
      for (const noteName of selectedNoteNames) {
        if (noteName !== 'AI Responses') {
          console.log(`🔄 Processing note: ${noteName}`);
          const existingNotes = await researchAgentApi.getNote(noteName) || '';
          console.log(`📋 Existing notes length for ${noteName}:`, existingNotes.length);
          const updatedNotes = existingNotes + pendingAiResponse;
          console.log(`🔄 Calling updateNote for ${noteName} with total length:`, updatedNotes.length);
          await researchAgentApi.updateNote(noteName, updatedNotes);
          console.log(`✅ Saved to ${noteName} successfully`);
        }
      }
      
      // Update local saved notes state to reflect the changes
      console.log('🔄 Updating local state...');
      setSavedNotes(prev => {
        console.log('📋 Previous saved notes:', Object.keys(prev));
        const updated = { ...prev };
        updated['AI Responses'] = updatedAiNotes;
        for (const noteName of selectedNoteNames) {
          if (noteName !== 'AI Responses') {
            const existingNotes = prev[noteName] || '';
            updated[noteName] = existingNotes + pendingAiResponse;
          }
        }
        console.log('✅ Updated saved notes:', Object.keys(updated));
        return updated;
      });
      
      console.log('AI response saved to selected notes:', selectedNoteNames);
      
      // Add success message to chat
      const successMessage: ChatMessage = {
        id: generateId(),
        content: `✅ AI response saved to notes: ${selectedNoteNames.join(', ')}`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(successMessage);
      
      // Reload notes to ensure consistency
      console.log('🔄 Reloading notes from vault...');
      await loadNotesFromVault();
      console.log('✅ Notes reloaded from vault');
      
      setPendingAiResponse('');
      setShowNoteSelectionModal(false);
      
    } catch (error) {
      console.error('Failed to save AI response to notes:', error);
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: `❌ Failed to save AI response to notes: ${error instanceof Error ? error.message : 'Unknown error'}`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
      
      alert(`Failed to save to notes: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Function to download notes as PDF
  const downloadNotesAsPDF = async (noteName: string, content: string) => {
    try {
      // Create a new window for printing
      const printWindow = window.open('', '_blank');
      if (!printWindow) {
        alert('Please allow popups to download PDF');
        return;
      }

      // Create HTML content for PDF
      const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>${noteName} - Research Notes</title>
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              line-height: 1.6;
              margin: 40px;
              color: #333;
            }
            h1, h2, h3, h4, h5, h6 {
              color: #2c3e50;
              margin-top: 24px;
              margin-bottom: 12px;
            }
            h1 {
              border-bottom: 2px solid #3498db;
              padding-bottom: 8px;
            }
            p {
              margin-bottom: 12px;
            }
            pre {
              background-color: #f8f9fa;
              border: 1px solid #e9ecef;
              border-radius: 4px;
              padding: 16px;
              overflow-x: auto;
            }
            code {
              background-color: #f8f9fa;
              padding: 2px 4px;
              border-radius: 3px;
              font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            }
            blockquote {
              border-left: 4px solid #3498db;
              margin: 0;
              padding-left: 16px;
              color: #666;
            }
            .header {
              text-align: center;
              margin-bottom: 40px;
              border-bottom: 1px solid #ddd;
              padding-bottom: 20px;
            }
            .footer {
              margin-top: 40px;
              border-top: 1px solid #ddd;
              padding-top: 20px;
              text-align: center;
              color: #666;
              font-size: 12px;
            }
            @media print {
              body { margin: 20px; }
              .no-print { display: none; }
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>${noteName}</h1>
            <p>Research Notes - Generated on ${new Date().toLocaleDateString()}</p>
          </div>
          <div class="content">
            ${content.replace(/\n/g, '<br>').replace(/#{1,6}\s/g, '<h3>').replace(/<h3>/g, '</p><h3>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>')}
          </div>
          <div class="footer">
            <p>Generated by Research Agent - ${new Date().toLocaleString()}</p>
          </div>
          <button class="no-print" onclick="window.print(); window.close();" style="position: fixed; top: 20px; right: 20px; padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">Download PDF</button>
        </body>
        </html>
      `;

      printWindow.document.write(htmlContent);
      printWindow.document.close();
      
      // Auto-trigger print dialog
      setTimeout(() => {
        printWindow.print();
      }, 500);
      
    } catch (error) {
      console.error('Failed to generate PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    }
  };

  // Load notes from vault
  const loadNotesFromVault = async () => {
    try {
      console.log('🔄 Loading notes from vault...');
      
      // Debug localStorage content
      console.log('🗄️ localStorage debugging:');
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('research_notes_')) {
          const value = localStorage.getItem(key);
          console.log(`Key: ${key}`, {
            rawValue: value,
            parsed: value ? JSON.parse(value) : null
          });
        }
      }
      
      const notes = await researchAgentApi.loadNotes();
      console.log('📋 Raw notes loaded:', notes);
      console.log('📊 Notes summary:', {
        totalNotes: Object.keys(notes).length,
        noteNames: Object.keys(notes),
        noteSizes: Object.keys(notes).map(name => ({
          name,
          size: notes[name]?.length || 0,
          isEmpty: !notes[name] || notes[name].trim() === ''
        }))
      });
      
      setSavedNotes(notes);
      console.log('✅ Notes loaded and state updated');
      
      // Add a system message when notes are loaded
      if (Object.keys(notes).length > 0) {
        // Remove this message - user doesn't need to see notes loaded notification
        /*
        const systemMessage: ChatMessage = {
          id: generateId(),
          content: `📝 Loaded ${Object.keys(notes).length} saved notes from vault.`,
          role: 'system',
          timestamp: new Date()
        };
        addChatMessage(systemMessage);
        */
      }
    } catch (error) {
      console.error('❌ Failed to load notes from vault:', error);
    }
  };

  // Parse note content to extract individual saved responses
  const parseNoteContent = (noteContent: string): ChatMessage[] => {
    if (!noteContent.trim()) {
      return [];
    }

    // Split by response separators (we'll use a consistent format)
    const responses = noteContent.split('\n--- Response ---\n').filter(content => content.trim());
    
    return responses.map((response, index) => ({
      id: generateId(),
      content: response.trim(),
      role: 'ai' as const,
      timestamp: new Date(Date.now() - (responses.length - index) * 60000) // Stagger timestamps
    }));
  };

  // Handle notes dropdown selection change
  const handleNotesDropdownChange = async (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = event.target.value;
    setSelectedNotesName(selectedValue);
    
    if (selectedValue === 'current') {
      // Restore original chat messages (exit note view mode)
      if (originalChatMessages.length > 0) {
        setChatMessages(originalChatMessages);
        setOriginalChatMessages([]); // Clear the backup
      }
      setCurrentNoteMessageId(null);
      setCurrentNotes(''); // Clear note content
      return;
    } else if (selectedValue === 'clear') {
      // Clear displayed notes and restore current session chat
      console.log('🧹 Clearing displayed notes...');
      
      // Always restore to original chat messages if they exist
      if (originalChatMessages.length > 0) {
        console.log('🔄 Restoring original chat messages');
        // Filter out system messages from the original messages
        const filteredMessages = originalChatMessages.filter(msg => msg.role !== 'system');
        setChatMessages(filteredMessages);
        setOriginalChatMessages([]);
      } else {
        // If no original messages backed up, filter current messages to remove system messages
        console.log('🧹 Filtering current messages to remove system messages');
        const filteredMessages = chatMessages.filter(msg => msg.role !== 'system');
        setChatMessages(filteredMessages);
      }
      
      setCurrentNoteMessageId(null);
      setSelectedNotesName('current'); // Reset to current session
      setCurrentNotes(''); // Clear any note content
      
      console.log('✅ Notes cleared, back to current session');
      return;
    } else {
      // Load the selected saved note and display ONLY its content (note view mode)
      try {
        const noteContent = await researchAgentApi.getNote(selectedValue);
        setCurrentNotes(noteContent);
        
        // Save current chat messages if not already saved
        if (originalChatMessages.length === 0) {
          setOriginalChatMessages(chatMessages);
        }
        
        // Parse note content to extract individual saved responses
        if (noteContent.trim()) {
          const savedResponses = parseNoteContent(noteContent);
          setChatMessages(savedResponses);
        } else {
          // Empty note - show placeholder
          const emptyNoteMessage: ChatMessage = {
            id: generateId(),
            content: `📝 Note "${selectedValue}" is empty. Start saving AI responses to this note!`,
            role: 'system',
            timestamp: new Date()
          };
          setChatMessages([emptyNoteMessage]);
        }
      } catch (error) {
        console.error('Failed to load note:', error);
      }
    }
  };

  // Handle delete notes
  const handleDeleteNote = async (noteName: string) => {
    console.log('🗑️ handleDeleteNote called for:', noteName);
    console.log('📊 Current savedNotes state:', Object.keys(savedNotes));
    console.log('🔍 Note exists in savedNotes?', savedNotes[noteName] !== undefined);

    if (confirm(`Are you sure you want to delete the note "${noteName}"? This action cannot be undone.`)) {
      try {
        console.log('✅ User confirmed deletion, proceeding...');
        console.log('🔧 Calling API deleteNote for:', noteName);
        
        await researchAgentApi.deleteNote(noteName);
        console.log('✅ API deleteNote completed successfully');
        
        // If the deleted note was currently selected, reset to current session
        if (selectedNotesName === noteName) {
          console.log('🔄 Resetting selected note to current session');
          setSelectedNotesName('current');
          setCurrentNotes('');
          
          // Also remove the note from chat if it's currently displayed
          if (currentNoteMessageId) {
            setChatMessages(prev => 
              prev.filter(msg => msg.id !== currentNoteMessageId)
            );
            setCurrentNoteMessageId(null);
          }
        }
        
        // Reload notes to update the list
        console.log('🔄 Reloading notes from vault...');
        await loadNotesFromVault();
        console.log('✅ Notes reloaded after deletion');

        // Add success message
        const successMessage: ChatMessage = {
          id: generateId(),
          content: `✅ Note "${noteName}" deleted successfully!`,
          role: 'system',
          timestamp: new Date()
        };
        addChatMessage(successMessage);

      } catch (error) {
        console.error('❌ Failed to delete note:', error);
        alert(`Failed to delete note: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    } else {
      console.log('❌ User cancelled deletion');
    }
  };

  const saveNotesToVault = async (fileName: string, content: string) => {
    try {
      // Save notes using the API with the user-provided filename
      await researchAgentApi.saveNotes({
        personal: content,
        research: selectedPaper?.summary || '',
        summary: `Notes for ${selectedPaper?.title || 'Research'}`,
        analysis: 'User generated notes'
      }, selectedPaper?.id, fileName);

      // Update local state with the filename
      setSavedNotes(prev => ({
        ...prev,
        [fileName]: content
      }));

      // Reload notes from vault to ensure consistency
      await loadNotesFromVault();

      // Remove notes save success message - user can see it in notes counter
      /*
      const systemMessage: ChatMessage = {
        id: generateId(),
        content: `✅ Notes "${fileName}" saved to vault successfully!`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(systemMessage);
      */

    } catch (error) {
      console.error('Failed to save notes to vault:', error);
    }
  };

  // Test connection on component mount
  useEffect(() => {
    const testConnection = async () => {
      try {
        const isConnected = await researchAgentApi.testConnection();
        setConnectionStatus(isConnected ? 'connected' : 'disconnected');
        
        if (isConnected) {
          // Connection successful - no need for system message
        } else {
          // Connection failed - silently handle
        }
      } catch (error) {
        setConnectionStatus('disconnected');
      }
    };

    testConnection();
  }, []);

  // Load notes after connection is established
  useEffect(() => {
    if (connectionStatus === 'connected') {
      loadNotesFromVault();
      initializeAiResponsesNotes();
    }
  }, [connectionStatus]);

  // Initialize AI Responses notes if they don't exist
  const initializeAiResponsesNotes = async () => {
    try {
      console.log('🔄 Initializing AI Responses notes...');
      
      // Test localStorage functionality first
      try {
        localStorage.setItem('test_key', 'test_value');
        const testValue = localStorage.getItem('test_key');
        localStorage.removeItem('test_key');
        if (testValue === 'test_value') {
          console.log('✅ localStorage is working properly');
        } else {
          console.error('❌ localStorage test failed');
          throw new Error('localStorage not functioning properly');
        }
      } catch (storageError) {
        console.error('❌ localStorage error:', storageError);
        alert('LocalStorage is not available. Notes may not save properly.');
        return;
      }
      
      const existingAiNotes = await researchAgentApi.getNote('AI Responses');
      console.log('📋 Existing AI Responses notes:', {
        found: !!existingAiNotes,
        length: existingAiNotes?.length || 0
      });
      
      if (!existingAiNotes || existingAiNotes.trim() === '') {
        console.log('📝 Creating initial AI Responses notes...');
        // Create initial AI Responses notes file
        const initialContent = `# AI Responses\n\nThis file automatically stores all AI responses from your research conversations.\n\n---\n\n`;
        await researchAgentApi.updateNote('AI Responses', initialContent);
        
        // Update local state
        setSavedNotes(prev => ({
          ...prev,
          'AI Responses': initialContent
        }));
        
        console.log('✅ AI Responses notes initialized with content:', initialContent.substring(0, 50) + '...');
      } else {
        console.log('✅ AI Responses notes already exist');
      }
    } catch (error) {
      console.error('❌ Failed to initialize AI Responses notes:', error);
      alert(`Failed to initialize notes: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Auto-scroll chat to bottom when new messages are added
  useEffect(() => {
    const chatContainer = document.getElementById('chatMessages');
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }, [chatMessages]);

  // Add a test message on component mount to show chat is working
  useEffect(() => {
    // Remove the chat activation message - not needed
    /*
    const timer = setTimeout(() => {
      if (chatMessages.length === 0) {
        const systemMessage: ChatMessage = {
          id: generateId(),
          content: 'Chat functionality is now active! Try typing a message below.',
          role: 'system',
          timestamp: new Date()
        };
        addChatMessage(systemMessage);
      }
    }, 2000);

    return () => clearTimeout(timer);
    */
  }, []);

  const renderPaperContent = () => {
    switch (activeView) {
      case 'abstract':
        return (
          <div className="abstract-view">
            {selectedPaper ? (
              <div className="paper-details">
                <div className="paper-header">
                  <h3>
                    {selectedPaper.title}
                  </h3>
                  <div className="paper-meta">
                    <p><strong>Authors:</strong> {selectedPaper.authors.join(', ')}</p>
                    <p><strong>Published:</strong> {selectedPaper.published}</p>
                    <p><strong>Categories:</strong> {selectedPaper.categories.join(', ')}</p>
                    <p><strong>arXiv ID:</strong> {selectedPaper.arxiv_id}</p>
                  </div>
                </div>
                <div className="paper-abstract">
                  <h4>Abstract</h4>
                  <p>{selectedPaper.summary}</p>
                  <div className="paper-actions">
                    <p><strong>💡 Need full paper analysis?</strong></p>
                    <p>This shows only the abstract. For detailed analysis of the full paper:</p>
                    <ol>
                      <li>Download the PDF: <a href={selectedPaper.pdf_url} target="_blank" rel="noopener noreferrer" className="pdf-link">📄 Download PDF</a></li>
                      <li>Upload it using the file upload feature</li>
                      <li>Ask questions about the full content</li>
                    </ol>
                  </div>
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <i className="fas fa-file-pdf fa-3x"></i>
                <h3>No Paper Selected</h3>
                <p>Search for papers and select one from the dropdown to view its abstract here</p>
              </div>
            )}
          </div>
        );
      case 'pdf':
        return (
          <div className="pdf-view">
            <div className="pdf-viewer-container">
              {selectedPaper ? (
                <div className="pdf-content">
                  {(() => {
                    // Get PDF URL
                    let pdfUrl = selectedPaper.pdf_url;
                    if (!pdfUrl && selectedPaper.arxiv_id) {
                      const arxivId = selectedPaper.arxiv_id.replace('arXiv:', '');
                      pdfUrl = `https://arxiv.org/pdf/${arxivId}.pdf`;
                    }
                    
                    return pdfUrl ? (
                      <div className="pdf-embed-container">
                        <iframe
                          src={`${pdfUrl}#toolbar=1&navpanes=1&scrollbar=1`}
                          width="100%"
                          height="100%"
                          title={`PDF: ${selectedPaper.title}`}
                          frameBorder="0"
                          className="pdf-iframe"
                        />
                      </div>
                    ) : (
                      <div className="pdf-loading">
                        <i className="fas fa-exclamation-triangle fa-2x"></i>
                        <h3>PDF Not Available</h3>
                        <p>PDF URL is not available for this paper. Try using the abstract view.</p>
                      </div>
                    );
                  })()}
                </div>
              ) : (
                <div className="pdf-loading">
                  <i className="fas fa-file-pdf fa-2x"></i>
                  <h3>PDF Viewer</h3>
                  <p>Select a paper to view its PDF document here</p>
                </div>
              )}
            </div>
          </div>
        );
      default:
        return (
          <div className="empty-state">
            <i className="fas fa-file-pdf fa-3x"></i>
            <h3>No Paper Selected</h3>
            <p>Search for papers and select one from the dropdown to view it here</p>
          </div>
        );
    }
  };
  return (
    <div className="app-container">
      {/* Header with Search and Paper Selection */}
      <header className="app-header">
        <div className="header-content">
          <h1><i className="fas fa-microscope"></i> Research Agent</h1>
          <div className="search-controls">
            <div className="search-box">
              <input 
                type="text" 
                id="searchInput" 
                placeholder="Search academic papers..."
                autoComplete="off"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSearch();
                  }
                }}
              />
              <button 
                id="searchBtn" 
                className="search-btn"
                onClick={handleSearch}
                disabled={isSearching || !searchQuery.trim()}
              >
                <i className="fas fa-search"></i>
                {isSearching ? ' Searching...' : ''}
              </button>
            </div>
            
            <div className="upload-section">
              <div className="upload-divider">OR</div>
              <label htmlFor="paperUpload" className="upload-btn">
                <i className="fas fa-upload"></i>
                {isUploading ? 'Uploading...' : 'Upload PDF'}
              </label>
              <input
                type="file"
                id="paperUpload"
                className="upload-input"
                accept=".pdf"
                onChange={handlePaperUpload}
                disabled={isUploading}
              />
            </div>
            
            <div className="paper-selector">
              <select 
                id="paperDropdown" 
                className="paper-dropdown"
                value={selectedPaper?.id || ''}
                onChange={(e) => {
                  const paperId = e.target.value;
                  const paper = searchResults.find(p => p.id === paperId) || uploadedPaperData;
                  if (paper) {
                    handlePaperSelect(paper);
                  }
                }}
                disabled={searchResults.length === 0 && !uploadedPaperData}
              >
                <option value="">
                  {searchResults.length === 0 && !uploadedPaperData ? 'Search for papers or upload PDF...' : 'Select a paper...'}
                </option>
                {uploadedPaperData && (
                  <option key={uploadedPaperData.id} value={uploadedPaperData.id}>
                    📄 {uploadedPaperData.title.length > 50 ? uploadedPaperData.title.substring(0, 50) + '...' : uploadedPaperData.title}
                  </option>
                )}
                {searchResults.map((paper) => (
                  <option key={paper.id} value={paper.id}>
                    {paper.title.length > 60 ? paper.title.substring(0, 60) + '...' : paper.title}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        <div className="panel-container" ref={containerRef}>
          {/* Left Panel: Paper Display */}
          <section 
            className="left-panel paper-panel"
            style={{ width: `${leftPanelWidth}%` }}
          >
            <div className="panel-header">
              <h2><i className="fas fa-file-pdf"></i> Paper Viewer</h2>
              <div className="paper-controls">
                <button 
                  id="openInNewTabBtn" 
                  className="control-btn"
                  disabled={!selectedPaper}
                  onClick={() => {
                    if (selectedPaper) {
                      // Construct PDF URL if not available
                      let pdfUrl = selectedPaper.pdf_url;
                      if (!pdfUrl && selectedPaper.arxiv_id) {
                        const arxivId = selectedPaper.arxiv_id.replace('arXiv:', '');
                        pdfUrl = `https://arxiv.org/pdf/${arxivId}.pdf`;
                      }
                      
                      if (pdfUrl) {
                        window.open(pdfUrl, '_blank');
                      } else {
                        const errorMessage: ChatMessage = {
                          id: generateId(),
                          content: 'PDF URL not available for this paper.',
                          role: 'system',
                          timestamp: new Date()
                        };
                        addChatMessage(errorMessage);
                      }
                    }
                  }}
                >
                  <i className="fas fa-external-link-alt"></i> Open in New Tab
                </button>
                <button 
                  id="summaryBtn" 
                  className="control-btn"
                  disabled={!selectedPaper}
                  onClick={async () => {
                    if (selectedPaper) {
                      try {
                        const summary = await researchAgentApi.generateSummary(selectedPaper.id);
                        const summaryMessage: ChatMessage = {
                          id: generateId(),
                          content: `Summary for "${selectedPaper.title}": ${summary}`,
                          role: 'ai',
                          timestamp: new Date()
                        };
                        addChatMessage(summaryMessage);
                      } catch (error) {
                        // Summary generation failed - silently ignore
                      }
                    }
                  }}
                >
                  <i className="fas fa-magic"></i> Generate Summary
                </button>
                <div className="view-toggle">
                  <button 
                    id="abstractViewBtn" 
                    className={`toggle-btn ${activeView === 'abstract' ? 'active' : ''}`}
                    onClick={() => handleViewChange('abstract')}
                  >
                    Abstract
                  </button>
                  <button 
                    id="pdfViewBtn" 
                    className={`toggle-btn ${activeView === 'pdf' ? 'active' : ''}`}
                    onClick={() => handleViewChange('pdf')}
                  >
                    PDF View
                  </button>
                </div>
              </div>
            </div>
            <div className="panel-content">
              <div id="paperViewer" className="paper-viewer">
                {renderPaperContent()}
              </div>
            </div>
          </section>

          {/* Resizable Divider */}
          <div 
            className="panel-divider" 
            id="panelDivider"
            onMouseDown={handleMouseDown}
            style={{ cursor: isResizing ? 'col-resize' : 'col-resize' }}
          ></div>

          {/* Right Panel: AI Agent & Notes */}
          <section 
            className="right-panel agent-panel"
            style={{ width: `${100 - leftPanelWidth}%` }}
          >
            <div className="panel-header">
              <h2>
                <i className="fas fa-robot"></i> AI Research Assistant
                {selectedNotesName !== 'current' && (
                  <span className="current-note-indicator"> - {selectedNotesName}</span>
                )}
              </h2>
              <div className="agent-controls">
                <div className="notes-selector">
                  <select 
                    id="notesDropdown" 
                    className="notes-dropdown"
                    value={selectedNotesName}
                    onChange={handleNotesDropdownChange}
                  >
                    <option value="current">Current Session</option>
                    <option value="clear">Clear Displayed Notes</option>
                    {Object.keys(savedNotes).map((noteName) => (
                      <option key={noteName} value={noteName}>
                        {noteName}
                      </option>
                    ))}
                  </select>
                  <div className="notes-info">
                    <span className="notes-count">
                      <i className="fas fa-sticky-note"></i> {Object.keys(savedNotes).length} saved
                    </span>
                    <button 
                      className="btn small secondary refresh-notes-btn" 
                      onClick={loadNotesFromVault}
                      title="Refresh notes from vault"
                    >
                      <i className="fas fa-sync-alt"></i>
                    </button>
                  </div>
                  <button id="newNotesBtn" className="control-btn" onClick={handleCreateNewNote}>
                    <i className="fas fa-plus"></i> New Notes
                  </button>
                  <button 
                    id="editNotesBtn" 
                    className="control-btn" 
                    onClick={handleShowNotesListForEdit}
                    disabled={Object.keys(savedNotes).length === 0}
                    title={Object.keys(savedNotes).length === 0 ? 'No notes to edit' : 'Edit existing notes'}
                  >
                    <i className="fas fa-edit"></i> Edit Notes
                  </button>
                  <button id="saveNotesBtn" className="control-btn" onClick={() => {
                    if (currentNotes && selectedPaper) {
                      saveNotesToVault(`notes_${selectedPaper.id}_${Date.now()}`, currentNotes);
                    }
                  }}>
                    <i className="fas fa-save"></i> Save
                  </button>
                </div>
              </div>
            </div>
            <div className="panel-content">
              {/* Chat Interface */}
              <div className="chat-section">
                <div 
                  id="chatMessages" 
                  className="chat-messages"
                  style={{
                    scrollbarWidth: 'thick' as any,
                    scrollbarColor: '#475569 #e2e8f0'
                  }}
                >
                  {chatMessages.length === 0 ? (
                    <div className="welcome-message">
                      <div className="agent-avatar">
                        <i className="fas fa-robot"></i>
                      </div>
                      <div className="message-content">
                        <p><strong>Welcome to Research Agent!</strong></p>
                        <p>I'm here to help you research academic papers. Here's what I can do:</p>
                        <ul>
                          <li>🔍 Search for papers using keywords</li>
                          <li>📖 Analyze and explain paper content</li>
                          <li>📝 Generate summaries and key insights</li>
                          <li>💬 Answer questions about research papers</li>
                          <li>📄 View PDFs directly in the browser</li>
                          <li>✨ Provide formatted responses with markdown support</li>
                        </ul>
                        <p>Start by searching for papers above, then select one to begin our conversation!</p>
                        <div className="feature-highlight">
                          <strong>🧠 AI Features:</strong>
                          <ul>
                            <li>Context-aware conversations about selected papers</li>
                            <li>Rich markdown responses with code blocks, lists, and formatting</li>
                            <li>Direct PDF access and download capabilities</li>
                            <li>Real-time paper analysis and insights</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  ) : (
                    chatMessages.map((message) => (
                      <div key={message.id} className={`message ${message.role}`}>
                        <div className="message-header">
                          <span className="role-indicator">
                            {message.role === 'user' && <i className="fas fa-user"></i>}
                            {message.role === 'ai' && <i className="fas fa-robot"></i>}
                            {message.role === 'system' && <i className="fas fa-info-circle"></i>}
                            {message.role === 'user' ? 'You' : message.role === 'ai' ? 'AI Assistant' : 'System'}
                          </span>
                          <span className="timestamp">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="message-content">
                          <ReactMarkdown 
                            remarkPlugins={[remarkGfm, remarkMath]}
                            rehypePlugins={[rehypeHighlight, rehypeKatex]}
                            components={{
                              code: ({className, children, ...props}: any) => {
                                const isInline = !className?.includes('language-');
                                return isInline ? (
                                  <code className="inline-code" {...props}>
                                    {children}
                                  </code>
                                ) : (
                                  <pre className="code-block">
                                    <code className={className} {...props}>
                                      {children}
                                    </code>
                                  </pre>
                                );
                              },
                              blockquote: ({children}) => (
                                <blockquote className="markdown-blockquote">
                                  {children}
                                </blockquote>
                              ),
                              h1: ({children}) => <h1 className="markdown-h1">{children}</h1>,
                              h2: ({children}) => <h2 className="markdown-h2">{children}</h2>,
                              h3: ({children}) => <h3 className="markdown-h3">{children}</h3>,
                              ul: ({children}) => <ul className="markdown-ul">{children}</ul>,
                              ol: ({children}) => <ol className="markdown-ol">{children}</ol>,
                              li: ({children}) => <li className="markdown-li">{children}</li>,
                              a: ({href, children}) => (
                                <a 
                                  href={href} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="markdown-link"
                                >
                                  {children}
                                </a>
                              )
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>
                        
                        {/* Debug info for all messages */}
                        {message.role === 'ai' && (
                            <div className="message-actions" style={{
                            marginTop: '15px',
                            paddingTop: '10px', 
                            borderTop: '2px solid #dee2e6',
                            display: 'flex',
                            justifyContent: 'flex-end',
                            backgroundColor: '#f8f9fa',
                            padding: '10px',
                            borderRadius: '4px',
                            position: 'relative',
                            zIndex: 1000
                          }}>
                            <button 
                              onClick={() => saveSpecificResponseToNotes(message.content, message.id)}
                              className="save-to-notes-btn"
                              style={{
                                backgroundColor: '#007bff',
                                color: '#ffffff',
                                border: '2px solid #0056b3',
                                padding: '12px 24px',
                                fontSize: '14px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                borderRadius: '6px',
                                display: 'inline-block',
                                minWidth: '150px',
                                minHeight: '40px',
                                boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                                transition: 'all 0.2s ease',
                                textAlign: 'center' as const,
                                lineHeight: '1.2',
                                opacity: 1,
                                visibility: 'visible' as const,
                                position: 'relative' as const,
                                zIndex: 9999
                              }}
                              onMouseOver={(e) => {
                                const target = e.target as HTMLButtonElement;
                                target.style.backgroundColor = '#0056b3';
                                target.style.transform = 'translateY(-1px)';
                              }}
                              onMouseOut={(e) => {
                                const target = e.target as HTMLButtonElement;
                                target.style.backgroundColor = '#007bff';
                                target.style.transform = 'translateY(0)';
                              }}
                            >
                              SAVE TO NOTES
                            </button>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                  {isSendingMessage && (
                    <div className="message ai">
                      <div className="message-header">
                        <span className="role-indicator">
                          <i className="fas fa-robot"></i>
                          AI Assistant
                        </span>
                      </div>
                      <div className="message-content">
                        <div className="typing-indicator">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div className="chat-input-container">
                  <div className="chat-input">
                    <textarea 
                      id="chatInput" 
                      placeholder="Ask me about the paper, request explanations, or ask for specific notes..."
                      rows={1}
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyPress={handleKeyPress}
                      disabled={isSendingMessage}
                    />
                    <button 
                      id="sendChatBtn" 
                      className="send-btn"
                      onClick={handleSendMessage}
                      disabled={isSendingMessage || !chatInput.trim()}
                    >
                      <i className={isSendingMessage ? "fas fa-spinner fa-spin" : "fas fa-paper-plane"}></i>
                    </button>
                  </div>
                  
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Status Bar */}
      <footer className="status-bar">
        <div className="status-left">
          <span id="connectionStatus" className="status-item">
            <i className={`fas fa-circle ${connectionStatus === 'connected' ? 'connected' : 'disconnected'}`}></i> 
            {connectionStatus === 'connected' ? 'API Connected' : 'API Disconnected'}
          </span>
          <span id="paperStatus" className="status-item">
            <i className="fas fa-file"></i> 
            {selectedPaper ? `Selected: ${selectedPaper.title.substring(0, 30)}...` : 'No paper selected'}
          </span>
        </div>
        <div className="status-right">
          <span id="searchStatus" className="status-item">
            <i className="fas fa-search"></i> 
            {searchResults.length > 0 ? `${searchResults.length} papers found` : 'No search results'}
          </span>
          <span id="chatStatus" className="status-item">
            <i className="fas fa-comments"></i> 
            {chatMessages.length} messages
          </span>
        </div>
      </footer>

      {/* Loading Overlay */}
      <div id="loadingOverlay" className="loading-overlay hidden">
        <div className="loading-content">
          <i className="fas fa-spinner fa-spin fa-2x"></i>
          <p id="loadingText">Loading...</p>
        </div>
      </div>

      {/* Notes Modal */}
      {showNotesModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3><i className="fas fa-sticky-note"></i> Create New Notes File</h3>
              <button className="close-btn" onClick={() => setShowNotesModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <label htmlFor="notesName">Notes File Name:</label>
              <input 
                type="text" 
                id="notesName" 
                placeholder="Enter notes file name..."
                value={notesFileName}
                onChange={(e) => setNotesFileName(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleCreateNotes();
                  }
                }}
              />
              <div className="modal-actions">
                <button className="btn primary" onClick={handleCreateNotes}>Create</button>
                <button className="btn secondary" onClick={() => setShowNotesModal(false)}>Cancel</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Note Selection Modal */}
      {showNoteSelectionModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3><i className="fas fa-save"></i> Save AI Response to Notes</h3>
              <button className="close-btn" onClick={() => setShowNoteSelectionModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <p>Select which notes to save this AI response to:</p>
              <div className="note-selection-list">
                {Object.keys(savedNotes).length > 0 ? (
                  <>
                    {Object.keys(savedNotes).map(noteName => (
                      <label key={noteName} className="note-selection-item">
                        <input 
                          type="checkbox" 
                          value={noteName}
                          defaultChecked={noteName === 'AI Responses'}
                          disabled={noteName === 'AI Responses'}
                        />
                        <span className={noteName === 'AI Responses' ? 'default-note' : ''}>
                          {noteName} {noteName === 'AI Responses' ? '(Always included)' : ''}
                        </span>
                      </label>
                    ))}
                    <div className="create-new-note-option">
                      <button 
                        className="btn small primary"
                        onClick={() => {
                          setShowNoteSelectionModal(false);
                          setShowNotesModal(true);
                        }}
                      >
                        <i className="fas fa-plus"></i> Create New Note
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="no-notes-section">
                    <p>No existing notes found.</p>
                    <button 
                      className="btn primary"
                      onClick={() => {
                        setShowNoteSelectionModal(false);
                        setShowNotesModal(true);
                      }}
                    >
                      <i className="fas fa-plus"></i> Create Your First Note
                    </button>
                  </div>
                )}
              </div>
              <div className="modal-actions">
                <button className="btn primary" onClick={() => {
                  const checkboxes = document.querySelectorAll('.note-selection-item input[type="checkbox"]:checked');
                  const selectedNotes = Array.from(checkboxes).map(cb => (cb as HTMLInputElement).value);
                  saveAiResponseToSelectedNotes(selectedNotes);
                }}>Save to Selected Notes</button>
                <button className="btn secondary" onClick={() => {
                  // Just save to AI Responses only
                  saveAiResponseToSelectedNotes(['AI Responses']);
                }}>Save to AI Responses Only</button>
                <button className="btn secondary" onClick={() => setShowNoteSelectionModal(false)}>Cancel</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Notes Modal */}
      {showEditNotesModal && (
        <div className="modal">
          <div className="modal-content edit-notes-modal">
            <div className="modal-header">
              <h3><i className="fas fa-edit"></i> Edit Notes: {editingNotesName}</h3>
              <button className="close-btn" onClick={() => setShowEditNotesModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="notes-editor">
                <textarea 
                  className="notes-textarea"
                  placeholder="Edit your notes here..."
                  value={editingNotesContent}
                  onChange={(e) => setEditingNotesContent(e.target.value)}
                  rows={15}
                />
              </div>
              <div className="modal-actions">
                <button className="btn primary" onClick={handleSaveEditedNotes}>
                  <i className="fas fa-save"></i> Save Changes
                </button>
                <button className="btn secondary" onClick={() => setShowEditNotesModal(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Notes List Modal */}
      {showNotesListModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3><i className="fas fa-list"></i> Select Notes to Edit</h3>
              <button className="close-btn" onClick={() => setShowNotesListModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="notes-list">
                {Object.keys(savedNotes).length === 0 ? (
                  <p className="no-notes-message">No saved notes found. Create some notes first!</p>
                ) : (
                  Object.keys(savedNotes).map((notesName) => (
                    <div key={notesName} className="notes-item">
                      <span className="notes-item-name">
                        {notesName}
                        {notesName === 'AI Responses' && (
                          <span className="protected-note-indicator"> (Protected)</span>
                        )}
                      </span>
                      <div className="notes-item-actions">
                        {notesName !== 'AI Responses' && (
                          <>
                            <button 
                              className="btn small primary" 
                              onClick={() => {
                                console.log('📝 Edit button clicked for:', notesName);
                                handleEditNotes(notesName);
                              }}
                              style={{
                                pointerEvents: 'auto',
                                cursor: 'pointer',
                                zIndex: 1000,
                                position: 'relative'
                              }}
                            >
                              <i className="fas fa-edit"></i> Edit
                            </button>
                            <button 
                              className="btn small danger" 
                              onClick={() => {
                                console.log('�️ Delete button clicked for:', notesName);
                                handleDeleteNote(notesName);
                              }}
                              style={{
                                pointerEvents: 'auto',
                                cursor: 'pointer',
                                zIndex: 1000,
                                position: 'relative'
                              }}
                            >
                              <i className="fas fa-trash"></i> Delete
                            </button>
                          </>
                        )}
                        <button 
                          className="btn small secondary" 
                          onClick={() => {
                            console.log('� PDF button clicked for:', notesName);
                            downloadNotesAsPDF(notesName, savedNotes[notesName]);
                          }}
                          title="Download as PDF"
                          style={{
                            pointerEvents: 'auto',
                            cursor: 'pointer',
                            zIndex: 1000,
                            position: 'relative'
                          }}
                        >
                          <i className="fas fa-download"></i> PDF
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
              <div className="modal-actions">
                <button className="btn secondary" onClick={() => setShowNotesListModal(false)}>
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResearchAgentNew;
