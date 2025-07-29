from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load tokenizer and model
model_name = "unitary/toxic-bert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

# Toxicity labels
labels = [
    "toxicity",
    "severe_toxicity",
    "obscene",
    "identity_attack",
    "insult",
    "threat"
]

# Function to split text into chunks of max 512 tokens


async def chunk_text(text, max_length=512, stride=256):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=False,
        add_special_tokens=True
    )

    input_ids = inputs["input_ids"][0]
    attention_mask = inputs["attention_mask"][0]

    chunks = []
    for i in range(0, len(input_ids), stride):
        chunk_ids = input_ids[i: i + max_length]
        chunk_mask = attention_mask[i: i + max_length]

        # Ensure proper tensor shape: [1, seq_len]
        chunks.append({
            "input_ids": chunk_ids.unsqueeze(0),
            "attention_mask": chunk_mask.unsqueeze(0)
        })

        if i + max_length >= len(input_ids):
            break

    return chunks

# Function to evaluate toxicity


async def detect_toxicity(text, threshold=0.5):
    chunks = await chunk_text(text)
    max_scores = torch.zeros(len(labels))

    for chunk in chunks:
        with torch.no_grad():
            outputs = model(**chunk)
            probs = torch.sigmoid(outputs.logits).squeeze()
            max_scores = torch.maximum(max_scores, probs)

    result = {label: float(score) for label, score in zip(labels, max_scores)}
    flagged = {k: v for k, v in result.items() if v >= threshold}

    return {
        "is_toxic": len(flagged) > 0,
        "flagged_labels": flagged,
        "all_scores": result
    }
