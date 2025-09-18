# Implementation Plan

- [x] 1. Enhance Pydantic models for batch operations and priority tracking



  - Modify ContactInfo model to include priority and last_talked_date fields
  - Update UserIntent model to support List[ContactInfo] for batch operations
  - Add get_advice action to UserIntent action literals
  - Enhance RelationshipMemoryState with proactive trigger fields
  - Write unit tests for enhanced model validation


  - _Requirements: 3.1, 3.2, 3.3, 3.4, 2.1, 2.2, 4.1_

- [ ] 2. Implement utility functions for date and interaction calculations
  - Create _calculate_days_until_event function for birthday/anniversary detection
  - Create _calculate_days_since_contact function for reconnection logic
  - Implement _format_triggers_for_llm function for proactive message context


  - Implement _format_memories_for_advice function for advice generation context
  - Write unit tests for date calculation edge cases and timezone handling
  - _Requirements: 1.1, 1.2, 1.5, 1.6, 1.7, 7.3_

- [ ] 3. Create proactive trigger detection system
  - Implement check_for_proactive_triggers LangGraph node
  - Add logic to scan contacts for upcoming birthdays within 30 days


  - Add logic to scan contacts for upcoming anniversaries within 30 days
  - Implement reconnection opportunity detection based on priority levels
  - Add error handling for vault access failures during proactive checks
  - Write unit tests for trigger detection logic with various contact scenarios
  - _Requirements: 1.1, 1.2, 1.3, 1.5, 1.6, 1.7, 8.2_

- [x] 4. Implement proactive response generation


  - Create generate_proactive_response LangGraph node
  - Implement LLM prompt for consolidating multiple triggers into coherent messages
  - Add logic to handle empty trigger lists gracefully
  - Implement friendly, conversational tone for proactive notifications
  - Add error handling for LLM generation failures with fallback messages
  - Write unit tests for response generation with various trigger combinations
  - _Requirements: 1.4, 5.1, 5.2, 5.3, 5.4, 8.3_



- [ ] 5. Create conversational advice generation system
  - Implement conversational_advice_tool LangGraph node
  - Add logic to retrieve contact information and associated memories
  - Create LLM prompt for generating contextual advice based on stored memories
  - Implement handling for contacts with no stored memories
  - Add support for different advice types (gifts, conversation topics, relationship management)


  - Write unit tests for advice generation with various memory scenarios
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 6. Enhance batch contact processing capabilities
  - Modify _add_contact_tool to handle List[ContactInfo] instead of single contact
  - Implement individual contact validation within batch processing
  - Add logic to continue processing remaining contacts when one fails


  - Create consolidated success/error reporting for batch operations
  - Implement automatic priority and last_talked_date setting for new contacts
  - Write unit tests for batch processing with mixed success/failure scenarios
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 8.1_

- [ ] 7. Implement interaction history tracking
  - Create update_interaction_tool utility function


  - Modify _add_memory_tool to automatically update last_talked_date
  - Add logic to set last_talked_date when creating new contacts
  - Implement contact display with days since last interaction
  - Add handling for contacts with no interaction history
  - Write unit tests for interaction timestamp updates
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_



- [ ] 8. Update LangGraph workflow routing and integration
  - Modify _build_langgraph_workflow to include new proactive nodes
  - Update workflow to start with check_for_proactive_triggers on startup
  - Add routing logic for proactive triggers vs normal intent parsing
  - Implement routing for get_advice intent to conversational_advice_tool
  - Update _route_to_tool function to handle batch operations and advice requests
  - Write integration tests for complete workflow paths

  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [ ] 9. Enhance intent parsing for batch operations and advice requests
  - Update _parse_intent_node system prompt to recognize batch contact inputs
  - Add parsing logic for multiple contacts in single user input
  - Implement intent recognition for advice requests about specific contacts
  - Add validation for batch contact parsing accuracy
  - Enhance confidence scoring for complex batch and advice intents


  - Write unit tests for intent parsing with batch and advice scenarios
  - _Requirements: 2.1, 2.6, 4.1, 4.2_

- [ ] 10. Implement enhanced error handling and validation
  - Add comprehensive error handling for batch operation failures
  - Implement graceful degradation when proactive checks fail
  - Add detailed validation error reporting for individual contacts in batches


  - Create fallback responses for advice generation failures
  - Implement logging for proactive check errors without interrupting workflow
  - Write unit tests for error scenarios and recovery mechanisms
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 11. Update VaultManager integration for enhanced contact storage
  - Modify vault storage schema to support priority and last_talked_date fields




  - Implement batch contact storage operations in VaultManager
  - Add methods for retrieving contacts with date-based filtering
  - Implement efficient querying for proactive trigger detection
  - Add data migration logic for existing contacts without new fields
  - Write unit tests for enhanced vault operations
  - _Requirements: 3.1, 3.2, 3.3, 1.1, 1.2_

- [ ] 12. Create comprehensive test suite for proactive features
  - Write integration tests for complete proactive workflow scenarios
  - Create end-to-end tests for batch contact import with various input formats
  - Implement performance tests for large contact databases (100+ contacts)
  - Add tests for proactive trigger detection with edge cases
  - Create tests for advice generation with different memory types and quantities
  - Write tests for error handling and recovery in batch operations
  - _Requirements: All requirements - comprehensive testing coverage_

- [ ] 13. Update agent entry point and startup logic
  - Modify handle method to support is_startup flag for proactive checks
  - Add logic to determine when to run proactive triggers vs normal processing
  - Implement conversation history tracking in agent state
  - Add support for maintaining context between proactive and user-initiated interactions
  - Update agent initialization to prepare for proactive capabilities
  - Write integration tests for agent startup and proactive trigger flow
  - _Requirements: 1.1, 1.3, 5.5, 6.1, 6.2_

- [ ] 14. Integrate and test complete proactive relationship manager system
  - Perform end-to-end testing of proactive startup flow
  - Test complete batch contact import scenarios with real-world data
  - Validate advice generation with comprehensive memory datasets
  - Test interaction between proactive triggers and user responses
  - Perform load testing with large contact databases
  - Validate HushhMCP compliance throughout all new features
  - Create user acceptance scenarios and validate against requirements
  - _Requirements: All requirements - final integration and validation_