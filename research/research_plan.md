# Research plan: attack-driven evaluation of image-encryption claims

## Objective
Develop a reproducible, threat-model-driven evaluation of recent chaos-based image-encryption schemes. Test whether commonly reported image statistics correspond to resistance against practical attacks, document reproducibility and implementation limits, and compare the schemes with authenticated-encryption baselines.

## Venue check against Vishnu's supplied IEEE title list (2026-10-25)
The supplied title list marks IEEE Transactions on Information Forensics and Security (T-IFS, row 164) as Q1, with JIF 8.7. It also marks IEEE Transactions on Dependable and Secure Computing (T-DSC, row 140) and IEEE Transactions on Image Processing (T-IP, row 159) as Q1. T-IFS remains the best conditional fit because its official scope covers information security and explicitly encourages reproducible research. T-DSC is a plausible alternative only if the contribution becomes a system-level dependability/security evaluation; T-IP would need a substantial image-processing method rather than image encryption statistics alone. The T-IFS venue choice is conditional on producing a novel, substantial security contribution; the current control-study draft is not ready for submission. The Society's current author information calls for a clear problem/significance/novelty statement, sufficient experimental evidence, correct scope, ORCID for all authors, and a 13-page maximum for an initial regular-paper submission. Check page count and current policies after compiling a complete author-ready version. Sources: https://signalprocessingsociety.org/publications-resources/ieee-transactions-information-forensics-and-security/about-transactions and https://signalprocessingsociety.org/publications-resources/information-authors.

## Interim findings from the six supplied papers

| Paper | Author-stated limitation | Additional limitation to test (inference, not yet verified by reproduction) |
|---|---|---|
| Niu et al., 2024, improved 4-D chaos + evolutionary operators | No clear concrete limitation stated in the conclusion. | Security conclusions rely mainly on statistical and simulation analyses; need a defined attacker model, cryptanalysis, finite-precision/key-generation analysis, and independently reproducible benchmarks. |
| Zhang et al., 2024, nonequal-length bitplane mapping / quantum image encryption | No clear concrete limitation stated in the conclusion. | Qiskit simulation does not establish practical hardware scaling; verify qubit/gate counts, complete resource costs, and classical preprocessing/postprocessing. |
| Zhu & Zhu, 2024, visual security + compressed sensing | Explicitly reports poor decryption under stronger noise and cropping because carrier-image feature extraction can mismatch. | Test robustness across attack types/intensities, and evaluate whether carrier-derived features create key-management or synchronization failure modes. |
| Yan et al., 2025, conservative chaos + DNA color encryption | No concrete limitation stated; future work points to other security applications. | Validate claims under chosen-plaintext / known-plaintext models, key quantization, and diverse data; assess portability and performance. |
| Geng et al., 2025, Thorp shuffle + pseudo dequeue | Explicitly focuses mainly on grayscale images and identifies efficiency/speed as future work. | Test color and high-resolution performance and use attack experiments beyond image-statistic checks. |
| Al-Dayel et al., 2025, 4-D chaos + cellular automaton | No clear concrete limitation stated in the conclusion. | Audit key-space calculation, threat model, key/nonce handling, and whether standard image metrics justify the cryptographic claims. |

These are preliminary observations from the supplied PDFs, not a completed cryptanalysis. The “additional limitation” column is a research hypothesis to test, not an accusation or established flaw.

## Shared gap to investigate
Entropy, histograms, adjacent-pixel correlation, NPCR, and UACI are useful descriptive measurements. They do not, by themselves, establish confidentiality against chosen-plaintext or chosen-ciphertext attacks, secure key management, or ciphertext integrity. We will pair descriptive metrics with explicit attacker capabilities and attack outcomes. The AEAD reference implementations are baselines, not a novel contribution.

## Target journal
Initial target: IEEE Transactions on Information Forensics and Security (T-IFS), listed as Q1 in the supplied IEEE title list. Its information-security scope is the best match if the final contribution contains substantive cryptanalysis or a rigorous security-evaluation method. IEEE Transactions on Dependable and Secure Computing (T-DSC), also listed Q1, is an alternative if the work develops a broader secure-system evaluation. Venue choice follows scope match and contribution strength.

## Work plan
1. Complete a paper-by-paper extraction of each algorithm, test corpus, metrics, comparisons, limitations, and reproducibility details.
2. Establish a reproducible image corpus with recorded source, credit, license/use note, dimensions, and hashes.
3. Build a runnable harness for image handling, authenticated-encryption baselines, image-statistic reporting, tamper rejection, and benchmark timing.
4. Reproduce selected schemes from the papers only when their algorithm descriptions are sufficiently complete; distinguish reproduced from author-reported numbers.
5. Design and execute scheme-specific known/chosen-plaintext, key/precision, integrity, and robustness tests. Do not claim an attack or repair before it works.
6. Decide whether the evidence supports a genuinely novel contribution suitable for T-IFS/T-DSC. If not, narrow the claim or select a better-fit venue before drafting conclusions.
7. Draft the paper from measured results; preserve scripts, environment information, and dataset attribution.

## Current status and limits
The AEAD benchmark prototype is implemented and has run successfully on six NASA images; source pages, credits, dimensions, and SHA-256 hashes are recorded. The run validated round-trip and tamper checks and exposed a nonce-related NPCR/UACI interpretation pitfall. These images are a software smoke-test set, not a final study dataset. No one of the six chaos-based schemes has yet been independently reproduced or cryptanalyzed. The next substantive milestone is to choose schemes with sufficient algorithm detail, reproduce them, and test explicit attacks. Publication cannot be guaranteed; the eventual work must meet the target journal's novelty and evidence standards.


## New evidence from first paper-specific audit
The Geng et al. paper derives four chaotic initial states from a SHA-256 digest of plaintext pixels, yet counts those states among nine independent values in its nominal key-space product. The new script computes the conditional five-parameter count and states the assumptions explicitly. The result corrects the nominal count from 10^135 to 10^75 only if the remaining five parameters are independently selectable secrets at the assumed precision; it does not establish a practical break. Next, verify parameter secrecy/ranges and reproduce the mapping/diffusion before any chosen-plaintext claim.


A partial Geng keystream implementation now applies both conflicting Eq. (17) readings. Under one disclosed RK4 setting, the W1 arrays differ at 99.61% of 4,096 positions. The paper does not disclose its ODE solver/step size, so this is an implementation-sensitivity result, not a reproduction of the authors reported image outputs. Full scrambling/diffusion and selected attacks remain outstanding.


A second publisher-source audit for Al-Dayel et al. verifies the total exponent 840 and catches the prose/final-product mismatch: three values at 10^15 possibilities contribute 10^45, not 10^48. It also flags six values described as derived from image channel pixels as requiring key-material classification before they are counted as independent secrets. The conditional arithmetic does not imply a key-recovery attack.


## Mode-preserving research corpus added
A curated USC-SIPI subset now contains 12 grayscale TIFF assets (10 native images and grayscale transforms of Mandrill/Baboon and Peppers) and 10 RGB TIFF images, including examples used in the supplied literature. Modes, dimensions, source IDs, transformations, and hashes are recorded. The official database says images are intended for research but warns that many copyrights are unknown; rights status is stored per file. A separate mode-preserving benchmark run completed 44 AEAD reference cases (22 assets × 2 ciphers) with round-trip, tag tamper, metadata tamper, and wrong-key checks. This addresses dataset/mode coverage and harness evaluation, but not yet reproduction of the six proposed ciphers.


A cross-paper test inventory and suite were added. The reference AEAD controls passed 44/44 exact round-trips and rejected 572/572 basic integrity/key probes. This does not test the six custom schemes. Implement a selected target cipher before presenting any security or speed comparison as a result of the proposed paper.

## New Geng specification evidence and next implementation gate
The seed-equation audit found that Eq. (14) is undefined whenever any of four SHA-byte XOR aggregates is zero. This occurred for one curated grayscale benchmark image and 161/10,000 one-pixel chosen-input variants. This is a reproducible seed-stage availability defect, not a confidentiality break. Visual inspection of the supplied Geng PDF also found forward encryption steps but no inverse/decryption procedure; it conflicts on W1 and does not state the ODE solver/step size or image-cipher parameter tuple. This blocks faithful end-to-end reproduction without new assumptions.

## Zhu & Zhu equation-domain finding and current reproduction gate
The follow-up audit rendered the supplied Zhu & Zhu PDF page 8. Eqs. (20)--(21) place the cosine/sine factors inside square roots. Given the paper's stated uniform D1,D2 in (0,1), each equation has a negative radicand on half of the D2 domain, and at least one is negative on 75% of the domain. A fixed-seed one-million-pair run observed 75.0047%. The next paragraph's Gaussian-measurement-matrix/SVD equations also contain repeated placeholder-looking expressions in the published PDF. A literal reproduction is therefore blocked unless the intended Box--Muller formula and matrix construction are clarified. The ordinary Box--Muller form can be evaluated as a separately labeled variant, but must not be substituted and reported as the published method.

The file-level AEAD prototype was run successfully after restoring Python dependencies from `work/python_deps`. It completed 44/44 file round-trips and all pixel-level tamper/wrong-key probes across 22 images and two algorithms. A paired nine-repetition benchmark compared PNG compression levels 6 and 1. Level 1 improved mean file-opening throughput by 39.6% for AES-GCM and 26.9% for ChaCha20-Poly1305 while increasing mean output size by 44.5%; sealing throughput was similar. These figures include Python image decoding/encoding and file I/O, and are not directly comparable with in-memory cipher throughput or the six papers' timing results. The source JSON summary, per-case timing CSV, and `results/image_aead_prototype_results.md` are the authoritative run records.

## Niu et al. equation-level audit added (2026-10-25)
The new `code/audit_niu_key_schedule.py` transcribes Eqs. (8)-(10) only. With row-major grayscale bytes as an explicit SHA-256 serialization assumption, nearest-integer rounding, and the paper's base state values, 1,000 seeded single-pixel edits all changed the resulting initial state. A floor-fraction comparison differed from nearest rounding for 7/12 grayscale corpus images; the article describes the bracketed operator as a rounding function, so floor is only a non-authoritative sensitivity variant. This is not a chosen-plaintext attack on the full cipher. The full cipher is still blocked by the omitted decryption steps and unspecified ODE solver/step size. See `results/niu_key_schedule_audit/niu_key_schedule_audit.md` and JSON/CSV outputs.

### Conditional chosen-plaintext equality distinguisher for Niu et al.
A formal CPA equality distinguisher applies if the published Niu steps are interpreted as stateless deterministic encryption under a fixed external initial key: query one image, then detect whether the challenge repeats it by comparing ciphertexts. Under correctness and the absence of per-message randomization, success is 1. This leaks equality only and is not an empirical run of the full cipher or plaintext recovery. See `results/niu_key_schedule_audit/niu_deterministic_cpa_analysis.md` for the exact assumptions, proof sketch, and reproduction limitations.

## Updated reproduction gate: Yan et al. (2025)
The supplied PDF page 12 and publisher HTML agree on Eq. (10), but the displayed $x_1$ initializer uses the $C_2$ channel sum twice; the normalization scope is unclear. The decryption section gives only a high-level instruction to reverse operations and swap addition/subtraction. A faithful reproduction is therefore not currently supportable. Yan is a candidate for a separately named, assumption-explicit variant only if exact sequence generation, numeric integration, DNA rule tables, traversal, padding, and inverse steps are specified. Do not silently repair Eq. (10) or report variant results as an exact reproduction.

## New direct chosen-input result: Zhang et al. (2024)
Equations (11)--(16) of the supplied Zhang PDF implement a cyclic XOR difference over A1, with A2 and a fixed key stream XORed in. Complementing every bit of A1 is in the kernel of that cyclic difference. Because the shift amount depends only on A2 and the next stage depends on B1, this produces identical downstream deterministic diffusion and ciphertext for distinct paired inputs, assuming the fixed-key steps as written. The equation implementation exhaustively checked all 65,536 assignments of (A1,A2,b1,b2) at L=4, plus 500/500 seeded synthetic pairs and all 12 USC-SIPI grayscale assets. For the paper's example high/low bitplane grouping, the paired plaintext is P XOR 240 at every pixel. This is a correctness/collision result, not key/plaintext recovery or a full Lorenz/Qiskit reproduction. It is now the highest-priority concrete scheme-specific finding. See `code/audit_zhang_diffusion_collision.py` and `results/zhang_diffusion_collision_audit/`.
