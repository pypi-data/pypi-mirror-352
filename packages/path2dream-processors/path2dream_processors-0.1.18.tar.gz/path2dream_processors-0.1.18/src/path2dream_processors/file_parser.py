from typing import List
from pathlib import Path
from enum import Enum
import os
from dotenv import load_dotenv
import asyncio
import aiohttp
from openai import AsyncOpenAI
import nest_asyncio
from llama_parse import LlamaParse
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Apply nest_asyncio for LlamaParse
nest_asyncio.apply()


class FileType(Enum):
    """File type enumeration."""
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    URL = "url"
    UNKNOWN = "unknown"


# File type constants
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma'}

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'}

VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}

DOCUMENT_EXTENSIONS = {
    # Base types
    '.pdf',
    # Documents and presentations
    '.abw', '.cgm', '.cwk', '.doc', '.docx', '.docm', '.dot', '.dotm', 
    '.hwp', '.key', '.lwp', '.mw', '.mcw', '.pages', '.pbd', '.ppt', 
    '.pptm', '.pptx', '.pot', '.potm', '.potx', '.rtf', '.sda', '.sdd', 
    '.sdp', '.sdw', '.sgl', '.sti', '.sxi', '.sxw', '.stw', '.sxg', 
    '.txt', '.uof', '.uop', '.uot', '.vor', '.wpd', '.wps', '.xml', 
    '.zabw', '.epub',
    # Spreadsheets  
    '.xlsx', '.xls', '.xlsm', '.xlsb', '.xlw', '.csv', '.dif', '.sylk',
    '.slk', '.prn', '.numbers', '.et', '.ods', '.fods', '.uos1', '.uos2',
    '.dbf', '.wk1', '.wk2', '.wk3', '.wk4', '.wks', '.123', '.wq1', 
    '.wq2', '.wb1', '.wb2', '.wb3', '.qpw', '.xlr', '.eth', '.tsv'
}


class APIBasedFileParser:
    """Real file parser using APIs with async support."""
    
    async def parse_files(self, file_paths: List[str]) -> str:
        """Parse multiple files asynchronously and return combined text representation."""
        if not file_paths:
            return ""
        
        results = []
        results.append("=== PARSED FILE CONTENT ===")
        
        # Create tasks for all files to parse them concurrently
        tasks = []
        for file_path in file_paths:
            task = self._parse_single_file(file_path)
            tasks.append(task)
        
        # Execute all parsing tasks concurrently
        file_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for file_path, result in zip(file_paths, file_results):
            file_type = self._get_file_type(file_path)
            
            # Format file name for display
            if file_type == FileType.URL:
                # Extract domain from URL for cleaner display
                parsed_url = urlparse(file_path)
                display_name = parsed_url.netloc
            else:
                display_name = Path(file_path).name
            
            results.append(f"\nFile: {display_name}")
            
            if isinstance(result, Exception):
                results.append(f"Error: {str(result)}")
            else:
                results.append(result)
            
            results.append("-" * 40)
        
        return "\n".join(results)
    
    async def _parse_single_file(self, file_path: str) -> str:
        """Parse a single file asynchronously."""
        try:
            file_type = self._get_file_type(file_path)
            
            if file_type == FileType.AUDIO:
                return await self._parse_audio(file_path)
            elif file_type == FileType.IMAGE:
                return await self._parse_image(file_path)
            elif file_type == FileType.DOCUMENT:
                return await self._parse_document(file_path)
            elif file_type == FileType.VIDEO:
                return await self._parse_video(file_path)
            elif file_type == FileType.URL:
                return await self._parse_url(file_path)
            else:
                raise NotImplementedError(f"File type '{file_type.value}' is not supported")
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _parse_audio(self, file_path: str) -> str:
        """Parse single audio file using OpenAI Whisper API asynchronously."""
        try:
            # Initialize async OpenAI client
            client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Open and transcribe audio file
            with open(file_path, 'rb') as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            return f"Audio transcription: {transcript}"
            
        except Exception as e:
            return f"Error transcribing audio: {str(e)}"
    
    async def _parse_image(self, file_path: str) -> str:
        """Parse single image file."""
        raise NotImplementedError("Image processing is not supported yet")
    
    async def _parse_document(self, file_path: str) -> str:
        """Parse single document file using LlamaParse API."""
        try:
            # Check if file is PDF (LlamaParse only supports PDF currently)
            file_extension = Path(file_path).suffix.lower()
            if file_extension != '.pdf':
                return f"Document parsing: Only PDF files are supported by LlamaParse. File type: {file_extension}"
            
            # Initialize LlamaParse client with balanced mode settings
            parser = LlamaParse(
                api_key=os.getenv('LLAMA_CLOUD_API_KEY'),
                result_type="markdown",  # Using markdown for better structure
                verbose=False,
                language="en",  # Can be changed to support other languages
                split_by_page=False,  # Get combined result
                premium_mode=False,  # Using balanced mode (default)
                fast_mode=False,  # Balanced mode - not fast, not premium
                max_timeout=5000,  # 5 second timeout
                show_progress=False
            )
            
            # Parse the document - LlamaParse runs in async context due to nest_asyncio
            loop = asyncio.get_event_loop()
            documents = await loop.run_in_executor(None, parser.load_data, file_path)
            
            # Extract text content
            if documents:
                content = "\n".join([doc.text for doc in documents])
                return f"Document content: {content}"
            else:
                return "Document parsing: No content extracted from the document"
                
        except Exception as e:
            return f"Error parsing document: {str(e)}"
    
    async def _parse_video(self, file_path: str) -> str:
        """Parse single video file."""
        raise NotImplementedError("Video processing is not supported yet")
    
    async def _parse_url(self, file_path: str) -> str:
        """Parse URL content using Jina Reader API asynchronously."""
        try:
            # Ensure the input is a valid URL
            if not file_path.startswith(('http://', 'https://')):
                return "Error parsing URL: Invalid URL format. URL must start with http:// or https://"
            
            # Use Jina Reader API to extract content
            jina_url = f"https://r.jina.ai/{file_path}"
            
            # Prepare headers
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'path2dream_processors/1.0'
            }
            
            # Add API key if available for better rate limits
            jina_api_key = os.getenv('JINA_API_KEY')
            if jina_api_key:
                headers['Authorization'] = f'Bearer {jina_api_key}'
            
            # Make async request to Jina Reader
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(jina_url, headers=headers) as response:
                    response.raise_for_status()
                    
                    # Parse response
                    content_type = response.headers.get('content-type', '')
                    if content_type.startswith('application/json'):
                        data = await response.json()
                        content = data.get('data', {}).get('content', '')
                        title = data.get('data', {}).get('title', '')
                        
                        if content:
                            result = f"Web content from: {title}\n\n{content}" if title else f"Web content: {content}"
                            return result
                        else:
                            return "URL parsing: No content extracted from the webpage"
                    else:
                        # If response is plain text (markdown)
                        content = (await response.text()).strip()
                        if content:
                            return f"Web content: {content}"
                        else:
                            return "URL parsing: No content extracted from the webpage"
                            
        except asyncio.TimeoutError:
            return "Error parsing URL: Request timeout (30 seconds exceeded)"
        except aiohttp.ClientError as e:
            return f"Error parsing URL: Network error - {str(e)}"
        except Exception as e:
            return f"Error parsing URL: {str(e)}"
    
    def _get_file_type(self, file_path: str) -> FileType:
        """Determine file type by extension or URL pattern."""
        if file_path.startswith(('http://', 'https://')):
            return FileType.URL
        
        suffix = Path(file_path).suffix.lower()
        
        if suffix in AUDIO_EXTENSIONS:
            return FileType.AUDIO
        elif suffix in IMAGE_EXTENSIONS:
            return FileType.IMAGE
        elif suffix in DOCUMENT_EXTENSIONS:
            return FileType.DOCUMENT
        elif suffix in VIDEO_EXTENSIONS:
            return FileType.VIDEO
        else:
            return FileType.UNKNOWN 