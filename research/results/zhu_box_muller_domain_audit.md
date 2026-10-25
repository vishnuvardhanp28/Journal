# Zhu & Zhu (2024): printed Box--Muller equation domain audit

## Scope

This audit transcribes Eqs. (20)--(21) from the supplied PDF, page 8, and evaluates their real-valued domain. It is not an end-to-end implementation of the cipher and is not a confidentiality attack. The page was rendered and inspected visually to distinguish the printed equation from a text-extraction issue.

The paper first defines (D_1,D_2) in the interval ((0,1)), then prints

\[
Z_1=\sqrt{(-2\ln D_1)\cos(2\pi D_2)},\qquad
Z_2=\sqrt{(-2\ln D_1)\sin(2\pi D_2)}.
\]

The trigonometric terms are inside the square roots in the supplied version of the article. Since \(-2\ln D_1>0\), a negative cosine or sine gives a negative radicand. For uniform (D_2\in(0,1)), each radicand is negative for half of the domain; at least one is negative for three quarters of the domain. The outputs therefore are not both real over the stated input domain.

## Reproducible check

The script `../code/audit_zhu_box_muller_domain.py` samples one million independent uniform pairs using NumPy's PCG64 generator with seed 20251025. Results:

| Event | Count | Observed proportion | Theoretical proportion |
|---|---:|---:|---:|
| Negative (Z_1) radicand | 499,928 | 49.9928% | 50% |
| Negative (Z_2) radicand | 499,651 | 49.9651% | 50% |
| At least one negative radicand | 750,047 | 75.0047% | 75% |

The standard Box--Muller comparator, where the square root applies to (-2\ln D_1) only and the sine/cosine terms multiply outside, produced finite real values for every sampled pair. This is a comparator, not a verified statement of the authors' intended code.

## Additional reproduction gaps visible in the same section

1. The paragraph after Eqs. (20)--(21) says to transform the sequences into Gaussian measurement matrices, but its matrix construction and SVD optimization equations repeatedly print placeholder-looking expressions such as `[ty, sy] = sort(Y1)` in places where distinct matrices and singular-value terms are required. These are present in the rendered supplied PDF, not only in extracted text.
2. Exact conventions for the two-dimensional DWT basis and boundary handling are not fully specified in the method text, though they affect the sparse matrix and reconstruction.
3. A literal run of Eqs. (20)--(21) cannot be assumed to match the reported results without a rule for negative radicands. Replacing the printed equations with the standard Box--Muller form would be an unverified correction.

## Interpretation

The equations as printed do not define real-valued sequences for 75% of the continuous uniform (D_2) domain. This is a publication-level specification/definedness issue. It does not by itself show that an implementation used by the authors is vulnerable, and it does not recover plaintext or keys. A faithful reproduction requires code, author clarification, or parallel reporting of the literal and explicitly corrected variants.

## Sources

- Zhu, S. and Zhu, C., “A visual security multi-key selection image encryption algorithm based on a new four-dimensional chaos and compressed sensing,” *Scientific Reports*, vol. 14, art. 15496, 2024, DOI: 10.1038/s41598-024-66320-6. See supplied PDF p. 8; the publisher HTML is available at https://doi.org/10.1038/s41598-024-66320-6.
- Box, G. E. P. and Muller, M. E., “A Note on the Generation of Random Normal Deviates,” *The Annals of Mathematical Statistics*, vol. 29, no. 2, pp. 610--611, 1958, DOI: 10.1214/aoms/1177706645.
