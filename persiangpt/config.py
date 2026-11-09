"""Small CPU-first Transformer configuration."""
from dataclasses import dataclass

@dataclass
class Config:
    vocab_size: int = 512
    block_size: int = 128
    n_layer: int = 2
    n_head: int = 2
    n_embd: int = 64
    dropout: float = 0.0

    @property
    def head_size(self):
        return self.n_embd // self.n_head

    def validate(self):
        if self.n_embd % self.n_head:
            raise ValueError("n_embd must be divisible by n_head")
        if self.block_size < 2 or self.n_layer < 1 or self.n_head < 1:
            raise ValueError("Invalid model dimensions")
        return self
