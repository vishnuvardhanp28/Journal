# Verification report

Run date: 2026-10-26 (Asia/Kolkata). Python 3.12.14 on Windows-11-10.0.26300-SP0 / AMD64.

## Reproduced checks

- Main AEAD control suite: 22 source assets (12 grayscale, 10 RGB), 44 image/algorithm cases, 30 timed in-memory repetitions per case.
- Exact pixel round-trips: 44/44.
- Corruption, metadata, truncation, random wrong-key and one-bit key-change probes: 572/572 rejected, 13 probes per image/algorithm case.
- Image-statistic rows: 44. Maximum-channel chi-square below 293.2478: 42/44 image/algorithm cases. These descriptive tests do not establish cryptographic security.
- Main in-memory mean throughput: AES-GCM 2022.02 MiB/s encrypt and 1917.66 MiB/s decrypt; ChaCha20-Poly1305 1239.89 / 1212.49 MiB/s.
- Image file wrapper: 44/44 exact file round trips; all 44 tamper and all 44 wrong-key probes rejected. File API timing is a separate 9-repeat run because the attempted 30-repeat disk/PNG run exceeded practical runtime and did not produce a new result.
- Expanded color diagnostics: CPA classifier accuracy 48.4--53.0% across four cases, each Wilson 95% interval includes chance; KPA prefix transfer 0/100; 13/13 integrity probes per case rejected. Timing screen p-values in the current run: AES-GCM 0.361, ChaCha20-Poly1305 0.455. An earlier AES p=0.0246 did not reproduce; no side-channel claim is made.
- Ten-by-ten comparison: 20 rows verified exact (10 original grayscale, 10 original RGB); 60 display panels were generated. The displayed ciphertexts are visualization-only; underlying encryption artifacts are binary AEAD containers.

## Research scope limits

AES-256-GCM and ChaCha20-Poly1305 are reference controls, not implementations of the six custom ciphers. The Zhang result is a conditional equation-level collision proof under the equations and deterministic fixed-key interpretation transcribed from the paper; no complete chaotic or quantum system is reproduced. Niu, Geng, Zhu, and other equation audits remain bounded to the specific published equations and assumptions stated in the manuscript. The current work still lacks an independently validated end-to-end reproduction and cryptanalysis of a selected custom cipher, matched cross-paper performance measurements, independent replication, and confirmed image reuse rights. The draft is therefore not yet supported as a TIFS-ready submission.

## Reproduction caveats

The USC-SIPI image TIFFs are omitted from the public supplement because reuse rights are uncertain for much of the corpus. The scripts expect the assets listed in the manifest. The manuscript source passed static structure/reference/image-path checks; this environment did not provide a TeX compiler, so final compilation and visual pagination must be checked in Overleaf.
