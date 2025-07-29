__all__ = [
    "spectral_norm_select",
    "ResBlock1D_BT",
    "ResBlock1D",
    "ResBlock2D",
    "ResBlocks",
]
from lt_utils.common import *
from ..torch_commons import *
from ..model_base import Model
import math
from ..misc_utils import log_tensor


def spectral_norm_select(module: nn.Module, enabled: bool):
    if enabled:
        return spectral_norm(module)
    return module


class ResBlock1D_BT(Model):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        dilation: Union[Sequence[int], int] = (1, 3, 5),
        activation: nn.Module = nn.LeakyReLU(0.1),
        num_groups: int = 1,
        batched: bool = True,
    ):
        super().__init__()
        self.conv = nn.ModuleList()
        if isinstance(dilation, int):
            dilation = [dilation]

        if batched:
            layernorm_fn = lambda x: nn.GroupNorm(num_groups=num_groups, num_channels=x)
        else:
            layernorm_fn = lambda x: nn.LayerNorm(normalized_shape=x)
        for i, dil in enumerate(dilation):

            self.conv.append(
                nn.ModuleDict(
                    dict(
                        net=nn.Sequential(
                            self._get_conv_layer(
                                in_channels, in_channels, kernel_size, dil
                            ),
                            activation,
                            self._get_conv_layer(
                                in_channels, in_channels, kernel_size, 1, True
                            ),
                            activation,
                        ),
                        l_norm=layernorm_fn(in_channels),
                    )
                )
            )
        self.final = nn.Sequential(
            self._get_conv_layer(in_channels, out_channels, kernel_size, 1, True),
            activation,
        )
        self.conv.apply(self.init_weights)

    def _get_conv_layer(
        self,
        channels_in: int,
        channels_out: int,
        kernel_size: int,
        dilation: int,
        pad_gate: bool = False,
    ):
        return weight_norm(
            nn.Conv1d(
                in_channels=channels_in,
                out_channels=channels_out,
                kernel_size=kernel_size,
                stride=1,
                dilation=dilation,
                padding=(
                    int((kernel_size * dilation - dilation) / 2)
                    if not pad_gate
                    else int((kernel_size * 1 - 1) / 2)
                ),
            )
        )

    def forward(self, x: Tensor):
        for i, layer in enumerate(self.conv):
            xt = layer["net"](x)
            x = xt + x
            x = layer["l_norm"](x)
        return self.final(x)

    def remove_weight_norm(self):
        for module in self.modules():
            try:
                remove_weight_norm(module)
            except ValueError:
                pass  # Not normed, skip

    @staticmethod
    def init_weights(m, mean=0.0, std=0.01):
        classname = m.__class__.__name__
        if "Conv" in classname:
            m.weight.data.normal_(mean, std)


class ResBlock1D(Model):
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

    def remove_weight_norm(self):
        for module in self.modules():
            try:
                remove_weight_norm(module)
            except ValueError:
                pass  # Not normed, skip

    @staticmethod
    def init_weights(m, mean=0.0, std=0.01):
        classname = m.__class__.__name__
        if "Conv" in classname:
            m.weight.data.normal_(mean, std)


class ResBlocks(Model):
    def __init__(
        self,
        channels: int,
        resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11],
        resblock_dilation_sizes: List[Union[int, List[int]]] = [
            [1, 3, 5],
            [1, 3, 5],
            [1, 3, 5],
        ],
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super().__init__()
        self.num_kernels = len(resblock_kernel_sizes)
        self.rb = nn.ModuleList()
        self.activation = activation

        for k, j in zip(resblock_kernel_sizes, resblock_dilation_sizes):
            self.rb.append(ResBlock1D(channels, k, j, activation))

        self.rb.apply(self.init_weights)

    def forward(self, x: torch.Tensor):
        xs = None
        for i, block in enumerate(self.rb):
            if i == 0:
                xs = block(x)
            else:
                xs += block(x)
        x = xs / self.num_kernels
        return self.activation(x)

    def remove_weight_norm(self):
        for module in self.modules():
            try:
                remove_weight_norm(module)
            except ValueError:
                pass  # Not normed, skip

    @staticmethod
    def init_weights(m, mean=0.0, std=0.01):
        classname = m.__class__.__name__
        if "Conv" in classname:
            m.weight.data.normal_(mean, std)


class ResBlock2D(Model):
    def __init__(
        self,
        in_channels,
        out_channels,
        downsample=False,
        spec_norm: bool = False,
    ):
        super().__init__()
        stride = 2 if downsample else 1

        self.block = nn.Sequential(
            spectral_norm_select(
                nn.Conv2d(in_channels, out_channels, 3, stride, 1), spec_norm
            ),
            nn.LeakyReLU(0.2),
            spectral_norm_select(
                nn.Conv2d(out_channels, out_channels, 3, 1, 1), spec_norm
            ),
        )

        self.skip = nn.Identity()
        if downsample or in_channels != out_channels:
            self.skip = spectral_norm_select(
                nn.Conv2d(in_channels, out_channels, 1, stride), spec_norm
            )
        # on less to be handled every cicle
        self.sqrt_2 = math.sqrt(2)

    def forward(self, x):
        return (self.block(x) + self.skip(x)) / self.sqrt_2
