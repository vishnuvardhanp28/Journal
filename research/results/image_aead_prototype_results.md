# Authenticated image wrapper: current file-level results

## Scope

This is a standard AEAD reference wrapper, not a new cipher and not an implementation of one of the six supplied papers. The caller supplies a 32-byte key. A fresh nonce is generated for every encryption; image mode and dimensions are authenticated. The wrapper supports grayscale (L) and RGB pixel data and outputs a lossless PNG on decryption.

## Correctness and integrity checks

- Dataset: 22 images (12 grayscale and 10 RGB), with original dimensions and pixel modes retained.
- Algorithms: AES-256-GCM and ChaCha20-Poly1305.
- Pixel API round-trips: 44/44.
- File API round-trips: 44/44.
- Ciphertext tamper rejected: 44/44.
- One-bit wrong-key probes rejected: 44/44.
- All checks passed in the latest run.

The file-level timing run used one warm-up and nine repetitions per image/algorithm/compression-level case. It tested lossless PNG compression levels 6 (Pillow default) and 1. Both outputs were reopened and compared byte-for-byte with the source pixel array after each repetition.

## Throughput results

Arithmetic mean of per-image throughput values across the 22 images:

| AEAD | PNG compression | Sealing (MiB/s) | Opening + PNG output (MiB/s) | Mean PNG size (bytes) |
|---|---:|---:|---:|---:|
| AES-256-GCM | 6 | 75.00 | 8.20 | 191,071 |
| AES-256-GCM | 1 | 78.55 | 11.45 | 276,159 |
| ChaCha20-Poly1305 | 6 | 74.23 | 8.37 | 191,071 |
| ChaCha20-Poly1305 | 1 | 74.30 | 10.62 | 276,159 |

Compared with level 6, level 1 increased opening throughput by 39.6% for AES-GCM and 26.9% for ChaCha20-Poly1305 in this run. Mean sealing throughput changed by less than 5%. Average output size increased from 191,071 to 276,159 bytes, or 44.5%. The opening timing includes authenticated decryption and writing the recovered image as a PNG; level 1 trades a larger output file for faster PNG encoding. This is a file-output optimization only. It does not establish faster encryption than any paper's method, since the six methods have not been reproduced and their benchmark conditions differ.

## Reproduce

From the `research` directory in PowerShell, use the dependency bundle already present in `work/python_deps`:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'work\python_deps')
python .\code\evaluate_image_aead_prototype.py
python .\code\audit_zhu_box_muller_domain.py
```

The machine-readable summary is `image_aead_prototype_summary.json`; per-image timings are in `image_aead_prototype_timing.csv`. The run was made with Python 3.14.5 on Windows 11 AMD64. Use matched hardware, software, images, and timing boundaries before any comparison with another cipher.

## Limits

The wrapper does not preserve EXIF or other file-container metadata. It verifies integrity and rejects corruption; it is not designed to recover images after lost or altered ciphertext. AES-GCM and ChaCha20-Poly1305 are established standard primitives and are included as security controls, not as novelty.
