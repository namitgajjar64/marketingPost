from langchain_groq.chat_models import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.2-90b-text-preview"
)
