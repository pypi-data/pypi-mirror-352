import os
import random
from typing import Iterator

from datasets import Dataset, IterableDataset
from fastcore.all import patch
from torch.utils.data.sampler import SequentialSampler
from transformers import Trainer, TrainerCallback

from HyperSloth.logging_config import get_hypersloth_logger


class ShuffleData(TrainerCallback):
    def on_epoch_begin(self, args, state, control, train_dataloader, **kwargs):
        local_rank = int(os.environ.get("HYPERSLOTH_LOCAL_RANK", "0"))

        if local_rank != 0:
            return

        logger = get_hypersloth_logger(log_level="INFO")
        logger.info(f"🔄 Starting epoch {state.epoch + 1}")

        try:
            from .._debug_dataloader import debug_chat_dataloader_for_training

            tok = kwargs["processing_class"]
            debug_chat_dataloader_for_training(train_dataloader, tokenizer=tok)
            logger.info(
                "📋 Dataloader examples logged to " ".log/dataloader_examples.html"
            )
        except Exception as e:
            logger.debug(f"Dataloader debugging failed (non-critical): {e}")


class RandomSamplerSeededByEpoch(SequentialSampler):
    def __init__(self, data_source) -> None:
        self.data_source = data_source
        self.epoch = 0
        self.logger = get_hypersloth_logger(log_level="DEBUG")

    def set_epoch(self, epoch: int) -> None:
        self.epoch = epoch

    def __iter__(self) -> Iterator[int]:
        dataset_size = len(self.data_source)
        ids = list(range(dataset_size))

        # Shuffle with epoch-specific seed
        R = random.Random(42 + self.epoch)
        R.shuffle(ids)

        self.logger.info(
            f"🎲 Sampler epoch {self.epoch}: emitting {dataset_size} indices\nFirst ids: {ids[:10]}\nLast ids: {ids[-10:]}"
        )
        yeild_ids = []
        for idx in ids:
            # self.logger.info(f"📤 Emitting index: {idx}")
            yeild_ids.append(idx)
            yield idx
        # write to log for debugging
        self.logger.info(
            f"🎲 Sampler epoch {self.epoch}: dataset_size={dataset_size}\n"
            f"   📋 First 10 indices: {yeild_ids[:10]}\n"
            f"   📋 Last 10 indices: {yeild_ids[-10:]}"
        )


def apply_patch_sampler(trainer: Trainer):
    logger = get_hypersloth_logger(log_level="INFO", allow_unknown_gpu=True)
    logger.info("🔧 Patching Trainer to use RandomSamplerSeededByEpoch")

    @patch
    def _get_train_sampler(
        self: Trainer, train_dataset=None
    ) -> RandomSamplerSeededByEpoch:
        """Get a custom sampler for the training dataset."""
        if train_dataset is None:
            train_dataset = self.train_dataset

        assert isinstance(
            train_dataset, (Dataset, IterableDataset)
        ), "train_dataset must be a Dataset or IterableDataset"

        return RandomSamplerSeededByEpoch(train_dataset)  # type: ignore

    logger.info(f"Add callback ShuffleData to Trainer {trainer.__class__.__name__}")
    trainer.add_callback(ShuffleData())

    return trainer
