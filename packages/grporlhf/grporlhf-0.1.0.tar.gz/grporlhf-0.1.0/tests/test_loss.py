# tests/test_loss.py
import torch, random
from grpo_rlhf.trainer import GRPOTrainer
from transformers import AutoModelForCausalLM, TrainingArguments

def test_grpo_loss_runs():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model = AutoModelForCausalLM.from_pretrained("sshleifer/tiny-gpt2").to(device)
    dummy   = {
        "input_ids":      torch.randint(0, 50257, (2, 16)).to(device),
        "attention_mask": torch.ones((2, 16)).to(device),
        "labels":         torch.randint(0, 50257, (2, 16)).to(device),
        "scores":         torch.tensor([[1.0, 0.0], [0.0, 1.0]]).to(device),
    }
    args = TrainingArguments(".", per_device_train_batch_size=2)
    trainer = GRPOTrainer(model=model, args=args, train_dataset=[dummy])
    loss = trainer.compute_loss(model, dummy)
    assert torch.isfinite(loss)
