from typing import List, Tuple
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain import hub


class TitleAndSummary(BaseModel):
    reasoning: str = Field(description="Provide your detailed reasoning chain of thought of what is important in this document to be included as title and summary?")
    title: str = Field(description="The title of the document")
    summary: str = Field(description="The short summarization of all insights of this document in relevance to the purpose of the project.")


class LangChainSummaryProcessor:
    def __init__(self):
        llm = ChatOpenAI(model="gpt-4.1", temperature=0)
        llm = llm.with_structured_output(TitleAndSummary)
        prompt = hub.pull("path2dream_context_summarizer")
        self.chain = prompt | llm

    async def generate_summary(self, context: str, text_blocks: List[str]) -> Tuple[str, str]:
        aggregated_text = "\n".join(text_blocks)
        result = await self.chain.ainvoke({"context": context, "new_document": aggregated_text})
        return result.title, result.summary
