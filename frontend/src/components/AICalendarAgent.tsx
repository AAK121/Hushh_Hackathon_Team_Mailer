import React, { useState } from 'react';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';

interface AICalendarAgentProps {
  onBack: () => void;
}

interface ExtractedEvent {
  summary: string;
  start_time: string;
  end_time: string;
  location?: string;
  description?: string;
  attendees?: string[];
  confidence: number;
  source_email?: string;
}

interface CalendarAgentResponse {
  status: string;
  user_id: string;
  action_performed?: string;
  session_id?: string;
  approval_status?: string;
  emails_processed?: number;
  events_extracted?: number;
  events_created?: number;
  calendar_links?: string[];
  extracted_events?: ExtractedEvent[];
  processing_time?: number;
  trust_links?: string[];
  errors?: string[];
}

interface EventModification {
  summary?: string;
  start_time?: string;
  end_time?: string;
  location?: string;
  description?: string;
  attendees?: string[];
}

type WorkflowStep = 'setup' | 'review' | 'success' | 'transitioning';

const AICalendarAgent: React.FC<AICalendarAgentProps> = ({ onBack }) => {
  const { user, getValidGoogleToken } = useAuth();
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('setup');
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<CalendarAgentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // HITL state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [extractedEvents, setExtractedEvents] = useState<ExtractedEvent[]>([]);
  const [selectedEvents, setSelectedEvents] = useState<Set<number>>(new Set());
  const [eventModifications, setEventModifications] = useState<Record<number, EventModification>>({});
  
  // Preserve original extraction data for final results
  const [originalExtractionData, setOriginalExtractionData] = useState<CalendarAgentResponse | null>(null);
  
  // Transition state
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [showTransition, setShowTransition] = useState(false);

  // Configuration options
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.7);
  const [maxEmails, setMaxEmails] = useState(50);
  const [action, setAction] = useState<'extract_events' | 'comprehensive_analysis' | 'analyze_only' | 'manual_event'>('extract_events');

  // Handle back navigation with transition
  const handleBackNavigation = () => {
    setIsTransitioning(true);
    
    // Add transition delay for smooth back animation
    setTimeout(() => {
      onBack();
    }, 300); // 300ms transition delay
  };

  const executeCalendarAgent = async () => {
    if (!user) {
      setError('User not authenticated');
      return;
    }

    if (!supabase) {
      setError('Supabase not configured');
      return;
    }

    // Start transition immediately for extract_events action
    if (action === 'extract_events') {
      console.log('🎬 Starting transition animation...');
      setShowTransition(true);
      setCurrentStep('transitioning');
      
      // Small delay to allow transition to start visually
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    setIsProcessing(true);
    setError(null);
    setResults(null);

    try {
      // Get current session from Supabase and ensure we have a valid Google token
      const { data, error: sessionError } = await supabase.auth.getSession();
      if (sessionError || !data.session) {
        throw new Error('No session found');
      }

      // Use the new token refresh functionality
      const googleToken = await getValidGoogleToken();
      const userId = data.session.user?.id;

      if (!googleToken) {
        throw new Error('No valid Google token available. Please sign in with Google again.');
      }

      console.log('🚀 Starting HushMCP Calendar Agent...');
      console.log('User ID:', userId);
      console.log('✅ Using refreshed Google token for API access');
      
      // Step 1: Create consent tokens for email and calendar access
      console.log('🔑 Creating consent tokens...');
      
      // Create email consent token
      const emailTokenResponse = await fetch('http://127.0.0.1:8001/consent/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          agent_id: 'agent_addtocalendar',
          scope: 'vault.read.email'
        })
      });

      if (!emailTokenResponse.ok) {
        const errorData = await emailTokenResponse.text();
        throw new Error(`Failed to create email consent token: ${emailTokenResponse.status} - ${errorData}`);
      }

      const emailTokenData = await emailTokenResponse.json();
      const emailConsentToken = emailTokenData.token;

      // Create calendar consent token
      const calendarTokenResponse = await fetch('http://127.0.0.1:8001/consent/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          agent_id: 'agent_addtocalendar',
          scope: 'vault.write.calendar'
        })
      });

      if (!calendarTokenResponse.ok) {
        const errorData = await calendarTokenResponse.text();
        throw new Error(`Failed to create calendar consent token: ${calendarTokenResponse.status} - ${errorData}`);
      }

      const calendarTokenData = await calendarTokenResponse.json();
      const calendarConsentToken = calendarTokenData.token;

      console.log('✅ Consent tokens created successfully');
      
      // Step 2: Execute the AddToCalendar agent with proper consent tokens
      console.log('🤖 Executing AddToCalendar agent...');
      
      const executeResponse = await fetch('http://127.0.0.1:8001/agents/addtocalendar/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          email_token: emailConsentToken,
          calendar_token: calendarConsentToken,
          google_access_token: googleToken,
          action: action,
          confidence_threshold: confidenceThreshold,
          max_emails: maxEmails
        })
      });

      if (!executeResponse.ok) {
        const errorData = await executeResponse.text();
        throw new Error(`Agent execution failed: ${executeResponse.status} - ${errorData}`);
      }

      const result: CalendarAgentResponse = await executeResponse.json();
      
      console.log('📊 Agent execution result:', result);
      setResults(result);

      // Handle HITL workflow
      if (action === 'extract_events' && result.extracted_events && result.session_id) {
        // Store original extraction data to preserve emails_processed count
        setOriginalExtractionData(result);
        setSessionId(result.session_id);
        setExtractedEvents(result.extracted_events);
        
        console.log('🎬 Completing transition to review step...');
        // Complete the transition to review step after processing
        setTimeout(() => {
          setCurrentStep('review');
          setShowTransition(false);
          console.log('🎬 Transition complete!');
        }, 500); // Give a bit more time for the transition to be visible
      } else {
        setCurrentStep('success');
        setShowTransition(false); // Reset transition state for non-extract actions
      }

    } catch (error) {
      console.error('💥 Error in calendar agent execution:', error);
      setError(error instanceof Error ? error.message : 'Unknown error occurred');
      // Reset transition state on error
      setCurrentStep('setup');
      setShowTransition(false);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleEventSelection = (eventIndex: number) => {
    const newSelected = new Set(selectedEvents);
    if (newSelected.has(eventIndex)) {
      newSelected.delete(eventIndex);
    } else {
      newSelected.add(eventIndex);
    }
    setSelectedEvents(newSelected);
  };

  const handleEventModification = (eventIndex: number, field: keyof EventModification, value: string | string[]) => {
    setEventModifications(prev => ({
      ...prev,
      [eventIndex]: {
        ...prev[eventIndex],
        [field]: value
      }
    }));
  };

  const approveSelectedEvents = async () => {
    if (!sessionId) {
      setError('No session ID available for approval');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const selectedIndices = Array.from(selectedEvents);
      
      const approvalResponse = await fetch('http://127.0.0.1:8001/agents/addtocalendar/approve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          action: 'approve_selected',
          selected_events: selectedIndices,
          event_modifications: eventModifications
        })
      });

      if (!approvalResponse.ok) {
        const errorData = await approvalResponse.text();
        throw new Error(`Approval failed: ${approvalResponse.status} - ${errorData}`);
      }

      const approvalResult: CalendarAgentResponse = await approvalResponse.json();
      console.log('✅ Events approved successfully:', approvalResult);
      
      // Merge approval results with original extraction data to preserve emails_processed
      const mergedResults: CalendarAgentResponse = {
        ...approvalResult,
        emails_processed: originalExtractionData?.emails_processed || approvalResult.emails_processed,
        events_extracted: originalExtractionData?.events_extracted || approvalResult.events_extracted,
        processing_time: originalExtractionData?.processing_time || approvalResult.processing_time
      };
      
      setResults(mergedResults);
      setCurrentStep('success');

    } catch (error) {
      console.error('💥 Error approving events:', error);
      setError(error instanceof Error ? error.message : 'Failed to approve events');
    } finally {
      setIsProcessing(false);
    }
  };

  const approveAllEvents = async () => {
    if (!sessionId) {
      setError('No session ID available for approval');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const approvalResponse = await fetch('http://127.0.0.1:8001/agents/addtocalendar/approve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          action: 'approve_all'
        })
      });

      if (!approvalResponse.ok) {
        const errorData = await approvalResponse.text();
        throw new Error(`Approval failed: ${approvalResponse.status} - ${errorData}`);
      }

      const approvalResult: CalendarAgentResponse = await approvalResponse.json();
      console.log('✅ All events approved successfully:', approvalResult);
      
      // Merge approval results with original extraction data to preserve emails_processed
      const mergedResults: CalendarAgentResponse = {
        ...approvalResult,
        emails_processed: originalExtractionData?.emails_processed || approvalResult.emails_processed,
        events_extracted: originalExtractionData?.events_extracted || approvalResult.events_extracted,
        processing_time: originalExtractionData?.processing_time || approvalResult.processing_time
      };
      
      setResults(mergedResults);
      setCurrentStep('success');

    } catch (error) {
      console.error('💥 Error approving all events:', error);
      setError(error instanceof Error ? error.message : 'Failed to approve all events');
    } finally {
      setIsProcessing(false);
    }
  };

  const rejectAllEvents = async () => {
    if (!sessionId) {
      setError('No session ID available for rejection');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const rejectionResponse = await fetch('http://127.0.0.1:8001/agents/addtocalendar/approve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          action: 'reject'
        })
      });

      if (!rejectionResponse.ok) {
        const errorData = await rejectionResponse.text();
        throw new Error(`Rejection failed: ${rejectionResponse.status} - ${errorData}`);
      }

      const rejectionResult: CalendarAgentResponse = await rejectionResponse.json();
      console.log('❌ All events rejected:', rejectionResult);
      
      // Reset to setup after rejection
      setCurrentStep('setup');
      setSessionId(null);
      setExtractedEvents([]);
      setSelectedEvents(new Set());
      setEventModifications({});
      setResults(null);
      setOriginalExtractionData(null);

    } catch (error) {
      console.error('💥 Error rejecting events:', error);
      setError(error instanceof Error ? error.message : 'Failed to reject events');
    } finally {
      setIsProcessing(false);
    }
  };

  const clearResults = () => {
    setResults(null);
    setOriginalExtractionData(null);
    setError(null);
    setCurrentStep('setup');
    setSessionId(null);
    setExtractedEvents([]);
    setSelectedEvents(new Set());
    setEventModifications({});
  };

  const formatDateTime = (dateTimeString: string) => {
    try {
      return new Date(dateTimeString).toLocaleString();
    } catch {
      return dateTimeString;
    }
  };

  const renderSetupStep = () => (
    <>
      {/* Header */}
      <HeaderSection>
        <BackButton onClick={handleBackNavigation} disabled={isTransitioning}>
          ← Back
        </BackButton>
      </HeaderSection>

      {/* Main Content */}
      <MainContent>
        <HeaderContent>
          <Title>🤖 AI Calendar Agent</Title>
          <Description>
            Extract events from your emails and create Google Calendar entries with human-in-the-loop approval.
          </Description>
        </HeaderContent>

        {/* Configuration Panel */}
        <ConfigurationPanel>
          <FormGroup>
            <Label>Action Type</Label>
            <Select
              value={action}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setAction(e.target.value as any)}
            >
              <option value="extract_events">🔍 Extract Events (HITL Review)</option>
              <option value="comprehensive_analysis">🚀 Full Analysis + Auto-Create</option>
              <option value="analyze_only">👁️ Analyze Only (Preview)</option>
              <option value="manual_event">✏️ Manual Event Creation</option>
            </Select>
          </FormGroup>

          <FormGroup>
            <Label>Confidence Threshold ({confidenceThreshold})</Label>
            <RangeInput
              type="range"
              min="0.1"
              max="1.0"
              step="0.1"
              value={confidenceThreshold}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setConfidenceThreshold(parseFloat(e.target.value))}
            />
          </FormGroup>

          <FormGroup>
            <Label>Max Emails to Process</Label>
            <NumberInput
              type="number"
              min="1"
              max="200"
              value={maxEmails}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMaxEmails(parseInt(e.target.value))}
            />
          </FormGroup>
        </ConfigurationPanel>

        {/* Execute Button */}
        <ButtonSection>
          <ExecuteButton
            onClick={executeCalendarAgent}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <ButtonContent>
                <Spinner />
                Processing...
              </ButtonContent>
            ) : (
              action === 'extract_events' ? '🔍 Extract Events for Review' : '🗓️ Execute Calendar Agent'
            )}
          </ExecuteButton>
        </ButtonSection>

        {/* Error Display */}
        {error && (
          <ErrorSection>
            <ErrorTitle>❌ Error</ErrorTitle>
            <ErrorText>{error}</ErrorText>
            <ClearButton onClick={clearResults}>
              Clear
            </ClearButton>
          </ErrorSection>
        )}

        {/* Info Panel */}
        <InfoPanel>
          <InfoTitle>ℹ️ How it works</InfoTitle>
          <InfoList>
            <InfoItem>• <strong>Extract Events (HITL):</strong> Review and approve events before creation</InfoItem>
            <InfoItem>• <strong>Full Analysis:</strong> Automatically extract and create calendar events</InfoItem>
            <InfoItem>• <strong>Analyze Only:</strong> Preview potential events without creating them</InfoItem>
            <InfoItem>• Uses HushMCP AddToCalendar agent with privacy-first consent management</InfoItem>
            <InfoItem>• Processes recent emails to find meeting invitations and appointments</InfoItem>
          </InfoList>
        </InfoPanel>
      </MainContent>
    </>
  );

  const renderTransitionStep = () => (
    <>
      {/* Header */}
      <HeaderSection>
        <BackButton onClick={handleBackNavigation} disabled={isTransitioning}>
          ← Back
        </BackButton>
      </HeaderSection>

      {/* Main Content with Transition */}
      <MainContent>
        <TransitionContainer showTransition={showTransition}>
          {/* Configuration Panel moving up */}
          <TransitionConfigPanel showTransition={showTransition}>
            <FormGroup>
              <Label>Action Type</Label>
              <Select value={action} disabled>
                <option value="extract_events">🔍 Extract Events (HITL Review)</option>
              </Select>
            </FormGroup>
            
            <FormGroup>
              <Label>Confidence Threshold ({confidenceThreshold})</Label>
              <RangeInput
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={confidenceThreshold}
                disabled
              />
            </FormGroup>

            <FormGroup>
              <Label>Max Emails to Process</Label>
              <NumberInput
                type="number"
                value={maxEmails}
                disabled
              />
            </FormGroup>
          </TransitionConfigPanel>

          {/* Processing indicator */}
          <TransitionProcessing showTransition={showTransition}>
            <Spinner />
            <ProcessingText>Processing emails and extracting events...</ProcessingText>
          </TransitionProcessing>

          {/* New header content sliding in */}
          <TransitionNewContent showTransition={showTransition}>
            <Title>📋 Review Extracted Events</Title>
            <Description>
              Review, edit, and approve calendar events before they are created in your Google Calendar.
            </Description>
          </TransitionNewContent>
        </TransitionContainer>
      </MainContent>
    </>
  );

  const renderReviewStep = () => (
    <>
      {/* Header */}
      <HeaderSection>
        <BackButton onClick={handleBackNavigation} disabled={isTransitioning}>
          ← Back
        </BackButton>
      </HeaderSection>

      {/* Main Content */}
      <MainContent>
        <HeaderContent>
          <Title>📋 Review Extracted Events</Title>
          <Description>
            Review, edit, and approve calendar events before they are created in your Google Calendar.
          </Description>
        </HeaderContent>

        {/* Event Review Panel */}
        {extractedEvents.length > 0 ? (
          <ReviewPanel>
            <ReviewHeader>
              <ReviewTitle>
                Found {extractedEvents.length} potential events
                {results?.emails_processed && ` from ${results.emails_processed} emails`}
              </ReviewTitle>
              <ReviewSubtitle>
                Select events to create and edit details as needed
              </ReviewSubtitle>
            </ReviewHeader>

            <EventsList>
              {extractedEvents.map((event, index) => (
                <EventReviewCard 
                  key={index} 
                  selected={selectedEvents.has(index)}
                  onClick={() => handleEventSelection(index)}
                  style={{
                    animationDelay: `${index * 0.1}s`,
                    animation: 'slideInUp 0.6s ease-out forwards'
                  }}
                >
                  <EventHeader>
                    <EventCheckbox>
                      <input
                        type="checkbox"
                        checked={selectedEvents.has(index)}
                        onChange={() => handleEventSelection(index)}
                        onClick={(e) => e.stopPropagation()} // Prevent double toggle
                      />
                    </EventCheckbox>
                    <EventTitleSection>
                      <EventTitle>{event.summary}</EventTitle>
                      <ConfidenceBadge confidence={event.confidence}>
                        {Math.round(event.confidence * 100)}% confident
                      </ConfidenceBadge>
                    </EventTitleSection>
                  </EventHeader>

                  <EventDetails>
                    <DetailRow>
                      <DetailLabel>📅 Start:</DetailLabel>
                      <DetailValue>{formatDateTime(event.start_time)}</DetailValue>
                    </DetailRow>
                    <DetailRow>
                      <DetailLabel>🏁 End:</DetailLabel>
                      <DetailValue>{formatDateTime(event.end_time)}</DetailValue>
                    </DetailRow>
                    {event.location && (
                      <DetailRow>
                        <DetailLabel>📍 Location:</DetailLabel>
                        <DetailValue>{event.location}</DetailValue>
                      </DetailRow>
                    )}
                    {event.source_email && (
                      <DetailRow>
                        <DetailLabel>📧 Source:</DetailLabel>
                        <DetailValue>{event.source_email}</DetailValue>
                      </DetailRow>
                    )}
                  </EventDetails>

                  {selectedEvents.has(index) && (
                    <EventEditSection>
                      <EditSectionTitle>✏️ Edit Event Details</EditSectionTitle>
                      <EditGrid>
                        <EditField>
                          <EditLabel>Event Title</EditLabel>
                          <EditInput
                            type="text"
                            placeholder="Event title"
                            defaultValue={event.summary}
                            onChange={(e) => handleEventModification(index, 'summary', e.target.value)}
                          />
                        </EditField>
                        
                        <EditField>
                          <EditLabel>Location</EditLabel>
                          <EditInput
                            type="text"
                            placeholder="Event location"
                            defaultValue={event.location || ''}
                            onChange={(e) => handleEventModification(index, 'location', e.target.value)}
                          />
                        </EditField>

                        <EditField>
                          <EditLabel>Start Time</EditLabel>
                          <EditInput
                            type="datetime-local"
                            defaultValue={event.start_time?.slice(0, 16)}
                            onChange={(e) => handleEventModification(index, 'start_time', e.target.value + ':00Z')}
                          />
                        </EditField>

                        <EditField>
                          <EditLabel>End Time</EditLabel>
                          <EditInput
                            type="datetime-local"
                            defaultValue={event.end_time?.slice(0, 16)}
                            onChange={(e) => handleEventModification(index, 'end_time', e.target.value + ':00Z')}
                          />
                        </EditField>

                        <EditFieldFull>
                          <EditLabel>Description</EditLabel>
                          <EditTextarea
                            placeholder="Event description"
                            defaultValue={event.description || ''}
                            onChange={(e) => handleEventModification(index, 'description', e.target.value)}
                            rows={3}
                          />
                        </EditFieldFull>

                        <EditFieldFull>
                          <EditLabel>Attendees (comma-separated emails)</EditLabel>
                          <EditInput
                            type="text"
                            placeholder="john@example.com, jane@example.com"
                            defaultValue={event.attendees?.join(', ') || ''}
                            onChange={(e) => handleEventModification(index, 'attendees', e.target.value.split(',').map(email => email.trim()).filter(Boolean))}
                          />
                        </EditFieldFull>
                      </EditGrid>
                    </EventEditSection>
                  )}
                </EventReviewCard>
              ))}
            </EventsList>

            {/* Approval Actions */}
            <ApprovalActions>
              <ActionButtonsGrid>
                <ApprovalButton 
                  variant="approve-all"
                  onClick={approveAllEvents}
                  disabled={isProcessing}
                >
                  {isProcessing ? <Spinner /> : '✅'} Approve All ({extractedEvents.length})
                </ApprovalButton>
                
                <ApprovalButton 
                  variant="approve-selected"
                  onClick={approveSelectedEvents}
                  disabled={isProcessing || selectedEvents.size === 0}
                >
                  {isProcessing ? <Spinner /> : '✅'} Approve Selected ({selectedEvents.size})
                </ApprovalButton>
                
                <ApprovalButton 
                  variant="reject"
                  onClick={rejectAllEvents}
                  disabled={isProcessing}
                >
                  {isProcessing ? <Spinner /> : '❌'} Reject All
                </ApprovalButton>

                <ApprovalButton 
                  variant="back"
                  onClick={() => setCurrentStep('setup')}
                  disabled={isProcessing}
                >
                  ← Back to Setup
                </ApprovalButton>
              </ActionButtonsGrid>
            </ApprovalActions>
          </ReviewPanel>
        ) : (
          <NoEventsFound>
            <NoEventsIcon>�</NoEventsIcon>
            <NoEventsTitle>No Events Found</NoEventsTitle>
            <NoEventsText>
              No potential calendar events were found in your recent emails.
              Try adjusting the confidence threshold or checking more emails.
            </NoEventsText>
            <RetryButton onClick={() => setCurrentStep('setup')}>
              ← Try Again
            </RetryButton>
          </NoEventsFound>
        )}

        {/* Error Display */}
        {error && (
          <ErrorSection>
            <ErrorTitle>❌ Error</ErrorTitle>
            <ErrorText>{error}</ErrorText>
            <ClearButton onClick={() => setError(null)}>
              Clear
            </ClearButton>
          </ErrorSection>
        )}
      </MainContent>
    </>
  );

  const renderSuccessStep = () => (
    <>
      {/* Header */}
      <HeaderSection>
        <BackButton onClick={handleBackNavigation} disabled={isTransitioning}>
          ← Back
        </BackButton>
      </HeaderSection>

      {/* Main Content */}
      <MainContent>
        <HeaderContent>
          <Title>🎉 Calendar Events Created!</Title>
          <Description>
            Your calendar events have been successfully created and added to your Google Calendar.
          </Description>
        </HeaderContent>

        {/* Results Display */}
        {results && (
          <ResultsSection>
            <ClearResultsSection>
              <ClearButton onClick={clearResults}>
                Create More Events
              </ClearButton>
            </ClearResultsSection>

            {/* Status Banner */}
            <StatusBanner status={results.status}>
              <StatusTitle status={results.status}>
                {results.status === 'success' ? '✅ Success' : '⚠️ ' + results.status}
              </StatusTitle>
              {results.processing_time && (
                <ProcessingTime>Processing time: {results.processing_time}s</ProcessingTime>
              )}
            </StatusBanner>

            {/* Statistics */}
            <StatsGrid>
              <StatCard>
                <StatNumber>{results.emails_processed || 0}</StatNumber>
                <StatLabel>Emails Processed</StatLabel>
              </StatCard>
              <StatCard>
                <StatNumber>{results.events_extracted || 0}</StatNumber>
                <StatLabel>Events Extracted</StatLabel>
              </StatCard>
              <StatCard>
                <StatNumber>{results.events_created || 0}</StatNumber>
                <StatLabel>Calendar Events Created</StatLabel>
              </StatCard>
            </StatsGrid>

            {/* Calendar Links */}
            {results.calendar_links && results.calendar_links.length > 0 && (
              <ResultCard>
                <SectionTitle>� Created Calendar Events</SectionTitle>
                <LinksList>
                  {results.calendar_links.map((link, index) => (
                    <CalendarLink
                      key={index}
                      href={link}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      📅 Calendar Event {index + 1}
                    </CalendarLink>
                  ))}
                </LinksList>
              </ResultCard>
            )}

            {/* Extracted Events */}
            {results.extracted_events && results.extracted_events.length > 0 && (
              <ResultCard>
                <SectionTitle>� Created Events Summary</SectionTitle>
                <EventsList>
                  {results.extracted_events.map((event, index) => (
                    <EventCard key={index}>
                      <EventHeader>
                        <EventTitle>{event.summary}</EventTitle>
                        <ConfidenceBadge confidence={event.confidence}>
                          {Math.round(event.confidence * 100)}% confident
                        </ConfidenceBadge>
                      </EventHeader>
                      <EventDetails>
                        <EventTime>Start: {formatDateTime(event.start_time)}</EventTime>
                        <EventTime>End: {formatDateTime(event.end_time)}</EventTime>
                      </EventDetails>
                    </EventCard>
                  ))}
                </EventsList>
              </ResultCard>
            )}

            {/* Trust Links */}
            {results.trust_links && results.trust_links.length > 0 && (
              <ResultCard>
                <SectionTitle>🛡️ Trust Links</SectionTitle>
                <TrustLinksList>
                  {results.trust_links.map((link, index) => (
                    <TrustLink key={index}>{link}</TrustLink>
                  ))}
                </TrustLinksList>
              </ResultCard>
            )}

            {/* Errors/Warnings */}
            {results.errors && results.errors.length > 0 && (
              <WarningsSection>
                <WarningsTitle>⚠️ Warnings</WarningsTitle>
                <WarningsList>
                  {results.errors.map((error, index) => (
                    <WarningItem key={index}>• {error}</WarningItem>
                  ))}
                </WarningsList>
              </WarningsSection>
            )}
          </ResultsSection>
        )}
      </MainContent>
    </>
  );

  return (
    <StyledWrapper className={isTransitioning ? 'transitioning' : ''}>
      <Container>
        {currentStep === 'setup' && renderSetupStep()}
        {currentStep === 'transitioning' && renderTransitionStep()}
        {currentStep === 'review' && renderReviewStep()}
        {currentStep === 'success' && renderSuccessStep()}
      </Container>
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  flex: 1;
  padding: 24px;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
  opacity: 1;
  transform: translateY(0);

  /* Dynamic animated background */
  background: linear-gradient(-45deg, #0f0f23, #1a1a2e, #16213e, #0f3460);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;

  /* Floating particles background */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
      radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
    animation: particleFloat 20s ease-in-out infinite;
    pointer-events: none;
  }

  /* Moving light effects */
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), 
        rgba(29, 78, 216, 0.15), 
        transparent 40%);
    animation: lightPulse 8s ease-in-out infinite;
    pointer-events: none;
  }

  &.transitioning {
    opacity: 0;
    transform: translateY(-20px);
  }

  @keyframes gradientShift {
    0% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
    100% {
      background-position: 0% 50%;
    }
  }

  @keyframes particleFloat {
    0%, 100% {
      transform: translateY(0px) rotate(0deg);
      opacity: 1;
    }
    33% {
      transform: translateY(-30px) rotate(120deg);
      opacity: 0.8;
    }
    66% {
      transform: translateY(-60px) rotate(240deg);
      opacity: 0.6;
    }
  }

  @keyframes lightPulse {
    0%, 100% {
      opacity: 0.3;
      transform: scale(1);
    }
    50% {
      opacity: 0.8;
      transform: scale(1.2);
    }
  }
`;

const Container = styled.div`
  max-width: 1024px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
`;

const HeaderSection = styled.div`
  margin-bottom: 24px;
`;

const BackButton = styled.button`
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.1) 0%, 
    rgba(255, 255, 255, 0.05) 100%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;

  /* Hover gradient effect */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
      transparent, 
      rgba(232, 28, 255, 0.2), 
      transparent);
    transition: left 0.5s;
  }

  &:hover:not(:disabled) {
    background: linear-gradient(135deg, 
      rgba(255, 255, 255, 0.2) 0%, 
      rgba(255, 255, 255, 0.1) 100%);
    border-color: rgba(232, 28, 255, 0.4);
    transform: translateY(-2px);
    box-shadow: 
      0 10px 25px rgba(232, 28, 255, 0.2),
      0 0 0 1px rgba(255, 255, 255, 0.1) inset;

    &::before {
      left: 100%;
    }
  }

  &:active:not(:disabled) {
    transform: translateY(0px);
    transition: transform 0.1s;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    animation: none;
  }
`;

const MainContent = styled.div`
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.1) 0%, 
    rgba(255, 255, 255, 0.05) 100%);
  padding: 32px 24px;
  border-radius: 20px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  position: relative;
  overflow: hidden;

  /* Animated border gradient */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 20px;
    padding: 2px;
    background: linear-gradient(45deg, 
      transparent, 
      rgba(232, 28, 255, 0.3), 
      rgba(64, 201, 255, 0.3), 
      transparent,
      rgba(232, 28, 255, 0.3));
    background-size: 300% 300%;
    animation: borderGlow 6s ease infinite;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: xor;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    pointer-events: none;
  }

  /* Inner glow effect */
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 150%;
    height: 150%;
    background: radial-gradient(circle, 
      rgba(232, 28, 255, 0.1) 0%, 
      rgba(64, 201, 255, 0.1) 30%, 
      transparent 70%);
    transform: translate(-50%, -50%);
    animation: innerGlow 10s ease-in-out infinite;
    pointer-events: none;
  }

  @keyframes borderGlow {
    0%, 100% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
  }

  @keyframes innerGlow {
    0%, 100% {
      opacity: 0.3;
      transform: translate(-50%, -50%) scale(1);
    }
    50% {
      opacity: 0.6;
      transform: translate(-50%, -50%) scale(1.1);
    }
  }
`;

const HeaderContent = styled.div`
  text-align: center;
  margin-bottom: 32px;
`;

const Title = styled.h2`
  font-size: 32px;
  font-weight: bold;
  color: white;
  margin-bottom: 16px;
`;

const Description = styled.p`
  color: rgba(255, 255, 255, 0.8);
  font-size: 18px;
  line-height: 1.6;
`;

const ConfigurationPanel = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  color: #717171;
  font-weight: 600;
  font-size: 12px;
  margin-bottom: 5px;
`;

const Select = styled.select`
  width: 100%;
  padding: 12px 16px;
  border-radius: 8px;
  color: #fff;
  font-family: inherit;
  background-color: transparent;
  border: 1px solid #414141;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: #e81cff;
  }

  option {
    background-color: #212121;
    color: white;
  }
`;

const RangeInput = styled.input`
  width: 100%;
  height: 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
  outline: none;
  cursor: pointer;
  appearance: none;

  &::-webkit-slider-thumb {
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: linear-gradient(145deg, #e81cff, #40c9ff);
    cursor: pointer;
  }

  &::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: linear-gradient(145deg, #e81cff, #40c9ff);
    cursor: pointer;
    border: none;
  }
`;

const NumberInput = styled.input`
  width: 100%;
  padding: 12px 16px;
  border-radius: 8px;
  color: #fff;
  font-family: inherit;
  background-color: transparent;
  border: 1px solid #414141;

  &:focus {
    outline: none;
    border-color: #e81cff;
  }

  &::placeholder {
    opacity: 0.5;
  }
`;

const ButtonSection = styled.div`
  text-align: center;
  margin-bottom: 24px;
`;

const ExecuteButton = styled.button`
  padding: 16px 32px;
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #e81cff, #40c9ff) border-box;
  border: 2px solid transparent;
  border-radius: 8px;
  color: white;
  font-family: inherit;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
    scale: 1.05;
    box-shadow: 0 8px 25px rgba(232, 28, 255, 0.3);
  }

  &:active {
    scale: 0.95;
  }

  &:disabled {
    background: linear-gradient(#414141, #414141) padding-box,
                linear-gradient(145deg, transparent 35%, #666, #444) border-box;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
    animation: none;
  }

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const ButtonContent = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
`;

const Spinner = styled.div`
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorSection = styled.div`
  margin-bottom: 24px;
  padding: 16px;
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #ef4444, #f87171) border-box;
  border: 2px solid transparent;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const ErrorTitle = styled.h3`
  color: #fca5a5;
  font-weight: 600;
  margin-bottom: 8px;
`;

const ErrorText = styled.p`
  color: #fecaca;
  margin-bottom: 8px;
`;

const ClearButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #e81cff, #40c9ff) border-box;
  border: 2px solid transparent;
  border-radius: 8px;
  color: white;
  font-family: inherit;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
    scale: 1.05;
  }

  &:active {
    scale: 0.95;
  }

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const ResultsSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const ClearResultsSection = styled.div`
  text-align: center;
`;

const StatusBanner = styled.div<{ status: string }>`
  padding: 16px;
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, 
                ${props => props.status === 'success' ? '#22c55e, #4ade80' : '#f59e0b, #fbbf24'}) border-box;
  border: 2px solid transparent;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const StatusTitle = styled.h3<{ status: string }>`
  font-weight: 600;
  margin-bottom: 8px;
  color: ${props => 
    props.status === 'success' 
      ? '#86efac' 
      : '#fcd34d'
  };
`;

const ProcessingTime = styled.p`
  color: rgba(255, 255, 255, 0.8);
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

const StatCard = styled.div`
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #e81cff, #40c9ff) border-box;
  border: 2px solid transparent;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const StatNumber = styled.div`
  font-size: 24px;
  font-weight: bold;
  color: white;
`;

const StatLabel = styled.div`
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
`;

const ResultCard = styled.div`
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #e81cff, #40c9ff) border-box;
  border: 2px solid transparent;
  padding: 16px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const SectionTitle = styled.h4`
  color: white;
  font-weight: 600;
  margin-bottom: 12px;
`;

const EventsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;

  @keyframes slideInUp {
    0% {
      opacity: 0;
      transform: translateY(30px);
    }
    100% {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const EventCard = styled.div`
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #e81cff, #40c9ff) border-box;
  border: 2px solid transparent;
  padding: 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;

  /* Hover effect */
  &:hover {
    transform: translateY(-2px);
    box-shadow: 
      0 10px 25px rgba(0, 0, 0, 0.3),
      0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    
    /* Animated shimmer effect */
    &::before {
      opacity: 1;
      animation: shimmer 2s ease-in-out infinite;
    }
  }

  /* Shimmer overlay */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
      transparent, 
      rgba(255, 255, 255, 0.1), 
      transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  @keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
  }
`;

const EventHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  gap: 16px;
  position: relative;
  z-index: 1;
`;

const EventTitle = styled.h3`
  color: white;
  font-weight: 600;
  font-size: 1.25rem;
  line-height: 1.4;
  margin: 0;
  flex: 1;
  transition: color 0.3s ease;
  
  /* Gradient text effect on hover */
  .event-card:hover & {
    background: linear-gradient(135deg, #e81cff, #40c9ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
`;

const ConfidenceBadge = styled.span<{ confidence?: number }>`
  font-size: 12px;
  font-weight: 600;
  background: ${props => 
    props.confidence && props.confidence > 0.8 
      ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(34, 197, 94, 0.4))' 
      : props.confidence && props.confidence > 0.6 
        ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.4))' 
        : 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.4))'
  };
  color: ${props => 
    props.confidence && props.confidence > 0.8 
      ? '#86efac' 
      : props.confidence && props.confidence > 0.6 
        ? '#93c5fd' 
        : '#fcd34d'
  };
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid ${props => 
    props.confidence && props.confidence > 0.8 
      ? 'rgba(34, 197, 94, 0.3)' 
      : props.confidence && props.confidence > 0.6 
        ? 'rgba(59, 130, 246, 0.3)' 
        : 'rgba(245, 158, 11, 0.3)'
  };
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  flex-shrink: 0;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px ${props => 
      props.confidence && props.confidence > 0.8 
        ? 'rgba(34, 197, 94, 0.3)' 
        : props.confidence && props.confidence > 0.6 
          ? 'rgba(59, 130, 246, 0.3)' 
          : 'rgba(245, 158, 11, 0.3)'
    };
  }
`;

// HITL Review Components
const ReviewPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const ReviewHeader = styled.div`
  text-align: center;
  padding: 16px;
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #e81cff, #40c9ff) border-box;
  border: 2px solid transparent;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const ReviewTitle = styled.h3`
  color: white;
  font-weight: 600;
  font-size: 18px;
  margin-bottom: 8px;
`;

const ReviewSubtitle = styled.p`
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
`;

const EventReviewCard = styled.div<{ selected: boolean }>`
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, 
                ${props => props.selected ? '#22c55e, #4ade80' : '#e81cff, #40c9ff'}) border-box;
  border: 2px solid transparent;
  padding: 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;

  /* Enhanced selected state */
  ${props => props.selected && `
    box-shadow: 
      0 8px 25px rgba(34, 197, 94, 0.4),
      0 0 0 1px rgba(34, 197, 94, 0.2) inset;
    transform: scale(1.02);
  `}

  /* Hover effects */
  &:hover {
    transform: ${props => props.selected ? 'scale(1.03)' : 'translateY(-2px)'};
    box-shadow: 
      0 10px 30px rgba(0, 0, 0, 0.3),
      0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    
    /* Shimmer effect */
    &::before {
      opacity: 1;
      animation: shimmer 2s ease-in-out infinite;
    }
  }

  /* Shimmer overlay */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
      transparent, 
      rgba(255, 255, 255, 0.1), 
      transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
  }

  /* Active/Click state */
  &:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
  }

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  @keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
  }
`;

const EventCheckbox = styled.div`
  display: flex;
  align-items: center;
  position: relative;

  input[type="checkbox"] {
    width: 22px;
    height: 22px;
    cursor: pointer;
    appearance: none;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    background: transparent;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    
    &:hover {
      border-color: rgba(232, 28, 255, 0.6);
      transform: scale(1.1);
      box-shadow: 0 0 10px rgba(232, 28, 255, 0.3);
    }

    &:checked {
      background: linear-gradient(135deg, #e81cff, #40c9ff);
      border-color: transparent;
      transform: scale(1.05);
      
      &::after {
        content: '✓';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 14px;
        font-weight: bold;
        animation: checkmark 0.3s ease-in-out;
      }
    }

    &:focus {
      outline: none;
      box-shadow: 0 0 0 2px rgba(232, 28, 255, 0.3);
    }
  }

  @keyframes checkmark {
    0% { 
      opacity: 0; 
      transform: translate(-50%, -50%) scale(0.5); 
    }
    100% { 
      opacity: 1; 
      transform: translate(-50%, -50%) scale(1); 
    }
  }
`;

const EventTitleSection = styled.div`
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
`;

const DetailRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
`;

const DetailLabel = styled.span`
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  font-weight: 500;
  min-width: 80px;
`;

const DetailValue = styled.span`
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
`;

const EventEditSection = styled.div`
  margin-top: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const EditSectionTitle = styled.h5`
  color: white;
  font-weight: 600;
  margin-bottom: 12px;
  font-size: 14px;
`;

const EditGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
`;

const EditField = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const EditFieldFull = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  grid-column: 1 / -1;
`;

const EditLabel = styled.label`
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  font-weight: 500;
`;

const EditInput = styled.input`
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: #e81cff;
    box-shadow: 0 0 0 2px rgba(232, 28, 255, 0.2);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

const EditTextarea = styled.textarea`
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: #e81cff;
    box-shadow: 0 0 0 2px rgba(232, 28, 255, 0.2);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

const ApprovalActions = styled.div`
  margin-top: 24px;
  padding: 20px;
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #e81cff, #40c9ff) border-box;
  border: 2px solid transparent;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const ActionButtonsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
`;

const ApprovalButton = styled.button<{ variant: 'approve-all' | 'approve-selected' | 'reject' | 'back' }>`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 8px;
  border: none;
  font-family: inherit;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  ${props => {
    switch (props.variant) {
      case 'approve-all':
        return `
          background: linear-gradient(145deg, #22c55e, #16a34a);
          color: white;
          &:hover:not(:disabled) {
            background: linear-gradient(145deg, #16a34a, #15803d);
            scale: 1.05;
            box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4);
          }
        `;
      case 'approve-selected':
        return `
          background: linear-gradient(145deg, #3b82f6, #2563eb);
          color: white;
          &:hover:not(:disabled) {
            background: linear-gradient(145deg, #2563eb, #1d4ed8);
            scale: 1.05;
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
          }
        `;
      case 'reject':
        return `
          background: linear-gradient(145deg, #ef4444, #dc2626);
          color: white;
          &:hover:not(:disabled) {
            background: linear-gradient(145deg, #dc2626, #b91c1c);
            scale: 1.05;
            box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
          }
        `;
      case 'back':
        return `
          background: linear-gradient(145deg, #6b7280, #4b5563);
          color: white;
          &:hover:not(:disabled) {
            background: linear-gradient(145deg, #4b5563, #374151);
            scale: 1.05;
            box-shadow: 0 8px 25px rgba(107, 114, 128, 0.4);
          }
        `;
    }
  }}

  &:active:not(:disabled) {
    scale: 0.95;
  }

  &:disabled {
    background: linear-gradient(145deg, #6b7280, #4b5563);
    cursor: not-allowed;
    opacity: 0.6;
    transform: none;
    box-shadow: none;
  }
`;

const NoEventsFound = styled.div`
  text-align: center;
  padding: 48px 24px;
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #f59e0b, #fbbf24) border-box;
  border: 2px solid transparent;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const NoEventsIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
`;

const NoEventsTitle = styled.h3`
  color: #fcd34d;
  font-weight: 600;
  margin-bottom: 12px;
`;

const NoEventsText = styled.p`
  color: #fde68a;
  margin-bottom: 24px;
  line-height: 1.5;
`;

const RetryButton = styled.button`
  padding: 12px 24px;
  background: linear-gradient(145deg, #f59e0b, #d97706);
  color: white;
  border: none;
  border-radius: 8px;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: linear-gradient(145deg, #d97706, #b45309);
    scale: 1.05;
    box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
  }

  &:active {
    scale: 0.95;
  }
`;

const EventDetails = styled.div`
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
`;

const EventTime = styled.p`
  margin: 2px 0;
`;

const LinksList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const CalendarLink = styled.a`
  display: block;
  padding: 12px 16px;
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #3b82f6, #60a5fa) border-box;
  border: 2px solid transparent;
  border-radius: 8px;
  color: #93c5fd;
  text-decoration: none;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  &:hover {
    scale: 1.02;
    color: #bfdbfe;
  }

  &:active {
    scale: 0.98;
  }

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const TrustLinksList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const TrustLink = styled.div`
  color: rgba(255, 255, 255, 0.7);
  font-family: monospace;
  font-size: 14px;
  word-break: break-all;
`;

const WarningsSection = styled.div`
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #f59e0b, #fbbf24) border-box;
  border: 2px solid transparent;
  padding: 16px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const WarningsTitle = styled.h4`
  color: #fcd34d;
  font-weight: 600;
  margin-bottom: 12px;
`;

const WarningsList = styled.ul`
  color: #fde68a;
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const WarningItem = styled.li`
  list-style: none;
`;

const InfoPanel = styled.div`
  margin-top: 32px;
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #e81cff, #40c9ff) border-box;
  border: 2px solid transparent;
  padding: 16px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  background-size: 200% 100%;
  animation: gradient 5s ease infinite;

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const InfoTitle = styled.h4`
  color: white;
  font-weight: 600;
  margin-bottom: 8px;
`;

const InfoList = styled.ul`
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const InfoItem = styled.li`
  list-style: none;
`;

// Transition Components
const TransitionContainer = styled.div<{ showTransition: boolean }>`
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  transform: ${props => props.showTransition ? 'translateY(-100px)' : 'translateY(0)'};
  opacity: ${props => props.showTransition ? '0.8' : '1'};
`;

const TransitionConfigPanel = styled.div<{ showTransition: boolean }>`
  background: linear-gradient(#212121, #212121) padding-box,
              linear-gradient(145deg, transparent 35%, #e81cff, #40c9ff) border-box;
  border: 2px solid transparent;
  padding: 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  margin-bottom: 24px;
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  transform: ${props => props.showTransition ? 'scale(0.9) translateY(-50px)' : 'scale(1) translateY(0)'};
  opacity: ${props => props.showTransition ? '0.7' : '1'};
  
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const TransitionProcessing = styled.div<{ showTransition: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 40px;
  opacity: ${props => props.showTransition ? '1' : '0'};
  transform: ${props => props.showTransition ? 'translateY(0)' : 'translateY(20px)'};
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s;
`;

const ProcessingText = styled.p`
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  text-align: center;
`;

const TransitionNewContent = styled.div<{ showTransition: boolean }>`
  opacity: ${props => props.showTransition ? '1' : '0'};
  transform: ${props => props.showTransition ? 'translateY(0)' : 'translateY(30px)'};
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.4s;
  text-align: center;
  margin-top: 20px;
`;

export default AICalendarAgent;
