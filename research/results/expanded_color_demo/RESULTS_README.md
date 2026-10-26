# Expanded color-image security and timing results

## Which image is which?

- `*.imgenc` is the actual encrypted binary file. It is not a PNG and cannot be opened as an image directly.
- `*_ciphertext_bytes.png` is only a visualization made by reshaping encrypted pixel bytes into RGB.
- `*_decrypted.png` is the lossless recovered image. Both samples were opened from their `.imgenc` files and verified byte-for-byte against the source TIFFs.
- Each sample has a matching `*_DEMO_ONLY.key.txt` key. The key is included only so the example can be decrypted. Since the key is disclosed, these samples are not secret and must never be used for real data.

The paper figure contains two image rows, each followed by its RGB histogram row: original, ciphertext-byte display, decrypted. USC-SIPI identifies images 4.1.07 and 4.1.08 as free to use.

## Measurements on two 256 x 256 RGB images

The following are diagnostics on AES-256-GCM and ChaCha20-Poly1305 reference controls. They are not tests of the six custom ciphers from the supplied papers.

- Exact decryption: 4/4 image-algorithm combinations, pixel-for-pixel.
- Ciphertext entropy: 7.99907--7.99912 bits/byte.
- Per-channel uniform-histogram chi-square: all 12/12 channel checks had p-values above 0.05 (range 0.242--0.878). This is descriptive, not a security test.
- Mean absolute neighbor correlation: 0.00273--0.00376.
- Fresh-nonce NPCR/UACI: same plaintext 99.609--99.613% / 33.452--33.482%; one-byte-changed plaintext 99.608--99.612% / 33.455--33.468%. Similar scores for unchanged and changed inputs show why these metrics do not isolate cipher diffusion when the nonce changes.
- CPA diagnostic: 500 equal-length all-zero/all-255 challenges per image-algorithm case; one ciphertext-byte-mean classifier scored 48.4--53.0%, with all Wilson 95% intervals including chance (50%). This is a small distinguisher check, not an IND-CPA proof.
- KPA diagnostic: one known pair used to transfer a 32-byte XOR/keystream prefix across 100 fresh-nonce targets; 0/100 prefixes recovered per case. This does not test general key recovery.
- Noise and integrity: salt-and-pepper and Gaussian byte noise at 0.1%, 1%, 5%, 10%, ciphertext/tag bit changes, metadata tampering, truncation, and 16-byte block reorder were rejected (13/13 probes per case).
- Key sensitivity / brute force: a one-bit key change was rejected; 100/100 random wrong keys per case were rejected. No exhaustive brute-force search was run. A 256-bit key implies an idealized average of 2^255 guesses, but this is a theoretical estimate, not a measured attack.
- COA and scrambling-only: entropy, histograms, correlation and displayed ciphertext were inspected; no plaintext recovery is claimed. There is no standalone permutation layer in AEAD, so a scrambling-only attack is inapplicable. Block reordering was tested as a tamper probe.
- Timing screen: 1,500 samples per data class. The current rerun did not show a significant class timing difference (AES-GCM Welch p=0.361; ChaCha20-Poly1305 p=0.455). An earlier exploratory run gave AES-GCM p=0.0246, which did not reproduce. The screen is noisy and supports no side-channel conclusion or constant-time guarantee.
- File timing, 30 repetitions per case: the mean of four per-case median sealing times was 3.97 ms; the corresponding open/authenticate/decrypt/write-PNG time was 25.61 ms. The full wrapper is O(n) time and O(n) memory in the number of pixel bytes; it is not a streaming implementation.

Timings include Python wrapper, file handling, and image codec work, and are specific to this machine and 256 x 256 examples. Do not compare them directly with the supplied papers' runtimes.

## Reproduction records

`expanded_security_demo.json`, `attack_diagnostics.csv`, `timing_attack_probe.csv`, and `file_timing.csv` retain per-case details. `visual_manifest.json` records source and output hashes. The runner is `expanded_color_image_security_demo.py` in the code supplement.
