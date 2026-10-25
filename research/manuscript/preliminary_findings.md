# Preliminary reproducible findings (not submission-ready)

## Scope

This is an evolving evidence record. It does not claim that any of the six supplied schemes has been broken. The standard-cipher runs are controls and the paper-specific results are limited to partial reproduction and key-space audits; a full reproduction/cryptanalysis is still required.

## Finding 1: a mode-preserving research corpus is in place

We curated 22 USC-SIPI TIFF assets: 10 native grayscale (mode L), 10 native RGB (mode RGB), and two additional grayscale transforms (mode L) of the Mandrill/Baboon and Peppers RGB images for paired analysis. Each file is recorded with its database ID, description, dimensions, native mode, source, rights note, and SHA-256 in `../data/benchmarks/usc_sipi/manifest.csv`. The set includes standard image-encryption examples such as Mandrill/Baboon, Peppers, and Jelly beans. The USC-SIPI catalog states the images are for research but warns that rights are unknown for many; 20 selected entries are marked unknown/uncertain in the manifest, and 2 Jelly-bean images are marked free for research. We will not reproduce image panels in a submission unless the rights are resolved.

## Finding 2: AEAD reference checks pass, while image metrics track nonce randomness

The mode-preserving harness compared AES-256-GCM and ChaCha20-Poly1305 over all 22 assets (44 image/cipher configurations, 9 timing repeats each). All 44 configurations passed exact round-trip recovery and rejected ciphertext/tag tampering, altered authenticated width metadata, and incorrect keys. All 44 isolated unsafe nonce-reuse controls reproduced ciphertext-XOR/plaintext-XOR leakage.

The mean reference-cipher encryption throughput was 1,484.22 MiB/s for the 12 grayscale files (10 native, 2 derived) and 1,229.20 MiB/s for the 10 RGB files on the recorded machine. These are implementation- and machine-specific figures, not fair comparisons with MATLAB versions in the source papers.

For grayscale, mean ciphertext byte entropy was 7.998619 bits/byte. Fresh-nonce encryption of the same plaintext twice produced mean ciphertext-body NPCR/UACI of 99.61445%/33.46785%; a one-byte plaintext change under a fresh nonce produced 99.61166%/33.44699%. For RGB, the corresponding pairs were 99.61670%/33.44238% and 99.61423%/33.47626%. This shows that near-ideal NPCR/UACI can arise from the nonce change itself and should not be read as proof that a specific cipher’s plaintext diffusion is secure.

The unsafe nonce-reuse experiment is a protocol-misuse control only; it is not a finding against any of the six papers. Full timing/diagnostic rows are in `../results/sipi_aead_timing.csv` and `../results/sipi_metric_diagnostics.csv`; the run summary is `../results/sipi_benchmark_summary.md`.

## Finding 3: Geng et al. have a verified specification conflict with measurable impact

The paper says in prose that sequence W generates W1, but displayed Eq. (17) uses y(i) for W1, and the diffusion prose again says W is processed. A partial, explicitly parameterized keystream reproduction implemented both readings on a 64×64 grayscale NASA test image. With fixed-step RK4, dt=0.001, and the paper’s displayed example parameters (not verified encryption settings), the W1 arrays differed at 4,080 of 4,096 positions (99.61%). The source paper does not state its ODE solver or step size, adding another reproduction gap. This quantifies ambiguity in the published method; it is not a cipher break. Code and output are `../code/geng_eq17_variant_audit.py` and `../results/geng_eq17_variant_audit.json`.

Geng et al. also derive four chaotic starting values from SHA-256 of plaintext pixels, then count four starting values plus five control parameters in a nominal (10^15)^9 = 10^135 key-space estimate. The four plaintext-derived values are not independent secret choices. Conditionally assuming the other five are independent secrets with 10^15 valid choices each gives a nominal 10^75 (about 249.14 bits), not a demonstrated attack or a finding that the remaining count is weak. Actual key entropy depends on parameter secrecy, valid ranges, quantization, and key establishment. The executable audit is `../code/audit_geng_keyspace.py`; output is `../results/geng_keyspace_audit.json`.

## Finding 4: Al-Dayel et al.’s key-space arithmetic and key inputs need clarification

The paper counts 8 CDS values, 42 KSGP values, and 3 values each for decimal diffusion and conversion, assuming 10^15 possibilities per value. Each three-value group contributes 10^45. The prose says 10^48 for each, while the final product uses 10^45 and yields the stated 10^840. The machine-checked arithmetic is in `../code/audit_aldayel_keyspace.py` and `../results/aldayel_keyspace_audit.json`.

The paper describes six of the values as obtained from initial/final RGB channel pixels, so they may be data-derived or intermediate state rather than independent secret keys. The scheme text also names secret symbols u, eta, sigma1–sigma3, key1, and key2, which are not clearly mapped to its 56-value enumeration. Excluding only the six pixel-derived values would produce a conditional 10^750 only if every other value were an independent secret with 10^15 valid choices; this is not established and is not a corrected security level. No key-recovery attack has been run against this scheme.

## Remaining work before a Q1 security-journal submission

- Complete a faithful implementation of at least one target cipher, including encryption and decryption, and compare against the authors’ reported outputs.
- Resolve the Geng Eq. (17) conflict and missing numerical integration choices; implement both variants through full diffusion and characterize the output differences.
- Specify a threat model and run reproducible known/chosen-plaintext attacks with stated success criteria and complexity.
- Continue comparable, publisher-source audits of all six papers, followed by selected implementations and attacks.
- Expand measurements across repeated runs and identified hardware; keep the image dataset’s rights limitations visible in any manuscript package.

The current work establishes a mode-preserving benchmark of 12 grayscale (10 native, 2 derived) and 10 RGB images, an AEAD control baseline, a measurable Geng specification ambiguity, and two key-space accounting concerns. It does not yet establish a novel cryptanalytic result sufficient for IEEE Transactions on Information Forensics and Security (T-IFS). T-IFS remains a conditional target from the supplied Q1 list; acceptance cannot be guaranteed.

## Primary sources

- Geng et al., “Image encryption scheme based on thorp shuffle and pseudo dequeue,” *Scientific Reports* 15, 11141 (2025), https://doi.org/10.1038/s41598-025-95263-9.
- Al-Dayel et al., “An image encryption scheme using 4-D chaotic system and cellular automaton,” *Scientific Reports* 15, 19499 (2025), https://doi.org/10.1038/s41598-025-95511-y.
- USC-SIPI catalog: https://sipi.usc.edu/database/database.php?volume=misc.
- USC-SIPI copyright notes: https://sipi.usc.edu/database/copyright.php.


## Finding 5: the cross-paper image-test battery passes AEAD integrity controls, not the six proposed ciphers

A paper-by-paper test inventory and reproducible runner were added. Across 44 image/cipher configurations (22 images × AES-256-GCM/ChaCha20-Poly1305), exact round-trips passed and all 572 basic corruption, metadata, truncation, and wrong-key probes were rejected. The battery reports histogram chi-square, global/local entropy, spatial correlations, Fourier summaries, MSE/PSNR, NPCR/UACI controls, key-bit sensitivity, and per-image timing. Fresh-nonce NPCR/UACI was almost the same for unchanged and one-byte-changed plaintexts, reinforcing that nonce randomization makes the common score a poor stand-alone diffusion test.

This is a reference-cipher result. It is not evidence that our prospective paper method outperforms the six supplied methods. Chaos-specific tests, Qiskit simulation, and genuine CPA/CCA/key-recovery attacks await a faithful target cipher implementation. Runtime comparisons against the papers are also pending matched hardware, code, image sizes, and timing boundaries. Full results are in `../results/paper_security_test_results.md`; the paper-by-paper applicability table is in `paper_security_test_inventory.md`.
## Finding 6: Geng et al.'s published SHA-256 seed formula has a reproducible zero-denominator case

Equation (14) divides by each of four XOR aggregates of SHA-256 bytes but states no handling when an aggregate is zero. The independent transcription fails on grayscale USC-SIPI image 5.1.09 (11/12 curated grayscale images pass; 5.1.09 has XOR aggregates [224, 223, 0, 8]). Across 10,000 unique one-pixel variants of a 512×512 Mandrill/Baboon image, 161 (1.61%; Wilson 95% CI 1.38–1.88%) produced at least one zero denominator. Under a uniform independent-byte model, the expected probability is 1−(255/256)^4 = 1.553%. The result establishes an input-dependent seed-stage failure in the stated formula, not plaintext recovery or a cipher break. Code and data are in ../code/audit_geng_seed_edge_case.py and ../results/geng_seed_edge_case_audit.json.

Visual inspection of the Geng methods pages also confirmed that the article describes forward encryption but does not give inverse/decryption steps, despite presenting decrypted images. The Eq. (17) W1 conflict and missing ODE integration settings remain unresolved. Therefore a faithful end-to-end security evaluation of Geng is not currently possible from the article alone; those gaps must be separated from any attack claim. See ../results/geng_specification_audit.md.
