# Technical limitations review of the six supplied papers

This review separates author-stated limitations from additional issues to investigate. No complete scheme has yet been reimplemented. Two bounded scheme-specific findings are now established from published equations: Niu's stateless deterministic reading leaks repeated-message equality, and Zhang's cyclic-XOR diffusion is non-injective under the stated fixed-key steps. The Zhang result demonstrates a decryption-correctness failure for a chosen plaintext pair; it does not recover a key or plaintext. Other scheme-specific vulnerabilities remain unverified.

## Paper-by-paper review

### 1. Niu, Zhou & Zhang (2024): improved 4-D chaotic system and evolutionary operators
**Paper:** *Image encryption scheme based on improved four-dimensional chaotic system and evolutionary operators*, Scientific Reports 14, 7033 (2024), DOI 10.1038/s41598-024-57756-x.

- **Stated limitations:** The conclusion does not identify a specific failure mode; it suggests exploring additional image-security schemes using chaotic systems and evolutionary strategies.
- **What to test:** The paper discusses high-dimensional system complexity, but the proposed scheme needs an independently measured runtime/memory profile. Recompute effective key entropy under the actual numeric representation. Test recoverability under explicit known- and chosen-plaintext attacks instead of treating statistical tests as an attack substitute.
- **Potential response in our study:** Provide a finite-precision implementation, attack scripts, key-space accounting based on representable keys, and hardware-specific throughput measurements.

### 2. Zhang, Zhou & Luo (2024): nonequal-length bitplane chaotic mapping / quantum image encryption
**Paper:** *Nonequal-length image encryption based on bitplane chaotic mapping*, Scientific Reports 14 (2024), DOI 10.1038/s41598-024-58612-8.

- **Stated limitations:** No concrete limitation is identified in the conclusion.
- **What to test:** The work reports quantum-image simulation and Qiskit validation. Simulation does not establish feasibility on quantum hardware or prove end-to-end quantum speedup. Account for qubit count, circuit depth, gate count, state preparation, measurement, classical preprocessing, and conversion cost. Verify the results independently for rectangular/color images and larger resolutions.
- **Potential response in our study:** Report complete resource counts and separate simulator results from any hardware-backed claims. Compare full pipeline cost against conventional authenticated encryption.

### 3. Zhu & Zhu (2024): visual security, multi-key selection, and compressed sensing
**Paper:** *A visual security multi-key selection image encryption algorithm based on a new four-dimensional chaos and compressed sensing*, Scientific Reports 14 (2024), DOI 10.1038/s41598-024-66320-6.

- **Stated limitation:** The authors explicitly report poor decryption when noise is stronger and under cropping/pruning attacks. Their explanation is that the carrier-image feature code extracted from an attacked ciphertext may differ from the original carrier feature code.
- **What to test:** Map the failure boundary by attack type, location, and severity; measure both recovered-image quality and whether decryption failure is reliably detected. Test whether a corrupted visual ciphertext can be accepted as a valid result.
- **Potential response in our study:** Add authenticated payloads and controlled error-correction/embedding tests, then report the recovery-versus-detection trade-off. Authentication detects corruption; it does not itself recover lost content.

### 4. Yan, Liu & Li (2025): conservative chaotic system and DNA color-image encryption
**Paper:** *DNA color image encryption based on conservative chaotic system*, Scientific Reports 15 (2025), DOI 10.1038/s41598-025-93649-3.

- **Stated limitations:** The conclusion proposes future use in secure communication and other data-encryption domains but does not state a specific failure of the reported image scheme.
- **What to test:** Reproduce the reported behavior across more than a few examples; evaluate finite-precision key behavior, exact key/parameter sensitivity, chosen-plaintext attacks, implementation cost, and repeat-encryption behavior. Check whether the image-derived key schedule can be implemented and synchronized without leaking or requiring undocumented state.
- **Potential response in our study:** State the adversary model and include attacks that attempt recovery, distinguisher advantage, or integrity violation, not only visual/statistical tests.

### 5. Geng et al. (2025): Thorp shuffle and pseudo dequeue
**Paper:** *Image encryption scheme based on thorp shuffle and pseudo dequeue*, Scientific Reports 15 (2025), DOI 10.1038/s41598-025-95263-9.

- **Stated limitations:** The authors say the study focuses mainly on grayscale images and identify extension to color images and improved speed/computational efficiency as future work.
- **What to test:** End-to-end color support, channel interactions, memory use, and performance as image size grows. Verify claimed key-space and attack resistance against explicit attack procedures.
- **Potential response in our study:** Include grayscale and RGB workloads at multiple resolutions, use a reproducible timing protocol, and compare against AES-GCM/ChaCha20-Poly1305 under the same machine and byte interface.

### 6. Al-Dayel et al. (2025): 4-D chaotic system and cellular automaton
**Paper:** *An image encryption scheme using 4-D chaotic system and cellular automaton*, Scientific Reports 15 (2025), DOI 10.1038/s41598-025-95511-y.

- **Stated limitations:** No concrete limitation is clearly stated in the conclusion.
- **What to test:** Audit the security model and the operational key-space calculation; test key reuse, weak/invalid keys, finite-precision behavior, known/chosen-plaintext resistance, tamper detection, and scaling. Treat entropy, correlation, NPCR, and UACI as descriptive properties rather than proof of resistance.
- **Potential response in our study:** Provide an executable independent reproduction and record any reproducibility gaps, then apply attacks consistent with an explicit threat model.

## Shared weaknesses to test across the set

1. **Metric-to-security leap:** Histograms, entropy, adjacent-pixel correlation, NPCR, and UACI describe output statistics and input sensitivity. They do not establish security against chosen-plaintext or chosen-ciphertext attacks. A separate cryptanalysis study has specifically examined limits of using NPCR/UACI alone.
2. **Attacker model:** A paper should state what an attacker can observe or choose, whether keys/nonces repeat, and what counts as a break. Claims like “resists attacks” need attack procedures and outcomes.
3. **Finite precision and key accounting:** A mathematical chaotic system has real-valued state; software uses finite-precision numbers. A key-space estimate must count effective, distinct, usable keys after quantization and invalid/weak parameter exclusions.
4. **Integrity and metadata:** Confidentiality alone does not detect modified ciphertext or corrupted shape/mode metadata. An authenticated-encryption baseline tests both confidentiality and integrity.
5. **Reproducibility and fair comparison:** Record exact datasets, source credits, implementation versions, hardware, timing procedure, and full pipeline costs. Separate authors’ reported results from our reproduced results.
6. **Robustness versus security:** Noise/cropping recovery is a channel/embedding property, not a substitute for cryptographic security. Measure recovery and corruption detection separately.

## Evidence needed before writing strong claims

- Independent reproduction of at least two target schemes, with clear deviations from each paper's algorithm.
- At least one concrete, reproducible attack or a substantial new evaluation methodology. A comparison to standard ciphers alone is not enough for the intended top security venue.
- Multiple licensed images and sizes, repeated timing runs, confidence intervals where appropriate, and all attack inputs/outputs.
- Correct disclosure of limitations; no claim that statistical scores prove security, and no fabricated data or results.

## Cross-paper evaluation gap supported by our control experiment

The supplied papers repeatedly use entropy, pixel correlation, NPCR, and UACI as evidence for security or differential-attack resistance. These are useful descriptive measurements, but they do not answer whether a specified attacker can recover information or cause undetected modification. This is a methodological weakness across the set, not evidence that any particular paper's cipher is broken.

Our control experiment used standard AES-256-GCM and ChaCha20-Poly1305 on six NASA images. With a fresh nonce for each encryption, encrypting an unchanged image twice gave mean ciphertext-body NPCR/UACI of 99.61094%/33.46139%. Encrypting a one-byte-modified image with a fresh nonce gave 99.60945%/33.45821%. The almost identical scores show that nonce randomization alone can produce values interpreted as strong diffusion; NPCR/UACI do not isolate the effect of changing one plaintext pixel when encryption randomness also changes.

In a deliberately unsafe control using the same nonce and key twice, a one-byte plaintext change yielded near-zero body NPCR/UACI, and XORing the two ciphertext bodies exactly recovered the XOR of the two plaintexts in all 12 image/cipher cases. This confirms that those image metrics are not a substitute for checking key/nonce lifecycle and concrete attacks. The test is a known property of stream encryption under nonce reuse; it is not a finding against any of the six supplied papers. The demonstration code labels and isolates this misuse case.

The control harness also verified exact round trips and rejection of ciphertext/tag tampering, altered authenticated metadata, and wrong keys in all 12 cases. This gives a concrete integrity-aware comparison protocol for future reproductions. The measurements remain preliminary: six smoke-test images and one unidentified processor are insufficient for broad performance or generalization claims.

## Revised study scope and target

The defensible study at this stage is an attack-driven evaluation-methodology paper: reproduce selected schemes from the six-paper set, distinguish statistical properties from security claims, and test concrete attacker capabilities under documented finite-precision implementations. The nonce experiment can serve as a control illustrating the metric confound, not as the main novelty. A T-IFS submission is not yet justified. It should remain a conditional target until scheme-specific reproduction and substantive cryptanalysis demonstrate a contribution within the journal's information-security scope. Acceptance at any journal cannot be guaranteed.

### Priority order for scheme reproduction

1. **Al-Dayel et al. (2025):** audit the claimed known/chosen-plaintext resistance and key-space calculation. The text derives a key space from 56 double-precision values and appears to assume about 10^15 possibilities per value; this needs careful checking because floating-point representability is not equivalent to independent uniformly selectable secret entropy. PDF text extraction corrupts superscripts, so verify against the rendered paper before quoting its exponent.
2. **Geng et al. (2025):** the authors explicitly limit the demonstrated scope mainly to grayscale imagery and identify speed/computational efficiency as future work. Reproduce exact algorithm and compare measured end-to-end costs; evaluate whether a stated theoretical complexity and the actual implementation agree.
3. **Zhu & Zhu (2024):** quantify the author-acknowledged degradation under stronger noise and cropping/pruning, and distinguish recovery quality from integrity detection.

These priorities are provisional. A scheme should only be selected for a full reproduction if the published algorithm specifies enough detail to implement it without inventing undocumented behavior.

### Additional reproducibility flags from the Geng et al. text

The method is a higher-priority reproduction candidate, but its description raises concrete audit questions that must be resolved from the equations, figures, and any author code before making a vulnerability claim:

- The chaotic seed derivation says the plaintext pixel data are SHA-256 hashed to produce the initial state, while the key-space section separately counts nine values (four initial states plus five system parameters) at 10^15 choices each. The paper should clarify which of these quantities are secret, externally selected keys, and whether the image-derived state contributes any secret entropy. A chosen-plaintext attacker can compute a hash of a chosen image; whether that enables an attack depends on the role and secrecy of the remaining parameters.
- The paper treats key sensitivity and NPCR/UACI comparisons as evidence against chosen/known-plaintext attacks, but the described section does not provide a concrete attack transcript, recovered secret, or adversarial success criterion. This is a gap in the evidence for the claim, not proof that an attack succeeds.
- The discussion of noise/clipping robustness reports recovered-image quality, while the scheme description does not present an authentication tag or explicit tamper-rejection mechanism. Recovery from corruption and cryptographic integrity should be measured separately.
- The complexity section gives theoretical O(MN log(MN)) and explicitly omits measured machine timings. Independent runtime, memory, and scaling measurements are therefore a direct missing experiment. It also describes grayscale evaluation and defers color extension.

Our first reproduction should therefore verify deterministic behavior for the same image and parameters, key separation (plaintext-derived versus externally chosen), exact inversion for all permutations/diffusion steps, and consistency of the claimed key count with the implemented inputs. A publisher-hosted HTML rendering was checked for the key-space and Eq. (17) statements. Other mathematical notation still needs independent transcription, and any implementation must document every interpretation.

### Executed key-space accounting audit for Geng et al.

The paper states that SHA-256 of the plaintext pixels is transformed into the four chaotic initial values, then estimates the key space as (10^15)^9 by counting those four initial values plus five system parameters (algorithm description, pp. 11–12; key-space discussion, p. 16). Since the four states are deterministic outputs of the plaintext-derived hash under the published description, they are not four additional independent secret choices. The executable arithmetic audit is `code/audit_geng_keyspace.py`; its output is `results/geng_keyspace_audit.json`.

Conditionally assuming the five control parameters are all independent, secret, and each has 10^15 valid choices, the nominal product is 10^75, or 249.14 bits—about 199.32 bits below the paper's 10^135 count. This correction does not make the remaining nominal count small and does not prove a practical attack. The material unresolved point is whether those five parameters are actually secret and how they are selected, constrained, shared, and represented. Decimal precision alone does not establish effective key entropy. This is a reproducible key-space-accounting concern, not a demonstrated plaintext-recovery vulnerability.

### Replication ambiguity: Geng et al., Eq. (17)

The publisher-hosted article confirms that the prose says sequence W is transformed into W1, but displayed Eq. (17) uses y(i) for W1; the diffusion prose then says W is processed. These conflicting instructions change the diffusion stream. This is a verified replication ambiguity, not a security break. The article says supporting data are available from the corresponding author on reasonable request, and gives no code-availability statement.


Publisher-source verification for Geng et al.: https://www.nature.com/articles/s41598-025-95263-9 (Eq. 17 and Data availability). The equation/prose mismatch is confirmed on the publisher HTML page; the article states data are available from the corresponding author on reasonable request.


## Al-Dayel et al. (2025): verified key-space arithmetic and classification concern

The publisher-hosted article gives the total as 10^840. Its component description counts 8 CDS values, 42 KSGP values, and 3 values each for decimal diffusion and conversion. Under the stated 10^15 choices per value, the corresponding component exponents are 120, 630, 45, and 45. The prose instead says each three-value component contributes 10^48, while its final product correctly uses 10^45 for each. The independently runnable check is `code/audit_aldayel_keyspace.py`, with output in `results/aldayel_keyspace_audit.json`.

The same section says the six decimal diffusion/conversion values are obtained from initial/final RGB channel pixel values. Such data-derived or intermediate values are not automatically independent secret-key choices. Excluding only those six would yield a conditional nominal 10^750 if all other 50 values were independent secrets with 10^15 valid choices each; that assumption is not verified, and the corrected number must not be presented as actual security. The scheme description also names secret parameters u, η, σ1–σ3, key1, and key2, while the 56-value enumeration instead lists κi, λi, μi, νi, ϱi, and Si(−1) for the KSGP; the relationship between the named inputs and counted values is not made clear. The ODE also has p, q, r, s, c1–c4, whereas the 8-value CDS count includes x0–w0 and c1–c4; p, q, r, s may be fixed public constants, but this should be stated. The paper needs to identify independent secret inputs and distinguish them from image-dependent state and intermediate values. This is a key-accounting and specification concern, not a demonstrated attack. Source: https://www.nature.com/articles/s41598-025-95511-y, “Key space analysis.”

## Geng et al. (2025): executed seed-equation edge-case audit

The paper's Eq. (14) divides by four XOR aggregates derived from grouped SHA-256 bytes and gives no zero-denominator case. The independent equation transcription fails for grayscale USC-SIPI asset 5.1.09 (one of 12): the third XOR aggregate is zero. In 10,000 unique one-pixel variants of 512×512 USC-SIPI Mandrill/Baboon, 161 (1.61%) had at least one zero XOR denominator (expected under uniform digest bytes: about 1.553%; Wilson 95% interval 1.38–1.88%). The first failure, input-generation seed, pixel, and digest are recorded in `results/geng_seed_edge_case_audit.json`; runner: `code/audit_geng_seed_edge_case.py`.

This is a reproducible input-definedness/availability issue in the stated seed equations, not a confidentiality or key-recovery attack. Visual inspection of PDF pp. 11–14 also confirms that the paper specifies forward encryption steps but no inverse/decryption procedure, despite showing decrypted images. The displayed Eq. (17) still conflicts with prose about W1, and the ODE solver/step size is not reported. Geng therefore cannot yet be treated as a faithful end-to-end reproduction without additional assumptions or author-provided details. Full evidence: `results/geng_specification_audit.md`.

## Niu et al. (2024): equation-level state audit and conditional CPA equality distinguisher

A new script transcribes the initial-state schedule in Eqs. (8)-(10) only: `code/audit_niu_key_schedule.py`. Using row-major grayscale byte serialization as an explicit SHA-256 assumption and the paper's example external base values, nearest-rounded states changed for all 1,000 seeded one-pixel probes of image 4.2.03. A floor-fraction variant differed on 7/12 grayscale images, but the paper describes the bracket operator as rounding; floor is therefore only a sensitivity variant, not an equally supported reading. Full details are in `results/niu_key_schedule_audit/niu_key_schedule_audit.md` and the JSON/CSV outputs.

The paper's per-image procedure derives states from the image hash and column means, generates deterministic chaotic sequences, and specifies no fresh nonce or random per-encryption input. Under the stateless interpretation with a fixed external key, a chosen-plaintext equality distinguisher queries one image, then recognizes whether the challenge repeats it by ciphertext equality. Correct deterministic encryption is injective for distinct messages of the same format, so the distinguisher succeeds with probability 1. This demonstrates equality leakage and failure of IND-CPA for that interpretation only. It does not recover image contents, a key, or ODE state. An undocumented per-message nonce or persistent state could change the result; the published algorithm does not specify one. This is a specification-based formal argument, not an empirical full-cipher attack. See `results/niu_key_schedule_audit/niu_deterministic_cpa_analysis.md`.

The publisher says generated/analyzed data are included in the article; its article page has no code-availability statement. The paper's decryption description calls it the inverse but omits the actual inverse procedure, and the image-cipher ODE solver and step size are not specified. Thus the full cipher is not independently reproduced in this project.

## Yan, Liu & Li (2025): rendered equation and inverse-procedure audit

I rendered page 12 of the supplied PDF and compared Eq. (10) with the publisher's HTML rendering. Both show the same expression: the $x_1$ line uses $C_2$ in both channel-sum terms, whereas the adjacent $x$ and $x_2$ lines use different channel pairs. The scope of the normalization in the displayed expression is also not unambiguous. This may be a publication or transcription error; the authors' intended formula cannot be inferred safely, so no corrected variant is presented as their method. The paper's decryption section only says to reverse the encryption steps, interchange addition/subtraction, remove padding, and merge channels; it does not specify a complete inverse sequence. These are direct barriers to a faithful independent reproduction, not evidence that the implemented cipher is vulnerable. The source is the supplied PDF, p. 12, cross-checked against the publisher HTML: https://www.nature.com/articles/s41598-025-93649-3.

The Yan scheme is a candidate for a clearly labelled independent variant only if its authors clarify Eq. (10), the exact pseudo-random sequence generation and ODE discretization settings, the DNA coding/operation rule tables, block traversal order, and inverse steps. Any assumed implementation would need its own label and results must not be attributed to an exact reproduction.

## Zhang et al. (2024): non-injective cyclic-XOR diffusion under the published equations

The supplied PDF pp. 6--7, Eqs. (11)--(16), defines a cyclic first difference. Let $D(x)_1=x_1\oplus x_L$ and $D(x)_i=x_i\oplus x_{i-1}$ for $i>1$. Its first diffusion output is $B_1=D(A_{11})\oplus A_2\oplus b_1$. Complementing every bit of $A_1$ complements its cyclic shift $A_{11}$, but leaves $D(A_{11})$ unchanged because both bits in each XOR pair flip. The shift amount depends only on $A_2$, so $B_1$ stays fixed. The second stage depends on the same $A_2$, $B_1$, and fixed key sequence; thus it also remains fixed. The later deterministic swap sequences depend on $s_0=\operatorname{mod}(\sum B_1/L,1)$ and fixed key material, so the same collision propagates through the described ciphertext construction.

For the paper's example grouping of four high and four low bitplanes, the paired image is $P'=P\oplus 240$ at every pixel. `code/audit_zhang_diffusion_collision.py` tested the transcribed diffusion on all 65,536 assignments at L=4, 500 seeded synthetic inputs, and all 12 grayscale USC-SIPI benchmark assets; every pair yielded identical post-diffusion sequences. The JSON records source and paired-image hashes. This is a chosen-plaintext collision and decryption-correctness failure under the stated deterministic equations, not key or plaintext recovery and not an end-to-end reproduction of the Lorenz/quantum circuit. Any undocumented random per-message operation would alter the conclusion and should be clarified by the authors. Evidence: supplied PDF pp. 6--7; output `results/zhang_diffusion_collision_audit/`.
