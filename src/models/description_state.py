"""Workflow Description State model"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime, timezone

from src.models.database import Base


class WorkflowDescriptionState(Base):
    """Tracks description generation jobs per workflow"""
    
    __tablename__ = 'workflow_description_state'
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, nullable=True)  # Optional: for future workflow integration
    novel_name = Column(String(255))  # Novel name for Phase 1
    job_id = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), nullable=False)  # pending, processing, completed, failed
    progress_data = Column(JSON)  # {descriptions_generated: X, total_videos: Y}
    
    # User inputs
    novel_context = Column(Text)
    playlist_url = Column(Text)
    subscribe_text = Column(Text)
    
    # AI-generated content (novel-level)
    generated_about = Column(Text)
    generated_what_to_expect = Column(Text)
    generated_subscribe = Column(Text)
    generated_tags = Column(Text)
    
    # Timestamps
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())
    
    # Error handling
    error_message = Column(Text)
    
    # Optimistic locking
    version = Column(Integer, default=1)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'job_id': self.job_id,
            'status': self.status,
            'progress': self.progress_data or {},
            'novel_context': self.novel_context,
            'playlist_url': self.playlist_url,
            'subscribe_text': self.subscribe_text,
            'generated_what_to_expect': self.generated_what_to_expect,
            'generated_tags': self.generated_tags,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'error_message': self.error_message,
            'version': self.version
        }

