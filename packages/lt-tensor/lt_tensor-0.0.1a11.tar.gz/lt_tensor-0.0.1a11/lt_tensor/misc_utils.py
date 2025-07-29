__all__ = [
    "log_tensor",
    "set_seed",
    "count_parameters",
    "freeze_all_except",
    "freeze_selected_weights",
    "unfreeze_all_except",
    "unfreeze_selected_weights",
    "clip_gradients",
    "detach_hidden",
    "one_hot",
    "safe_divide",
    "batch_pad",
    "sample_tensor",
    "TorchCacheUtils",
    "clear_cache",
    "default_device",
    "soft_restore",
    "Packing",
    "Padding",
    "Masking",
    "LogTensor",
    "get_losses",
]

import re
import gc
import sys
import random
import numpy as np
from lt_utils.type_utils import is_str
from .torch_commons import *
from lt_utils.misc_utils import cache_wrapper
from lt_utils.common import *
from lt_utils.misc_utils import ff_list
import torch.nn.functional as F


def soft_restore(tensor, epsilon=1e-6):
    return torch.where(tensor == 0, torch.full_like(tensor, epsilon), tensor)


def try_torch(fn: str, *args, **kwargs):
    tryed_torch = False
    not_present_message = (
        f"Both `torch` and `torch.nn.functional` does not contain the module `{fn}`"
    )
    try:
        if hasattr(F, fn):
            return getattr(F, fn)(*args, **kwargs)
        elif hasattr(torch, fn):
            tryed_torch = True
            return getattr(torch, fn)(*args, **kwargs)
        return not_present_message
    except Exception as a:
        try:
            if not tryed_torch and hasattr(torch, fn):
                return getattr(torch, fn)(*args, **kwargs)
            return str(a)
        except Exception as e:
            return str(e) + " | " + str(a)


def log_tensor(
    item: Union[Tensor, np.ndarray],
    title: Optional[str] = None,
    print_details: bool = True,
    print_tensor: bool = False,
    dim: Optional[int] = None,
):
    assert isinstance(item, (Tensor, np.ndarray))
    has_title = is_str(title)

    if has_title:
        print("========[" + title.title() + "]========")
        _b = 20 + len(title.strip())
    print(f"shape: {item.shape}")
    print(f"dtype: {item.dtype}")
    if print_details:
        print(f"ndim: {item.ndim}")
        if isinstance(item, Tensor):
            print(f"device: {item.device}")
            print(f"min: {item.min():.4f}")
            print(f"max: {item.max():.4f}")
            try:
                print(f"std: {item.std(dim=dim):.4f}")
            except:
                pass
            try:

                print(f"mean: {item.mean(dim=dim):.4f}")
            except:
                pass
    if print_tensor:
        print(item)
    if has_title:
        print("".join(["-"] * _b), "\n")
    else:
        print("\n")
    sys.stdout.flush()


def get_losses(base: Tensor, target: Tensor, return_valid_only: bool = False):
    losses = {}
    losses["mse_loss"] = try_torch("mse_loss", base, target)
    losses["l1_loss"] = try_torch("l1_loss", base, target)
    losses["huber_loss"] = try_torch("huber_loss", base, target)
    losses["poisson_nll_loss"] = try_torch("poisson_nll_loss", base, target)
    losses["smooth_l1_loss"] = try_torch("smooth_l1_loss", base, target)
    losses["cross_entropy"] = try_torch("cross_entropy", base, target)
    losses["soft_margin_loss"] = try_torch("soft_margin_loss", base, target)
    losses["nll_loss"] = try_torch("nll_loss", base, target)
    losses["gaussian_nll_loss"] = try_torch("gaussian_nll_loss", base, target, var=1.0)
    losses["gaussian_nll_loss-var_0.25"] = try_torch(
        "gaussian_nll_loss", base, target, var=0.25
    )
    losses["gaussian_nll_loss-var_4.0"] = try_torch(
        "gaussian_nll_loss", base, target, var=4.0
    )
    if not return_valid_only:
        return losses
    valid = {}
    for name, loss in losses.items():
        if isinstance(loss, str):
            continue
        valid[name] = loss
    return valid


class LogTensor:
    negative_slope = 0.1
    do_print: bool = True
    end_with: str = "\n"
    stored_items: List[
        Dict[str, Union[str, Number, Tensor, List[Union[Tensor, Number, str]]]]
    ] = []
    max_stored_items: int = 32

    def _setup_message(self, title: str, t: Union[Tensor, str, int]):
        try:
            if isinstance(t, Tensor):
                try:
                    message = f"{title}: {t}"
                    if t.ndim == 0 and t.shape[0] == 1:
                        message = f"{title}: {t.item():.5f}"
                    elif t.ndim == 1 and t.shape[-1] == 1:
                        message = f"{title}: {t[-1].item():.5f}"
                    else:
                        message = f"{title}: {t.item()}"
                except:
                    message = f"{title}: {t}"
            else:
                t = str(t).replace("\n", " ")
                t = (
                    re.sub(r"\s+", " ", t)
                    .replace("( ", "(")
                    .replace("[ ", "[")
                    .replace(" ]", "]")
                    .replace(" )", ")")
                )
                message = f"{title}: {t}"
        except Exception as e:
            message = f"{title}: {e}"
        return message

    def _print(self, message: str):
        if self.do_print:
            print(message)
            sys.stdout.flush()

    def _process(
        self,
        name: str,
        resp: Union[Callable[[Any], Any], Any],
        do_not_print: bool = False,
    ):
        if callable(resp):
            try:
                response = resp()
            except Exception as e:
                response = str(e)
                print(e)
        else:
            response = resp
        if not do_not_print and self.do_print:
            msg = self._setup_message(name, response)
            self._print(msg)
        return dict(item=name, value=response)

    def __call__(
        self,
        inputs: Union[Tensor, np.ndarray, Sequence[Number]],
        title: Optional[str] = None,
        target: Optional[Union[Tensor, np.ndarray, Sequence[Number]]] = None,
        *,
        log_tensor: bool = False,
        log_device: bool = False,
        log_mean: bool = False,
        log_std: bool = False,
        dim_mean: int = -1,
        dim_std: int = -1,
        print_extended: bool = False,
        external_logs: List[Tuple[str, Union[Dict[str, Any], List[Any], Any]]] = [
            ("softmax", {"dim": 0}),
            ("relu", None),
            ("leaky_relu", [0.1]),
            ("min", 0),
            ("max", dict(dim=-1)),
        ],
        validate_item_type: bool = False,
        exclude_invalid_losses: bool = True,
        **kwargs,
    ):
        invalid_type = not isinstance(inputs, (Tensor, np.ndarray, list, tuple))
        _main_item_tp = type(inputs)
        assert (
            not validate_item_type or not invalid_type
        ), f"Invalid Type: {_main_item_tp}"
        if invalid_type:
            self._print(f"Invalid Type: {_main_item_tp}")
            return

        inputs = self._setup_tensor(inputs)
        target = self._setup_tensor(target)
        if is_str(title):
            title = re.sub(r"\s+", " ", title.replace("_", " "))
            has_title = is_str(title)
            if has_title:
                self._print("========[ " + title.title() + " ]========")
        else:
            title = "Unnamed"

        current_register = {"title": title, "values": []}
        current_register["shape"] = self._process("shape", inputs.shape)
        current_register["ndim"] = self._process("ndim", inputs.ndim)
        current_register["dtype"] = self._process("dtype", inputs.dtype)
        if log_device:
            current_register["device"] = self._process("device", inputs.device)

        if log_mean:
            fn = lambda: inputs.mean(
                dim=dim_mean,
            )
            current_register["mean"] = self._process("mean", fn)

        if log_std:
            fn = lambda: inputs.std(dim=dim_std)
            current_register["std"] = self._process("std", fn)

        if external_logs:
            old_print = self.do_print
            self.do_print = print_extended
            self._print("\n---[ External Logs ] ---")
            for log_fn, log_args in external_logs:
                if isinstance(log_args, Sequence) and not isinstance(log_args, str):
                    value = try_torch(log_fn, inputs, *log_args)
                elif isinstance(log_args, dict):
                    value = try_torch(log_fn, inputs, **log_args)
                elif log_args is None:
                    value = try_torch(log_fn, inputs)
                else:
                    value = try_torch(log_fn, inputs, log_args)

                results = self._process(log_fn, value)
                current_register[log_fn] = results
            self.do_print = old_print

        if target is not None:
            losses = get_losses(inputs, target, exclude_invalid_losses)
            started_ls = False
            if self.do_print:
                for loss, res in losses.items():
                    if isinstance(res, str):
                        continue
                    if not started_ls:
                        self._print("\n---[ Losses ] ---")
                        started_ls = True
                    self._print(f"{loss}: {res:.5f}")
            current_register["loss"] = losses

        if log_tensor:
            current_register["values"].append(
                self._process("Tensor", inputs, not print_extended)
            )

        self._print(self.end_with)
        self._store_item_and_update(current_register)
        return current_register

    def _store_item_and_update(self, current_register: Dict[str, Any]):
        self.stored_items.append(current_register.copy())
        self.stored_items = self.stored_items[-self.max_stored_items :]

    def _setup_tensor(self, itm):
        if isinstance(itm, (list, tuple)):
            try:
                itm = torch.tensor(itm)
            except:
                itm = torch.tensor(ff_list(itm))
        elif isinstance(itm, np.ndarray):
            itm = torch.from_numpy(itm)
        elif isinstance(itm, Tensor):
            itm = itm.detach().cpu()
        else:
            itm = None
        return itm


def set_seed(seed: int):
    """Set random seed for reproducibility."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if torch.mps.is_available():
        torch.mps.manual_seed(seed)
    if torch.xpu.is_available():
        torch.xpu.manual_seed_all(seed)


def count_parameters(model: nn.Module) -> int:
    """Returns total number of trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def freeze_all_except(model: nn.Module, except_layers: Optional[list[str]] = None):
    """Freezes all model parameters except specified layers."""
    no_exceptions = not except_layers
    for name, param in model.named_parameters():
        if no_exceptions:
            param.requires_grad_(False)
        elif any(layer in name for layer in except_layers):
            param.requires_grad_(False)


def freeze_selected_weights(model: nn.Module, target_layers: list[str]):
    """Freezes only parameters on specified layers."""
    for name, param in model.named_parameters():
        if any(layer in name for layer in target_layers):
            param.requires_grad_(False)


def unfreeze_all_except(model: nn.Module, except_layers: Optional[list[str]] = None):
    """Unfreezes all model parameters except specified layers."""
    no_exceptions = not except_layers
    for name, param in model.named_parameters():
        if no_exceptions:
            param.requires_grad_(True)
        elif not any(layer in name for layer in except_layers):
            param.requires_grad_(True)


def unfreeze_selected_weights(model: nn.Module, target_layers: list[str]):
    """Unfreezes only parameters on specified layers."""
    for name, param in model.named_parameters():
        if not any(layer in name for layer in target_layers):
            param.requires_grad_(True)


def clip_gradients(model: nn.Module, max_norm: float = 1.0):
    """Applies gradient clipping."""
    return nn.utils.clip_grad_norm_(model.parameters(), max_norm)


def detach_hidden(hidden):
    """Detaches hidden states (for RNNs)."""
    if isinstance(hidden, torch.Tensor):
        return hidden.detach()
    else:
        return tuple(detach_hidden(h) for h in hidden)


def one_hot(labels: torch.Tensor, num_classes: int) -> torch.Tensor:
    """One-hot encodes a tensor of labels."""
    return F.one_hot(labels, num_classes).float()


def safe_divide(a: torch.Tensor, b: torch.Tensor, eps: float = 1e-8):
    """Safe division for tensors (prevents divide-by-zero)."""
    return a / (b + eps)


def batch_pad(tensors: list[torch.Tensor], padding_value: float = 0.0) -> torch.Tensor:
    """Pads a list of tensors to the same shape (assumes 2D+ tensors)."""
    max_shape = [
        max(s[i] for s in [t.shape for t in tensors]) for i in range(tensors[0].dim())
    ]
    padded = []
    for t in tensors:
        pad_dims = [(0, m - s) for s, m in zip(t.shape, max_shape)]
        pad_flat = [p for pair in reversed(pad_dims) for p in pair]  # reverse for F.pad
        padded.append(F.pad(t, pad_flat, value=padding_value))
    return torch.stack(padded)


def sample_tensor(tensor: torch.Tensor, num_samples: int = 5):
    """Randomly samples values from tensor for preview."""
    flat = tensor.flatten()
    idx = torch.randperm(len(flat))[:num_samples]
    return flat[idx]


class TorchCacheUtils:
    cached_shortcuts: dict[str, Callable[[None], None]] = {}

    has_cuda: bool = torch.cuda.is_available()
    has_xpu: bool = torch.xpu.is_available()
    has_mps: bool = torch.mps.is_available()

    _ignore: list[str] = []

    def __init__(self):
        pass

    def _apply_clear(self, device: str):
        if device in self._ignore:
            gc.collect()
            return
        try:
            clear_fn = self.cached_shortcuts.get(
                device, getattr(torch, device).empty_cache
            )
            if device not in self.cached_shortcuts:
                self.cached_shortcuts.update({device: clear_fn})

        except Exception as e:
            print(e)
            self._ignore.append(device)

    def clear(self):
        gc.collect()
        if self.has_xpu:
            self._apply_clear("xpu")
        if self.has_cuda:
            self._apply_clear("cuda")
        if self.has_mps:
            self._apply_clear("mps")
        gc.collect()


_clear_cache_cls = TorchCacheUtils()


def clear_cache():
    _clear_cache_cls.clear()


@cache_wrapper
def default_device(idx: Optional[int] = None):
    try:
        if torch.cuda.is_available():
            return torch.device("cuda", idx)
        if torch.xpu.is_available():
            return torch.device("xpu", idx)
        if torch.mps.is_available():
            return torch.device("mps", idx)
        if hasattr(torch, "is_vulkan_available"):
            if getattr(torch, "is_vulkan_available")():
                return torch.device("vulkan", idx)
    except:
        pass
    finally:
        return torch.device(torch.zeros(1).device)


class Packing:
    """
    example:

    ```
    x_lengths = torch.tensor([5, 3, 6])
    x_padded = torch.randn(3, 6, 256)  # padded input [B, T, C]

    # 1. RNN expects packed input
    x_packed = Padding.pack_sequence(x_padded, x_lengths)
    output_packed, _ = rnn(x_packed)

    # 2. Recover padded for loss
    output = Padding.unpack_sequence(output_packed, total_length=x_padded.size(1))

    # 3. Mask for loss
    mask = torch.arange(x_padded.size(1))[None, :] < x_lengths[:, None]
    loss = (F.mse_loss(output, target, reduction="none") * mask.unsqueeze(-1)).sum() / mask.sum()
    ```
    """

    @staticmethod
    def pack_sequence(x: Tensor, lengths: Tensor):
        """
        Pack padded sequence for RNN/LSTM.
        Args:
            x (Tensor): Padded input [B, T, C]
            lengths (Tensor): Actual lengths [B]
        Returns:
            PackedSequence

        """
        return nn.utils.rnn.pack_padded_sequence(
            x,
            lengths.cpu().numpy(),
            batch_first=True,
            enforce_sorted=False,
        )

    @staticmethod
    def unpack_sequence(packed, total_length: int) -> Tensor:
        """Unpacks RNN PackedSequence to padded [B, T, C]."""
        output, _ = nn.utils.rnn.pad_packed_sequence(
            packed,
            batch_first=True,
            total_length=total_length,
        )
        return output


class Padding:

    @staticmethod
    def pad_to(x: Tensor, target_length: int, pad_value: float = 0.0) -> Tensor:
        """
        Pad input tensor along time axis (dim=1) to target length.
        Args:
            x (Tensor): Input tensor [B, T, C]
            target_length (int): Target time length
            pad_value (float): Fill value
        Returns:
            Padded tensor [B, target_length, C]
        """
        B, T, C = x.size()
        if T >= target_length:
            return x
        pad = x.new_full((B, target_length - T, C), pad_value)
        return torch.cat([x, pad], dim=1)

    @staticmethod
    def pad_sequence(
        inputs: Tensor,
        size: int,
        direction: Literal["left", "right"] = "left",
        pad_id: Union[int, float] = 0,
    ) -> Tensor:
        """
        Pads a single tensor to the specified size in 1D.
        Args:
            inputs (Tensor): Tensor of shape [T] or [B, T]
            size (int): Desired size along the last dimension
            direction (str): 'left' or 'right'
            pad_id (int): Value to pad with
        Returns:
            Padded tensor
        """
        total = size - inputs.shape[-1]
        if total < 1:
            return inputs
        pad_config = (total, 0) if direction == "left" else (0, total)
        return F.pad(inputs, pad_config, value=pad_id)

    @staticmethod
    def pad_batch_1d(
        batch: List[Tensor],
        pad_value: float = 0.0,
        pad_to_multiple: Optional[int] = None,
        direction: Literal["left", "right"] = "right",
    ) -> Tuple[Tensor, Tensor]:
        """
        Pad list of 1D tensors to same length with optional multiple alignment.
        Returns:
            Padded tensor [B, T], Lengths [B]
        """
        lengths = torch.tensor([t.size(0) for t in batch])
        max_len = lengths.max().item()

        if pad_to_multiple:
            max_len = (
                (max_len + pad_to_multiple - 1) // pad_to_multiple
            ) * pad_to_multiple

        padded = []
        for t in batch:
            padded.append(Padding.pad_sequence(t, max_len, direction, pad_value))
        return torch.stack(padded), lengths

    @staticmethod
    def pad_batch_2d(
        batch: List[Tensor],
        pad_value: float = 0.0,
        pad_to_multiple: Optional[int] = None,
        direction: Literal["left", "right"] = "right",
    ) -> Tuple[Tensor, Tensor]:
        """
        Pad list of 2D tensors (e.g. [T, D]) to same T.
        Returns:
            Padded tensor [B, T, D], Lengths [B]
        """
        lengths = torch.tensor([t.size(0) for t in batch])
        feat_dim = batch[0].size(1)
        max_len = lengths.max().item()

        if pad_to_multiple:
            max_len = (
                (max_len + pad_to_multiple - 1) // pad_to_multiple
            ) * pad_to_multiple

        padded = []
        for t in batch:
            pad_len = max_len - t.size(0)
            if direction == "left":
                pad_tensor = t.new_full((pad_len, feat_dim), pad_value)
                padded.append(torch.cat([pad_tensor, t], dim=0))
            else:
                pad_tensor = t.new_full((pad_len, feat_dim), pad_value)
                padded.append(torch.cat([t, pad_tensor], dim=0))
        return torch.stack(padded), lengths

    # --- Batching ---

    @staticmethod
    def pad_batch_1d(
        batch: List[Tensor],
        pad_value: float = 0.0,
        pad_to_multiple: Optional[int] = None,
        direction: Literal["left", "right"] = "right",
    ) -> Tuple[Tensor, Tensor]:
        """Pads list of 1D tensors → [B, T]"""
        lengths = torch.tensor([t.size(0) for t in batch])
        max_len = lengths.max().item()
        if pad_to_multiple:
            max_len = (
                (max_len + pad_to_multiple - 1) // pad_to_multiple
            ) * pad_to_multiple

        padded = [Padding.pad_sequence(t, max_len, direction, pad_value) for t in batch]
        return torch.stack(padded), lengths

    @staticmethod
    def pad_batch_2d(
        batch: List[Tensor],
        pad_value: float = 0.0,
        pad_to_multiple: Optional[int] = None,
        direction: Literal["left", "right"] = "right",
    ) -> Tuple[Tensor, Tensor]:
        """Pads list of 2D tensors [T, D] → [B, T, D]"""
        lengths = torch.tensor([t.size(0) for t in batch])
        feat_dim = batch[0].size(1)
        max_len = lengths.max().item()
        if pad_to_multiple:
            max_len = (
                (max_len + pad_to_multiple - 1) // pad_to_multiple
            ) * pad_to_multiple

        padded = []
        for t in batch:
            pad_len = max_len - t.size(0)
            pad_tensor = t.new_full((pad_len, feat_dim), pad_value)
            padded_tensor = (
                torch.cat([pad_tensor, t], dim=0)
                if direction == "left"
                else torch.cat([t, pad_tensor], dim=0)
            )
            padded.append(padded_tensor)
        return torch.stack(padded), lengths

    @staticmethod
    def pad_batch_nd(
        batch: List[Tensor],
        pad_value: float = 0.0,
        dim: int = 0,
        pad_to_multiple: Optional[int] = None,
    ) -> Tuple[Tensor, Tensor]:
        """
        General N-D padding along time axis (dim=0, usually).
        Handles shapes like:
            [T, C] → [B, T, C]
            [T, H, W] → [B, T, H, W]
        """
        lengths = torch.tensor([t.size(dim) for t in batch])
        max_len = lengths.max().item()
        if pad_to_multiple:
            max_len = (
                (max_len + pad_to_multiple - 1) // pad_to_multiple
            ) * pad_to_multiple

        padded = []
        for t in batch:
            pad_len = max_len - t.size(dim)
            pad_shape = list(t.shape)
            pad_shape[dim] = pad_len
            pad_tensor = t.new_full(pad_shape, pad_value)
            padded_tensor = torch.cat([t, pad_tensor], dim=dim)
            padded.append(padded_tensor)

        return torch.stack(padded), lengths


class Masking:

    @staticmethod
    def apply_mask(x: Tensor, mask: Tensor, fill_value: Number = 0) -> Tensor:
        """
        Apply a mask to a tensor, setting masked positions to `fill_value`.
        Args:
            x (Tensor): Input tensor of shape [..., T, D].
            mask (Tensor): Mask of shape [..., T] where True = masked.
            fill_value (Number): Value to fill masked positions with.
        Returns:
            Tensor: Masked tensor.
        """
        return x.masked_fill(mask.unsqueeze(-1), fill_value)

    @staticmethod
    def get_padding_mask(
        lengths: Optional[Tensor] = None,
        tokens: Optional[Tensor] = None,
        padding_id: int = 0,
    ) -> Tensor:
        """
        Generate a padding mask: 1 for real tokens, 0 for padding.
        Args:
            lengths (Tensor): Tensor of shape [B] with sequence lengths.
            tokens (Tensor): Tensor of shape [B, T] with token ids.
            padding_id (int): Padding token id (default=0).
        Returns:
            Tensor: Boolean mask of shape [B, T].
        """
        assert (
            tokens is not None or lengths is not None
        ), "Either tokens or lengths must be provided."

        if tokens is not None:
            return tokens != padding_id

        B = lengths.size(0)
        max_len = lengths.max().item()
        arange = torch.arange(max_len, device=lengths.device).unsqueeze(0).expand(B, -1)
        return arange < lengths.unsqueeze(1)

    @staticmethod
    def get_padding_mask_fps(lengths: Tensor) -> Tensor:
        """
        Legacy-style padding mask using 1-based comparison.
        """
        mask = (
            torch.arange(lengths.max(), device=lengths.device)
            .unsqueeze(0)
            .expand(lengths.shape[0], -1)
        )
        return (mask + 1) > lengths.unsqueeze(1)

    @staticmethod
    def get_causal_mask(
        size: Union[int, tuple[int, ...]],
        device: Optional[Union[str, torch.device]] = None,
    ) -> Tensor:
        """
        Generate a causal mask for self-attention.
        Args:
            size (int or tuple): Size (T) or (1, T, T)
        Returns:
            Tensor: [1, T, T] boolean causal mask
        """
        if isinstance(size, int):
            size = (1, size, size)
        return torch.tril(torch.ones(size, dtype=torch.bool, device=device))

    @staticmethod
    def combine_masks(pad_mask: Tensor, causal_mask: Tensor) -> Tensor:
        """
        Combine padding and causal masks.
        Args:
            pad_mask (Tensor): [B, T] padding mask
            causal_mask (Tensor): [1, T, T] causal mask
        Returns:
            Tensor: [B, T, T] combined mask
        """
        return (
            causal_mask & pad_mask.unsqueeze(1).expand(-1, pad_mask.size(1), -1).bool()
        )
