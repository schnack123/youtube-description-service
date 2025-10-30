"""Description generation API routes"""
import logging
import uuid
from datetime import datetime, timezone
from threading import Thread
from flask import Blueprint, request, jsonify

from src.models.database import get_db
from src.models.description_state import WorkflowDescriptionState
from src.services.openai_service import OpenAIService
from src.services.s3_service import S3Service
from src.services.template_service import TemplateService
from src.utils.validators import validate_generate_request

logger = logging.getLogger(__name__)

descriptions_bp = Blueprint('descriptions', __name__)


def generate_descriptions_task(
    job_id: str,
    novel_name: str,
    novel_context: str,
    playlist_url: str,
    subscribe_text: str,
    force: bool = False
):
    """
    Background task to generate descriptions for all videos.
    Uses short-lived database transactions to avoid blocking other services.
    
    Args:
        job_id: Unique job identifier
        novel_name: Name of the novel
        novel_context: User-provided context
        playlist_url: Full playlist URL
        subscribe_text: Subscribe call-to-action
        force: Force regeneration even if descriptions exist
    """
    def update_job_status(status, **kwargs):
        """Helper to update job status with short-lived transaction"""
        session = get_db()
        try:
            state = session.query(WorkflowDescriptionState).filter_by(job_id=job_id).first()
            if state:
                state.status = status
                for key, value in kwargs.items():
                    setattr(state, key, value)
                session.commit()
        finally:
            session.close()
    
    try:
        # Step 0: Update status to processing (short transaction)
        update_job_status('processing')
        
        # Initialize services (no database connection)
        openai_service = OpenAIService()
        s3_service = S3Service()
        
        # Step 1: Generate ALL content in one API call (no database connection during API call)
        logger.info(f"Generating AI content for novel: {novel_name}")
        
        # Single unified API call for all four sections
        sections = openai_service.generate_all_sections(novel_name, novel_context)
        about = sections['about']
        what_to_expect = sections['what_to_expect']
        subscribe = sections['subscribe']
        seo_tags = sections['tags']
        
        # Save AI-generated content to database (short transaction)
        update_job_status(
            'processing',
            generated_about=about,
            generated_what_to_expect=what_to_expect,
            generated_subscribe=subscribe,
            generated_tags=seo_tags
        )
        
        # Step 2: Fetch all timestamp files (no database connection)
        timestamp_files = s3_service.fetch_timestamp_files(novel_name)
        
        if not timestamp_files:
            # Short transaction to mark as failed
            update_job_status(
                'failed',
                error_message=f"No timestamp files found for novel: {novel_name}",
                completed_at=datetime.now(timezone.utc)
            )
            return
        
        total_videos = len(timestamp_files)
        descriptions_generated = 0
        
        # Update progress (short transaction)
        update_job_status(
            'processing',
            progress_data={
                'total_videos': total_videos,
                'descriptions_generated': 0,
                'percent_complete': 0
            }
        )
        
        # Step 3: Generate description for each video (no database connection during I/O)
        for file_info in timestamp_files:
            video_name = file_info['video_name']
            
            try:
                # Check if description already exists (unless force=True)
                if not force and s3_service.description_exists(novel_name, video_name):
                    logger.info(f"Description already exists for {video_name}, skipping")
                    descriptions_generated += 1
                    
                    # Update progress (short transaction)
                    update_job_status(
                        'processing',
                        progress_data={
                            'total_videos': total_videos,
                            'descriptions_generated': descriptions_generated,
                            'percent_complete': (descriptions_generated / total_videos) * 100
                        }
                    )
                    continue
                
                # Read timestamp file (no database connection)
                timestamps = s3_service.read_timestamp_file(novel_name, video_name)
                
                # Build description (no database connection)
                description = TemplateService.build_description(
                    playlist_url=playlist_url,
                    novel_name=novel_name,
                    about=about,
                    what_to_expect=what_to_expect,
                    subscribe=subscribe,
                    timestamps=timestamps,
                    seo_tags=seo_tags
                )
                
                # Validate description
                is_valid, error = TemplateService.validate_description(description)
                if not is_valid:
                    logger.error(f"Invalid description for {video_name}: {error}")
                    continue
                
                # Save to S3 (no database connection)
                s3_service.save_description(novel_name, video_name, description)
                
                descriptions_generated += 1
                
                # Update progress (short transaction)
                update_job_status(
                    'processing',
                    progress_data={
                        'total_videos': total_videos,
                        'descriptions_generated': descriptions_generated,
                        'percent_complete': (descriptions_generated / total_videos) * 100
                    }
                )
                
                logger.info(f"Generated description {descriptions_generated}/{total_videos}")
                
            except Exception as e:
                logger.error(f"Error processing video {video_name}: {e}")
                continue
        
        # Mark as completed (short transaction)
        update_job_status(
            'completed',
            completed_at=datetime.now(timezone.utc),
            progress_data={
                'total_videos': total_videos,
                'descriptions_generated': descriptions_generated,
                'percent_complete': 100
            }
        )
        
        logger.info(f"Job {job_id} completed: {descriptions_generated}/{total_videos} descriptions generated")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        # Short transaction to mark as failed
        update_job_status(
            'failed',
            error_message=str(e),
            completed_at=datetime.now(timezone.utc)
        )


@descriptions_bp.route('/generate-descriptions', methods=['POST'])
def generate_descriptions():
    """Generate descriptions for a novel"""
    try:
        data = request.json
        
        # Validate request
        is_valid, error = validate_generate_request(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error}), 400
        
        novel_name = data['novel_name']
        novel_context = data['novel_context']
        playlist_url = data['playlist_url']
        subscribe_text = data.get('subscribe_text', '')  # Optional now (AI generates it)
        force = data.get('force', False)
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create job state in database
        session = get_db()
        try:
            # Check if there's already a processing job for this novel
            # Note: This assumes workflow_id exists. For now, we'll skip this check
            # since we don't have workflow_id in the request
            
            state = WorkflowDescriptionState(
                job_id=job_id,
                novel_name=novel_name,
                status='pending',
                novel_context=novel_context,
                playlist_url=playlist_url,
                subscribe_text=subscribe_text,
                started_at=datetime.now(timezone.utc),
                progress_data={'total_videos': 0, 'descriptions_generated': 0, 'percent_complete': 0}
            )
            
            session.add(state)
            session.commit()
            
            # Start background task
            thread = Thread(
                target=generate_descriptions_task,
                args=(job_id, novel_name, novel_context, playlist_url, subscribe_text, force)
            )
            thread.start()
            
            return jsonify({
                'success': True,
                'job_id': job_id,
                'status': 'processing',
                'message': f'Description generation started for {novel_name}',
                'poll_url': f'/jobs/{job_id}'
            }), 200
            
        finally:
            session.close()
        
    except Exception as e:
        logger.error(f"Error starting description generation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@descriptions_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get status of a description generation job"""
    try:
        session = get_db()
        try:
            state = session.query(WorkflowDescriptionState).filter_by(job_id=job_id).first()
            
            if not state:
                return jsonify({'success': False, 'error': 'Job not found'}), 404
            
            response = {
                'job_id': state.job_id,
                'status': state.status,
                'progress': state.progress_data or {},
                'started_at': state.started_at.isoformat() if state.started_at else None,
                'completed_at': state.completed_at.isoformat() if state.completed_at else None,
                'updated_at': state.updated_at.isoformat() if state.updated_at else None
            }
            
            if state.status == 'failed':
                response['error_message'] = state.error_message
            
            if state.status == 'completed':
                response['message'] = f"All {state.progress_data.get('descriptions_generated', 0)} descriptions generated successfully"
            
            return jsonify(response), 200
            
        finally:
            session.close()
        
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@descriptions_bp.route('/descriptions/<novel_name>', methods=['GET'])
def list_descriptions(novel_name):
    """List all description files for a novel"""
    try:
        s3_service = S3Service()
        video_names = s3_service.list_descriptions(novel_name)
        
        return jsonify({
            'success': True,
            'novel_name': novel_name,
            'total_descriptions': len(video_names),
            'videos': video_names
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing descriptions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@descriptions_bp.route('/descriptions/<novel_name>/<video_name>', methods=['GET'])
def get_description(novel_name, video_name):
    """Get a specific description for preview"""
    try:
        s3_service = S3Service()
        description = s3_service.get_description(novel_name, video_name)
        
        if description is None:
            return jsonify({
                'success': False,
                'error': 'Description not found'
            }), 404
        
        return jsonify({
            'success': True,
            'novel_name': novel_name,
            'video_name': video_name,
            'description': description
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting description: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

