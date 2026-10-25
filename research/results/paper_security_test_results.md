# Cross-paper security test run: reference-cipher results

## What was run

The six supplied papers were checked for their reported evaluation procedures. We ran the tests that can be meaningfully applied to the current authenticated-encryption controls: AES-256-GCM and ChaCha20-Poly1305 over 12 grayscale and 10 RGB USC-SIPI assets. The 44 image/cipher cases each used nine timed encrypt/decrypt repetitions. Differential diagnostics used five fresh-nonce trials per case.

This is **not a run against a new proposed cipher or against the six papers' custom ciphers**. It is a verified control suite while the target implementation remains to be built.

## Results

| Measure | AES-256-GCM | ChaCha20-Poly1305 |
|---|---:|---:|
| Exact round-trips | 22/22 images | 22/22 images |
| Ciphertext-integrity and wrong-key probes rejected | 286/286 | 286/286 |
| Mean byte entropy | 7.99897 bits/byte | 7.99897 bits/byte |
| Mean absolute adjacent-pixel correlation, over channels/directions | 0.00235 | 0.00246 |
| Mean fresh-nonce NPCR/UACI, same plaintext | 99.611% / 33.460% | 99.609% / 33.470% |
| Mean fresh-nonce NPCR/UACI, one-byte plaintext change | 99.611% / 33.461% | 99.610% / 33.458% |
| Mean encryption throughput across the 22 images | 1,838.81 MiB/s | 1,152.49 MiB/s |

The integrity probes comprised 13 cases per image/cipher: ciphertext and tag bit flips, authenticated metadata change, three central white-fill occlusion areas (1/64, 1/16, and 1/4 of the raster), four salt-and-pepper corruption levels, one-byte container truncation, random wrong key, and one-bit key change. All 572 probes failed closed. A nominal 256-bit key was used for both reference algorithms; this is a key-size statement, not a complete effective-security bound.

At the chi-square cutoff 293.2478 for 255 degrees of freedom and significance 0.05 (the cutoff used in one supplied paper), all channels were below the cutoff in 41 of 44 image/cipher cases. The remaining three cases are not proof of a weakness: multiple independent statistical tests have expected false positives. Mean normalized Fourier-spectrum entropy was 0.9857 for AES-GCM and 0.9857 for ChaCha20-Poly1305; this, like histogram, spatial correlation, local entropy, MSE and PSNR, is descriptive only.

Fresh-nonce NPCR/UACI is nearly identical for same-plaintext and changed-plaintext comparisons. The nonce randomization dominates these scores, which is why the values cannot establish the intrinsic diffusion of an encryption algorithm. AEAD occlusion/noise experiments verify rejection after corruption; they do not claim partial image recovery.

## Runtime interpretation

In this run, AES-GCM had higher mean throughput than ChaCha20-Poly1305. These figures come from the Python cryptography package on the current Windows 11 AMD64 machine. They cannot establish that our research method is faster than any supplied paper: the papers use different implementations, hardware, input sizes, and timing boundaries. The recorded timing CSV has per-image medians; the JSON includes descriptive size-scaling fits.

## Work still required for the paper's own method

- Implement one selected target paper faithfully (or finalize a new algorithm) and verify exact encryption/decryption before rerunning this matrix.
- Run chaos-map dynamics, key-stream NIST SP 800-22, and sample-entropy tests only for a reproduced chaotic generator, with its stated precision and solver settings.
- Run actual CPA/CCA and key-recovery attempts against the target construction; the current probes are basic corruption and key-mismatch checks, not a cryptanalytic attack.
- Re-run all comparable timing baselines on identical hardware, software, image sizes, and timing boundaries before claiming lower runtime.
- Do not claim superiority from near-8 entropy, low correlation, high NPCR/UACI, histogram tests, or a large nominal key-space count alone.

## Files

- `../code/paper_security_test_suite.py` — reproducible runner.
- `paper_test_suite_summary.json` — run scope, checks, timing environment, and size-scaling fit.
- `paper_test_timing.csv` — per-image encryption/decryption timing.
- `paper_test_image_statistics.csv` — per-image statistical and spectral diagnostics.
- `paper_test_integrity_attacks.csv` — all 572 corruption/key probes.
- `../manuscript/paper_security_test_inventory.md` — per-paper test map and applicability.


