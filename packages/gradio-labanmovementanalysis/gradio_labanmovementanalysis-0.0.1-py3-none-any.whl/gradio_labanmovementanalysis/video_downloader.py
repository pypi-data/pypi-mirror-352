"""
Video downloader for YouTube, Vimeo and other platforms
"""

import os
import re
import tempfile
import logging
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse, parse_qs
import subprocess

logger = logging.getLogger(__name__)


class VideoDownloader:
    """Download videos from various platforms"""
    
    # Gradio component compatibility
    events = {}
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize video downloader.
        
        Args:
            temp_dir: Directory for temporary files
        """
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="laban_video_")
        self.supported_platforms = {
            'youtube': self._download_youtube,
            'vimeo': self._download_vimeo,
            'direct': self._download_direct
        }
        
    def download(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """
        Download video from URL.
        
        Args:
            url: Video URL (YouTube, Vimeo, or direct video link)
            
        Returns:
            Tuple of (local_path, metadata)
        """
        platform = self._detect_platform(url)
        
        if platform not in self.supported_platforms:
            raise ValueError(f"Unsupported platform: {platform}")
            
        logger.info(f"Downloading video from {platform}: {url}")
        
        try:
            return self.supported_platforms[platform](url)
        except Exception as e:
            logger.error(f"Failed to download video: {str(e)}")
            raise
    
    def _detect_platform(self, url: str) -> str:
        """Detect video platform from URL"""
        domain = urlparse(url).netloc.lower()
        
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'vimeo.com' in domain:
            return 'vimeo'
        elif url.endswith(('.mp4', '.avi', '.mov', '.webm')):
            return 'direct'
        else:
            # Try to determine if it's a direct video link
            return 'direct'
    
    def _download_youtube(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """Download video from YouTube using yt-dlp"""
        try:
            import yt_dlp
        except ImportError:
            raise ImportError("yt-dlp is required for YouTube downloads. Install with: pip install yt-dlp")
        
        # Extract video ID
        video_id = self._extract_youtube_id(url)
        output_path = os.path.join(self.temp_dir, f"youtube_{video_id}.mp4")
        
        # yt-dlp options
        ydl_opts = {
            'format': 'best[height<=720][ext=mp4]/best[height<=720]/best',  # Limit to 720p for performance
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        metadata = {}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract info
                info = ydl.extract_info(url, download=True)
                
                # Store metadata
                metadata = {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', ''),
                    'platform': 'youtube',
                    'video_id': video_id
                }
                
                logger.info(f"Downloaded YouTube video: {metadata['title']}")
                
            except Exception as e:
                raise Exception(f"Failed to download YouTube video: {str(e)}")
        
        return output_path, metadata
    
    def _download_vimeo(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """Download video from Vimeo using yt-dlp"""
        try:
            import yt_dlp
        except ImportError:
            raise ImportError("yt-dlp is required for Vimeo downloads. Install with: pip install yt-dlp")
        
        # Extract video ID
        video_id = self._extract_vimeo_id(url)
        output_path = os.path.join(self.temp_dir, f"vimeo_{video_id}.mp4")
        
        # yt-dlp options
        ydl_opts = {
            'format': 'best[height<=720][ext=mp4]/best[height<=720]/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
        }
        
        metadata = {}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract info
                info = ydl.extract_info(url, download=True)
                
                # Store metadata
                metadata = {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'description': info.get('description', ''),
                    'platform': 'vimeo',
                    'video_id': video_id
                }
                
                logger.info(f"Downloaded Vimeo video: {metadata['title']}")
                
            except Exception as e:
                raise Exception(f"Failed to download Vimeo video: {str(e)}")
        
        return output_path, metadata
    
    def _download_direct(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """Download video from direct URL"""
        import requests
        
        # Generate filename from URL
        filename = os.path.basename(urlparse(url).path) or "video.mp4"
        output_path = os.path.join(self.temp_dir, filename)
        
        try:
            # Download with streaming
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get content length
            total_size = int(response.headers.get('content-length', 0))
            
            # Write to file
            with open(output_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress logging
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if int(progress) % 10 == 0:
                                logger.debug(f"Download progress: {progress:.1f}%")
            
            metadata = {
                'title': filename,
                'platform': 'direct',
                'url': url,
                'size': total_size
            }
            
            logger.info(f"Downloaded direct video: {filename}")
            
        except Exception as e:
            raise Exception(f"Failed to download direct video: {str(e)}")
        
        return output_path, metadata
    
    def _extract_youtube_id(self, url: str) -> str:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
            r'youtu\.be\/([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
                
        raise ValueError(f"Could not extract YouTube video ID from: {url}")
    
    def _extract_vimeo_id(self, url: str) -> str:
        """Extract Vimeo video ID from URL"""
        patterns = [
            r'vimeo\.com\/(\d+)',
            r'player\.vimeo\.com\/video\/(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
                
        raise ValueError(f"Could not extract Vimeo video ID from: {url}")
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary directory: {str(e)}")


class SmartVideoInput:
    """Smart video input handler that supports URLs and local files"""
    
    events = {}  # Gradio component compatibility
    
    def __init__(self):
        self.downloader = VideoDownloader()
        self._temp_files = []
        
    def process_input(self, input_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process video input - can be local file or URL.
        
        Args:
            input_path: Local file path or video URL
            
        Returns:
            Tuple of (local_path, metadata)
        """
        # Check if it's a URL
        if input_path.startswith(('http://', 'https://', 'www.')):
            # Download video
            local_path, metadata = self.downloader.download(input_path)
            self._temp_files.append(local_path)
            return local_path, metadata
        else:
            # Local file
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Video file not found: {input_path}")
                
            metadata = {
                'title': os.path.basename(input_path),
                'platform': 'local',
                'path': input_path
            }
            
            return input_path, metadata
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"Removed temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {str(e)}")
        
        self._temp_files.clear()
        self.downloader.cleanup() 