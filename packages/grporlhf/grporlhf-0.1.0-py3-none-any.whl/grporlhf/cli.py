import argparse, torch
from . import GRPOTrainer, build_dataset, load_config
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default=None, help="YAML config path")
    args = p.parse_args()

    cfg = load_config(args.config)

    tokenizer = AutoTokenizer.from_pretrained(cfg["model_name"])
    model     = AutoModelForCausalLM.from_pretrained(cfg["model_name"])

    ds = build_dataset(cfg["dataset_path"], tokenizer, cfg["max_length"])
    targs = TrainingArguments(**cfg["training_args"])

    trainer = GRPOTrainer(
    model=model,
    args=targs,
    train_dataset=ds,
    beta=cfg.get("beta", 1.0),
    )
    trainer.train()
    trainer.save_model(cfg["output_dir"])

if __name__ == "__main__":
    main()
