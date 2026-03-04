from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

class OpenAIEmbeddings:
    """Wrapper for the OpenAI embeddings client. If the OPENAI_API_KEY is not set it defaults to the environment variable."""
    def __init__(self, openai_api_key: str | None = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.client = self.build_client()
        
    
    def build_client(self):
        return OpenAI(api_key=self.openai_api_key)
