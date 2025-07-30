from lt_tensor.torch_commons import *
import torch.nn.functional as F
from lt_tensor.model_base import Model
from lt_utils.common import *


class PeriodDiscriminator(Model):
    def __init__(
        self,
        period: int,
        use_spectral_norm=False,
        kernel_size: int = 5,
        stride: int = 3,
    ):
        super().__init__()
        self.period = period
        self.stride = stride
        self.kernel_size = kernel_size
        self.norm_f = weight_norm if use_spectral_norm == False else spectral_norm

        self.channels = [32, 128, 512, 1024, 1024]
        self.first_pass = nn.Sequential(
            self.norm_f(
                nn.Conv2d(
                    1, self.channels[0], (kernel_size, 1), (stride, 1), padding=(2, 0)
                )
            ),
            nn.LeakyReLU(0.1),
        )

        self.convs = nn.ModuleList(
            [
                self._get_next(self.channels[i + 1], self.channels[i], i == 3)
                for i in range(4)
            ]
        )

        self.post_conv = nn.Conv2d(1024, 1, (stride, 1), 1, padding=(1, 0))

    def _get_next(self, out_dim: int, last_in: int, is_last: bool = False):
        stride = (self.stride, 1) if not is_last else 1

        return nn.Sequential(
            self.norm_f(
                nn.Conv2d(
                    last_in,
                    out_dim,
                    (self.kernel_size, 1),
                    stride,
                    padding=(2, 0),
                )
            ),
            nn.LeakyReLU(0.1),
        )

    def forward(self, x: torch.Tensor):
        """
        x: (B, T)
        """
        b, t = x.shape
        if t % self.period != 0:
            pad_len = self.period - (t % self.period)
            x = F.pad(x, (0, pad_len), mode="reflect")
            t = t + pad_len

        x = x.view(b, 1, t // self.period, self.period)  # (B, 1, T//P, P)

        f_map = []
        x = self.first_pass(x)
        f_map.append(x)
        for conv in self.convs:
            x = conv(x)
            f_map.append(x)
        x = self.post_conv(x)
        f_map.append(x)
        return x.flatten(1, -1), f_map


class ScaleDiscriminator(nn.Module):
    def __init__(self, use_spectral_norm=False):
        super().__init__()
        norm_f = weight_norm if use_spectral_norm == False else spectral_norm
        self.activation = nn.LeakyReLU(0.1)
        self.convs = nn.ModuleList(
            [
                norm_f(nn.Conv1d(1, 128, 15, 1, padding=7)),
                norm_f(nn.Conv1d(128, 128, 41, 2, groups=4, padding=20)),
                norm_f(nn.Conv1d(128, 256, 41, 2, groups=16, padding=20)),
                norm_f(nn.Conv1d(256, 512, 41, 4, groups=16, padding=20)),
                norm_f(nn.Conv1d(512, 1024, 41, 4, groups=16, padding=20)),
                norm_f(nn.Conv1d(1024, 1024, 41, 1, groups=16, padding=20)),
                norm_f(nn.Conv1d(1024, 1024, 5, 1, padding=2)),
            ]
        )
        self.post_conv = norm_f(nn.Conv1d(1024, 1, 3, 1, padding=1))

    def forward(self, x: torch.Tensor):
        """
        x: (B, T)
        """
        f_map = []
        x = x.unsqueeze(1)  # (B, 1, T)
        for conv in self.convs:
            x = self.activation(conv(x))
            f_map.append(x)
        x = self.post_conv(x)
        f_map.append(x)
        return x.flatten(1, -1), f_map


class MultiScaleDiscriminator(Model):
    def __init__(self, layers: int = 3):
        super().__init__()
        self.pooling = nn.AvgPool1d(4, 2, padding=2)
        self.discriminators = nn.ModuleList(
            [ScaleDiscriminator(i == 0) for i in range(layers)]
        )

    def forward(self, x: torch.Tensor):
        """
        x: (B, T)
        Returns: list of outputs from each scale discriminator
        """
        outputs = []
        features = []
        for i, d in enumerate(self.discriminators):
            if i != 0:
                x = self.pooling(x)
            out, f_map = d(x)
            outputs.append(out)
            features.append(f_map)
        return outputs, features


class MultiPeriodDiscriminator(Model):
    def __init__(self, periods: List[int] = [2, 3, 5, 7, 11]):
        super().__init__()
        self.discriminators = nn.ModuleList([PeriodDiscriminator(p) for p in periods])

    def forward(self, x: torch.Tensor):
        """
        x: (B, T)
        Returns: list of tuples of outputs from each period discriminator and the f_map.
        """
        # torch.log(torch.clip(x, min=clip_val))
        out_map = []
        feat_map = []
        for d in self.discriminators:
            out, feat = d(x)
            out_map.append(out)
            feat_map.append(feat)
        return out_map, feat_map


def discriminator_loss(real_out_map, fake_out_map):
    loss = 0.0
    rl, fl = [], []
    for real_out, fake_out in zip(real_out_map, fake_out_map):
        real_loss = torch.mean((1.0 - real_out) ** 2)
        fake_loss = torch.mean(fake_out**2)
        loss += real_loss + fake_loss
        rl.append(real_loss.item())
        fl.append(fake_loss.item())
    return loss, sum(rl), sum(fl)


def generator_adv_loss(fake_disc_outputs: List[Tensor]):
    loss = 0.0
    for fake_out in fake_disc_outputs:
        fake_score = fake_out[0]
        loss += -torch.mean(fake_score)
    return loss


def feature_loss(
    fmap_r,
    fmap_g,
    weight=2.0,
    loss_fn: Callable[[Tensor, Tensor], Tensor] = F.l1_loss,
):
    loss = 0.0
    for dr, dg in zip(fmap_r, fmap_g):
        for rl, gl in zip(dr, dg):
            loss += loss_fn(rl - gl)
    return loss * weight


def generator_loss(disc_generated_outputs):
    loss = 0.0
    gen_losses = []
    for dg in disc_generated_outputs:
        l = torch.mean((1.0 - dg) ** 2)
        gen_losses.append(l.item())
        loss += l

    return loss, gen_losses
