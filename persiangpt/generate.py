"""Generate text from a PersianGPT checkpoint."""
import argparse
import torch
from config import Config
from model import PersianGPT

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", default="checkpoints/tiny.pt")
    p.add_argument("--prompt", default="سلام")
    p.add_argument("--tokens", type=int, default=100)
    args = p.parse_args()
    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    cfg = Config(**ckpt["config"]).validate()
    vocab = ckpt["vocab"]
    stoi = {ch: i for i, ch in enumerate(vocab)}
    unknown = [ch for ch in args.prompt if ch not in stoi]
    if unknown:
        raise SystemExit("Prompt contains characters absent from training vocabulary.")
    model = PersianGPT(cfg)
    model.load_state_dict(ckpt["model"])
    model.eval()
    idx = torch.tensor([[stoi[ch] for ch in args.prompt]], dtype=torch.long)
    result = model.generate(idx, max_new_tokens=args.tokens)[0].tolist()
    print("".join(vocab[i] for i in result))

if __name__ == "__main__":
    main()
