__all__ = ["Model", "_ModelExtended", "LossTracker"]

import gc
import json
import math
import warnings
from .torch_commons import *
from lt_utils.common import *
from lt_utils.misc_utils import log_traceback, get_current_time

T = TypeVar("T")

ROOT_DEVICE = torch.zeros(1).device

POSSIBLE_OUTPUT_TYPES: TypeAlias = Union[
    Tensor,
    Sequence[Tensor],
    Dict[Union[str, Tensor, Any], Union[Sequence[Tensor], Tensor, Any]],
]


class LossTracker:
    last_file = f"logs/history_{get_current_time()}.json"

    def __init__(self, max_len=50_000):
        self.max_len = max_len
        self.history = {
            "train": [],
            "eval": [],
        }

    def append(self, loss: float, mode: Literal["train", "eval"] = "train"):
        assert mode in self.history, f"Invalid mode '{mode}'. Use 'train' or 'eval'."
        self.history[mode].append(float(loss))
        if len(self.history[mode]) > self.max_len:
            self.history[mode] = self.history[mode][-self.max_len :]

    def get(self, mode: Literal["train", "eval"] = "train"):
        return self.history.get(mode, [])

    def save(self, path: Optional[PathLike] = None):
        if path is None:
            path = f"logs/history_{get_current_time()}.json"

        Path(path).parent.mkdir(exist_ok=True, parents=True)
        with open(path, "w") as f:
            json.dump(self.history, f, indent=2)

        self.last_file = path

    def load(self, path: Optional[PathLike] = None):
        if path is None:
            _path = self.last_file
        else:
            _path = path
        with open(_path) as f:
            self.history = json.load(f)
        if path is not None:
            self.last_file = path

    def plot(self, backend: Literal["matplotlib", "plotly"] = "plotly"):
        if backend == "plotly":
            try:
                import plotly.graph_objs as go
            except ModuleNotFoundError:
                warnings.warn(
                    "No installation of plotly was found. To use it use 'pip install plotly' and restart this application!"
                )
                return
            fig = go.Figure()
            for mode, losses in self.history.items():
                if losses:
                    fig.add_trace(go.Scatter(y=losses, name=mode.capitalize()))
            fig.update_layout(
                title="Training vs Evaluation Loss",
                xaxis_title="Step",
                yaxis_title="Loss",
                template="plotly_dark",
            )
            fig.show()

        elif backend == "matplotlib":
            import matplotlib.pyplot as plt

            for mode, losses in self.history.items():
                if losses:
                    plt.plot(losses, label=f"{mode.capitalize()} Loss")
            plt.title("Loss over Time")
            plt.xlabel("Step")
            plt.ylabel("Loss")
            plt.legend()
            plt.grid(True)
            plt.show()


class Model(nn.Module, ABC):
    """
    This makes it easier to assign a device and retrieves it later
    """

    _device: torch.device = ROOT_DEVICE
    _autocast: bool = False
    _loss_history: LossTracker = LossTracker(100_000)
    _is_unfrozen: bool = False

    @property
    def autocast(self):
        return self._autocast

    @autocast.setter
    def autocast(self, value: bool):
        self._autocast = value

    @property
    def device(self):
        return self._device

    @device.setter
    def device(self, device: Union[torch.device, str]):
        assert isinstance(device, (str, torch.device))
        self._device = torch.device(device) if isinstance(device, str) else device
        self._apply_device_to()

    def _apply_device_to(self):
        """Add here components that are needed to have device applied to them,
        that usually the '.to()' function fails to apply

        example:
        ```
        def _apply_device_to(self):
            self.my_tensor = self.my_tensor.to(device=self.device)
        ```
        """
        pass

    def freeze_weight(self, weight: Union[str, nn.Module], freeze: bool):
        assert isinstance(weight, (str, nn.Module))
        if isinstance(weight, str):
            if hasattr(self, weight):
                w = getattr(self, weight)
                if isinstance(w, nn.Module):

                    w.requires_grad_(not freeze)
        else:
            weight.requires_grad_(not freeze)

    def _freeze_unfreeze(
        self,
        weight: Union[str, nn.Module],
        task: Literal["freeze", "unfreeze"] = "freeze",
        _skip_except: bool = False,
    ):
        try:
            assert isinstance(weight, (str, nn.Module))
            if isinstance(weight, str):
                w_txt = f"Failed to {task} the module '{weight}'. Reason: is not a valid attribute of {self._get_name()}"
                if hasattr(self, weight):
                    w_txt = f"Failed to {task} the module '{weight}'. Reason: is not a Module type."
                    w = getattr(self, weight)
                    if isinstance(w, nn.Module):
                        w_txt = f"Successfully {task} the module '{weight}'."
                        w.requires_grad_(task == "unfreeze")

            else:
                w.requires_grad_(task == "unfreeze")
                w_txt = f"Successfully '{task}' the module '{weight}'."
            return w_txt
        except Exception as e:
            if not _skip_except:
                raise e
            return str(e)

    def freeze_weight(
        self,
        weight: Union[str, nn.Module],
        _skip_except: bool = False,
    ):
        return self._freeze_unfreeze(weight, "freeze", _skip_except)

    def unfreeze_weight(
        self,
        weight: Union[str, nn.Module],
        _skip_except: bool = False,
    ):
        return self._freeze_unfreeze(weight, "freeze", _skip_except)

    def freeze_all(self, exclude: Optional[List[str]] = None):
        no_exclusions = not exclude
        frozen = []
        not_frozen = []
        for name, param in self.named_parameters():
            if no_exclusions:
                try:
                    if param.requires_grad:
                        param.requires_grad_(False)
                        frozen.append(name)
                    else:
                        not_frozen.append((name, "was_frozen"))
                except Exception as e:
                    not_frozen.append((name, str(e)))
            elif any(layer in name for layer in exclude):
                try:
                    if param.requires_grad:
                        param.requires_grad_(False)
                        frozen.append(name)
                    else:
                        not_frozen.append((name, "was_frozen"))
                except Exception as e:
                    not_frozen.append((name, str(e)))
            else:
                not_frozen.append((name, "excluded"))
        return dict(frozen=frozen, not_frozen=not_frozen)

    def unfreeze_all(self, exclude: Optional[list[str]] = None):
        """Unfreezes all model parameters except specified layers."""
        no_exclusions = not exclude
        unfrozen = []
        not_unfrozen = []
        for name, param in self.named_parameters():
            if no_exclusions:
                try:
                    if not param.requires_grad:
                        param.requires_grad_(True)
                        unfrozen.append(name)
                    else:
                        not_unfrozen.append((name, "was_unfrozen"))
                except Exception as e:
                    not_unfrozen.append((name, str(e)))
            elif any(layer in name for layer in exclude):
                try:
                    if not param.requires_grad:
                        param.requires_grad_(True)
                        unfrozen.append(name)
                    else:
                        not_unfrozen.append((name, "was_unfrozen"))
                except Exception as e:
                    not_unfrozen.append((name, str(e)))
            else:
                not_unfrozen.append((name, "excluded"))
        return dict(unfrozen=unfrozen, not_unfrozen=not_unfrozen)

    def to(self, *args, **kwargs):
        device, dtype, non_blocking, convert_to_format = torch._C._nn._parse_to(
            *args, **kwargs
        )

        if dtype is not None:
            if not (dtype.is_floating_point or dtype.is_complex):
                raise TypeError(
                    "nn.Module.to only accepts floating point or complex "
                    f"dtypes, but got desired dtype={dtype}"
                )
            if dtype.is_complex:
                warnings.warn(
                    "Complex modules are a new feature under active development whose design may change, "
                    "and some modules might not work as expected when using complex tensors as parameters or buffers. "
                    "Please file an issue at https://github.com/pytorch/pytorch/issues/new?template=bug-report.yml "
                    "if a complex module does not work as expected."
                )

        def convert(t: Tensor):
            try:
                if convert_to_format is not None and t.dim() in (4, 5):
                    return t.to(
                        device,
                        dtype if t.is_floating_point() or t.is_complex() else None,
                        non_blocking,
                        memory_format=convert_to_format,
                    )
                return t.to(
                    device,
                    dtype if t.is_floating_point() or t.is_complex() else None,
                    non_blocking,
                )
            except NotImplementedError as e:
                if str(e) == "Cannot copy out of meta tensor; no data!":
                    raise NotImplementedError(
                        f"{e} Please use torch.nn.Module.to_empty() instead of torch.nn.Module.to() "
                        f"when moving module from meta to a different device."
                    ) from None
                else:
                    raise

        self._apply(convert)
        self.device = device
        self._apply_device_to()
        return self

    def ipu(self, device: Optional[Union[int, torch.device]] = None) -> T:
        super().ipu(device)
        dvc = "ipu"
        if device is not None:
            dvc += (
                ":" + str(device) if isinstance(device, (int, float)) else device.index
            )
        self.device = dvc
        self._apply_device_to()
        return self

    def xpu(self, device: Optional[Union[int, torch.device]] = None) -> T:
        super().xpu(device)
        dvc = "xpu"
        if device is not None:
            dvc += (
                ":" + str(device) if isinstance(device, (int, float)) else device.index
            )
        self.device = dvc
        self._apply_device_to()
        return self

    def cuda(self, device: Optional[Union[int, torch.device]] = None) -> T:
        super().cuda(device)
        dvc = "cuda"
        if device is not None:
            dvc += (
                ":" + str(device) if isinstance(device, (int, float)) else device.index
            )
        self.device = dvc
        self._apply_device_to()
        return self

    def mtia(self, device: Optional[Union[int, torch.device]] = None) -> T:
        super().mtia(device)
        dvc = "mtia"
        if device is not None:
            dvc += (
                ":" + str(device) if isinstance(device, (int, float)) else device.index
            )
        self.device = dvc
        self._apply_device_to()
        return self

    def cpu(self) -> T:
        super().cpu()
        self.device = "cpu"
        self._apply_device_to()
        return self

    def count_trainable_parameters(self, module_name: Optional[str] = None):
        """Gets the number of trainable parameters from either the entire model or from a specific module."""
        if module_name is not None:
            assert hasattr(self, module_name), f"Module {module_name} does not exits"
            module = getattr(self, module_name)
            return sum(
                [
                    x.numel()
                    for x in module.parameters()
                    if hasattr(x, "requires_grad") and x.requires_grad
                ]
            )
        return sum(
            [
                x.numel()
                for x in self.parameters()
                if hasattr(x, "requires_grad") and x.requires_grad
            ]
        )

    def count_non_trainable_parameters(self, module_name: Optional[str] = None):
        """Gets the number of non-trainable parameters from either the entire model or from a specific module."""
        if module_name is not None:
            assert hasattr(self, module_name), f"Module {module_name} does not exits"
            module = getattr(self, module_name)
            return sum(
                [
                    x.numel()
                    for x in module.parameters()
                    if not hasattr(x, "requires_grad") or not x.requires_grad
                ]
            )
        return sum(
            [
                x.numel()
                for x in self.parameters()
                if not hasattr(x, "requires_grad") or not x.requires_grad
            ]
        )

    def get_weights(self, module_name: Optional[str] = None) -> List[Tensor]:
        """Returns the weights of the model entry model or from a specified module"""
        if module_name is not None:
            assert hasattr(self, module_name), f"Module {module_name} does not exits"
            module = getattr(self, module_name)
            params = []
            if isinstance(module, nn.Module):
                return [x.data.detach() for x in module.parameters()]
            elif isinstance(module, (Tensor, nn.Parameter)):
                return [module.data.detach()]
            raise (f"{module_name} is has no weights")
        return [x.data.detach() for x in self.parameters()]

    def print_trainable_parameters(
        self, module_name: Optional[str] = None
    ) -> List[Tensor]:
        params = format(self.count_trainable_parameters(module_name), ",").replace(
            ",", "."
        )
        if module_name:
            print(f'Trainable Parameters from "{module_name}": {params}')
        else:
            print(f"Trainable Parameters: {params}")

    def print_non_trainable_parameters(
        self, module_name: Optional[str] = None
    ) -> List[Tensor]:
        params = format(self.count_non_trainable_parameters(module_name), ",").replace(
            ",", "."
        )
        if module_name:
            print(f'Non-Trainable Parameters from "{module_name}": {params}')
        else:
            print(f"Non-Trainable Parameters: {params}")

    def save_weights(
        self,
        path: Union[Path, str],
        replace: bool = False,
    ):
        path = Path(path)
        model_dir = path
        if path.exists():
            if path.is_dir():
                model_dir = Path(path, f"model_{get_current_time()}.pt")
            elif path.is_file():
                if replace:
                    path.unlink()
                else:
                    model_dir = Path(path.parent, f"model_{get_current_time()}.pt")
        else:
            if not "." in str(path):
                model_dir = Path(path, f"model_{get_current_time()}.pt")
        path.parent.mkdir(exist_ok=True, parents=True)
        torch.save(obj=self.state_dict(), f=str(model_dir))

    def load_weights(
        self,
        path: Union[Path, str],
        raise_if_not_exists: bool = False,
        strict: bool = True,
        assign: bool = False,
        weights_only: bool = False,
        mmap: Optional[bool] = None,
        **torch_loader_kwargs,
    ):
        path = Path(path)
        if not path.exists():
            assert not raise_if_not_exists, "Path does not exists!"
            return None
        if path.is_dir():
            possible_files = list(Path(path).rglob("*.pt"))
            assert (
                possible_files or not raise_if_not_exists
            ), "No model could be found in the given path!"
            if not possible_files:
                return None
            path = sorted(possible_files)[-1]
        state_dict = torch.load(
            str(path), weights_only=weights_only, mmap=mmap, **torch_loader_kwargs
        )
        incompatible_keys = self.load_state_dict(
            state_dict,
            strict=strict,
            assign=assign,
        )
        return incompatible_keys

    @torch.no_grad()
    def inference(self, *args, **kwargs):
        if self.training:
            self.eval()
        return self(*args, **kwargs)

    def train_step(
        self,
        *inputs,
        **kwargs,
    ):
        """Train Step"""
        if not self.training:
            self.train()
        return self(*inputs, **kwargs)

    def __call__(self, *args, **kwds) -> POSSIBLE_OUTPUT_TYPES:
        if self.autocast and not self.training:
            with torch.autocast(device_type=self.device.type):
                return super().__call__(*args, **kwds)
        else:
            return super().__call__(*args, **kwds)

    @abstractmethod
    def forward(
        self, *args, **kwargs
    ) -> Union[Tensor, Sequence[Tensor], Dict[Any, Union[Any, Tensor]]]:
        pass

    def add_loss(
        self, loss: Union[float, list[float]], mode: Literal["train", "eval"] = "train"
    ):
        if isinstance(loss, Number) and loss:
            self._loss_history.append(loss, mode)
        elif isinstance(loss, (list, tuple)):
            if loss:
                self._loss_history.append(sum(loss) / len(loss), mode=mode)
        elif isinstance(loss, Tensor):
            try:
                self._loss_history.append(loss.detach().flatten().mean().item())
            except Exception as e:
                log_traceback(e, "add_loss - Tensor")

    def save_loss_history(self, path: Optional[PathLike] = None):
        self._loss_history.save(path)

    def load_loss_history(self, path: Optional[PathLike] = None):
        self._loss_history.load(path)

    def get_loss_avg(self, mode: Literal["train", "eval"], quantity: int = 0):
        t_list = self._loss_history.get("train")
        if not t_list:
            return float("nan")
        if quantity > 0:
            t_list = t_list[-quantity:]
        return sum(t_list) / len(t_list)

    def freeze_unfreeze_loss(
        self,
        losses: Optional[Union[float, List[float]]] = None,
        trigger_loss: float = 0.1,
        excluded_modules: Optional[List[str]] = None,
        eval_last: int = 1000,
    ):
        """If a certain threshold is reached the weights will freeze or unfreeze the modules.
        the biggest use-case for this function is when training GANs where the balance
        from the discriminator and generator must be kept.

        Args:
            losses (Union[float, List[float]], Optional): The loss value or a list of losses that will be used to determine if it has reached or not the threshold. Defaults to None.
            trigger_loss (float, optional): The value where the weights will be either freeze or unfreeze. Defaults to 0.1.
            excluded_modules (list[str], optional): The list of modules (names) that is not to be changed by either freezing nor unfreezing. Defaults to None.
            eval_last (float, optional): The number of previous losses to be locked behind to calculate the current averange. Default to 1000.

        returns:
            bool: True when its frozen and false when its trainable.
        """
        if losses is not None:
            calculated = None
            self.add_loss(losses)

        value = self.get_loss_avg("train", eval_last)

        if value <= trigger_loss:
            if self._is_unfrozen:
                self.freeze_all(excluded_modules)
                self._is_unfrozen = False
            return True
        else:
            if not self._is_unfrozen:
                self.unfreeze_all(excluded_modules)
                self._is_unfrozen = True
            return False


class _ModelExtended(Model):
    """Planed, but not ready, maybe in the near future?"""
    criterion: Optional[Callable[[Tensor, Tensor], Tensor]] = None
    optimizer: Optional[optim.Optimizer] = None

    def train_step(
        self,
        *inputs,
        loss_label: Optional[Tensor] = None,
        **kwargs,
    ):
        if not self.training:
            self.train()
        if self.optimizer is not None:
            self.optimizer.zero_grad()
        if self.autocast:
            if self.criterion is None:
                raise RuntimeError(
                    "To use autocast during training, you must assign a criterion first!"
                )
            with torch.autocast(device_type=self.device.type):
                out = self.forward(*loss_label, **kwargs)
                loss = self.criterion(out, loss_label)

            if self.optimizer is not None:
                loss.backward()
                self.optimizer.step()
            return loss
        elif self.criterion is not None:
            out = self.forward(*loss_label, **kwargs)
            loss = self.criterion(out, loss_label)
            if self.optimizer is not None:
                loss.backward()
                self.optimizer.step()
            return loss
        else:
            return self(*inputs, **kwargs)
