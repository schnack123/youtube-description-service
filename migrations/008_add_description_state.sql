-- Migration 008: Add YouTube Description Service tables
-- Created: 2025-10-30
-- Description: Adds workflow_description_state and ai_prompts tables

-- Table 1: workflow_description_state
-- Tracks description generation jobs per workflow
CREATE TABLE IF NOT EXISTS workflow_description_state (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER,  -- Optional: for future workflow integration
    novel_name VARCHAR(255),  -- Novel name for Phase 1
    job_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL,  -- pending, processing, completed, failed
    progress_data JSONB,  -- { descriptions_generated: X, total_videos: Y }
    
    -- User inputs
    novel_context TEXT,
    playlist_url TEXT,
    subscribe_text TEXT,
    
    -- AI-generated content (novel-level)
    generated_about TEXT,
    generated_what_to_expect TEXT,
    generated_tags TEXT,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Error handling
    error_message TEXT,
    
    -- Optimistic locking
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_description_workflow ON workflow_description_state(workflow_id);
CREATE INDEX idx_description_status ON workflow_description_state(status);
CREATE INDEX idx_description_job_id ON workflow_description_state(job_id);

-- Table 2: ai_prompts
-- Store AI prompts in database for easy editing
CREATE TABLE IF NOT EXISTS ai_prompts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_prompts_name ON ai_prompts(name);

-- Initialize default prompts
INSERT INTO ai_prompts (name, description, prompt_text) VALUES
('full_description', 'Prompt for generating the complete YouTube description content', 
'Generate a complete YouTube audiobook description with three distinct sections.

Novel Title: {novel_name}
Context: {novel_context}

Generate the following sections:

**SECTION 1: ABOUT (8-13 lines)**
- Introduce the story world and premise
- For fanfiction: mention the original universe and what makes this unique
- Use descriptive, immersive language
- Set the tone and atmosphere
- End with what makes this story special
- NO promotional language

**SECTION 2: WHAT TO EXPECT (3-6 sentences)**
- Quick summary of content type and themes
- Highlight unique aspects (system mechanics, character journey, setting blend)
- Use emotive language that creates excitement
- Focus on what makes this story unique
- NO promotional language

**SECTION 3: TAGS (500 characters MAXIMUM)**
- Hashtag format (#tag)
- Mix of broad and specific tags
- Include: genre, tropes, themes, character types, settings
- Highly discoverable YouTube keywords
- Order: specific → broad
- EXACTLY 500 characters or less (CRITICAL!)

Example format:
ABOUT:
[8-13 lines of engaging story introduction...]

WHAT_TO_EXPECT:
[3-6 sentences highlighting key elements...]

TAGS:
#SpecificTag #BroadTag #Genre #Trope #AudioNovel...

Generate all three sections now:')
ON CONFLICT (name) DO NOTHING;


-- Migration complete
SELECT 'Migration 008 completed successfully' AS status;

