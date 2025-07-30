import math
from typing import Type, Union


class Training_context:
    """Syntatic sugar to keep track of training step"""

    def __init__(
        self,
        Trainer: Type,
        effective_batch_size: int,
        dataloader_batch_size: int,
        eval_freq_estep: int,
        max_estep: int,
    ):
        self.Trainer = Trainer
        self.effective_batch_size = effective_batch_size
        self.dataloader_batch_size = dataloader_batch_size
        self.eval_freq_estep = eval_freq_estep
        self.max_estep = max_estep
        self._steps_per_estep: Union[int, None] = None

    def __enter__(self):
        self.Trainer.step += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @property
    def steps_per_estep(self):
        if not self._steps_per_estep:
            self._steps_per_estep = math.ceil(
                self.effective_batch_size / self.dataloader_batch_size
            )
        return self._steps_per_estep

    @property
    def step(self):
        return self.Trainer.step

    @property
    def estep(self):
        return self.Trainer.step // self.steps_per_estep

    @property
    def is_state_to_update(self):
        return self.step != 0 and not (self.step % self.steps_per_estep)

    @property
    def is_state_to_eval(self):
        return self.is_state_to_update and not (self.estep % self.eval_freq_estep)

    @property
    def is_state_to_exit(self):
        return self.estep >= self.max_estep


if __name__ == "__main__":
    pass
