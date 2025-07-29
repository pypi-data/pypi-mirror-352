__all__ = ["WaveMelDataset"]
from lt_tensor.torch_commons import *
from lt_utils.common import *
import random
from torch.utils.data import Dataset, DataLoader, Sampler
from lt_tensor.processors import AudioProcessor
import torch.nn.functional as FT
from lt_tensor.misc_utils import log_tensor


class WaveMelDataset(Dataset):
    """Untested!"""

    data: Union[list[dict[str, Tensor]], Tuple[Tensor, Tensor]] = []

    def __init__(
        self,
        audio_processor: AudioProcessor,
        path: PathLike,
        limit_files: Optional[int] = None,
        max_frame_length: Optional[int] = None,
    ):
        super().__init__()
        assert max_frame_length is None or max_frame_length >= (
            (audio_processor.n_fft // 2) + 1
        )
        self.post_n_fft = (audio_processor.n_fft // 2) + 1
        self.ap = audio_processor
        self.files = self.ap.find_audios(path)
        if limit_files:
            random.shuffle(self.files)
            self.files = self.files[:limit_files]
        self.data = []

        for file in self.files:
            results = self.load_data(file, max_frame_length)
            self.data.extend(results)

    def _add_dict(self, audio_raw: Tensor, audio_mel: Tensor, file: PathLike):
        return {"mel": audio_mel, "raw": audio_raw, "file": file}

    def load_data(self, file: PathLike, audio_frames_limit: Optional[int] = None):
        initial_audio = self.ap.load_audio(file)
        if not audio_frames_limit or initial_audio.shape[-1] <= audio_frames_limit:
            audio_mel = self.ap.compute_mel(initial_audio, add_base=True)
            return [self._add_dict(initial_audio, audio_mel, file)]
        results = []
        for fragment in torch.split(
            initial_audio, split_size_or_sections=audio_frames_limit, dim=-1
        ):
            if fragment.shape[-1] < self.post_n_fft:
                # sometimes the tensor will be too small to be able to pass on mel
                continue
            audio_mel = self.ap.compute_mel(fragment, add_base=True)
            results.append(self._add_dict(fragment, audio_mel, file))
        return results

    def get_data_loader(
        self,
        batch_size: int = 1,
        shuffle: Optional[bool] = None,
        sampler: Optional[Union[Sampler, Iterable]] = None,
        batch_sampler: Optional[Union[Sampler[list], Iterable[list]]] = None,
        num_workers: int = 0,
        pin_memory: bool = False,
        drop_last: bool = False,
        timeout: float = 0,
    ):
        return DataLoader(
            self,
            batch_size=batch_size,
            shuffle=shuffle,
            sampler=sampler,
            batch_sampler=batch_sampler,
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=drop_last,
            timeout=timeout,
            collate_fn=self.collate_fn,
        )

    @staticmethod
    def collate_fn(batch: Sequence[Dict[str, Tensor]]):
        mels = []
        audios = []
        files = []
        for x in batch:
            mels.append(x["mel"])
            audios.append(x["raw"])
            files.append(x["file"])
        # Find max time in mel (dim -1), and max audio length
        max_mel_len = max([m.shape[-1] for m in mels])
        max_audio_len = max([a.shape[-1] for a in audios])

        padded_mels = torch.stack(
            [FT.pad(m, (0, max_mel_len - m.shape[-1])) for m in mels]
        )  # shape: [B, 80, T_max]

        padded_audios = torch.stack(
            [FT.pad(a, (0, max_audio_len - a.shape[-1])) for a in audios]
        )  # shape: [B, L_max]

        return padded_mels, padded_audios, files

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]
