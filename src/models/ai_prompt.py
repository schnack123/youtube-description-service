"""AI Prompt model"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func

from src.models.database import Base


class AIPrompt(Base):
    """Store AI prompts in database for easy editing"""
    
    __tablename__ = 'ai_prompts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    prompt_type = Column(String(50), nullable=False, default='user')  # 'system' or 'user'
    description = Column(Text)
    prompt_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'prompt_type': self.prompt_type,
            'description': self.description,
            'prompt_text': self.prompt_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

