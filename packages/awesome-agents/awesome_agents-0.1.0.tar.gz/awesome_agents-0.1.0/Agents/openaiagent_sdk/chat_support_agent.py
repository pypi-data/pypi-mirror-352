from agents import Agent, Runner, function_tool
import asyncio
from agentsapi.utils.utils import init
init()
from datetime import datetime, timedelta
import random
# Define some tools for our agents
@function_tool
def check_order_status(order_id: str) -> str:
    """Check the status of an order by ID."""
    # Simulate order database
    statuses = ["Processing", "Shipped", "Delivered", "Cancelled"]
    return f"Order {order_id} is currently {random.choice(statuses)}."
@function_tool
def get_shipping_estimate(product_id: str, destination: str) -> str:
    """Get shipping estimate for a product to a destination."""
    # Simulate shipping calculation
    days = random.randint(2, 10)
    estimated_date = (datetime.now() + timedelta(days=days)).strftime("%B %d, %Y")
    return f"Shipping to {destination} takes approximately {days} days. Estimated delivery: {estimated_date}"
@function_tool
def process_refund(order_id: str, reason: str) -> str:
    """Process a refund request."""
    return f"Refund for order {order_id} has been initiated. Reason: {reason}. It will be processed within 3-5 business days."
# Create specialized agents
order_agent = Agent(
    name="order_specialist",
    instructions="""You are an order specialist. 
    Help customers check their order status and provide shipping estimates.
    Be friendly and professional.""",
    tools=[check_order_status, get_shipping_estimate]
)
refund_agent = Agent(
    name="refund_specialist",
    instructions="""You are a refund specialist.
    Help customers process refunds for their orders.
    Be empathetic and helpful.""",
    tools=[process_refund]
)
# Create the main triage agent
support_agent = Agent(
    name="customer_support",
    instructions="""You are a customer support agent for an e-commerce store.
    If customers have questions about order status or shipping, hand off to the order specialist.
    If customers want to request a refund, hand off to the refund specialist.
    For general questions, answer directly.
    Always be polite and helpful.""",
    handoffs=[order_agent, refund_agent]
)
async def main():
    # Simulate a customer support conversation
    queries = [
        "What's the status of my order #12345?",
        "I want to return my purchase because it's damaged. Order #54321.",
        "Do you offer gift wrapping services?",
        "How long will shipping take for product XYZ-789 to Seattle?"
    ]

    for i, query in enumerate(queries):
        print(f"\n--- Customer Query {i+1} ---")
        print(f"Customer: {query}")

        result = await Runner.run(support_agent, query)

        print(f"Agent: {result.final_output}")
if __name__ == "__main__":
    asyncio.run(main())