import torch.nn.functional as F
from transformers import Trainer


class GRPOTrainer(Trainer):
    """Hugging-Face Trainer subclass implementing GRPO loss.

    Args:
        beta (float): temperature for scaling preference scores.
    """
    def __init__(self, beta: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.beta = beta

    def compute_loss(self, model, inputs, return_outputs=False):
        # ---- pad-masked log-probs ---------
        labels         = inputs.pop("labels")
        attention_mask = inputs["attention_mask"]
        outputs        = model(**inputs)
        log_probs      = F.log_softmax(outputs.logits, dim=-1)

        # Mask pad tokens
        active_positions = attention_mask.view(-1) == 1
        nll = F.nll_loss(
            log_probs.view(-1, log_probs.size(-1))[active_positions],
            labels.view(-1)[active_positions],
            reduction="none",
        ).view(labels.size())

        # KL term (GRPO)
        group_scores = inputs["scores"] * self.beta      # temp scaling
        target_dist  = F.softmax(group_scores, dim=1)
        pi_logp      = (-nll.sum(dim=1))                 # log Pi
        kl           = (target_dist * (target_dist.log() - pi_logp)).sum()
        loss         = nll.mean() + kl / len(labels)

        return (loss, outputs) if return_outputs else loss
