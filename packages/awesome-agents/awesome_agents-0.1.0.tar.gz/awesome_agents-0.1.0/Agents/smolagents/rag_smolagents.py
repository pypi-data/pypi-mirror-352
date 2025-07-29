import datasets
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load dataset
knowledge_base = datasets.load_dataset("m-ric/huggingface_doc", split="train")
knowledge_base = knowledge_base.filter(lambda row: row["source"].startswith("huggingface/transformers"))
# Convert into Document format
source_docs = [
    Document(page_content=doc["text"], metadata={"source": doc["source"].split("/")[1]})
    for doc in knowledge_base
]

# Split documents into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50, add_start_index=True, strip_whitespace=True,
    separators=["\n\n", "\n", ".", " ", ""]
)

docs_processed = text_splitter.split_documents(source_docs)
print(docs_processed)

from smolagents import Tool
from langchain_community.retrievers import BM25Retriever


class RetrieverTool(Tool):
    name = "retriever"
    description = "Retrieves relevant sections from Transformers documentation."
    inputs = {
        "query": {
            "type": "string",
            "description": "A search query optimized for semantic similarity with target documents."
        }
    }
    output_type = "string"

    def __init__(self, docs, **kwargs):
        super().__init__(**kwargs)
        self.retriever = BM25Retriever.from_documents(docs, k=10)

    def forward(self, query: str) -> str:
        assert isinstance(query, str), "Your search query must be a string"
        docs = self.retriever.invoke(query)
        return "\nRetrieved documents:\n" + "".join(
            [f"\n\n===== Document {i} =====\n" + doc.page_content for i, doc in enumerate(docs)]
        )


retriever_tool = RetrieverTool(docs_processed)

print(retriever_tool)

# Create an Agent With Smolagents
# The agent needs:
#
# Tools – The retriever tool.
#
# Model – A language model, such as Meta Llama-3.3-70B-Instruct, accessed via Hugging Face’s Inference API.

from smolagents import HfApiModel, CodeAgent

agent = CodeAgent(
    tools=[retriever_tool],
    model=HfApiModel(),
    max_steps=4,
    verbosity_level=2
)
#
# Run the Agent
# Now, we can test the Agentic RAG system by asking a technical question.

agent_output = agent.run("For a transformers model training, which is slower, the forward or the backward pass?")
print("Final output:")
print(agent_output)
