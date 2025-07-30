__all__ = ["AudioSettings", "AudioDecoder"]
import gc
import math
import itertools
from lt_utils.common import *
import torch.nn.functional as F
from lt_tensor.torch_commons import *
from lt_tensor.model_base import Model
from lt_tensor.misc_utils import log_tensor
from lt_utils.misc_utils import log_traceback
from lt_tensor.processors import AudioProcessor
from lt_tensor.misc_utils import set_seed, clear_cache
from lt_utils.type_utils import is_dir, is_pathlike, is_file
from lt_tensor.config_templates import updateDict, ModelConfig
from lt_tensor.model_zoo.istft.generator import iSTFTGenerator
from lt_tensor.model_zoo.rsd import ResBlock1D, ConvNets, get_weight_norm
from lt_tensor.model_zoo.disc import MultiPeriodDiscriminator, MultiScaleDiscriminator


def feature_loss(real_feats, fake_feats):
    loss = 0.0
    for r, f in zip(real_feats, fake_feats):
        for ri, fi in zip(r, f):
            loss += F.l1_loss(ri, fi)
    return loss


def generator_adv_loss(fake_preds):
    loss = 0.0
    for f in fake_preds:
        loss += torch.mean((f - 1.0) ** 2)
    return loss


def discriminator_loss(real_preds, fake_preds):
    loss = 0.0
    for r, f in zip(real_preds, fake_preds):
        loss += torch.mean((r - 1.0) ** 2) + torch.mean(f**2)
    return loss


class AudioSettings(ModelConfig):
    def __init__(
        self,
        n_mels: int = 80,
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
        msd_layers: int = 3,
        mpd_periods: List[int] = [2, 3, 5, 7, 11],
        seed: Optional[int] = None,
        lr: float = 1e-5,
        adamw_betas: List[float] = [0.75, 0.98],
        scheduler_template: Callable[
            [optim.Optimizer], optim.lr_scheduler.LRScheduler
        ] = lambda optimizer: optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.998),
    ):
        self.in_channels = n_mels
        self.upsample_rates = upsample_rates
        self.upsample_kernel_sizes = upsample_kernel_sizes
        self.upsample_initial_channel = upsample_initial_channel
        self.resblock_kernel_sizes = resblock_kernel_sizes
        self.resblock_dilation_sizes = resblock_dilation_sizes
        self.n_fft = n_fft
        self.activation = activation
        self.mpd_periods = mpd_periods
        self.msd_layers = msd_layers
        self.seed = seed
        self.lr = lr
        self.adamw_betas = adamw_betas
        self.scheduler_template = scheduler_template


class AudioDecoder(Model):
    def __init__(
        self,
        audio_processor: AudioProcessor,
        settings: Optional[AudioSettings] = None,
        generator: Optional[Union[Model, "iSTFTGenerator"]] = None,  # non initalized!
    ):
        super().__init__()
        if settings is None:
            self.settings = AudioSettings()
        elif isinstance(settings, dict):
            self.settings = AudioSettings(**settings)
        elif isinstance(settings, AudioSettings):
            self.settings = settings
        else:
            raise ValueError(
                "Cannot initialize the waveDecoder with the given settings. "
                "Use either a dictionary, or the class WaveSettings to setup the settings. "
                "Alternatively, leave it None to use the default values."
            )
        if self.settings.seed is not None:
            set_seed(self.settings.seed)
        if generator is None:
            generator = iSTFTGenerator
        self.generator: iSTFTGenerator = generator(
            in_channels=self.settings.in_channels,
            upsample_rates=self.settings.upsample_rates,
            upsample_kernel_sizes=self.settings.upsample_kernel_sizes,
            upsample_initial_channel=self.settings.upsample_initial_channel,
            resblock_kernel_sizes=self.settings.resblock_kernel_sizes,
            resblock_dilation_sizes=self.settings.resblock_dilation_sizes,
            n_fft=self.settings.n_fft,
            activation=self.settings.activation,
        )
        self.generator.eval()
        self.g_optim = None
        self.d_optim = None
        self.gan_training = False
        self.audio_processor = audio_processor
        self.register_buffer("msd", None, persistent=False)
        self.register_buffer("mpd", None, persistent=False)

    def setup_training_mode(self, load_weights_from: Optional[PathLike] = None):
        """The location must be path not a file!"""
        self.finish_training_setup()
        if self.msd is None:
            self.msd = MultiScaleDiscriminator(self.settings.msd_layers)
        if self.mpd is None:
            self.mpd = MultiPeriodDiscriminator(self.settings.mpd_periods)
        if load_weights_from is not None:
            if is_dir(path=load_weights_from, validate=False):
                try:
                    self.msd.load_weights(Path(load_weights_from, "msd.pt"))
                except Exception as e:
                    log_traceback(e, "MSD Loading")
                try:
                    self.mpd.load_weights(Path(load_weights_from, "mpd.pt"))
                except Exception as e:
                    log_traceback(e, "MPD Loading")

        self.update_schedulers_and_optimizer()
        self.msd.to(device=self.device)
        self.mpd.to(device=self.device)

        self.gan_training = True
        return True

    def update_schedulers_and_optimizer(self):
        self.g_optim = optim.AdamW(
            self.generator.parameters(),
            lr=self.settings.lr,
            betas=self.settings.adamw_betas,
        )
        self.g_scheduler = self.settings.scheduler_template(self.g_optim)
        if any([self.mpd is None, self.msd is None]):
            return
        self.d_optim = optim.AdamW(
            itertools.chain(self.mpd.parameters(), self.msd.parameters()),
            lr=self.settings.lr,
            betas=self.settings.adamw_betas,
        )
        self.d_scheduler = self.settings.scheduler_template(self.d_optim)

    def set_lr(self, new_lr: float = 1e-4):
        if self.g_optim is not None:
            for groups in self.g_optim.param_groups:
                groups["lr"] = new_lr

        if self.d_optim is not None:
            for groups in self.d_optim.param_groups:
                groups["lr"] = new_lr
        return self.get_lr()

    def get_lr(self) -> Tuple[float, float]:
        g = float("nan")
        d = float("nan")
        if self.g_optim is not None:
            g = self.g_optim.param_groups[0]["lr"]
        if self.d_optim is not None:
            d = self.d_optim.param_groups[0]["lr"]
        return g, d

    def save_weights(self, path, replace=True):
        is_pathlike(path, check_if_empty=True, validate=True)
        if str(path).endswith(".pt"):
            path = Path(path).parent
        else:
            path = Path(path)
        self.generator.save_weights(Path(path, "generator.pt"), replace)
        if self.msd is not None:
            self.msd.save_weights(Path(path, "msp.pt"), replace)
        if self.mpd is not None:
            self.mpd.save_weights(Path(path, "mpd.pt"), replace)

    def load_weights(
        self,
        path,
        raise_if_not_exists=False,
        strict=True,
        assign=False,
        weights_only=False,
        mmap=None,
        **torch_loader_kwargs
    ):
        is_pathlike(path, check_if_empty=True, validate=True)
        if str(path).endswith(".pt"):
            path = Path(path)
        else:
            path = Path(path, "generator.pt")

        self.generator.load_weights(
            path,
            raise_if_not_exists,
            strict,
            assign,
            weights_only,
            mmap,
            **torch_loader_kwargs,
        )

    def finish_training_setup(self):
        gc.collect()
        self.mpd = None
        clear_cache()
        gc.collect()
        self.msd = None
        clear_cache()
        self.gan_training = False

    def forward(self, mel_spec: Tensor) -> Tuple[Tensor, Tensor]:
        """Returns the generated spec and phase"""
        return self.generator.forward(mel_spec)

    def inference(
        self,
        mel_spec: Tensor,
        return_dict: bool = False,
    ) -> Union[Dict[str, Tensor], Tensor]:
        spec, phase = super().inference(mel_spec)
        wave = self.audio_processor.inverse_transform(
            spec,
            phase,
            self.settings.n_fft,
            hop_length=4,
            win_length=self.settings.n_fft,
        )
        if not return_dict:
            return wave[:, : wave.shape[-1] - 256]
        return {
            "wave": wave[:, : wave.shape[-1] - 256],
            "spec": spec,
            "phase": phase,
        }

    def set_device(self, device: str):
        self.to(device=device)
        self.generator.to(device=device)
        self.audio_processor.to(device=device)
        self.msd.to(device=device)
        self.mpd.to(device=device)

    def train_step(
        self,
        mels: Tensor,
        real_audio: Tensor,
        stft_scale: float = 1.0,
        mel_scale: float = 1.0,
        adv_scale: float = 1.0,
        fm_scale: float = 1.0,
        fm_add: float = 0.0,
        is_discriminator_frozen: bool = False,
        is_generator_frozen: bool = False,
    ):
        if not self.gan_training:
            self.setup_training_mode()
        spec, phase = super().train_step(mels)
        real_audio = real_audio.squeeze(1)
        fake_audio = self.audio_processor.inverse_transform(
            spec,
            phase,
            self.settings.n_fft,
            hop_length=4,
            win_length=self.settings.n_fft,
            # length=real_audio.shape[-1]
        )[:, : real_audio.shape[-1]]
        # smallest = min(real_audio.shape[-1], fake_audio.shape[-1])
        # real_audio = real_audio[:, :, :smallest].squeeze(1)
        # fake_audio = fake_audio[:, :smallest]

        disc_kwargs = dict(
            real_audio=real_audio,
            fake_audio=fake_audio.detach(),
            am_i_frozen=is_discriminator_frozen,
        )
        if is_discriminator_frozen:
            with torch.no_grad():
                disc_out = self._discriminator_step(**disc_kwargs)
        else:
            disc_out = self._discriminator_step(**disc_kwargs)

        generato_kwargs = dict(
            mels=mels,
            real_audio=real_audio,
            fake_audio=fake_audio,
            **disc_out,
            stft_scale=stft_scale,
            mel_scale=mel_scale,
            adv_scale=adv_scale,
            fm_add=fm_add,
            fm_scale=fm_scale,
            am_i_frozen=is_generator_frozen,
        )

        if is_generator_frozen:
            with torch.no_grad():
                return self._generator_step(**generato_kwargs)
        return self._generator_step(**generato_kwargs)

    def _discriminator_step(
        self,
        real_audio: Tensor,
        fake_audio: Tensor,
        am_i_frozen: bool = False,
    ):
        # ========== Discriminator Forward Pass ==========

        # MPD
        real_mpd_preds, _ = self.mpd(real_audio)
        fake_mpd_preds, _ = self.mpd(fake_audio)
        # MSD
        real_msd_preds, _ = self.msd(real_audio)
        fake_msd_preds, _ = self.msd(fake_audio)

        loss_d_mpd = discriminator_loss(real_mpd_preds, fake_mpd_preds)
        loss_d_msd = discriminator_loss(real_msd_preds, fake_msd_preds)
        loss_d = loss_d_mpd + loss_d_msd

        if not am_i_frozen:
            self.d_optim.zero_grad()
            loss_d.backward()
            self.d_optim.step()

        return {
            "loss_d": loss_d.item(),
        }

    def _generator_step(
        self,
        mels: Tensor,
        real_audio: Tensor,
        fake_audio: Tensor,
        loss_d: float,
        stft_scale: float = 1.0,
        mel_scale: float = 1.0,
        adv_scale: float = 1.0,
        fm_scale: float = 1.0,
        fm_add: float = 0.0,
        am_i_frozen: bool = False,
    ):
        # ========== Generator Loss ==========
        real_mpd_feats = self.mpd(real_audio)[1]
        real_msd_feats = self.msd(real_audio)[1]

        fake_mpd_preds, fake_mpd_feats = self.mpd(fake_audio)
        fake_msd_preds, fake_msd_feats = self.msd(fake_audio)

        loss_adv_mpd = generator_adv_loss(fake_mpd_preds)
        loss_adv_msd = generator_adv_loss(fake_msd_preds)
        loss_fm_mpd = feature_loss(real_mpd_feats, fake_mpd_feats)
        loss_fm_msd = feature_loss(real_msd_feats, fake_msd_feats)

        loss_stft = self.audio_processor.stft_loss(fake_audio, real_audio) * stft_scale
        loss_mel = (
            F.l1_loss(self.audio_processor.compute_mel(fake_audio), mels) * mel_scale
        )
        loss_fm = ((loss_fm_mpd + loss_fm_msd) * fm_scale) + fm_add

        loss_adv = (loss_adv_mpd + loss_adv_msd) * adv_scale

        loss_g = loss_adv + loss_fm + loss_stft + loss_mel
        if not am_i_frozen:
            self.g_optim.zero_grad()
            loss_g.backward()
            self.g_optim.step()
        return {
            "loss_g": loss_g.item(),
            "loss_d": loss_d,
            "loss_adv": loss_adv.item(),
            "loss_fm": loss_fm.item(),
            "loss_stft": loss_stft.item(),
            "loss_mel": loss_mel.item(),
            "lr_g": self.g_optim.param_groups[0]["lr"],
            "lr_d": self.d_optim.param_groups[0]["lr"],
        }

    def step_scheduler(
        self, is_disc_frozen: bool = False, is_generator_frozen: bool = False
    ):
        if self.d_scheduler is not None and not is_disc_frozen:
            self.d_scheduler.step()
        if self.g_scheduler is not None and not is_generator_frozen:
            self.g_scheduler.step()

    def reset_schedulers(self, lr: Optional[float] = None):
        """
        In case you have adopted another strategy, with this function,
        it is possible restart the scheduler and set the lr to another value.
        """
        if lr is not None:
            self.set_lr(lr)
        if self.d_optim is not None:
            self.d_scheduler = None
            self.d_scheduler = self.settings.scheduler_template(self.d_optim)
        if self.g_optim is not None:
            self.g_scheduler = None
            self.g_scheduler = self.settings.scheduler_template(self.g_optim)


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
