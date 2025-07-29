import os

from agentsapi.utils.utils import init

os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://localhost:6006"

import os
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4317"
os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "grpc"

from phoenix.otel import register

# configure the Phoenix tracer
tracer_provider = register(
    project_name="my-llm-app", # Default is 'default'
    auto_instrument=True # Auto-instrument your app based on installed OI dependencies
)



init()

import os

# Set OpenTelemetry endpoint for Phoenix
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4317"
os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "grpc"

from phoenix.otel import register

# Register tracer
register(
    project_name="my-llm-app",
    auto_instrument=True
)

# Use new OpenAI Client (v1+)
from openai import OpenAI

client = OpenAI()  # Replace with your key

# Create a trace span for manual tracking (optional)
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("call-openai-chat"):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ]
    )

    print(response.choices[0].message.content)
