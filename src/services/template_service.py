"""Template service for building YouTube descriptions"""
import logging

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for building YouTube descriptions from components"""
    
    @staticmethod
    def build_description(
        playlist_url: str,
        novel_name: str,
        about: str,
        what_to_expect: str,
        subscribe: str,
        timestamps: str,
        seo_tags: str
    ) -> str:
        """
        Build complete YouTube description from template.
        
        Args:
            playlist_url: Full playlist URL
            novel_name: Name of the novel
            about: AI-generated "About" section (8-13 lines)
            what_to_expect: AI-generated "What to Expect" section (3-6 sentences)
            subscribe: AI-generated subscribe call-to-action (2-3 sentences)
            timestamps: Timestamp content from S3
            seo_tags: AI-generated SEO hashtags (500 chars)
            
        Returns:
            Complete formatted description
        """
        # Build the complete description
        description = f"""Full Playlist: {playlist_url}

📚 About "{novel_name}"

{about}

⭐ What to Expect

{what_to_expect}

🔔 Subscribe for More

{subscribe}

⏰ Timestamps:

{timestamps}

Tags:
{seo_tags}"""
        
        logger.info(f"Built description ({len(description)} chars)")
        
        return description
    
    @staticmethod
    def validate_description(description: str) -> tuple[bool, str]:
        """
        Validate a built description.
        
        Args:
            description: Complete description text
            
        Returns:
            (is_valid, error_message)
        """
        if not description:
            return False, "Description is empty"
        
        if len(description) > 5000:
            return False, "Description exceeds YouTube's 5000 character limit"
        
        # Check for required sections
        required_sections = [
            'Full Playlist:',
            'About',
            'What to Expect',
            'Subscribe for More',
            'Timestamps:',
            'Tags:'
        ]
        
        for section in required_sections:
            if section not in description:
                return False, f"Missing required section: {section}"
        
        return True, ""

