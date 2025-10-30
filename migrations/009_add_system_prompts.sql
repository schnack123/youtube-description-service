-- Migration 009: Add system prompts for output format control
-- Created: 2025-10-30
-- Description: Add prompt_type column and system prompts for structured output

-- Add prompt_type column to ai_prompts
ALTER TABLE ai_prompts ADD COLUMN IF NOT EXISTS prompt_type VARCHAR(50) DEFAULT 'user';

-- Update existing prompts to be 'user' type
UPDATE ai_prompts SET prompt_type = 'user' WHERE prompt_type IS NULL;

-- Create index on prompt_type
CREATE INDEX IF NOT EXISTS idx_ai_prompts_type ON ai_prompts(prompt_type);

-- Insert system prompt for description generation
INSERT INTO ai_prompts (name, prompt_type, description, prompt_text) VALUES
('description_system', 'system', 'System prompt that defines the output format for description generation',
'You are an expert at writing engaging YouTube descriptions for audiobook content.

CRITICAL: You must return your response in EXACTLY this format with these three sections:

ABOUT:
[Write 8-13 lines introducing the story world and premise]

WHAT_TO_EXPECT:
[Write 3-6 sentences summarizing content type and themes]

TAGS:
[Write hashtags, maximum 500 characters]

RULES:
1. Use EXACTLY these section headers: "ABOUT:", "WHAT_TO_EXPECT:", "TAGS:"
2. Each section must be on its own line
3. Leave one blank line between sections
4. Do NOT include "SECTION 1" or "SECTION 2" prefixes
5. Do NOT add extra formatting or explanations
6. Return ONLY the three sections with their content

Example output:
ABOUT:
In a world where magic meets farming, our protagonist discovers an ancient system.
The enchanted fields respond to care and cultivation.
[...8-13 lines total...]

WHAT_TO_EXPECT:
Magical farming mechanics blend with epic fantasy adventure.
[...3-6 sentences total...]

TAGS:
#MagicalFarming #Fantasy #Audiobook #System')
ON CONFLICT (name) DO NOTHING;

-- Update the full_description prompt to work with the new system prompt
UPDATE ai_prompts SET
    prompt_text = 'Generate a complete YouTube audiobook description for the following novel.

Novel Title: {novel_name}
Context: {novel_context}

Requirements for ABOUT section (8-13 lines):
- Introduce the story world and premise
- For fanfiction: mention the original universe and what makes this unique
- Use descriptive, immersive language
- Set tone and atmosphere
- NO promotional language

Requirements for WHAT_TO_EXPECT section (3-6 sentences):
- Quick summary of content type and themes
- Highlight unique aspects (system mechanics, character journey, setting blend)
- Use emotive language
- Focus on what makes this unique
- NO promotional language

Requirements for TAGS section (500 characters MAXIMUM):
- Hashtag format (#tag)
- Mix of broad and specific tags
- Include: genre, tropes, themes, character types, settings
- Highly discoverable YouTube keywords
- Order: specific → broad

Generate all three sections following the format specified in the system prompt.',
    updated_at = NOW()
WHERE name = 'full_description';

SELECT 'Migration 009 completed - System prompts added' AS status;

