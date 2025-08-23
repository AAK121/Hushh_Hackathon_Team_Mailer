import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';

interface AgentFormData {
  name: string;
  description: string;
  short_description: string;
  category: string;
  price: number;
  icon: string;
  features: string[];
  developer: string;
  version: string;
  tags: string[];
  is_featured: boolean;
  is_premium: boolean;
}

interface AgentAdminProps {
  onBack: () => void;
}

const AgentAdmin: React.FC<AgentAdminProps> = ({ onBack }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  
  const [formData, setFormData] = useState<AgentFormData>({
    name: '',
    description: '',
    short_description: '',
    category: 'Productivity',
    price: 0,
    icon: '🤖',
    features: [''],
    developer: '',
    version: '1.0.0',
    tags: [''],
    is_featured: false,
    is_premium: false
  });

  const categories = ['Productivity', 'Communication', 'Analytics', 'Marketing', 'Development', 'Creative'];
  const commonIcons = ['🤖', '📧', '📅', '💬', '✉️', '📊', '📱', '💻', '✅', '🎨', '🔧', '⚡', '🚀', '💡', '🔍', '📈'];

  const handleInputChange = (field: keyof AgentFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleArrayInputChange = (field: 'features' | 'tags', index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => i === index ? value : item)
    }));
  };

  const addArrayItem = (field: 'features' | 'tags') => {
    setFormData(prev => ({
      ...prev,
      [field]: [...prev[field], '']
    }));
  };

  const removeArrayItem = (field: 'features' | 'tags', index: number) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      // Validate form
      if (!formData.name || !formData.description || !formData.short_description) {
        throw new Error('Please fill in all required fields');
      }

      // Filter out empty features and tags
      const cleanedFeatures = formData.features.filter(f => f.trim());
      const cleanedTags = formData.tags.filter(t => t.trim());

      if (cleanedFeatures.length === 0) {
        throw new Error('Please add at least one feature');
      }

      const agentData = {
        ...formData,
        features: cleanedFeatures,
        tags: cleanedTags,
        downloads: 0,
        rating: 0
      };

      if (supabase) {
        const { error } = await supabase
          .from('agents')
          .insert([agentData]);

        if (error) throw error;

        setMessage({ type: 'success', text: 'Agent added successfully! 🎉' });
        
        // Reset form
        setFormData({
          name: '',
          description: '',
          short_description: '',
          category: 'Productivity',
          price: 0,
          icon: '🤖',
          features: [''],
          developer: '',
          version: '1.0.0',
          tags: [''],
          is_featured: false,
          is_premium: false
        });
      } else {
        // Demo mode
        setMessage({ type: 'success', text: 'Agent added successfully! (Demo mode - not saved to database)' });
        console.log('Demo mode - Agent data:', agentData);
      }
    } catch (error) {
      console.error('Error adding agent:', error);
      setMessage({ 
        type: 'error', 
        text: error instanceof Error ? error.message : 'Failed to add agent' 
      });
    } finally {
      setLoading(false);
    }
  };

  const styles = {
    container: {
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #4c6ef5 0%, #667eea 100%)',
      padding: '2rem',
      paddingTop: '8rem',
    },
    header: {
      textAlign: 'center' as const,
      marginBottom: '3rem',
      color: 'white',
    },
    title: {
      fontSize: '2.5rem',
      fontWeight: '700',
      marginBottom: '1rem',
      background: 'linear-gradient(45deg, #fff, #f0f8ff)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text',
    },
    subtitle: {
      fontSize: '1.1rem',
      opacity: 0.9,
      maxWidth: '600px',
      margin: '0 auto',
    },
    formContainer: {
      maxWidth: '800px',
      margin: '0 auto',
      background: 'rgba(255, 255, 255, 0.95)',
      borderRadius: '1.5rem',
      padding: '3rem',
      boxShadow: '0 25px 50px rgba(0, 0, 0, 0.15)',
      border: '1px solid rgba(255, 255, 255, 0.3)',
    },
    formGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '2rem',
    },
    formGroup: {
      marginBottom: '1.5rem',
    },
    label: {
      display: 'block',
      fontSize: '0.9rem',
      fontWeight: '600',
      color: '#374151',
      marginBottom: '0.5rem',
    },
    input: {
      width: '100%',
      padding: '0.75rem',
      borderRadius: '0.5rem',
      border: '1px solid #d1d5db',
      fontSize: '1rem',
      outline: 'none',
      transition: 'border-color 0.2s ease',
      boxSizing: 'border-box' as const,
    },
    textarea: {
      width: '100%',
      padding: '0.75rem',
      borderRadius: '0.5rem',
      border: '1px solid #d1d5db',
      fontSize: '1rem',
      outline: 'none',
      transition: 'border-color 0.2s ease',
      resize: 'vertical' as const,
      minHeight: '100px',
      boxSizing: 'border-box' as const,
    },
    select: {
      width: '100%',
      padding: '0.75rem',
      borderRadius: '0.5rem',
      border: '1px solid #d1d5db',
      fontSize: '1rem',
      outline: 'none',
      background: 'white',
      cursor: 'pointer',
      boxSizing: 'border-box' as const,
    },
    iconGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(8, 1fr)',
      gap: '0.5rem',
      marginTop: '0.5rem',
    },
    iconButton: {
      padding: '0.5rem',
      border: '2px solid #e5e7eb',
      borderRadius: '0.5rem',
      background: 'white',
      fontSize: '1.5rem',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      textAlign: 'center' as const,
    },
    iconButtonActive: {
      borderColor: '#4c6ef5',
      background: '#f0f4ff',
    },
    arrayContainer: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '0.5rem',
    },
    arrayItem: {
      display: 'flex',
      gap: '0.5rem',
      alignItems: 'center',
    },
    arrayInput: {
      flex: 1,
      padding: '0.5rem',
      borderRadius: '0.5rem',
      border: '1px solid #d1d5db',
      fontSize: '0.9rem',
      outline: 'none',
    },
    addButton: {
      padding: '0.5rem 1rem',
      borderRadius: '0.5rem',
      border: 'none',
      background: '#10b981',
      color: 'white',
      fontSize: '0.9rem',
      cursor: 'pointer',
      transition: 'background 0.2s ease',
    },
    removeButton: {
      padding: '0.5rem',
      borderRadius: '0.5rem',
      border: 'none',
      background: '#ef4444',
      color: 'white',
      fontSize: '0.9rem',
      cursor: 'pointer',
      width: '2rem',
      height: '2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
    checkboxContainer: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      marginTop: '0.5rem',
    },
    checkbox: {
      width: '1.2rem',
      height: '1.2rem',
      cursor: 'pointer',
    },
    submitButton: {
      width: '100%',
      padding: '1rem 2rem',
      borderRadius: '0.75rem',
      border: 'none',
      background: 'linear-gradient(45deg, #4c6ef5, #667eea)',
      color: 'white',
      fontSize: '1.1rem',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      marginTop: '2rem',
    },
    submitButtonDisabled: {
      opacity: 0.6,
      cursor: 'not-allowed',
    },
    backButton: {
      position: 'absolute' as const,
      top: '2rem',
      left: '2rem',
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      padding: '0.75rem 1.5rem',
      background: 'rgba(255, 255, 255, 0.2)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.3)',
      borderRadius: '2rem',
      color: 'white',
      textDecoration: 'none',
      fontSize: '0.9rem',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
    },
    message: {
      padding: '1rem',
      borderRadius: '0.5rem',
      marginBottom: '1rem',
      textAlign: 'center' as const,
      fontWeight: '500',
    },
    messageSuccess: {
      background: '#d1fae5',
      color: '#065f46',
      border: '1px solid #10b981',
    },
    messageError: {
      background: '#fee2e2',
      color: '#991b1b',
      border: '1px solid #ef4444',
    },
  };

  return (
    <div style={styles.container}>
      <button onClick={onBack} style={styles.backButton}>
        ← Back to Store
      </button>

      <div style={styles.header}>
        <h1 style={styles.title}>🛠️ Agent Admin</h1>
        <p style={styles.subtitle}>
          Add new agents to the HushMCP Agent Store
        </p>
      </div>

      <div style={styles.formContainer}>
        {message && (
          <div style={{
            ...styles.message,
            ...(message.type === 'success' ? styles.messageSuccess : styles.messageError)
          }}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={styles.formGrid}>
            <div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Agent Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="e.g., Super Task Manager"
                  style={styles.input}
                  required
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Short Description *</label>
                <input
                  type="text"
                  value={formData.short_description}
                  onChange={(e) => handleInputChange('short_description', e.target.value)}
                  placeholder="Brief description for the card"
                  style={styles.input}
                  required
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                  style={styles.select}
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Price ($)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.price}
                  onChange={(e) => handleInputChange('price', parseFloat(e.target.value) || 0)}
                  style={styles.input}
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Developer</label>
                <input
                  type="text"
                  value={formData.developer}
                  onChange={(e) => handleInputChange('developer', e.target.value)}
                  placeholder="Company or developer name"
                  style={styles.input}
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Version</label>
                <input
                  type="text"
                  value={formData.version}
                  onChange={(e) => handleInputChange('version', e.target.value)}
                  placeholder="e.g., 1.0.0"
                  style={styles.input}
                />
              </div>
            </div>

            <div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Full Description *</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Detailed description of the agent's capabilities"
                  style={styles.textarea}
                  required
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Icon</label>
                <div style={styles.iconGrid}>
                  {commonIcons.map(icon => (
                    <button
                      key={icon}
                      type="button"
                      onClick={() => handleInputChange('icon', icon)}
                      style={{
                        ...styles.iconButton,
                        ...(formData.icon === icon ? styles.iconButtonActive : {})
                      }}
                    >
                      {icon}
                    </button>
                  ))}
                </div>
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Features *</label>
                <div style={styles.arrayContainer}>
                  {formData.features.map((feature, index) => (
                    <div key={index} style={styles.arrayItem}>
                      <input
                        type="text"
                        value={feature}
                        onChange={(e) => handleArrayInputChange('features', index, e.target.value)}
                        placeholder="Feature description"
                        style={styles.arrayInput}
                      />
                      {formData.features.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeArrayItem('features', index)}
                          style={styles.removeButton}
                        >
                          ×
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={() => addArrayItem('features')}
                    style={styles.addButton}
                  >
                    + Add Feature
                  </button>
                </div>
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Tags</label>
                <div style={styles.arrayContainer}>
                  {formData.tags.map((tag, index) => (
                    <div key={index} style={styles.arrayItem}>
                      <input
                        type="text"
                        value={tag}
                        onChange={(e) => handleArrayInputChange('tags', index, e.target.value)}
                        placeholder="Tag (lowercase)"
                        style={styles.arrayInput}
                      />
                      {formData.tags.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeArrayItem('tags', index)}
                          style={styles.removeButton}
                        >
                          ×
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={() => addArrayItem('tags')}
                    style={styles.addButton}
                  >
                    + Add Tag
                  </button>
                </div>
              </div>

              <div style={styles.formGroup}>
                <div style={styles.checkboxContainer}>
                  <input
                    type="checkbox"
                    id="featured"
                    checked={formData.is_featured}
                    onChange={(e) => handleInputChange('is_featured', e.target.checked)}
                    style={styles.checkbox}
                  />
                  <label htmlFor="featured" style={styles.label}>Featured Agent</label>
                </div>
                <div style={styles.checkboxContainer}>
                  <input
                    type="checkbox"
                    id="premium"
                    checked={formData.is_premium}
                    onChange={(e) => handleInputChange('is_premium', e.target.checked)}
                    style={styles.checkbox}
                  />
                  <label htmlFor="premium" style={styles.label}>Premium Agent</label>
                </div>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              ...styles.submitButton,
              ...(loading ? styles.submitButtonDisabled : {})
            }}
          >
            {loading ? 'Adding Agent...' : 'Add Agent to Store'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AgentAdmin;
