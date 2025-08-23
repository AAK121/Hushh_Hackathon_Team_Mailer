# Missing Frontend Features Documentation

## Overview
This document outlines all backend agent features that are not properly integrated with the frontend. The backend API (api.py) provides comprehensive endpoints for 5 main agents, but the frontend components are not fully utilizing these capabilities.

## 1. **MailerPanda Agent**

### Backend Features Available (API Endpoints):
- `/agents/mailerpanda/execute` - Full campaign execution with AI generation
- `/agents/mailerpanda/approve` - Human-in-the-loop approval workflow
- `/agents/mailerpanda/session/{campaign_id}` - Campaign session tracking
- `/agents/mailerpanda/mass-email` - Mass email with context personalization toggle
- `/agents/mailerpanda/analyze-excel` - Excel file analysis for personalization

### Missing Frontend Features:
1. **Description-Based Personalization** 
   - Backend supports AI-powered personalization using contact descriptions
   - Frontend lacks UI toggle for enabling/disabling personalization
   - No support for personalization_mode selection (smart/conservative/aggressive)

2. **Excel File Analysis**
   - Backend can analyze Excel files for context columns
   - Frontend missing preview of personalization opportunities
   - No display of contacts with/without descriptions

3. **Approval Workflow**
   - Backend supports approve/reject/modify/regenerate actions
   - Frontend lacks proper approval UI with all actions
   - Missing feedback mechanism for modifications

4. **Dynamic API Key Support**
   - Backend accepts dynamic API keys (Google, Mailjet)
   - Frontend hardcodes or doesn't pass API keys

## 2. **Relationship Memory Agent**

### Backend Features Available:
- `/agents/relationship_memory/execute` - Full relationship management
- `/agents/relationship_memory/proactive` - Proactive relationship checks
- `/agents/relationship_memory/chat/start` - Interactive chat sessions
- `/agents/relationship_memory/chat/message` - Chat messaging
- `/agents/relationship_memory/chat/{session_id}/history` - Chat history
- `/agents/relationship_memory/chat/sessions` - List all sessions

### Missing Frontend Features:
1. **Proactive Relationship Management**
   - Backend supports proactive triggers for reconnections
   - Frontend lacks proactive notification system
   - No display of upcoming important dates

2. **Natural Language Processing**
   - Backend uses AI for intent parsing (add contacts, memories, reminders)
   - Frontend uses hardcoded responses instead of API

3. **Chat Session Management**
   - Backend supports persistent chat sessions
   - Frontend doesn't utilize session endpoints
   - No history retrieval or session management

4. **Advanced Contact Features**
   - Backend supports priority levels for contacts
   - Missing last_talked_date tracking
   - No batch contact operations

5. **Memory and Reminder Management**
   - Backend has full CRUD for memories and reminders
   - Frontend shows placeholder text instead of actual functionality

## 3. **ChanduFinance Agent**

### Backend Features Available:
- `/agents/chandufinance/execute` - Comprehensive financial management
- Commands: setup_profile, update_income, add_goal, personal_stock_analysis, behavioral_coaching, etc.

### Missing Frontend Features:
1. **Profile Management**
   - Backend supports complete financial profile setup
   - Frontend missing profile creation/update forms
   - No risk tolerance or investment experience inputs

2. **Goal Management**
   - Backend supports financial goal tracking
   - Frontend lacks goal creation with target amounts and dates
   - Missing priority levels for goals

3. **Stock Analysis**
   - Backend provides personalized stock analysis
   - Frontend doesn't have stock ticker input
   - No display of analysis results

4. **Educational Content**
   - Backend offers explain_like_im_new, investment_education
   - Frontend missing educational content display
   - No complexity level selection

5. **Behavioral Coaching**
   - Backend provides AI-powered financial coaching
   - Frontend lacks coaching interface
   - No topic selection for coaching

## 4. **AddToCalendar Agent**

### Current Implementation Gaps:
1. **Manual Event Creation**
   - Backend supports manual_event action
   - Frontend form incomplete

2. **Dynamic API Key Support**
   - Backend accepts dynamic Google API keys
   - Frontend doesn't pass API keys properly

3. **Trust Links**
   - Backend generates trust links for delegation
   - Frontend doesn't display or use trust links

## 5. **Research Agent** (Completely Missing)

### Backend Features Available:
- `/agents/research/search/arxiv` - ArXiv paper search
- `/agents/research/upload` - PDF upload and processing
- `/agents/research/paper/{paper_id}/summary` - AI summaries
- `/agents/research/paper/{paper_id}/process/snippet` - Snippet processing
- `/agents/research/session/notes` - Note saving

### Missing Frontend Features:
1. **Complete Research Agent Component**
   - No frontend component exists for research agent
   - Need to create full UI for paper search and management
   - PDF upload interface required
   - Note-taking functionality needed

## API Service Layer Issues

### Current hushMcpApi.ts Limitations:
1. **Missing Research Agent Methods**
   - No methods for research agent endpoints
   - Need to add search, upload, summary, snippet, notes methods

2. **Incomplete Relationship Memory Integration**
   - Missing proactive check method
   - Chat session management incomplete

3. **ChanduFinance Not Integrated**
   - No methods for ChanduFinance agent
   - Need complete command execution support

## Recommended Implementation Priority

### High Priority:
1. Complete Relationship Memory chat integration
2. Add ChanduFinance profile and goal management
3. Implement MailerPanda personalization toggle
4. Create Research Agent component

### Medium Priority:
1. Relationship Memory proactive features
2. ChanduFinance stock analysis
3. MailerPanda approval workflow enhancements
4. AddToCalendar trust links

### Low Priority:
1. Educational content in ChanduFinance
2. Behavioral coaching interface
3. Advanced Excel analysis preview

## Required Frontend Components to Create/Update

1. **New Components Needed:**
   - ResearchAgent.tsx
   - ChanduFinanceProfile.tsx
   - RelationshipProactive.tsx
   - PersonalizationToggle.tsx

2. **Components to Update:**
   - RelationshipAgent.tsx (add real API integration)
   - FinanceAgent.tsx (integrate with ChanduFinance backend)
   - MailerPandaAgent.tsx (add personalization features)
   - AddToCalendarAgent.tsx (complete manual event)

3. **Service Updates:**
   - hushMcpApi.ts (add all missing methods)
   - Create new research-api.ts
   - Create new finance-api.ts
