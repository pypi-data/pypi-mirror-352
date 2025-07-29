import os, google.genai
from opik.integrations.genai import track_genai

from agentsapi.utils.utils import init
init()
client = google.genai.Client()
gemini_client = track_genai(client)
response = gemini_client.models.generate_content(
    model="gemini-2.0-flash-001", contents="Write a haiku about AI engineering."
)
print(response.text)

# model: gemini-2.0-flash-001
# created_from: genai
# create_time: null
# response_id: null
# model_version: gemini-2.0-flash-001
# prompt_feedback: null
# usage_metadata:
# cache_tokens_details: null
# cached_content_token_count: null
# candidates_token_count: 18
# candidates_tokens_details:
# - modality: TEXT
# token_count: 18
# prompt_token_count: 7
# prompt_tokens_details:
# - modality: TEXT
# token_count: 7
# thoughts_token_count: null
# tool_use_prompt_token_count: null
# tool_use_prompt_tokens_details: null
# total_token_count: 25
# traffic_type: null
# automatic_function_calling_history: []
# parsed: null