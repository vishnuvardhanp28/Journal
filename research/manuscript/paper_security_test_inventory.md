# Cross-paper security-test inventory and applicability

## Scope

This inventory was compiled from the six supplied PDFs. The completed 22-image run in `results/paper_test_suite_summary.json` evaluates only AES-256-GCM and ChaCha20-Poly1305 reference controls. A separate equation-level audit found a chosen-input collision in Zhang et al.'s Eqs. (11)--(16), but does not reproduce the complete Lorenz/quantum cipher. No other target cipher has been run end to end; a fair performance comparison still requires implementing the target algorithm.

| Supplied paper | Tests and analyses reported | Status in our current run |
|---|---|---|
| Niu et al. (2024), improved 4-D chaotic system and evolutionary operators, DOI `10.1038/s41598-024-57756-x` | Chaotic dynamics (Lyapunov exponent, bifurcation, fractal dimension, initial-condition sensitivity, sample entropy); NIST sequence tests; key-space/key sensitivity; histogram and chi-square; adjacent-pixel correlation; global entropy; NPCR/UACI; pepper-noise and clipping/cropping robustness; comparative/runtime analysis. | Image statistics, chi-square, correlations, global/local entropy, NPCR/UACI controls, noise/occlusion integrity rejection, key-bit sensitivity, and runtime are run on AEAD references. Chaotic-system and NIST-keystream analyses require the paper's generator and are pending. |
| Zhang et al. (2024), nonequal-length bit-plane chaotic mapping, DOI `10.1038/s41598-024-58612-8` | Key-space and key sensitivity; histograms, adjacent correlation, entropy, Fourier spectrum; NPCR/UACI; salt-and-pepper noise and cutting/occlusion robustness; time/complexity analysis; Qiskit simulation. | Statistics, Fourier summaries, NPCR/UACI controls, corruption rejection, key-bit sensitivity, and timing are run on AEAD references. A separate equation-level chosen-input collision audit of Eqs. (11)--(16) matched outputs in all 65,536 assignments at L=4, 500/500 seeded synthetic pairs, and 12/12 grayscale assets; this establishes a conditional decryption-correctness issue but is not a full cipher or quantum simulation. Qiskit and target-specific robustness/performance tests remain pending. |
| Zhu and Zhu (2024), visual-security multi-key selection with 4-D chaos and compressed sensing, DOI `10.1038/s41598-024-66320-6` | NIST SP 800-22 sequence tests; carrier-feature robustness/uniqueness; key-space and encryption/decryption-key sensitivity; correlation, entropy/histogram, noise robustness; time complexity; discussion of chosen-plaintext/chosen-ciphertext resistance. | Ciphertext image statistics, key-bit sensitivity, chosen-plaintext one-byte-change controls, tamper rejection, and timing are run on AEAD references. These controls are not a CPA/CCA cryptanalysis. NIST tests, quantum image-representation and feature-code robustness, and the paper's custom construction are pending. |
| Yan et al. (2025), DNA color encryption with a conservative chaotic system, DOI `10.1038/s41598-025-93649-3` | Chaotic dynamics and initial/key sensitivity; key-space analysis; histogram, entropy, and correlation; encryption/decryption behavior; ciphertext cropping/anti-cropping; comparative analysis. | General image statistics, key-bit sensitivity, round-trip, and corruption rejection are run on AEAD references. Chaos dynamics and the paper's deletion/white-fill anti-cropping behavior require its own implementation and are pending. |
| Geng et al. (2025), Thorp shuffle and pseudo dequeue, DOI `10.1038/s41598-025-95263-9` | Chaotic dynamics (Lyapunov, bifurcation, fractal dimension, sample entropy, sensitivity); NIST tests; key space/sensitivity; histogram chi-square; adjacent correlation; global and local Shannon entropy; floating-frequency analysis; NPCR/UACI; noise/cropping with MSE/PSNR; complexity/runtime. | Most image-level statistics, spectrum, local entropy, NPCR/UACI controls, MSE/PSNR diagnostics, occlusion/noise rejection, and runtime are run on AEAD references. Floating-frequency behavior and every test of Geng's cipher remain pending full reproduction. Existing Eq. 17, key-space, and zero-denominator audits are separate partial audits, not a full cipher test. |
| Al-Dayel et al. (2025), 4-D chaos and cellular automaton, DOI `10.1038/s41598-025-95511-y` | Key-space/key sensitivity; NPCR/UACI; entropy; adjacent correlation; histograms and chi-square; MSE/PSNR; noise and occlusion; chosen-plaintext resistance assertion; complexity/runtime. | Corresponding generic metrics, basic chosen-plaintext perturbation controls, authenticated corruption rejection, and timing are run on AEAD references. No actual CPA, exhaustive search, or attack on Al-Dayel's construction has been run. |

## Tests actually executed

- Dataset: 12 grayscale assets and 10 RGB assets. Two grayscale files are derived from their paired RGB benchmarks.
- Algorithms: AES-256-GCM and ChaCha20-Poly1305, 44 image/cipher cases total; each exact round-trip was checked.
- Integrity/key probes: 13 per image/cipher case (single-bit ciphertext change, tag change, authenticated width edit, central white-fill occlusions covering 1/64, 1/16, and 1/4 of the ciphertext raster, salt-and-pepper substitutions at densities 0.001, 0.01, 0.1, and 0.2, one-byte container truncation, random wrong key, and one-bit key change). All 572 probes were rejected.
- Image statistics on the length-preserving ciphertext body, reinterpreted in each source image's dimensions/mode: byte and per-channel entropy, 16x16 local Shannon entropy, horizontal/vertical/two diagonal correlations, per-channel histogram chi-square, Fourier spectrum flatness and normalized spectral entropy, and descriptive plaintext/ciphertext MSE and PSNR.
- Differential/key-sensitivity diagnostics: five fresh-nonce trials per case for same-plaintext and one-byte-changed plaintext NPCR/UACI, plus same-nonce/different-key NPCR/UACI. Fresh nonces make these image-difference scores unsuitable as isolated measures of intrinsic diffusion; they are retained to show the metric limitation.
- Runtime: one warm-up and nine paired encrypt/decrypt timings per image and cipher. A linear fit is stored as a descriptive scaling summary, not a proof of asymptotic complexity.

## Headline results

- Exact decryption passed in 44/44 image/cipher cases; all 572 integrity/key probes rejected the damaged message or wrong key.
- Mean ciphertext byte entropy across the run was approximately 7.99894 bits/byte (AES-GCM) and 7.99895 bits/byte (ChaCha20-Poly1305). Mean absolute adjacent-pixel spatial correlation was approximately 0.00214 for AES-GCM and 0.00240 for ChaCha20-Poly1305.
- With fresh nonces, mean NPCR/UACI were about 99.61%/33.46% for both same-plaintext and one-byte-changed comparisons. This demonstrates that nonce randomness alone can produce the usual “ideal” image metric values.
- Under the chi-square threshold 293.2478 (255 degrees of freedom), all channels were below threshold in 39/44 image/cipher cases. These are repeated hypothesis tests on random byte samples; occasional threshold exceedance is expected and is not by itself evidence of a cipher weakness.
- Mean encryption throughput, averaged equally across the 22 images, was 2,022.02 MiB/s for AES-GCM and 1,239.89 MiB/s for ChaCha20-Poly1305 in this Python/Windows environment. These are reference baselines only. They cannot establish a speed improvement over the six papers because their code, hardware, image sizes, and timing boundaries are not matched.

## Tests that remain necessary before claiming superiority

1. Select and faithfully implement a specific target cipher or define an original, well-specified method. The current workbench is not the proposed paper algorithm.
2. Reproduce the target paper's plaintext/ciphertext outputs and decryption results before comparing metrics.
3. Run the target's actual chaotic-sequence tests only if the method contains that generator; use the published precision, solver, step size, sequence length, and full NIST procedure.
4. Define a threat model and execute genuine known/chosen-plaintext and chosen-ciphertext attacks, key-recovery attempts, nonce/reuse tests, and work-factor accounting against the target implementation.
5. Benchmark target and baseline implementations on identical hardware/software, identical images and dimensions, warm-up policy, timing boundaries, and repeated trials. Report full distributions, not only the best run.
6. Treat NPCR/UACI, entropy, histogram chi-square, correlation, MSE/PSNR, and NIST pass rates as diagnostics; none alone demonstrates semantic security or resistance to a defined attack.

## Sources

- Niu et al. (2024), https://doi.org/10.1038/s41598-024-57756-x
- Zhang et al. (2024), https://doi.org/10.1038/s41598-024-58612-8
- Zhu and Zhu (2024), https://doi.org/10.1038/s41598-024-66320-6
- Yan et al. (2025), https://doi.org/10.1038/s41598-025-93649-3
- Geng et al. (2025), https://doi.org/10.1038/s41598-025-95263-9
- Al-Dayel et al. (2025), https://doi.org/10.1038/s41598-025-95511-y



