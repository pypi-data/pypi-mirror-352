from typing import List
from abc import ABC, abstractmethod

class SummaryProcessor(ABC):
    """Interface for generating document summary."""
    
    @abstractmethod
    def generate_summary(self, text_blocks: List[str]) -> str:
        """
        Generate summary based on text blocks.
        
        Args:
            text_blocks: List of document text blocks
            
        Returns:
            Document summary
        """
        pass 


class MockSummaryProcessor(SummaryProcessor):
    """Mock summary processor for initial development."""
    
    def generate_summary(self, text_blocks: List[str]) -> str:
        """Generate test document summary."""
        if not text_blocks:
            return "Document contains no text content."
        
        word_count = len(" ".join(text_blocks).split())
        block_count = len(text_blocks)
        
        return (
            f"Document Summary:\n"
            f"- Text blocks: {block_count}\n"
            f"- Approximate word count: {word_count}\n"
            f"- Content type: {'Short' if word_count < 100 else 'Medium' if word_count < 500 else 'Long'}\n"
            f"- Main topics: development, testing, architecture\n"
            f"- Status: Processed successfully"
        ) 
