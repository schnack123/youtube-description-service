"""Admin API routes for managing AI prompts"""
import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

from src.models.database import get_db
from src.models.ai_prompt import AIPrompt
from src.utils.validators import validate_prompt_update

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/prompts', methods=['GET'])
def list_prompts():
    """List all AI prompts"""
    try:
        session = get_db()
        try:
            prompts = session.query(AIPrompt).all()
            
            return jsonify({
                'success': True,
                'total_prompts': len(prompts),
                'prompts': [prompt.to_dict() for prompt in prompts]
            }), 200
            
        finally:
            session.close()
        
    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/prompts/<prompt_name>', methods=['GET'])
def get_prompt(prompt_name):
    """Get a specific prompt by name"""
    try:
        session = get_db()
        try:
            prompt = session.query(AIPrompt).filter_by(name=prompt_name).first()
            
            if not prompt:
                return jsonify({
                    'success': False,
                    'error': f'Prompt "{prompt_name}" not found'
                }), 404
            
            return jsonify({
                'success': True,
                'prompt': prompt.to_dict()
            }), 200
            
        finally:
            session.close()
        
    except Exception as e:
        logger.error(f"Error getting prompt: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/prompts/<prompt_name>', methods=['PATCH'])
def update_prompt(prompt_name):
    """Update a prompt's content"""
    try:
        data = request.json
        
        # Validate request
        is_valid, error = validate_prompt_update(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error}), 400
        
        session = get_db()
        try:
            prompt = session.query(AIPrompt).filter_by(name=prompt_name).first()
            
            if not prompt:
                return jsonify({
                    'success': False,
                    'error': f'Prompt "{prompt_name}" not found'
                }), 404
            
            # Update prompt content
            prompt.prompt_text = data['prompt_text']
            prompt.updated_at = datetime.now(timezone.utc)
            
            # Optionally update description
            if 'description' in data:
                prompt.description = data['description']
            
            session.commit()
            
            logger.info(f"Updated prompt: {prompt_name}")
            
            return jsonify({
                'success': True,
                'message': f'Prompt "{prompt_name}" updated successfully',
                'prompt': prompt.to_dict()
            }), 200
            
        finally:
            session.close()
        
    except Exception as e:
        logger.error(f"Error updating prompt: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

