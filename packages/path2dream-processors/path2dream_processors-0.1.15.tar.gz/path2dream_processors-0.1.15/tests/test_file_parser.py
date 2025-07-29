import pytest
import os
import asyncio
from unittest.mock import patch, mock_open, MagicMock, AsyncMock
import aiohttp
from aioresponses import aioresponses

from path2dream_processors.file_parser import APIBasedFileParser, FileType


class TestAPIBasedFileParser:
    """Test suite for APIBasedFileParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = APIBasedFileParser()
    
    @pytest.mark.asyncio
    async def test_parse_files_empty_list(self):
        """Test parsing empty file list."""
        result = await self.parser.parse_files([])
        assert result == ""
    
    def test_get_file_type_audio(self):
        """Test file type detection for audio files."""
        test_cases = [
            "test.mp3",
            "test.wav", 
            "test.m4a",
            "test.flac"
        ]
        for file_path in test_cases:
            assert self.parser._get_file_type(file_path) == FileType.AUDIO
    
    def test_get_file_type_image(self):
        """Test file type detection for image files."""
        test_cases = [
            "test.jpg",
            "test.png",
            "test.gif"
        ]
        for file_path in test_cases:
            assert self.parser._get_file_type(file_path) == FileType.IMAGE
    
    def test_get_file_type_document(self):
        """Test file type detection for document files."""
        test_cases = [
            "test.pdf",
            "test.docx",
            "test.txt"
        ]
        for file_path in test_cases:
            assert self.parser._get_file_type(file_path) == FileType.DOCUMENT
    
    def test_get_file_type_url(self):
        """Test file type detection for URLs."""
        test_cases = [
            "http://example.com",
            "https://example.com"
        ]
        for file_path in test_cases:
            assert self.parser._get_file_type(file_path) == FileType.URL
    
    def test_get_file_type_unknown(self):
        """Test file type detection for unknown files."""
        assert self.parser._get_file_type("test.unknown") == FileType.UNKNOWN
    
    @pytest.mark.asyncio
    @patch('path2dream_processors.file_parser.AsyncOpenAI')
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake audio data")
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    async def test_parse_audio_success(self, mock_file, mock_openai_class):
        """Test successful audio parsing with OpenAI Whisper API."""
        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_transcript = MagicMock()
        mock_transcript.__str__ = lambda x: "This is a test transcription"
        mock_client.audio.transcriptions.create.return_value = mock_transcript
        
        # Test
        result = await self.parser._parse_audio("test.mp3")
        
        # Assertions
        assert "Audio transcription: This is a test transcription" in result
        mock_openai_class.assert_called_once_with(api_key='test_key')
        mock_client.audio.transcriptions.create.assert_called_once()
        call_args = mock_client.audio.transcriptions.create.call_args
        assert call_args[1]['model'] == 'whisper-1'
        assert call_args[1]['response_format'] == 'text'
    
    @pytest.mark.asyncio
    @patch('path2dream_processors.file_parser.AsyncOpenAI')
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    async def test_parse_audio_file_not_found(self, mock_file, mock_openai_class):
        """Test audio parsing when file is not found."""
        result = await self.parser._parse_audio("nonexistent.mp3")
        assert "Error transcribing audio" in result
        assert "File not found" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {}, clear=True)
    async def test_parse_audio_no_api_key(self):
        """Test audio parsing when API key is not set."""
        result = await self.parser._parse_audio("test.mp3")
        assert "Error transcribing audio" in result
    
    @pytest.mark.asyncio
    @patch('path2dream_processors.file_parser.LlamaParse')
    @patch('asyncio.get_event_loop')
    @patch.dict(os.environ, {'LLAMA_CLOUD_API_KEY': 'test_key'})
    async def test_parse_document_pdf_success(self, mock_get_loop, mock_llama_parse_class):
        """Test successful PDF document parsing with LlamaParse API."""
        # Setup mock
        mock_parser = MagicMock()
        mock_llama_parse_class.return_value = mock_parser
        
        # Mock document object
        mock_doc = MagicMock()
        mock_doc.text = "This is the extracted PDF content with structured data."
        
        # Mock loop and executor
        mock_loop = AsyncMock()
        mock_get_loop.return_value = mock_loop
        mock_loop.run_in_executor.return_value = [mock_doc]
        
        # Test
        result = await self.parser._parse_document("test.pdf")
        
        # Assertions
        assert "Document content: This is the extracted PDF content with structured data." in result
        mock_llama_parse_class.assert_called_once()
        # Check that LlamaParse was initialized with correct parameters
        call_args = mock_llama_parse_class.call_args
        assert call_args[1]['api_key'] == 'test_key'
        assert call_args[1]['result_type'] == 'markdown'
        assert call_args[1]['fast_mode'] is False  # Balanced mode
        mock_loop.run_in_executor.assert_called_once_with(None, mock_parser.load_data, "test.pdf")
    
    @pytest.mark.asyncio
    async def test_parse_document_non_pdf(self):
        """Test document parsing with non-PDF file."""
        result = await self.parser._parse_document("test.docx")
        assert "Only PDF files are supported by LlamaParse" in result
        assert "File type: .docx" in result
    
    @pytest.mark.asyncio
    @patch('path2dream_processors.file_parser.LlamaParse')
    @patch('asyncio.get_event_loop')
    @patch.dict(os.environ, {'LLAMA_CLOUD_API_KEY': 'test_key'})
    async def test_parse_document_no_content(self, mock_get_loop, mock_llama_parse_class):
        """Test document parsing when no content is extracted."""
        # Setup mock
        mock_parser = MagicMock()
        mock_llama_parse_class.return_value = mock_parser
        
        # Mock loop and executor with empty documents
        mock_loop = AsyncMock()
        mock_get_loop.return_value = mock_loop
        mock_loop.run_in_executor.return_value = []  # No documents returned
        
        # Test
        result = await self.parser._parse_document("test.pdf")
        
        # Assertions
        assert "No content extracted from the document" in result
    
    @pytest.mark.asyncio
    @patch('path2dream_processors.file_parser.LlamaParse')
    @patch('asyncio.get_event_loop')
    @patch.dict(os.environ, {'LLAMA_CLOUD_API_KEY': 'test_key'})
    async def test_parse_document_api_error(self, mock_get_loop, mock_llama_parse_class):
        """Test document parsing when API returns an error."""
        # Setup mock to raise exception
        mock_parser = MagicMock()
        mock_llama_parse_class.return_value = mock_parser
        
        # Mock loop and executor with exception
        mock_loop = AsyncMock()
        mock_get_loop.return_value = mock_loop
        mock_loop.run_in_executor.side_effect = Exception("API Error: Invalid file format")
        
        # Test
        result = await self.parser._parse_document("test.pdf")
        
        # Assertions
        assert "Error parsing document" in result
        assert "API Error: Invalid file format" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {}, clear=True)
    async def test_parse_document_no_api_key(self):
        """Test document parsing when API key is not set."""
        result = await self.parser._parse_document("test.pdf")
        assert "Error parsing document" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {'JINA_API_KEY': 'test_key'})
    async def test_parse_url_success(self):
        """Test successful URL parsing with Jina Reader API."""
        with aioresponses() as m:
            # Mock the response
            mock_response_data = {
                'data': {
                    'title': 'Test Page',
                    'content': 'This is the main content of the webpage with clean text.'
                }
            }
            m.get("https://r.jina.ai/https://example.com/test", 
                  payload=mock_response_data,
                  headers={'content-type': 'application/json'})
            
            # Test
            result = await self.parser._parse_url("https://example.com/test")
            
            # Assertions
            assert "Web content from: Test Page" in result
            assert "This is the main content of the webpage with clean text." in result
    
    @pytest.mark.asyncio
    async def test_parse_url_invalid_url(self):
        """Test URL parsing with invalid URL format."""
        result = await self.parser._parse_url("invalid-url")
        assert "Error parsing URL: Invalid URL format" in result
    
    @pytest.mark.asyncio
    async def test_parse_url_timeout(self):
        """Test URL parsing with timeout."""
        with aioresponses() as m:
            # Mock timeout
            m.get("https://r.jina.ai/https://example.com/test", 
                  exception=asyncio.TimeoutError())
            
            # Test
            result = await self.parser._parse_url("https://example.com/test")
            
            # Assertions
            assert "Error parsing URL: Request timeout" in result
    
    @pytest.mark.asyncio
    async def test_parse_url_network_error(self):
        """Test URL parsing with network error."""
        with aioresponses() as m:
            # Mock network error
            m.get("https://r.jina.ai/https://example.com/test", 
                  exception=aiohttp.ClientError("Network error"))
            
            # Test
            result = await self.parser._parse_url("https://example.com/test")
            
            # Assertions
            assert "Error parsing URL: Network error" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {'JINA_API_KEY': 'test_key'})
    async def test_parse_url_no_content(self):
        """Test URL parsing when no content is extracted."""
        with aioresponses() as m:
            # Mock response with no content
            mock_response_data = {
                'data': {
                    'title': 'Test Page',
                    'content': ''
                }
            }
            m.get("https://r.jina.ai/https://example.com/test", 
                  payload=mock_response_data,
                  headers={'content-type': 'application/json'})
            
            # Test
            result = await self.parser._parse_url("https://example.com/test")
            
            # Assertions
            assert "No content extracted from the webpage" in result
    
    @pytest.mark.asyncio
    @patch('path2dream_processors.file_parser.APIBasedFileParser._parse_audio')
    @patch('path2dream_processors.file_parser.APIBasedFileParser._parse_document')
    @patch('path2dream_processors.file_parser.APIBasedFileParser._parse_url')
    async def test_parse_files_multiple_types(self, mock_parse_url, mock_parse_document, mock_parse_audio):
        """Test parsing multiple files of different types."""
        # Setup mocks
        mock_parse_audio.return_value = "Audio content"
        mock_parse_document.return_value = "Document content"
        mock_parse_url.return_value = "URL content"
        
        # Test
        files = ["audio.mp3", "document.pdf", "https://example.com"]
        result = await self.parser.parse_files(files)
        
        # Assertions
        assert "=== PARSED FILE CONTENT ===" in result
        assert "audio.mp3" in result
        assert "document.pdf" in result
        assert "example.com" in result  # Domain extracted from URL
        assert "Audio content" in result
        assert "Document content" in result
        assert "URL content" in result
        
        # Verify all methods were called
        mock_parse_audio.assert_called_once_with("audio.mp3")
        mock_parse_document.assert_called_once_with("document.pdf")
        mock_parse_url.assert_called_once_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_parse_video_not_implemented(self):
        """Test that video parsing raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await self.parser._parse_video("test.mp4")
    
    @pytest.mark.asyncio
    async def test_parse_image_not_implemented(self):
        """Test that image parsing raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await self.parser._parse_image("test.jpg")


class TestAudioParsingIntegration:
    """Integration tests for audio parsing with real OpenAI API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = APIBasedFileParser()
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY not set - skipping integration test"
    )
    async def test_real_audio_file_parsing(self):
        """Test parsing a real audio file with OpenAI Whisper API."""
        # Test file path (user should have this file)
        test_file = "/Users/fun/Downloads/test.mp3"
        
        # Skip if test file doesn't exist
        if not os.path.exists(test_file):
            pytest.skip(f"Test file {test_file} not found")
        
        # Parse the audio file
        result = await self.parser._parse_audio(test_file)
        
        # Verify result
        assert "Audio transcription:" in result
        assert "Error" not in result
        # The actual transcription content will depend on the audio file
        print(f"Transcription result: {result}")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY not set - skipping integration test"
    )
    async def test_parse_files_with_real_audio(self):
        """Test parsing files including real audio with the main parse_files method."""
        # Test file path (user should have this file)
        test_file = "/Users/fun/Downloads/test.mp3"
        
        # Skip if test file doesn't exist
        if not os.path.exists(test_file):
            pytest.skip(f"Test file {test_file} not found")
        
        # Parse multiple files including the audio
        files = [test_file]
        result = await self.parser.parse_files(files)
        
        # Verify result structure
        assert "=== PARSED FILE CONTENT ===" in result
        assert "test.mp3" in result
        assert "Audio transcription:" in result
        print(f"Full parsing result: {result}")


class TestDocumentParsingIntegration:
    """Integration tests for document parsing with real LlamaParse API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = APIBasedFileParser()
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv('LLAMA_CLOUD_API_KEY'),
        reason="LLAMA_CLOUD_API_KEY not set - skipping integration test"
    )
    async def test_real_pdf_file_parsing(self):
        """Test parsing a real PDF file with LlamaParse API."""
        # Test file path (user should have this file)
        test_file = "/Users/fun/Downloads/test.pdf"
        
        # Skip if test file doesn't exist
        if not os.path.exists(test_file):
            pytest.skip(f"Test file {test_file} not found")
        
        # Parse the PDF file
        result = await self.parser._parse_document(test_file)
        
        # Verify result
        assert "Document content:" in result
        assert "Error" not in result
        # The actual content will depend on the PDF file
        print(f"Document parsing result: {result}")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv('LLAMA_CLOUD_API_KEY'),
        reason="LLAMA_CLOUD_API_KEY not set - skipping integration test"
    )
    async def test_parse_files_with_real_pdf(self):
        """Test parsing files including real PDF with the main parse_files method."""
        # Test file path (user should have this file)
        test_file = "/Users/fun/Downloads/test.pdf"
        
        # Skip if test file doesn't exist
        if not os.path.exists(test_file):
            pytest.skip(f"Test file {test_file} not found")
        
        # Parse multiple files including the PDF
        files = [test_file]
        result = await self.parser.parse_files(files)
        
        # Verify result structure
        assert "=== PARSED FILE CONTENT ===" in result
        assert "test.pdf" in result
        assert "Document content:" in result
        print(f"Full parsing result: {result}")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv('LLAMA_CLOUD_API_KEY'),
        reason="LLAMA_CLOUD_API_KEY not set - skipping integration test"
    )
    async def test_parse_mixed_files_with_real_data(self):
        """Test parsing mixed file types with real API calls."""
        # Test files (user should have these files)
        audio_file = "/Users/fun/Downloads/test.mp3"
        pdf_file = "/Users/fun/Downloads/test.pdf"
        test_url = "https://www.domestika.com/en/courses/2291-watercolor-landscapes-in-a-naturalist-style"
        
        # Build file list with available files
        files = []
        if os.path.exists(audio_file) and os.getenv('OPENAI_API_KEY'):
            files.append(audio_file)
        if os.path.exists(pdf_file):
            files.append(pdf_file)
        files.append(test_url)  # URL parsing doesn't require file existence
        
        if not files:
            pytest.skip("No test files available")
        
        # Parse all files
        result = await self.parser.parse_files(files)
        
        # Verify result structure
        assert "=== PARSED FILE CONTENT ===" in result
        print(f"Mixed files parsing result: {result}")


class TestUrlParsingIntegration:
    """Integration tests for URL parsing with real Jina Reader API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = APIBasedFileParser()
    
    @pytest.mark.asyncio
    async def test_real_url_parsing(self):
        """Test parsing a real URL with Jina Reader API."""
        # Test URL
        test_url = "https://www.domestika.com/en/courses/2291-watercolor-landscapes-in-a-naturalist-style"
        
        # Parse the URL
        result = await self.parser._parse_url(test_url)
        
        # Verify result (should work even without API key)
        assert "Web content" in result
        assert "Error" not in result or "timeout" in result.lower()  # Accept timeout as valid
        print(f"URL parsing result: {result}")
    
    @pytest.mark.asyncio
    async def test_parse_files_with_real_url(self):
        """Test parsing files including real URL with the main parse_files method."""
        # Test URL
        test_url = "https://www.domestika.com/en/courses/2291-watercolor-landscapes-in-a-naturalist-style"
        
        # Parse URL
        files = [test_url]
        result = await self.parser.parse_files(files)
        
        # Verify result structure
        assert "=== PARSED FILE CONTENT ===" in result
        assert "domestika.com" in result  # Domain extracted
        print(f"Full URL parsing result: {result}") 