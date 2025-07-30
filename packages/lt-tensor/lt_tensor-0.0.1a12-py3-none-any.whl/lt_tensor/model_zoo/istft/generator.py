__all__ = ["iSTFTGenerator", "ResBlocks"]
import gc
import math
import itertools
from lt_utils.common import *
from lt_tensor.torch_commons import *
from lt_tensor.model_base import Model
from lt_tensor.misc_utils import log_tensor
from lt_tensor.model_zoo.rsd import ResBlock1D, ConvNets, get_weight_norm
from lt_utils.misc_utils import log_traceback
from lt_tensor.processors import AudioProcessor
from lt_utils.type_utils import is_dir, is_pathlike
from lt_tensor.misc_utils import set_seed, clear_cache
from lt_tensor.model_zoo.disc import MultiPeriodDiscriminator, MultiScaleDiscriminator
import torch.nn.functional as F
from lt_tensor.config_templates import updateDict, ModelConfig


class ResBlocks(ConvNets):
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


class iSTFTGenerator(ConvNets):
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
        hop_length: int = 256,
    ):
        super().__init__()
        self.num_kernels = len(resblock_kernel_sizes)
        self.num_upsamples = len(upsample_rates)
        self.hop_length = hop_length
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
        self.reflection_pad = nn.ReflectionPad1d((1, 0))

        self.phase = nn.Sequential(
            nn.LeakyReLU(0.2),
            nn.Conv1d(self.post_n_fft, self.post_n_fft, kernel_size=3, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(self.post_n_fft, self.post_n_fft, kernel_size=3, padding=1),
        )
        self.spec = nn.Sequential(
            nn.LeakyReLU(0.2),
            nn.Conv1d(self.post_n_fft, self.post_n_fft, kernel_size=3, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(self.post_n_fft, self.post_n_fft, kernel_size=3, padding=1),
        )

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
                    ).apply(self.init_weights),
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
        spec = torch.exp(self.spec(x[:, : self.post_n_fft, :]))
        phase = torch.sin(self.phase(x[:, self.post_n_fft :, :]))

        return spec, phase
