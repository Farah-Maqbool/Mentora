from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
import os
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

llm = HuggingFaceInferenceAPI(
    model_name="meta-llama/Llama-3.3-70B-Instruct",
    temperature=0.7,
    api_key=groq_api_key,
    provider="groq"
)

response = llm.complete("Hello, How are you?")

print(response)