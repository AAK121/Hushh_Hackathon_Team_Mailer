import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { CogIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';

interface SettingsProps {
  onBack: () => void;
}

interface SettingsState {
  emailHeight: number;
}

const Settings: React.FC<SettingsProps> = ({ onBack }) => {
  const [settings, setSettings] = useState<SettingsState>({
    emailHeight: 80, // Default height in pixels
  });

  // Load settings from localStorage on component mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('email-app-settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(parsed);
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, []);

  // Save settings to localStorage whenever settings change
  useEffect(() => {
    localStorage.setItem('email-app-settings', JSON.stringify(settings));
    
    // Dispatch custom event to notify other components of settings change
    window.dispatchEvent(new CustomEvent('settingsChanged', { 
      detail: settings 
    }));
  }, [settings]);

  const handleEmailHeightChange = (value: number) => {
    setSettings(prev => ({
      ...prev,
      emailHeight: value
    }));
  };

  return (
    <StyledWrapper>
      <div className="container">
        <div className="settings-box">
          {/* Header */}
          <div className="header">
            <button onClick={onBack} className="back-button">← Back</button>
            <span className="title">
              <CogIcon className="title-icon" />
              Settings
            </span>
          </div>

          {/* Settings Content */}
          <div className="settings-content">
            {/* Email Display Settings */}
            <div className="settings-section">
              <div className="section-header">
                <AdjustmentsHorizontalIcon className="section-icon" />
                <h3 className="section-title">Email Display</h3>
              </div>
              
              <div className="setting-item">
                <div className="setting-info">
                  <label className="setting-label">Email Item Height</label>
                  <p className="setting-description">
                    Adjust the height of email items in the inbox list for better readability.
                  </p>
                </div>
                
                <div className="setting-control">
                  <div className="slider-container">
                    <input
                      type="range"
                      min="60"
                      max="150"
                      step="5"
                      value={settings.emailHeight}
                      onChange={(e) => handleEmailHeightChange(parseInt(e.target.value))}
                      className="height-slider"
                    />
                    <div className="slider-labels">
                      <span className="label-min">Compact</span>
                      <span className="label-current">{settings.emailHeight}px</span>
                      <span className="label-max">Spacious</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Preview */}
              <div className="preview-section">
                <h4 className="preview-title">Preview</h4>
                <div className="email-preview" style={{ height: `${settings.emailHeight}px` }}>
                  <div className="preview-email">
                    <div className="preview-header">
                      <div className="preview-sender">John Doe</div>
                      <div className="preview-time">2:30 PM</div>
                    </div>
                    <div className="preview-subject">Sample Email Subject</div>
                    <div className="preview-snippet">This is a preview of how your emails will look with the current height setting...</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Settings Sections can be added here */}
            <div className="settings-section">
              <div className="section-header">
                <h3 className="section-title">More Settings Coming Soon</h3>
              </div>
              <p className="coming-soon">
                Additional customization options will be available in future updates.
              </p>
            </div>
          </div>
        </div>
      </div>
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;

  .container {
    --form-width: 800px;
    --aspect-ratio: 1.2;
    --settings-box-color: var(--primary-main, #272757);
    --input-color: var(--primary-medium, #505081);
    --button-color: var(--primary-dark, #0F0E47);
    --footer-color: rgba(255, 255, 255, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    overflow: hidden;
    background: var(--settings-box-color);
    border-radius: 24px;
    width: calc(var(--form-width) + 1px);
    height: calc(var(--form-width) * var(--aspect-ratio) + 1px);
    z-index: 8;
    box-shadow:
      0 4px 8px rgba(0, 0, 0, 0.2),
      0 8px 16px rgba(0, 0, 0, 0.2),
      0 0 8px rgba(255, 255, 255, 0.1),
      0 0 16px rgba(255, 255, 255, 0.08);
  }

  .container::before {
    content: "";
    position: absolute;
    inset: -50px;
    z-index: -2;
    background: conic-gradient(
      from 45deg,
      transparent 75%,
      #fff,
      transparent 100%
    );
    animation: spin 4s ease-in-out infinite;
  }

  @keyframes spin {
    100% {
      transform: rotate(360deg);
    }
  }

  .settings-box {
    background: var(--settings-box-color);
    border-radius: 24px;
    padding: 28px;
    width: var(--form-width);
    height: calc(var(--form-width) * var(--aspect-ratio));
    position: absolute;
    z-index: 10;
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    box-shadow:
      inset 0 40px 60px -8px rgba(255, 255, 255, 0.12),
      inset 4px 0 12px -6px rgba(255, 255, 255, 0.12),
      inset 0 0 12px -4px rgba(255, 255, 255, 0.12);
    overflow-y: auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    color: white;
  }

  .title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 24px;
    font-weight: bold;
  }

  .title-icon {
    width: 24px;
    height: 24px;
  }

  .back-button {
    background: var(--button-color);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 12px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: 0.3s;
    box-shadow:
      inset 0px 3px 6px -4px rgba(255, 255, 255, 0.6),
      inset 0px -3px 6px -2px rgba(0, 0, 0, 0.8);
  }

  .back-button:hover {
    background: rgba(255, 255, 255, 0.25);
    box-shadow:
      inset 0px 3px 6px rgba(255, 255, 255, 0.6),
      inset 0px -3px 6px rgba(0, 0, 0, 0.8),
      0px 0px 8px rgba(255, 255, 255, 0.05);
  }

  .settings-content {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .settings-section {
    background: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
  }

  .section-icon {
    width: 20px;
    height: 20px;
    color: var(--primary-light, #8686AC);
  }

  .section-title {
    color: white;
    font-size: 18px;
    font-weight: 600;
    margin: 0;
  }

  .setting-item {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .setting-info {
    flex: 1;
  }

  .setting-label {
    color: white;
    font-size: 16px;
    font-weight: 600;
    display: block;
    margin-bottom: 4px;
  }

  .setting-description {
    color: var(--footer-color);
    font-size: 14px;
    margin: 0;
    line-height: 1.4;
  }

  .setting-control {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .slider-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .height-slider {
    width: 100%;
    height: 8px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.2);
    outline: none;
    cursor: pointer;
    appearance: none;
  }

  .height-slider::-webkit-slider-thumb {
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-medium, #505081), var(--primary-dark, #0F0E47));
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(80, 80, 129, 0.4);
  }

  .height-slider::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-medium, #505081), var(--primary-dark, #0F0E47));
    cursor: pointer;
    border: none;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
  }

  .slider-labels {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--footer-color);
  }

  .label-current {
    background: rgba(80, 80, 129, 0.2);
    color: var(--primary-light, #8686AC);
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
  }

  .preview-section {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .preview-title {
    color: white;
    font-size: 14px;
    font-weight: 600;
    margin: 0 0 12px 0;
  }

  .email-preview {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 12px;
    transition: height 0.2s ease;
    overflow: hidden;
  }

  .preview-email {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
  }

  .preview-sender {
    color: white;
    font-weight: 600;
    font-size: 14px;
  }

  .preview-time {
    color: var(--footer-color);
    font-size: 12px;
  }

  .preview-subject {
    color: white;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .preview-snippet {
    color: var(--footer-color);
    font-size: 12px;
    line-height: 1.3;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .coming-soon {
    color: var(--footer-color);
    font-size: 14px;
    margin: 0;
    font-style: italic;
  }
`;

export default Settings;
