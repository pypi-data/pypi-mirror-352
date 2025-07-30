__all__ = [
    "spectral_norm_select",
    "get_weight_norm",
    "ResBlock1D",
    "ResBlock2D",
]
from lt_utils.common import *
from lt_tensor.torch_commons import *
from lt_tensor.model_base import Model
from lt_tensor.misc_utils import log_tensor
import math


def spectral_norm_select(module: nn.Module, enabled: bool):
    if enabled:
        return spectral_norm(module)
    return module


def get_weight_norm(norm_type: Optional[Literal["weight", "spectral"]] = None):
    if not norm_type:
        return lambda x: x
    if norm_type == "weight":
        return lambda x: weight_norm(x)
    return lambda x: spectral_norm(x)


class ConvNets(Model):

    def remove_weight_norm(self):
        for module in self.modules():
            try:
                remove_weight_norm(module)
            except ValueError:
                pass

    @staticmethod
    def init_weights(m, mean=0.0, std=0.01):
        classname = m.__class__.__name__
        if "Conv" in classname:
            m.weight.data.normal_(mean, std)


class ResBlock1D(ConvNets):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3, 5),
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super(ResBlock1D, self).__init__()
        self.convs = nn.ModuleList(
            [
                self._get_conv_layer(i, channels, kernel_size, 1, dilation, activation)
                for i in range(3)
            ]
        )
        self.convs.apply(self.init_weights)

    def _get_conv_layer(self, id, ch, k, stride, d, actv):
        get_padding = lambda ks, d: int((ks * d - d) / 2)
        return nn.Sequential(
            actv,  # 1
            weight_norm(
                nn.Conv1d(
                    ch, ch, k, stride, dilation=d[id], padding=get_padding(k, d[id])
                )
            ),  # 2
            actv,  # 3
            weight_norm(
                nn.Conv1d(ch, ch, k, stride, dilation=1, padding=get_padding(k, 1))
            ),  # 4
        )

    def forward(self, x: torch.Tensor):
        for cnn in self.convs:
            x = cnn(x) + x
        return x


class ResBlock2D(Model):
    def __init__(
        self,
        in_channels,
        out_channels,
        downsample=False,
    ):
        super().__init__()
        stride = 2 if downsample else 1

        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, stride, 1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(out_channels, out_channels, 3, 1, 1),
        )

        self.skip = nn.Identity()
        if downsample or in_channels != out_channels:
            self.skip = spectral_norm_select(
                nn.Conv2d(in_channels, out_channels, 1, stride)
            )
        # on less to be handled every cicle
        self.sqrt_2 = math.sqrt(2)

    def forward(self, x):
        return (self.block(x) + self.skip(x)) / self.sqrt_2
