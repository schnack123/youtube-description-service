"""Azure OpenAI service for generating descriptions"""
import logging
from typing import Optional
from openai import AzureOpenAI, OpenAI

from src.config import config
from src.models.ai_prompt import AIPrompt
from src.models.database import get_db

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with Azure OpenAI or standard OpenAI"""
    
    def __init__(self):
        """Initialize OpenAI client based on configuration"""
        if config.USE_AZURE_OPENAI:
            logger.info(f"Using Azure OpenAI with deployment: {config.AZURE_OPENAI_DEPLOYMENT}")
            self.client = AzureOpenAI(
                api_key=config.OPENAI_API_KEY,
                api_version="2024-10-21",  # Updated API version for newer features
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT
            )
            self.model = config.AZURE_OPENAI_DEPLOYMENT
            self.is_azure = True
        else:
            logger.info(f"Using standard OpenAI with model: {config.OPENAI_MODEL}")
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            self.model = config.OPENAI_MODEL
            self.is_azure = False
        
        # Determine which token parameter to use based on model
        # GPT-5-nano and newer models require max_completion_tokens
        self.uses_max_completion_tokens = 'gpt-5' in self.model.lower() or 'o1' in self.model.lower()
        
        logger.info(f"Model config: max_completion_tokens={self.uses_max_completion_tokens}")
    
    def _get_prompt_template(self, prompt_name: str, prompt_type: str = 'user') -> str:
        """
        Load prompt template from database.
        
        Args:
            prompt_name: Name of the prompt (e.g., 'what_to_expect', 'seo_tags', 'description_system')
            prompt_type: Type of prompt ('user' or 'system')
            
        Returns:
            Prompt template text
            
        Raises:
            ValueError: If prompt not found
        """
        session = get_db()
        try:
            prompt = session.query(AIPrompt).filter_by(name=prompt_name, prompt_type=prompt_type).first()
            if not prompt:
                raise ValueError(f"Prompt '{prompt_name}' (type: {prompt_type}) not found in database")
            return prompt.prompt_text
        finally:
            session.close()
    
    def generate_all_sections(self, novel_name: str, novel_context: str) -> dict:
        """
        Generate all description sections in one API call.
        
        Args:
            novel_name: Name of the novel
            novel_context: User-provided context about the novel
            
        Returns:
            Dict with 'about', 'what_to_expect', and 'tags' keys
        """
        try:
            # Load system prompt from database (defines output format)
            system_prompt = self._get_prompt_template('description_system', 'system')
            
            # Load user prompt template from database
            user_prompt_template = self._get_prompt_template('full_description', 'user')
            
            # Fill in user prompt variables
            user_prompt = user_prompt_template.format(
                novel_name=novel_name,
                novel_context=novel_context
            )
            
            logger.info(f"Generating all sections for novel: {novel_name}")
            logger.info(f"Using system prompt: description_system")
            
            # Build API call parameters
            api_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            }
            
            # Use correct token parameter based on model (increased to 10000)
            if self.uses_max_completion_tokens:
                api_params["max_completion_tokens"] = 10000
            else:
                api_params["max_tokens"] = 10000
            
            response = self.client.chat.completions.create(**api_params)
            
            # Extract content
            if not response.choices or len(response.choices) == 0:
                raise ValueError("No choices in OpenAI response")
            
            content = response.choices[0].message.content
            if content is None or not content.strip():
                logger.error(f"Empty response from OpenAI. Response object: {response}")
                raise ValueError("OpenAI returned empty content")
            
            full_content = content.strip()
            logger.info(f"Generated full content ({len(full_content)} chars)")
            
            # Parse the four sections
            # Expected format: "ABOUT:\n[content]\n\nWHAT_TO_EXPECT:\n[content]\n\nSUBSCRIBE:\n[content]\n\nTAGS:\n[content]"
            about = ""
            what_to_expect = ""
            subscribe = ""
            tags = ""
            
            try:
                # Log first 300 chars for debugging
                logger.info(f"Content preview: {full_content[:300]}...")
                
                # Split by section headers (case-insensitive)
                content_upper = full_content.upper()
                
                # Find section positions
                about_start = 0
                wte_start = content_upper.find("WHAT_TO_EXPECT:")
                subscribe_start = content_upper.find("SUBSCRIBE:")
                tags_start = content_upper.find("TAGS:")
                
                logger.info(f"Section positions - WTE: {wte_start}, SUBSCRIBE: {subscribe_start}, TAGS: {tags_start}")
                
                if wte_start > 0 and subscribe_start > 0 and tags_start > 0:
                    # Extract all four sections
                    about_section = full_content[about_start:wte_start]
                    about = about_section.replace("ABOUT:", "").replace("About:", "").strip()
                    
                    wte_section = full_content[wte_start:subscribe_start]
                    what_to_expect = wte_section.replace("WHAT_TO_EXPECT:", "").replace("What_to_Expect:", "").strip()
                    
                    subscribe_section = full_content[subscribe_start:tags_start]
                    subscribe = subscribe_section.replace("SUBSCRIBE:", "").replace("Subscribe:", "").strip()
                    
                    tags_section = full_content[tags_start:]
                    tags = tags_section.replace("TAGS:", "").replace("Tags:", "").strip()
                    
                    # Ensure tags are under 500 characters
                    if len(tags) > 500:
                        logger.warning(f"Tags too long ({len(tags)} chars), truncating to 500")
                        tags = tags[:497] + "..."
                    
                    logger.info(f"✅ Parsed all 4 sections successfully")
                else:
                    # Fallback parsing
                    logger.warning(f"Could not find all section markers. Found - WTE: {wte_start > 0}, SUBSCRIBE: {subscribe_start > 0}, TAGS: {tags_start > 0}")
                    about = full_content.replace("ABOUT:", "").strip()
            
            except Exception as parse_error:
                logger.error(f"Error parsing sections: {parse_error}", exc_info=True)
                # Fallback: use full content as about
                about = full_content
            
            logger.info(f"Final sections - About: {len(about)} chars, WTE: {len(what_to_expect)} chars, Subscribe: {len(subscribe)} chars, Tags: {len(tags)} chars")
            
            return {
                'about': about,
                'what_to_expect': what_to_expect,
                'subscribe': subscribe,
                'tags': tags
            }
            
        except Exception as e:
            logger.error(f"Error generating description sections: {e}")
            raise
