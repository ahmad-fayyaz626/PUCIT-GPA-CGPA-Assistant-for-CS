# here we will set the llm configuration and the model to be used for the agent
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
#load the env file
load_dotenv()
llm = init_chat_model(os.getenv("LLM_MODEL"), api_key=os.getenv("API_KEY"))

