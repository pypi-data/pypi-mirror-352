from langchain_openai import ChatOpenAI

from agents.utils.utils import init

# Load environment variables

# Initialize shared LLM instance
init()
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0) 