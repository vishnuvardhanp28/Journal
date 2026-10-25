# Geng et al. specification and seed-edge audit

## Scope and source checks

This audit examines the Geng et al. image-encryption description in the supplied PDF and the paper's stated seed equations. The article was text-extracted and the forward-method pages (PDF pp. 11–14) and initial system-parameter pages (PDF pp. 4–5) were visually inspected. No full cipher, inverse, or confidentiality attack is claimed here.

## Reproducibility gaps verified in the paper

1. **Plaintext-derived starting state without a described delivery path.** Figure 11 and Eqs. (13)–(15) use the plaintext image pixels as SHA-256 input to derive four chaotic starting values. The depicted flow does not show how a receiver obtains those values before decryption, and the article does not specify an external key/initial-state transmission protocol.
2. **No decryption procedure is specified.** The methods pages give the forward shuffle and DNA diffusion. The next section begins the security analysis; the article reports decrypted outputs but does not give inverse steps or decryption equations. A faithful round-trip implementation cannot be reconstructed from the paper text alone.
3. **Eq. (17) conflicts with its prose.** The displayed equation defines W1 using y(i), while the paragraph introducing the equation and the diffusion steps refer to W. The earlier partial audit measured a 99.61% keystream-position difference for these readings under one explicitly chosen RK4 setting; that setting is not author-verified.
4. **Numerical integration is underspecified.** The article says the ODE is iterated but does not state an integrator, step size, or finite-precision convention for the image cipher.
5. **The illustrated parameter settings differ.** The phase-diagram example on PDF p. 4 uses e=5, while the Lyapunov example on PDF p. 5 uses e=-0.98. The paper does not separately identify the exact parameter tuple used for the image-encryption tables. These may be distinct analysis settings, but the encryption configuration remains unclear.
6. **Eq. (14) has undefined denominators for valid inputs.** The equations divide by XOR aggregates e2, e4, e6, and e8, and the paper states no zero-denominator handling.

## Executed zero-denominator test

The seed equations were run on every grayscale asset in the curated USC-SIPI subset. **11 of 12 succeeded; image 5.1.09 did not.** For its pixel-byte SHA-256, the four XOR aggregates were `[224, 223, 0, 8]`, so the third XOR denominator is zero. The implemented equation transcription raises a `ValueError` for this input.

A second experiment generated 10,000 unique one-pixel modifications of the 512×512 Mandrill/Baboon benchmark (USC-SIPI 4.2.03). The probe sequence is reproducible with seed `1196641863`. **161/10,000 (1.61%)** produced at least one zero XOR denominator; the Wilson 95% interval is 1.38–1.88%. If the four disjoint SHA-256 byte-group XORs are modeled as independent uniform bytes, the expected probability is `1-(255/256)^4 = 1.553%`, or about 155 of 10,000. The first failure was query 43, changing pixel (row 195, column 6) from 97 to 19; its first XOR aggregate was 0 and the seed implementation raised the expected exception.

This establishes an **input-dependent seed-generation failure** in the published formula as written. It does not demonstrate plaintext recovery, key recovery, or compromise of successfully processed images. The auditable code and machine-readable output are `../code/audit_geng_seed_edge_case.py` and `geng_seed_edge_case_audit.json`.

## Consequence for this study

The Geng method cannot yet serve as a faithful end-to-end cipher reproduction: its paper omits inverse operations and the numerical configuration, contains a conflicting keystream equation, and has an unhandled zero-denominator case. We should report these as specification/availability findings, not as a successful cryptanalytic break. Next, implement a different supplied method whose forward and inverse procedures are fully specified; retain Geng as a reproducibility case study unless author-provided details resolve the gaps.

## Source

Geng et al., “Image encryption scheme based on thorp shuffle and pseudo dequeue,” *Scientific Reports* 15, 11141 (2025), DOI: https://doi.org/10.1038/s41598-025-95263-9. The relevant method is PDF pp. 11–14; the illustrated system settings are on PDF pp. 4–5.
