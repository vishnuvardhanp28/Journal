# USC-SIPI benchmark run (2026-10-25)

## Dataset

- 22 TIFF assets: 12 grayscale and 10 RGB. The gray group includes 10 native monochrome images plus grayscale transforms of the Mandrill/Baboon and Peppers RGB images, enabling paired color/gray analyses. The RGB group has 10 native color images.
- All 22 stored files have distinct SHA-256 hashes. Paired images are related by content and are not independent image samples.
- Image IDs, titles, dimensions, source, transformation, rights notes, and hashes are recorded in `../data/benchmarks/usc_sipi/manifest.csv` and `.json`.
- The set includes examples used in image-processing literature, including Mandrill/Baboon, Peppers, and Jelly beans. USC-SIPI describes its database as for research, but copyright status is unknown for most entries. Two Jelly-bean images are marked free for research; verify rights for other figures before publication.

## Harness and checks

- Compared AES-256-GCM and ChaCha20-Poly1305 with 9 timing repeats per image and cipher (44 image/cipher configurations).
- All 44 configurations passed exact round-trip recovery and rejected ciphertext/tag tampering, altered authenticated width metadata, and incorrect keys.
- All 44 isolated unsafe nonce-reuse controls reproduced the ciphertext-XOR/plaintext-XOR relation. This is an intentionally unsafe control only.

## Results

| Group | Images | Mean encryption throughput | Mean byte entropy | Same plaintext, fresh nonce NPCR/UACI | One-byte change, fresh nonce NPCR/UACI |
|---|---:|---:|---:|---:|---:|
| Grayscale (10 native + 2 derived) | 12 | 1484.22 MiB/s | 7.998619 bits/byte | 99.61445% / 33.46785% | 99.61166% / 33.44699% |
| RGB | 10 | 1229.20 MiB/s | 7.999340 bits/byte | 99.61670% / 33.44238% | 99.61423% / 33.47626% |

Fresh nonce randomness yields near-ideal NPCR/UACI in both same-plaintext and one-byte-change comparisons. Thus those scores do not isolate plaintext diffusion or prove security. Throughput is implementation- and machine-specific and is not comparable directly with reported timings from the six papers.

## Scope and rights

This is a mode-preserving reference-cipher baseline, not a reproduction of any supplied chaos-based cipher and not a general security proof. The unsafe nonce-reuse experiment is a protocol-misuse control. Keep third-party image panels out of a submission until image reuse permissions are confirmed; cite the dataset and retain its per-image rights notes.
