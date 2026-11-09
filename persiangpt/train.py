"""Train PersianGPT from scratch on a UTF-8 text corpus."""
import argparse
import json
from pathlib import Path
import torch
from config import Config
from model import PersianGPT

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True, help="UTF-8 plain text corpus")
    p.add_argument("--steps", type=int, default=1000)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--out", default="checkpoints/tiny.pt")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    torch.manual_seed(args.seed)

    text = Path(args.data).read_text(encoding="utf-8")
    vocab = sorted(set(text))
    stoi = {ch: i for i, ch in enumerate(vocab)}
    ids = torch.tensor([stoi[ch] for ch in text], dtype=torch.long)
    if len(ids) < 200:
        raise SystemExit("Corpus too small: provide at least 200 characters.")
    cfg = Config(vocab_size=len(vocab)).validate()
    model = PersianGPT(cfg)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    device = torch.device("cpu")
    model.to(device)

    def batch():
        ix = torch.randint(0, len(ids) - cfg.block_size - 1, (args.batch_size,))
        x = torch.stack([ids[i:i+cfg.block_size] for i in ix]).to(device)
        y = torch.stack([ids[i+1:i+cfg.block_size+1] for i in ix]).to(device)
        return x, y

    for step in range(args.steps):
        x, y = batch()
        _, loss = model(x, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if step % 100 == 0:
            print(f"step={step} loss={loss.item():.4f}", flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.state_dict(), "config": cfg.__dict__, "vocab": vocab}, out)
    print(f"Saved checkpoint: {out}")

if __name__ == "__main__":
    main()
