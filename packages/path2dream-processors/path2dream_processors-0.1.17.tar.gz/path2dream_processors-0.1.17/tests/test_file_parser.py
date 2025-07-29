import pytest
import os
from path2dream_processors.file_parser import APIBasedFileParser


@pytest.mark.asyncio
async def test_real_audio_parsing():
    """Test parsing real audio file with OpenAI Whisper API."""
    if not os.getenv('OPENAI_API_KEY'):
        pytest.fail("OPENAI_API_KEY environment variable is required for this test")
    
    parser = APIBasedFileParser()
    
    # Try multiple possible test file locations
    test_files = [
        "tests/data/test.mp3",
        "/Users/fun/Downloads/test.mp3"
    ]
    
    test_file = None
    for path in test_files:
        if os.path.exists(path):
            test_file = path
            break
    
    if not test_file:
        pytest.fail(f"No test audio file found. Create one of: {test_files}")
    
    result = await parser._parse_audio(test_file)
    
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    assert "Audio transcription:" in result
    assert "Error" not in result


@pytest.mark.asyncio
async def test_real_pdf_parsing():
    """Test parsing real PDF file with LlamaParse API."""
    if not os.getenv('LLAMA_CLOUD_API_KEY'):
        pytest.fail("LLAMA_CLOUD_API_KEY environment variable is required for this test")
    
    parser = APIBasedFileParser()
    
    # Try multiple possible test file locations
    test_files = [
        "tests/data/test.pdf",
        "/Users/fun/Downloads/test.pdf"
    ]
    
    test_file = None
    for path in test_files:
        if os.path.exists(path):
            test_file = path
            break
    
    if not test_file:
        pytest.fail(f"No test PDF file found. Create one of: {test_files}")
    
    result = await parser._parse_document(test_file)
    
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    assert "Document content:" in result
    assert "Error" not in result


@pytest.mark.asyncio
async def test_real_url_parsing():
    """Test parsing real URL with Jina Reader API."""
    parser = APIBasedFileParser()
    test_url = "https://www.python.org/"
    
    result = await parser._parse_url(test_url)
    
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    assert ("Web content" in result or "Error" in result)  # Either success or expected error


@pytest.mark.asyncio
async def test_real_parse_files_integration():
    """Test parsing multiple real files with actual API calls."""
    parser = APIBasedFileParser()
    
    # Build list of available files/URLs to test
    files = []
    
    # Check for audio file in multiple locations
    audio_files = ["tests/data/test.mp3", "/Users/fun/Downloads/test.mp3"]
    for audio_file in audio_files:
        if os.path.exists(audio_file) and os.getenv('OPENAI_API_KEY'):
            files.append(audio_file)
            break
    
    # Check for PDF file in multiple locations
    pdf_files = ["tests/data/test.pdf", "/Users/fun/Downloads/test.pdf"]
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file) and os.getenv('LLAMA_CLOUD_API_KEY'):
            files.append(pdf_file)
            break
    
    # Always add URL (works even without API key)
    files.append("https://www.python.org/")
    
    if len(files) == 1:  # Only URL
        pytest.fail("No test files found. Add test files to tests/data/ or provide API keys")
    
    result = await parser.parse_files(files)
    
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    assert "=== PARSED FILE CONTENT ===" in result 