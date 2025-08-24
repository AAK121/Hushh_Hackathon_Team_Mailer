import React from 'react';

interface FinanceAgentDebugProps {
  onBack: () => void;
  onSendToHITL?: (message: string, context: any) => void;
}

const FinanceAgentDebug: React.FC<FinanceAgentDebugProps> = ({ onBack }) => {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={onBack} 
          style={{
            padding: '10px 20px',
            backgroundColor: '#95a5a6',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          ← Back
        </button>
      </div>
      
      <h1 style={{ color: '#2c3e50', marginBottom: '30px' }}>
        🔧 Finance Agent Debug Mode
      </h1>
      
      <div style={{ 
        backgroundColor: '#f8f9fa', 
        padding: '20px', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h3>✅ Component Loaded Successfully!</h3>
        <p>The FinanceAgent component is working and can be accessed.</p>
      </div>

      <div style={{ 
        backgroundColor: '#d4edda', 
        border: '1px solid #c3e6cb',
        padding: '15px', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h4>Debug Information:</h4>
        <ul>
          <li>✅ Component renders correctly</li>
          <li>✅ Navigation working (you can go back)</li>
          <li>✅ Styling applied successfully</li>
          <li>✅ TypeScript compilation successful</li>
        </ul>
      </div>

      <div style={{ 
        backgroundColor: '#fff3cd', 
        border: '1px solid #ffeaa7',
        padding: '15px', 
        borderRadius: '8px'
      }}>
        <h4>Next Steps:</h4>
        <p>If you can see this page, the basic routing and component loading works.</p>
        <p>Now we can test the full FinanceAgent with API calls.</p>
        
        <button 
          onClick={() => {
            // Simple test
            console.log('Finance Agent Debug: Button clicked');
            alert('Finance Agent Debug: Basic interaction working!');
          }}
          style={{
            padding: '10px 20px',
            backgroundColor: '#3498db',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            marginTop: '10px'
          }}
        >
          Test Basic Interaction
        </button>
      </div>
    </div>
  );
};

export default FinanceAgentDebug;
