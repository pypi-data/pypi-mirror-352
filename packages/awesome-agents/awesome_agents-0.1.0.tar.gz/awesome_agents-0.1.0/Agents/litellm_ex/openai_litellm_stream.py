import litellm
import os
from agents.utils.utils import init

init()
## set ENV variables
#os.environ["OPENAI_API_KEY"] = "your-api-key"

response = litellm.completion(
    model="openai/gpt-4o",
    messages=[{ "content": "Hello, how are you?","role": "user"}],
    stream=True,
)
print(response)

print(litellm)

print(litellm)