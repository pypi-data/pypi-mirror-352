__all__ = [
    "masked_cross_entropy",
    "adaptive_l1_loss",
    "contrastive_loss",
    "smooth_l1_loss",
    "hybrid_loss",
    "diff_loss",
    "cosine_loss",
    "gan_loss",
    "ft_n_loss",
]
import math
import random
from lt_tensor.torch_commons import *
from lt_utils.common import *
import torch.nn.functional as F

def ft_n_loss(output: Tensor, target: Tensor, weight: Optional[Tensor] = None):
    if weight is not None:
        return torch.mean((torch.abs(output - target) + weight) **0.5)
    return torch.mean(torch.abs(output - target)**0.5)

def adaptive_l1_loss(
    inp: Tensor,
    tgt: Tensor,
    weight: Optional[Tensor] = None,
    scale: float = 1.0,
    inverted: bool = False,
):

    if weight is not None:
        loss = torch.mean(torch.abs((inp - tgt) + weight.mean()))
    else:
        loss = torch.mean(torch.abs(inp - tgt))
    loss *= scale
    if inverted:
        return -loss
    return loss


def smooth_l1_loss(inp: Tensor, tgt: Tensor, beta=1.0, weight=None):
    diff = torch.abs(inp - tgt)
    loss = torch.where(diff < beta, 0.5 * diff**2 / beta, diff - 0.5 * beta)
    if weight is not None:
        loss *= weight
    return loss.mean()


def contrastive_loss(x1: Tensor, x2: Tensor, label: Tensor, margin: float = 1.0):
    # label == 1: similar, label == 0: dissimilar
    dist = torch.nn.functional.pairwise_distance(x1, x2)
    loss = label * dist**2 + (1 - label) * torch.clamp(margin - dist, min=0.0) ** 2
    return loss.mean()


def cosine_loss(inp, tgt):
    cos = torch.nn.functional.cosine_similarity(inp, tgt, dim=-1)
    return 1 - cos.mean()  # Lower is better


class GanLosses:
    @staticmethod
    def get_loss(
        pred: Tensor,
        target_is_real: bool,
        loss_type: Literal["bce", "mse", "hinge", "wasserstein"] = "bce",
    ) -> Tensor:
        if loss_type == "bce":  # Standard GAN
            target = torch.ones_like(pred) if target_is_real else torch.zeros_like(pred)
            return F.binary_cross_entropy_with_logits(pred, target)

        elif loss_type == "mse":  # LSGAN
            target = torch.ones_like(pred) if target_is_real else torch.zeros_like(pred)
            return F.mse_loss(torch.sigmoid(pred), target)

        elif loss_type == "hinge":
            if target_is_real:
                return torch.mean(F.relu(1.0 - pred))
            else:
                return torch.mean(F.relu(1.0 + pred))

        elif loss_type == "wasserstein":
            return -pred.mean() if target_is_real else pred.mean()

        else:
            raise ValueError(f"Unknown loss_type: {loss_type}")

    @staticmethod
    def generator_loss(fake_pred: Tensor, loss_type: str = "bce") -> Tensor:
        return GanLosses.get_loss(fake_pred, target_is_real=True, loss_type=loss_type)

    @staticmethod
    def discriminator_loss(
        real_pred: Tensor, fake_pred: Tensor, loss_type: str = "bce"
    ) -> Tensor:
        real_loss = GanLosses.get_loss(
            real_pred, target_is_real=True, loss_type=loss_type
        )
        fake_loss = GanLosses.get_loss(
            fake_pred.detach(), target_is_real=False, loss_type=loss_type
        )
        return (real_loss + fake_loss) * 0.5


def masked_cross_entropy(
    logits: torch.Tensor,  # [B, T, V]
    targets: torch.Tensor,  # [B, T]
    lengths: torch.Tensor,  # [B]
    reduction: str = "mean",
) -> torch.Tensor:
    """
    CrossEntropyLoss with masking for variable-length sequences.
    - logits: unnormalized scores [B, T, V]
    - targets: ground truth indices [B, T]
    - lengths: actual sequence lengths [B]
    """
    B, T, V = logits.size()
    logits = logits.view(-1, V)
    targets = targets.view(-1)

    # Create mask
    mask = torch.arange(T, device=lengths.device).expand(B, T) < lengths.unsqueeze(1)
    mask = mask.reshape(-1)

    # Apply CE only where mask == True
    loss = F.cross_entropy(
        logits[mask], targets[mask], reduction="mean" if reduction == "mean" else "none"
    )
    if reduction == "none":
        return loss
    return loss


def diff_loss(pred_noise, true_noise, mask=None):
    """Standard diffusion noise-prediction loss (e.g., DDPM)"""
    if mask is not None:
        return F.mse_loss(pred_noise * mask, true_noise * mask)
    return F.mse_loss(pred_noise, true_noise)


def hybrid_diff_loss(pred_noise, true_noise, alpha=0.5):
    """Combines L1 and L2"""
    l1 = F.l1_loss(pred_noise, true_noise)
    l2 = F.mse_loss(pred_noise, true_noise)
    return alpha * l1 + (1 - alpha) * l2


def gan_d_loss(real_preds, fake_preds, use_lsgan=True):
    loss = 0
    for real, fake in zip(real_preds, fake_preds):
        if use_lsgan:
            loss += F.mse_loss(real, torch.ones_like(real)) + F.mse_loss(
                fake, torch.zeros_like(fake)
            )
        else:
            loss += -torch.mean(torch.log(real + 1e-7)) - torch.mean(
                torch.log(1 - fake + 1e-7)
            )
    return loss
