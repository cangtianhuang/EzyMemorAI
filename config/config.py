import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODELEND')
    LLM_MODEL = os.getenv('LLM_MODELEND')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
    TIKTOKEN_MODEL = 'gpt2'
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200