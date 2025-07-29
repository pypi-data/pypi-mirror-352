### ✅ 1. **Summarization**

from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
summary = summarizer("The quick brown fox jumps over the lazy dog.", max_length=50, min_length=10, do_sample=False)
print(summary[0]['summary_text'])

### ✅ 2. **Text Classification (Sentiment Analysis)**


from transformers import pipeline

classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=-1)
result = classifier("Hugging Face is awesome!")

print(f" result = {result}")

### ✅ 3. **Named Entity Recognition (NER)**


from transformers import pipeline

ner = pipeline("ner", grouped_entities=True, device=-1)
entities = ner("Hugging Face Inc. is a company based in New York.")
print(entities)

### ✅ 4. **Question Answering**

from transformers import pipeline

qa = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", device=-1)
answer = qa(question="Where is Hugging Face based?", context="Hugging Face Inc. is a company based in New York.")
print(answer['answer'])

### ✅ 5. **Translation (English to French)**


from transformers import pipeline

translator = pipeline("translation_en_to_fr", model="Helsinki-NLP/opus-mt-en-fr", device=-1)
translated = translator("Hugging Face is creating a tool that democratizes AI.")
print(translated[0]['translation_text'])

### ✅ 6. **Text Generation (e.g., GPT-2)**


from transformers import pipeline

generator = pipeline("text-generation", model="gpt2", device=-1)
result = generator("Once upon a time,", max_length=50, num_return_sequences=1)
print(result[0]['generated_text'])

### ✅ 7. **Text-to-Text (T5 - General Task Handler)**

from transformers import pipeline

t5 = pipeline("text2text-generation", model="t5-small", device=-1)
result = t5("translate English to German: The house is wonderful.")
print(result[0]['generated_text'])

### ✅ 8. **Zero-Shot Classification**


from transformers import pipeline

zero_shot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=-1)
result = zero_shot("This is a great course on deep learning.", candidate_labels=["education", "politics", "economy"])
print(result)

### ✅ 9. **Text Embedding (Semantic Search use case)**


from transformers import pipeline

embedder = pipeline("feature-extraction", model="sentence-transformers/all-MiniLM-L6-v2", device=-1)
embedding = embedder("How do I reset my password?")
print(f"Vector length: {len(embedding[0][0])}")

### ✅ 10. **Fill-Mask (Masked Language Modeling)**

from transformers import pipeline

unmasker = pipeline("fill-mask", model="bert-base-uncased", device=-1)
results = unmasker("The capital of France is [MASK].")
for r in results:
    print(f"{r['token_str']} — score: {r['score']:.4f}")

### ✅ 11. **Language Detection**

from transformers import pipeline

lang_detect = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection", device=-1)
print(lang_detect("Bonjour, je m'appelle Jean."))

### ✅ 12. **Grammar Correction**

from transformers import pipeline

grammar_corrector = pipeline("text2text-generation", model="pszemraj/flan-t5-large-grammar-synthesis", device=-1)
output = grammar_corrector("She no went to the market", max_length=64)
print(output[0]['generated_text'])

### ✅ 13. **Summarizing Legal or Scientific Text**

from transformers import pipeline

legal_summarizer = pipeline("summarization", model="nlpaueb/legal-bert-small-uncased", device=-1)
text = "The plaintiff argued that the contractual obligations were breached due to unforeseen circumstances..."
# It's better to use domain-specific summarizers for legal/biomedical content.




## ✅ 14. **Image Classification**

from transformers import pipeline
from PIL import Image
import requests

image_classifier = pipeline("image-classification", model="google/vit-base-patch16-224", device=-1)
img = Image.open(requests.get("https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/beach.png", stream=True).raw)
result = image_classifier(img)
print(result)


## ✅ 15. **Object Detection**

from transformers import pipeline
from PIL import Image
import requests

detector = pipeline("object-detection", model="facebook/detr-resnet-50", device=-1)
image = Image.open(requests.get("https://huggingface.co/datasets/Narsil/image_dummy/raw/main/lena.png", stream=True).raw)
outputs = detector(image)
print(outputs)

## ✅ 16. **Image-to-Text (Captioning)**

from transformers import pipeline
from PIL import Image
import requests

captioner = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning", device=-1)
img = Image.open(requests.get("https://huggingface.co/datasets/Narsil/image_dummy/raw/main/lena.png", stream=True).raw)
result = captioner(img)
print(result[0]["generated_text"])

## ✅ 17. **Automatic Speech Recognition (ASR)**

from transformers import pipeline

asr = pipeline("automatic-speech-recognition", model="openai/whisper-small", device=-1)
result = asr("https://huggingface.co/datasets/Narsil/asr_dummy/resolve/main/1.flac")
print(result['text'])

## ✅ 18. **Text-to-Speech (TTS)** – *(needs `TTS` library or `bark` models)*

#Hugging Face doesn’t support TTS directly in `pipeline`, but here's one using Bark:
#
# ```bash
# pip install bark
# ```

#
# from bark import generate_audio
# audio_array = generate_audio("Hello, how are you?")

## ✅ 19. **Code Generation**

from transformers import pipeline

code_gen = pipeline("text-generation", model="Salesforce/codegen-350M-multi", device=-1)
result = code_gen("def fibonacci(n):", max_length=64)
print(result[0]["generated_text"])

## ✅ 20. **Multilingual Translation (Auto detect language)**

from transformers import pipeline

translator = pipeline("translation", model="Helsinki-NLP/opus-mt", device=-1)
text = "Bonjour, comment allez-vous?"
output = translator(text, src_lang="fr", tgt_lang="en")
print(output[0]['translation_text'])
