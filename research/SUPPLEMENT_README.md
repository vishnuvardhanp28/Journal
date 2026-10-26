# Reproducibility supplement

Contains scripts, source manifest, and machine-readable outputs for a pilot study. No custom cipher from the six papers has been reproduced end-to-end. AES-GCM and ChaCha20-Poly1305 are reference controls only. The source tree was rerun on Python 3.12.14; exact dependency versions are listed in `code/requirements.txt`.

## Rebuild the complete 10-by-10 image comparison

The ZIP contains NASA pilot images and manifests, but the USC-SIPI TIFFs are not redistributed because many image rights are unknown. Download the official USC-SIPI miscellaneous archive from https://sipi.usc.edu/database/database.php?volume=misc, extract its `misc` folder to `data/source_archives/usc_sipi_misc/misc/`, then run `python code/prepare_sipi_benchmark.py`. From the supplement root, run `python code/make_image_comparison_montage.py`. It requires exactly 10 original grayscale and 10 original RGB entries, performs a fresh AES-256-GCM encryption/decryption round trip for each, writes 60 image panels and a 20-row verification CSV, and rebuilds `manuscript/figures/image_comparison_montage.png`. Temporary per-image keys are discarded. The ciphertext-byte panels are display-only.

Install the pinned packages with `python -m pip install -r code/requirements.txt` in Python 3.12. `scipy` is required by the expanded histogram/timing diagnostics; the requirements file now includes it.

## Color and grayscale image demonstrations

The `results/expanded_color_demo/` folder contains the color figure, AES-GCM encrypted binary examples, demo-only key sidecars, decrypted PNGs, and JSON/CSV results. `results/grayscale_demo/` contains two luminance-converted examples with corresponding encrypted `.imgenc` files, display-only ciphertext bytes, exact decrypted PNGs, demo-only keys, and grayscale histogram figure. The source images 4.1.07 and 4.1.08 are USC-SIPI USC jelly-bean images listed as free to use. The demo keys are included solely to permit decryption of examples; they are disclosed, make those samples insecure, and must never be reused.

The color ciphertext display images reshape ciphertext-body bytes as RGB; the grayscale previews reshape them as grayscale bytes. They are visualizations, not the `.imgenc` files. Exact decryption was checked pixel-for-pixel for the color and grayscale illustrations. Diagnostics include fresh-nonce NPCR/UACI, entropy, histograms, correlation, limited CPA/KPA probes, noise and integrity checks, wrong-key probes, timing screens, and per-file timing. Their limits are stated in the report and manuscript.

## Niu et al. equation audit

`code/audit_niu_key_schedule.py` and `results/niu_key_schedule_audit/` reproduce only Eqs. (8)-(10), with an explicit SHA-256 byte-serialization assumption. This is not an end-to-end cipher test. The current manuscript source is copied under `manuscript/`.

The separate six-image NASA pilot also records a controlled nonce-lifecycle experiment: fresh-nonce NPCR/UACI for same and one-byte-changed inputs, plus an isolated unsafe nonce-reuse demonstration with ciphertext-XOR verification. It is a reference-cipher misuse control, not a test of the six custom schemes. The rows are in `results/metric_nonce_diagnostics.csv` and summarized in `results/experiment_summary.md`.

No cryptographic security proof, constant-time proof, or measured brute-force result is claimed. See `results/VERIFICATION_REPORT.md` for the latest rerun counts, updated measurements, run environment, and explicit remaining limitations. The current main in-memory suite uses 30 timed repetitions per image/algorithm case; the file-wrapper study retains its verified nine-repeat run.

The Niu audit folder also includes a formal, conditional chosen-plaintext equality distinguisher analysis. It assumes stateless deterministic encryption under a fixed key as described in the paper; it proves equality leakage only, not plaintext recovery or a completed cipher attack.

## Zhang et al. equation-level chosen-input collision

`code/audit_zhang_diffusion_collision.py` transcribes the published binary diffusion equations. Complementing the `A1` sequence leaves its cyclic XOR difference unchanged, so the deterministic later stages receive the same inputs under fixed keys. For the paper's example four-high/four-low bitplane grouping, the paired plaintext is `P XOR 240` at each pixel. All 65,536 assignments at `L=4`, 500 seeded synthetic probes, and all 12 USC-SIPI grayscale assets produced matching post-diffusion outputs. This shows a non-injective mapping and decryption-correctness failure under the equations as written; it does not recover a key or plaintext and does not reproduce the full Lorenz/Qiskit cipher. The result JSON records both source and paired-image hashes.

To rerun the asset checks, obtain the grayscale TIFFs listed in `data/benchmarks/usc_sipi/manifest.csv` from the cited USC-SIPI source and place them in `data/benchmarks/usc_sipi/grayscale/`. They are not redistributed here because rights are uncertain for much of the corpus. The script checks the source-file hash records in its output. From this package root, run `python code/audit_zhang_diffusion_collision.py`; Pillow is required. The script stops with a clear error if the grayscale assets are absent.

## Rebuild grayscale figure

`code/make_grayscale_demo.py` creates a grayscale preview, AES-GCM container, exact decrypted PNG, and original/ciphertext/decrypted histograms from USC-SIPI images 4.1.07 and 4.1.08. The grayscale samples are luminance conversions of those two photographs. Install the dependencies in `code/requirements.txt`, obtain the source TIFFs from USC-SIPI, then run `python code/make_grayscale_demo.py` from the supplement root. The script writes to `results/grayscale_demo/` by default. Demo keys are intentionally disclosed; never reuse them.

The methodology diagram is stored at `manuscript/figures/methodology_overview.png`; regenerate it with `python code/make_methodology_figure.py` from the supplement root.
