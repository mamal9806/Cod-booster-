# PersianGPT (CPU-first)

PersianGPT is an experimental language-model project trained from random initialization. It is not a wrapper around a pretrained model and it is not comparable to ChatGPT.

## Important KataBump Free-tier constraint

According to the current KataBump documentation, the free plan provides **308 MB RAM, 716 MB disk, and 25% CPU**, and requires renewal every four days. That is not enough for a practical PyTorch training environment and is too constrained for hosting a PyTorch Transformer reliably.

Therefore this repository separates:
- **Training:** run on a machine with more memory (or a temporary notebook/compute environment); the model is a small decoder-only Transformer implemented with PyTorch.
- **KataBump free tier:** run the dependency-free status/API process in `main.py`. It reports whether a trained checkpoint exists but does not pretend to generate AI responses without a compatible inference runtime.

Do not upload large datasets or checkpoints to the free tier. Keep backups elsewhere.

## Project layout

- `config.py`: tiny CPU-oriented model/training settings.
- `model.py`: decoder-only Transformer, initialized from random weights.
- `train.py`: next-token pretraining from a UTF-8 text file.
- `generate.py`: sample text from a trained checkpoint.
- `main.py`: lightweight standard-library HTTP status endpoint for KataBump.
- `tests/`: small architecture/configuration tests.

## Train (outside KataBump Free)

Use Python 3.10+ and install PyTorch for your platform:

```bash
python -m pip install torch
python persiangpt/train.py --data data.txt --steps 1000
python persiangpt/generate.py --prompt "سلام" --checkpoint checkpoints/tiny.pt
```

The training corpus must be text you are allowed to use. Start with a small, clean UTF-8 corpus. The first version uses a character vocabulary; this is intentionally simple and will later be replaced by a subword tokenizer.

## Run the KataBump lightweight status service

Set the startup file to `main.py`. No third-party package is required.

```bash
python main.py
```

The process listens on `0.0.0.0` and uses the `PORT` environment variable (default 8080). `GET /` and `GET /health` return JSON status. This is a deployment/health check, **not model inference**.

## Training caveats

The default model is deliberately tiny. Training from random initialization needs a substantial amount of representative data and compute to learn useful language behavior. A small demo corpus only proves that the pipeline works; it will not create a capable Persian assistant. Training loss alone does not establish conversational quality.

Checkpoints contain model weights and vocabulary. Keep them private if your training data or model artifacts are sensitive.
