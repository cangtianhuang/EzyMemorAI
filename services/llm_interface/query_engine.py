from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever

from services.llm_interface.model_config import get_llm_model
from services.llm_interface.prompt_templates import SEARCH_TEMPLATE


class QueryEngine:
    def __init__(self, prompt_template: str | None = None, search_k: int = 1):
        self.llm = get_llm_model()
        self.prompt = SEARCH_TEMPLATE
        self.search_k = search_k
        self.qa_chain = None

    def create_chain(self, retriever: VectorStoreRetriever) -> Any:
        print_runnable = RunnableLambda(lambda x: print(f"Content: {x}") or x)
        self.qa_chain = (
                {
                    "question": RunnablePassthrough(),
                    "context": retriever
                }
                | print_runnable
                | self.prompt
                | self.llm
                | StrOutputParser()
        )
        return self.qa_chain

    def search(self, question: str) -> Any:
        return self.qa_chain.invoke(question)
