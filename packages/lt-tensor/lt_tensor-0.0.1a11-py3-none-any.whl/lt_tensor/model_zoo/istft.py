from ..torch_commons import *
from ..model_base import Model
from .rsd import ResBlocks
from ..misc_utils import log_tensor

import torch.nn.functional as F


class Generator(Model):
    """Based on the adaptation made by from Rishikesh
    A Generator for audio processing, can be usd for tother things."""

    def __init__(
        self,
        in_channels: int = 80,
        upsample_rates: List[Union[int, List[int]]] = [8, 8],
        upsample_kernel_sizes: List[Union[int, List[int]]] = [16, 16],
        upsample_initial_channel: int = 512,
        resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11],
        resblock_dilation_sizes: List[Union[int, List[int]]] = [
            [1, 3, 5],
            [1, 3, 5],
            [1, 3, 5],
        ],
        n_fft: int = 16,
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super().__init__()
        self.num_kernels = len(resblock_kernel_sizes)
        self.num_upsamples = len(upsample_rates)
        self.conv_pre = weight_norm(
            nn.Conv1d(in_channels, upsample_initial_channel, 7, 1, padding=3)
        )
        self.blocks = nn.ModuleList()
        self.activation = activation
        for i, (u, k) in enumerate(zip(upsample_rates, upsample_kernel_sizes)):
            self.blocks.append(
                self._make_blocks(
                    (i, k, u),
                    upsample_initial_channel,
                    resblock_kernel_sizes,
                    resblock_dilation_sizes,
                )
            )

        ch = upsample_initial_channel // (2 ** (i + 1))
        self.post_n_fft = n_fft // 2 + 1
        self.conv_post = weight_norm(nn.Conv1d(ch, n_fft + 2, 7, 1, padding=3))
        self.conv_post.apply(self.init_weights)
        self.reflection_pad = torch.nn.ReflectionPad1d((1, 0))

    def _make_blocks(
        self,
        state: Tuple[int, int, int],
        upsample_initial_channel: int,
        resblock_kernel_sizes: List[Union[int, List[int]]],
        resblock_dilation_sizes: List[int | List[int]],
    ):
        i, k, u = state
        channels = upsample_initial_channel // (2 ** (i + 1))
        return nn.ModuleDict(
            dict(
                up=nn.Sequential(
                    self.activation,
                    weight_norm(
                        nn.ConvTranspose1d(
                            upsample_initial_channel // (2**i),
                            channels,
                            k,
                            u,
                            padding=(k - u) // 2,
                        )
                    ),
                ),
                residual=ResBlocks(
                    channels,
                    resblock_kernel_sizes,
                    resblock_dilation_sizes,
                    self.activation,
                ),
            )
        )

    def forward(self, x):
        x = self.conv_pre(x)
        for block in self.blocks:
            x = block["up"](x)
            x = block["residual"](x)

        x = self.reflection_pad(x)
        x = self.conv_post(x)
        spec = torch.exp(x[:, : self.post_n_fft, :])
        phase = torch.sin(x[:, self.post_n_fft :, :])

        return spec, phase

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
