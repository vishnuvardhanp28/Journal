# Niu et al. Eqs. (8)-(10): key-schedule audit

## Scope

This is an equation-level audit of the published initial-state schedule, not a reproduction of the image cipher. The transcription uses the paper's example external base values (0.01 for each state), SHA-256 on row-major 8-bit grayscale pixel bytes, and MATLAB-style nearest-integer rounding for the bracketed operation in Eq. (8). The paper does not specify the hash byte serialization, so that choice is an explicit assumption.

The floor-fraction calculation is only a sensitivity variant. The article calls the bracket a rounding function, so nearest rounding is the primary implementation; the floor variant is not asserted to be equally faithful.

## Results

- Corpus: 12 grayscale USC-SIPI images.
- Nearest and floor variants yielded different four-value initial states for 7/12 images.
- Chosen-input schedule probe: 1,000 unique one-pixel edits of USC-SIPI image 4.2.03, generated with Python `random.Random(0x4E495532)`.
- All 1,000 edits produced distinct SHA-256 digests; all 1,000 changed the four derived initial values under nearest rounding and under the floor variant.

These findings show that this transcription's schedule is image-dependent for these inputs. They do not demonstrate plaintext recovery, key recovery, or a break of Niu et al.'s full cipher.

## Reproduction gates in the paper

The paper says decryption is the inverse of encryption but omits the inverse steps. It does not name the numerical ODE solver or integration step size used for the image cipher. Since the initial state uses the plaintext digest and column means, a receiver needs a defined way to regenerate that state; the article does not explain whether this requires the original plaintext or separately transmitted auxiliary state.

## Files

- Runner: `code/audit_niu_key_schedule.py`
- Machine-readable results: `results/niu_key_schedule_audit/niu_key_schedule_audit.json`
- Corpus results: `results/niu_key_schedule_audit/niu_key_schedule_corpus.csv`
- Paper: Niu et al., *Image encryption scheme based on improved four-dimensional chaotic system and evolutionary operators*, Scientific Reports 14, 7033 (2024), DOI 10.1038/s41598-024-57756-x. Equations 8-10 and the encryption/decryption description are available on the [publisher article](https://www.nature.com/articles/s41598-024-57756-x).
