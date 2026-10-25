# Image-encryption study workbench

The current code is an exploratory evaluation harness. It is not a new cipher and does not yet reproduce any of the six supplied papers.

## Contents

- `research_plan.md` — research objective, target journal, stages, and limits.
- `limitations_review.md` — author-stated limitations separated from testable hypotheses.
- `code/secure_image_bench.py` — RGB image framing, AES-256-GCM and ChaCha20-Poly1305 baselines, integrity checks, descriptive image metrics, and timing.
- `code/download_nasa_assets.py` — downloads the six listed NASA image assets and records metadata.
- `data/images/` — test images downloaded from NASA's Image and Video Library.
- `data/image_manifest.csv` and `.json` — item title, NASA ID, credited creator, source link, download link, date, and usage note.
- `results/` — latest CSV measurements and environment information.
- `manuscript/paper_outline.md` — a working outline; the abstract and claims wait for actual attack results.

## Run

Use Python 3.12+ and install the packages in `code/requirements.txt`. Run the downloader only when a fresh corpus is needed, then run `secure_image_bench.py` from any working directory. The script locates files relative to its own folder.

The nonce-reuse rows are an intentionally unsafe lab demonstration. The script includes them only to show that image-level NPCR/UACI scores are not security proofs. Never reuse a GCM or ChaCha20-Poly1305 nonce with the same key in a deployed system.

## Citation and image use

Use the per-item credit in `data/image_manifest.csv` if an asset appears in a manuscript or figure. NASA says its content is generally not subject to US copyright, while third-party material may carry separate restrictions; verify each item and follow the current NASA media guidelines before publication. The previous test image with a noncommercial credit was removed from the corpus.

- manuscript/introduction_draft.md — cautious first-pass introduction; the contribution statement is explicitly pending cryptanalysis.

The six NASA images are a software smoke-test corpus only; they are not a sufficient or representative final research dataset. The manifest also records SHA-256 hashes and dimensions. A final study needs a larger, license-checked benchmark with diverse image classes and sizes.

- `code/audit_geng_keyspace.py` — conditional key-space arithmetic audit for the Geng et al. paper; see `results/geng_keyspace_audit.json`. It is not a cipher break.

- `manuscript/preliminary_findings.md` — evidence-backed pilot results and the explicit remaining gates; not a submission-ready manuscript.

- `code/geng_eq17_variant_audit.py` — partial SHA-seed/chaotic-keystream reproduction quantifying both Eq. (17) interpretations; it is not a full cipher reproduction. Results: `results/geng_eq17_variant_audit.json`.

- `code/audit_aldayel_keyspace.py` — verifies key-space arithmetic and flags data-derived key material; not a cryptanalysis. Output: `results/aldayel_keyspace_audit.json`.


## Mode-preserving research image benchmark

- `data/benchmarks/usc_sipi/` contains 10 native grayscale, 10 native RGB, and 2 derived grayscale USC-SIPI TIFF images, with per-file dimensions, SHA-256, source IDs, and rights notes in `manifest.csv`/`manifest.json`.
- The selection includes standard research images such as Mandrill/Baboon, Peppers, and Jelly beans. The official USC-SIPI database describes the images as for research, but warns that many rights are unknown. See the dataset README and do not reproduce image panels in a journal submission until reuse rights are checked.
- `code/prepare_sipi_benchmark.py` re-curates the selected files from the downloaded official archive.
- `code/benchmark_sipi_corpus.py` benchmarks AES-GCM and ChaCha20-Poly1305 while preserving grayscale vs RGB modes; output CSVs and summary are in `results/sipi_*`.



## Paper security test battery

- `code/paper_security_test_suite.py` runs the image-level and integrity diagnostics that can be applied to the current AEAD reference controls. It does not test the six papers' custom ciphers.
- `manuscript/paper_security_test_inventory.md` maps the tests reported by each supplied paper and distinguishes completed, adapted, and cipher-specific pending tests.
- `results/paper_security_test_results.md` summarizes results; per-image timing, statistics, and attack rows are in `results/paper_test_*.csv`.
- Run after installing `code/requirements.txt`: `python code/paper_security_test_suite.py`.

- `code/audit_geng_seed_edge_case.py` probes zero denominators in the Geng et al. SHA-256 seed equations using the grayscale benchmark and 10,000 one-pixel chosen-input variants. Results: `results/geng_seed_edge_case_audit.json`; interpretation and the paper's reproduction gaps: `results/geng_specification_audit.md`.

- `code/audit_zhu_box_muller_domain.py` checks the literal real-valued domain of Eqs. (20)--(21) in Zhu & Zhu (2024) over one million fixed-seed uniform pairs. Results: `results/zhu_box_muller_domain_audit.json` and `results/zhu_box_muller_domain_audit.md`. This is a formula-domain audit, not a cipher break or end-to-end reproduction.

- `code/image_aead_prototype.py` implements an authenticated image container around AES-256-GCM and ChaCha20-Poly1305. `code/evaluate_image_aead_prototype.py` checks pixel and file round-trips, tampering, wrong keys, and repeated file-level timings on the 22-image USC-SIPI subset. Its latest results are in `results/image_aead_prototype_summary.json` and `results/image_aead_prototype_timing.csv`. This remains a reference prototype, not a new cipher or a reproduced chaos-based algorithm.

- `results/image_aead_prototype_results.md` summarizes the latest paired file benchmark at PNG compression levels 6 and 1. The level-1 setting improves file-opening throughput at the cost of larger lossless PNG output; this is a file-serialization trade-off, not a claim of faster encryption than the six papers.

## Niu et al. audit extension
An equation-level audit of Niu et al. Eqs. (8)-(10) now accompanies the Geng and Zhu equation audits. It records the explicit grayscale SHA-256 serialization assumption, evaluates 12 grayscale assets and 1,000 one-pixel probes, and distinguishes the paper's nearest-rounding description from a floor-only variant. It is not an end-to-end reproduction or direct cipher attack. Full reproduction remains blocked by omitted decryption steps and an unspecified ODE solver/step size. Run `python .\code\audit_niu_key_schedule.py` from the research folder to reproduce its output.

## Zhang et al. chosen-input collision audit
The new `code/audit_zhang_diffusion_collision.py` transcribes the published bit-plane cyclic-XOR diffusion equations. Complementing every bit of `A1` leaves its cyclic difference unchanged; with `A2` and fixed key streams held constant, the later deterministic diffusion and confusion inputs also remain identical. For the article's example grouping of upper/lower bitplanes, the paired plaintext is the original grayscale image XOR 240 at every pixel. The equation probe found collisions in all 65,536 assignments at L=4, 500/500 seeded synthetic pairs, and all 12 grayscale USC-SIPI images. This is an equation-level ciphertext collision/correctness result, not key or plaintext recovery and not a complete quantum-cipher reproduction. Source and paired-image hashes are in `results/zhang_diffusion_collision_audit/`.
