import torch
from datasets import load_dataset


def build_dataset(path: str, tokenizer, max_len: int = 512):
    """Load JSONL ↦ tokenized DatasetDict."""
    ds = load_dataset("json", data_files=path)["train"]

    def _tokenize(example):
        enc = tokenizer(
            example["prompt"],
            truncation=True,
            max_length=max_len,
            padding="max_length",
            return_tensors="pt",
        )
        enc["scores"] = torch.tensor(example["scores"], dtype=torch.float)
        enc["labels"] = enc["input_ids"].clone()
        return enc

    return ds.map(_tokenize, batched=False).with_format("torch")
