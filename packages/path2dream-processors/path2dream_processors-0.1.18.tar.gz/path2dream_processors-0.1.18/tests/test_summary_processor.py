import pytest
import os
from path2dream_processors.summary_processor import LangChainSummaryProcessor


@pytest.mark.asyncio
async def test_real_summary_generation():
    """Real integration test that calls OpenAI API and checks response."""
    if not os.getenv('OPENAI_API_KEY'):
        pytest.fail("OPENAI_API_KEY environment variable is required for this test")
    
    processor = LangChainSummaryProcessor()
    
    context = "Software testing documentation"
    text_blocks = [
        "This document covers unit testing best practices in Python.",
        "It includes examples of pytest usage and test organization.",
        "The guide also discusses integration testing strategies."
    ]
    
    title, summary = await processor.generate_summary(context, text_blocks)
    
    assert isinstance(title, str), f"Title should be string, got {type(title)}"
    assert isinstance(summary, str), f"Summary should be string, got {type(summary)}"
    assert len(title.strip()) > 0, "Title should not be empty"
    assert len(summary.strip()) > 0, "Summary should not be empty" 