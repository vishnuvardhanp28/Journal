# Niu et al. deterministic chosen-plaintext equality analysis

## Source basis

The Niu et al. article derives its per-image initial state from the input image's SHA-256 digest and column averages (Eqs. 8-10), then generates chaotic sequences from those initial values and applies deterministic sorting, bit rearrangement, crossover/mutation masks, and ciphertext feedback (Eqs. 11-17). The published image procedure does not specify a fresh nonce, random salt, or other per-encryption random input. It says decryption is the inverse of encryption but does not give the inverse steps. Source: Niu et al., *Scientific Reports* 14, 7033 (2024), DOI 10.1038/s41598-024-57756-x; [publisher article](https://www.nature.com/articles/s41598-024-57756-x), Sections “Key generation” and “Complete the encryption process.”

## Threat model and assumptions

- Attacker has chosen-plaintext encryption access under one fixed external initial key.
- Queries use images of the same dimensions, channel mode, and output formatting.
- The implementation follows the published per-image initialization and resets to the fixed external key for each image.
- Encryption is deterministic, as the published steps specify no fresh per-message nonce or random input.
- The correctness claim means two distinct plaintext images cannot produce the same ciphertext under the same fixed key and format; otherwise decryption could not return the correct distinct inputs.

The conclusion is conditional on this stateless interpretation. An undocumented stateful mechanism or per-message random input would change the analysis and needs to be specified and tested.

## Distinguisher

1. Choose distinct, equal-size images `P0` and `P1`.
2. Query `P0` and store `C0 = Enc_K(P0)`.
3. Submit `(P0, P1)` as the challenge pair and receive `C* = Enc_K(Pb)`.
4. Guess `b = 0` if `C* == C0`, else guess `b = 1`.

For deterministic, correct encryption, the guess is always right: `C* == C0` exactly when `Pb == P0`. The challenge success probability is 1, the maximum in the standard IND-CPA game. This establishes repeated-message equality leakage under the assumptions above. It does not recover any image content, key, or internal state.

This analysis follows directly from the published deterministic interface; it is not an empirical run of the complete Niu cipher. The separate `audit_niu_key_schedule.py` script implements only Eqs. (8)-(10), not the full encryption procedure. The ODE solver, integration step size, hash-byte serialization, and inverse procedure remain unspecified or under-specified in the paper.
