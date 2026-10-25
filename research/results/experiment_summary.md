# Exploratory benchmark run: 2026-10-25

## Setup
Six images were downloaded from NASA's Image and Video Library. Their source pages, NASA IDs, creator credits, and download URLs are in `../data/image_manifest.csv`. One candidate image marked with a CC BY-NC-SA credit was excluded and replaced before this run.

The test compares two reference authenticated-encryption implementations: AES-256-GCM and ChaCha20-Poly1305. Each case used a fresh 256-bit random key per image/cipher and newly generated 96-bit nonces. Image bytes and dimensions/mode metadata were authenticated. Nine timing repeats were used per image/cipher; timing is exploratory and machine-specific.

Environment recorded in `environment.json`: Python 3.12.14, Windows 11, AMD64 Family 25 Model 68 (AuthenticAMD), cryptography 50.0.2, NumPy 2.3.5, Pillow 12.3.0.

## Checks

- 12/12 image/cipher cases round-tripped exactly.
- 12/12 cases rejected a flipped ciphertext/tag, altered authenticated metadata, and an incorrect key.
- 12 timing rows and 12 metric-diagnostic rows were written.

## Results

Across the 12 cases, mean byte entropy was 7.99995 bits/byte (range 7.99988–7.99999). Mean encryption throughput was 710.19 MiB/s (range 556.47–1091.46 MiB/s) in this runtime and on this machine; this is not a cross-paper or cross-hardware comparison.

When the same image was encrypted twice with fresh nonces, mean NPCR/UACI between ciphertext bodies was 99.60983% / 33.46169%. A one-byte plaintext change encrypted with another fresh nonce produced 99.60974% / 33.46120%. The near-identical values show that, for this protocol, changing the nonce alone produces near-ideal-looking image-difference scores; those scores do not prove that the plaintext change caused the diffusion.

In the explicitly unsafe nonce-reuse demonstration, a one-byte plaintext change yielded mean NPCR 0.000027% / UACI 0.000000107%, and the ciphertext XOR equaled the plaintext XOR in all 12 cases. This is an implementation failure demonstration, not an attack against any of the six supplied papers. Nonce reuse is prohibited in real use.

## What this does and does not establish

This run validates the benchmark harness and provides a metric-control example. It does not reproduce or cryptanalyze any of the six chaos-based schemes, establish a novel cipher, or justify a security claim about those papers. The intended paper still needs independent scheme reproductions and at least one substantive attack or evaluation contribution. Any final claims will need a larger, fully documented corpus and repeated measurements on identified hardware.

The six NASA images are a smoke-test corpus, not evidence of generalization. A final evaluation needs a larger, license-reviewed corpus with diverse image classes and multiple resolutions.
