-- Create agents table for the Agent Store
CREATE TABLE IF NOT EXISTS agents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    short_description VARCHAR(500) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    rating DECIMAL(3,2) DEFAULT 0.00 CHECK (rating >= 0 AND rating <= 5),
    downloads INTEGER DEFAULT 0,
    icon VARCHAR(10) DEFAULT '🤖',
    screenshots TEXT[] DEFAULT '{}',
    features TEXT[] DEFAULT '{}',
    developer VARCHAR(255) NOT NULL,
    version VARCHAR(50) DEFAULT '1.0.0',
    tags TEXT[] DEFAULT '{}',
    is_featured BOOLEAN DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create purchases table to track user purchases
CREATE TABLE IF NOT EXISTS agent_purchases (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    purchase_price DECIMAL(10,2) NOT NULL,
    purchased_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, agent_id)
);

-- Create reviews table for agent ratings and reviews
CREATE TABLE IF NOT EXISTS agent_reviews (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, agent_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_agents_category ON agents(category);
CREATE INDEX IF NOT EXISTS idx_agents_featured ON agents(is_featured);
CREATE INDEX IF NOT EXISTS idx_agents_premium ON agents(is_premium);
CREATE INDEX IF NOT EXISTS idx_agents_rating ON agents(rating);
CREATE INDEX IF NOT EXISTS idx_agents_downloads ON agents(downloads);
CREATE INDEX IF NOT EXISTS idx_agent_purchases_user ON agent_purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_reviews_agent ON agent_reviews(agent_id);

-- Insert sample data
INSERT INTO agents (name, description, short_description, category, price, rating, downloads, icon, features, developer, version, tags, is_featured, is_premium) VALUES
('EmailBot Pro', 'Advanced email automation and response management system with AI-powered insights and smart filtering capabilities.', 'Automate your email workflow with AI', 'Communication', 29.99, 4.8, 15420, '📧', ARRAY['AI Response Generation', 'Smart Filtering', 'Analytics Dashboard', 'Multi-account Support'], 'HushTech', '2.1.0', ARRAY['email', 'automation', 'ai', 'productivity'], TRUE, TRUE),

('DataViz Master', 'Create stunning data visualizations and interactive dashboards with ease. Perfect for business intelligence and reporting.', 'Beautiful data visualization made simple', 'Analytics', 49.99, 4.9, 8750, '📊', ARRAY['Interactive Charts', 'Real-time Data', 'Export Options', 'Team Collaboration'], 'ChartCorp', '1.5.2', ARRAY['charts', 'analytics', 'visualization', 'data'], TRUE, TRUE),

('Social Scheduler', 'Schedule and manage your social media posts across multiple platforms with advanced analytics and team management features.', 'Schedule posts across all platforms', 'Marketing', 19.99, 4.6, 23100, '📱', ARRAY['Multi-platform Support', 'Content Calendar', 'Analytics', 'Team Management'], 'SocialTech', '3.0.1', ARRAY['social media', 'scheduling', 'marketing', 'automation'], FALSE, FALSE),

('Code Assistant', 'AI-powered coding companion that helps with code generation, debugging, and optimization across multiple programming languages.', 'Your AI coding companion', 'Development', 39.99, 4.7, 12300, '💻', ARRAY['Code Generation', 'Bug Detection', 'Performance Optimization', 'Multiple Languages'], 'DevTools Inc', '1.8.0', ARRAY['coding', 'ai', 'development', 'debugging'], TRUE, TRUE),

('Task Organizer', 'Smart task management with AI-powered prioritization and scheduling. Integrate with your calendar and collaborate with teams.', 'Organize tasks with AI intelligence', 'Productivity', 15.99, 4.5, 18900, '✅', ARRAY['Smart Prioritization', 'Calendar Integration', 'Team Collaboration', 'Progress Tracking'], 'ProductiveTech', '2.3.1', ARRAY['tasks', 'productivity', 'organization', 'ai'], FALSE, FALSE),

('Creative Studio', 'AI-powered design tool for creating stunning graphics, logos, and marketing materials with professional templates and brand kits.', 'Create stunning designs with AI', 'Creative', 34.99, 4.8, 9650, '🎨', ARRAY['AI Design Generation', 'Template Library', 'Brand Kit', 'Export Options'], 'CreativeAI', '1.2.0', ARRAY['design', 'creative', 'ai', 'graphics'], TRUE, TRUE),

('Document Scanner', 'Advanced OCR and document processing agent with AI-powered text extraction and intelligent categorization.', 'Digitize and organize documents', 'Productivity', 24.99, 4.4, 14200, '📄', ARRAY['OCR Technology', 'Smart Categorization', 'Cloud Storage', 'Batch Processing'], 'DocTech Solutions', '1.7.3', ARRAY['ocr', 'documents', 'scanning', 'organization'], FALSE, FALSE),

('Voice Assistant Pro', 'Natural language processing agent for voice commands, transcription, and intelligent conversation management.', 'Your intelligent voice companion', 'Communication', 32.99, 4.6, 11800, '🎤', ARRAY['Voice Recognition', 'Real-time Transcription', 'Command Processing', 'Multi-language Support'], 'VoiceTech Labs', '2.0.4', ARRAY['voice', 'ai', 'transcription', 'commands'], TRUE, FALSE),

('Financial Tracker', 'Comprehensive financial management agent with expense tracking, budget planning, and investment analysis features.', 'Manage your finances intelligently', 'Analytics', 27.99, 4.7, 16500, '💰', ARRAY['Expense Tracking', 'Budget Planning', 'Investment Analysis', 'Financial Reports'], 'FinanceAI Corp', '1.9.1', ARRAY['finance', 'budgeting', 'expenses', 'analytics'], FALSE, TRUE),

('Meeting Assistant', 'AI-powered meeting management with automatic scheduling, note-taking, and action item tracking across teams.', 'Streamline your meetings with AI', 'Productivity', 21.99, 4.3, 13700, '📅', ARRAY['Auto Scheduling', 'Meeting Notes', 'Action Items', 'Calendar Integration'], 'MeetingTech', '1.4.2', ARRAY['meetings', 'scheduling', 'productivity', 'collaboration'], FALSE, FALSE);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update the updated_at column
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agent_reviews_updated_at BEFORE UPDATE ON agent_reviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
