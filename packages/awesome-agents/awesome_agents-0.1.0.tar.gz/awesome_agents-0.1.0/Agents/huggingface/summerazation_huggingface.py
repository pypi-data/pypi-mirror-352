from transformers import pipeline
import torch

transcript_path = "sample_transcript.txt"


# --- Step 1: Load transcript from text file ---
def load_transcript(file_path):
    with open(file_path, "r") as f:
        return f.read()


# --- Step 2: Summarize using Open-source LLM ---
def summarize_text(text, model_name="Falconsai/text_summarization"):
    print("Loading summarization model...")
    summarizer = pipeline("summarization", model=model_name, device=-1)
    summary = summarizer(text, max_length=150, min_length=40, do_sample=False)[0]['summary_text']
    return summary


# --- Step 3: Main Function ---
def run_note_taker(transcript_file):
    transcript = load_transcript(transcript_file)
    print("\n--- Transcript ---\n", transcript)

    summary = summarize_text(transcript)
    print("\n--- Summary ---\n", summary)

    # Save to file
    with open("meeting_notes.md", "w") as f:
        f.write("# Meeting Summary\n\n")
        f.write(summary)
        f.write("\n\n---\n\n")
        f.write("## Full Transcript\n\n")
        f.write(transcript)


# --- Example Run ---
if __name__ == "__main__":
    transcript_path = "sample_transcript.txt"  # Your input
    run_note_taker(transcript_path)
