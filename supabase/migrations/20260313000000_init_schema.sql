-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Skills table
CREATE TABLE skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  author VARCHAR(255),
  repository_url VARCHAR(255) UNIQUE,
  category VARCHAR(100),
  readme_content TEXT,
  installation_count INTEGER DEFAULT 0,
  rating NUMERIC(3,2) DEFAULT 0.0,
  security_score INTEGER DEFAULT 0,
  security_risk_level VARCHAR(50) DEFAULT 'unknown',
  security_report JSONB,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table
CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  icon VARCHAR(100),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Skill versions table
CREATE TABLE skill_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
  version VARCHAR(50) NOT NULL,
  release_notes TEXT,
  download_url VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(skill_id, version)
);

-- Analytics table
CREATE TABLE analytics (
  id BIGSERIAL PRIMARY KEY,
  skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL,
  user_agent TEXT,
  ip_address INET,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Search indexes
CREATE INDEX idx_skills_name ON skills USING gin(name gin_trgm_ops);
CREATE INDEX idx_skills_description ON skills USING gin(description gin_trgm_ops);
CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_security_score ON skills(security_score);
CREATE INDEX idx_skills_installation_count ON skills(installation_count DESC);

-- Enable RLS
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;

-- Read policies for public access
CREATE POLICY "Public read access to skills" ON skills FOR SELECT USING (true);
CREATE POLICY "Public read access to categories" ON categories FOR SELECT USING (true);
CREATE POLICY "Public read access to skill versions" ON skill_versions FOR SELECT USING (true);

-- Insert default categories
INSERT INTO categories (name, description, icon) VALUES
('AI Content', 'AI-powered content creation tools', 'file-text'),
('Research', 'Research and data analysis tools', 'search'),
('Automation', 'Workflow automation tools', 'zap'),
('Coding', 'Coding and development tools', 'code'),
('Data Analysis', 'Data processing and visualization tools', 'bar-chart'),
('Social Media', 'Social media management tools', 'share-2'),
('Productivity', 'Productivity and time management tools', 'clock'),
('Security', 'Security and privacy tools', 'shield');
