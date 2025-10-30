"""S3/R2 storage service"""
import logging
from typing import List, Optional, Dict
import boto3
from botocore.exceptions import ClientError

from src.config import config

logger = logging.getLogger(__name__)


class S3Service:
    """Service for interacting with S3/R2 storage"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.client = boto3.client(
            's3',
            endpoint_url=config.S3_ENDPOINT,
            aws_access_key_id=config.S3_ACCESS_KEY_ID,
            aws_secret_access_key=config.S3_SECRET_ACCESS_KEY,
            region_name=config.S3_REGION
        )
        self.bucket = config.S3_BUCKET_NAME
    
    def fetch_timestamp_files(self, novel_name: str) -> List[Dict[str, str]]:
        """
        Fetch all timestamp files for a novel.
        
        Args:
            novel_name: Name of the novel
            
        Returns:
            List of dicts with 'key' and 'video_name' for each timestamp file
        """
        try:
            prefix = f"{novel_name}/Timestamps/"
            logger.info(f"Fetching timestamp files from: {prefix}")
            
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                logger.warning(f"No timestamp files found for novel: {novel_name}")
                return []
            
            files = []
            for obj in response['Contents']:
                key = obj['Key']
                # Extract video name from key (remove prefix and extension)
                video_name = key.replace(prefix, '').replace('.txt', '')
                
                # Skip empty or directory entries
                if video_name:
                    files.append({
                        'key': key,
                        'video_name': video_name
                    })
            
            logger.info(f"Found {len(files)} timestamp files")
            return files
            
        except ClientError as e:
            logger.error(f"Error fetching timestamp files: {e}")
            raise
    
    def read_timestamp_file(self, novel_name: str, video_name: str) -> str:
        """
        Read timestamp file content from S3.
        
        Args:
            novel_name: Name of the novel
            video_name: Name of the video (without extension)
            
        Returns:
            Timestamp file content as string
        """
        try:
            key = f"{novel_name}/Timestamps/{video_name}.txt"
            logger.info(f"Reading timestamp file: {key}")
            
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=key
            )
            
            content = response['Body'].read().decode('utf-8')
            logger.info(f"Read timestamp file ({len(content)} chars)")
            
            return content
            
        except ClientError as e:
            logger.error(f"Error reading timestamp file: {e}")
            raise
    
    def save_description(self, novel_name: str, video_name: str, description: str) -> bool:
        """
        Save description to S3.
        
        Args:
            novel_name: Name of the novel
            video_name: Name of the video (without extension)
            description: Description content to save
            
        Returns:
            True if successful
        """
        try:
            key = f"{novel_name}/Youtube/{video_name}.txt"
            logger.info(f"Saving description to: {key}")
            
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=description.encode('utf-8'),
                ContentType='text/plain'
            )
            
            logger.info(f"Successfully saved description ({len(description)} chars)")
            return True
            
        except ClientError as e:
            logger.error(f"Error saving description: {e}")
            raise
    
    def description_exists(self, novel_name: str, video_name: str) -> bool:
        """
        Check if a description file already exists.
        
        Args:
            novel_name: Name of the novel
            video_name: Name of the video (without extension)
            
        Returns:
            True if description exists
        """
        try:
            key = f"{novel_name}/Youtube/{video_name}.txt"
            
            self.client.head_object(
                Bucket=self.bucket,
                Key=key
            )
            
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Error checking description existence: {e}")
                raise
    
    def get_description(self, novel_name: str, video_name: str) -> Optional[str]:
        """
        Get description content from S3 if it exists.
        
        Args:
            novel_name: Name of the novel
            video_name: Name of the video (without extension)
            
        Returns:
            Description content or None if not found
        """
        try:
            key = f"{novel_name}/Youtube/{video_name}.txt"
            
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=key
            )
            
            content = response['Body'].read().decode('utf-8')
            return content
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            else:
                logger.error(f"Error getting description: {e}")
                raise
    
    def list_descriptions(self, novel_name: str) -> List[str]:
        """
        List all description files for a novel.
        
        Args:
            novel_name: Name of the novel
            
        Returns:
            List of video names that have descriptions
        """
        try:
            prefix = f"{novel_name}/Youtube/"
            
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            video_names = []
            for obj in response['Contents']:
                key = obj['Key']
                # Extract video name from key
                video_name = key.replace(prefix, '').replace('.txt', '')
                
                if video_name:
                    video_names.append(video_name)
            
            return video_names
            
        except ClientError as e:
            logger.error(f"Error listing descriptions: {e}")
            raise

