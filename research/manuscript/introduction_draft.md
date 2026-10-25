# Introduction draft — provisional

## 1. Introduction

Digital images carry sensitive information in medical, personal, scientific, and remote-sensing applications. Recent image-encryption proposals have explored high-dimensional chaotic dynamics and combinations with evolutionary operators, bitplane mappings, compressed sensing, DNA encodings, Thorp shuffling, and cellular automata [1–6]. These approaches differ in their algorithms and goals, including color-image protection, unequal-size image handling, and visual-security embedding.

A central evaluation challenge is that an encrypted image can look statistically random without the encryption scheme being secure against a capable adversary. Entropy, histograms, neighbor correlation, NPCR, and UACI can describe selected output properties or plaintext sensitivity. Prior work on chaos-based image cryptosystems cautions that NPCR/UACI are not sufficient security tools on their own and recommends evaluating the security model, implementation, key definition, cost, and known attacks as well [7]. Software implementations also represent chaotic state with finite-precision numbers, so the actual sequence and effective key space must be measured in the implementation rather than inferred only from real-valued equations [7].

The six studies considered here provide a useful set of recent design cases, but their limitations are not uniform. Zhu and Zhu report that their visual-security scheme can lose decryption quality under stronger noise and cropping because the carrier-image feature code may no longer match. Geng and colleagues identify a grayscale focus and the need to improve speed and computational efficiency. The other supplied papers do not state a specific failure in their conclusions; their possible gaps therefore require direct reproduction and attack testing before they can be described as drawbacks [1–6].

This study will evaluate the six schemes under an explicit attacker model and a reproducible implementation protocol. It will separate descriptive image statistics from confidentiality, integrity, robustness, and computational cost. AES-GCM and ChaCha20-Poly1305 will serve as established authenticated-encryption reference implementations, with image metadata authenticated as associated data. NIST specifies GCM as authenticated encryption with associated data; this makes it a useful protocol baseline, not a proposed contribution [8]. The evaluation will report when a published algorithm description is ambiguous, and will distinguish author-reported values from independently reproduced measurements.

The study is organized around four research questions:

1. **RQ1:** Which reported results can be reproduced from the published algorithm descriptions, datasets, and stated implementation details?
2. **RQ2:** Do reproduced schemes withstand scheme-appropriate known- or chosen-plaintext attacks under the stated key and precision assumptions?
3. **RQ3:** Do the schemes detect ciphertext or authenticated-metadata modification, and how do they behave under noise and cropping where robustness is claimed?
4. **RQ4:** What are the end-to-end runtime and memory costs across image types and resolutions relative to authenticated-encryption baselines?

**Contribution statement — pending evidence.** This section will be finalized only after the reproductions and attacks are complete. A comparison of image statistics and execution speed alone will not be presented as a top-tier security contribution. The final paper must identify at least one concrete, reproducible cryptanalytic finding or a substantial new evaluation method and scope each conclusion to the schemes and configurations actually tested.

### References used in this draft

[1] Y. Niu, H. Zhou, and X. Zhang, “Image encryption scheme based on improved four-dimensional chaotic system and evolutionary operators,” *Scientific Reports*, 2024. https://doi.org/10.1038/s41598-024-57756-x

[2] R. Zhang, R. Zhou, and J. Luo, “Nonequal-length image encryption based on bitplane chaotic mapping,” *Scientific Reports*, 2024. https://doi.org/10.1038/s41598-024-58612-8

[3] S. Zhu and C. Zhu, “A visual security multi-key selection image encryption algorithm based on a new four-dimensional chaos and compressed sensing,” *Scientific Reports*, 2024. https://doi.org/10.1038/s41598-024-66320-6

[4] M. Yan, M. Liu, and C. Li, “DNA color image encryption based on conservative chaotic system,” *Scientific Reports*, 2025. https://doi.org/10.1038/s41598-025-93649-3

[5] S. Geng, D. Guo, X. Zhang, Y. Wang, and Y. Niu, “Image encryption scheme based on thorp shuffle and pseudo dequeue,” *Scientific Reports*, 2025. https://doi.org/10.1038/s41598-025-95263-9

[6] I. Al-Dayel et al., “An image encryption scheme using 4-D chaotic system and cellular automaton,” *Scientific Reports*, 2025. https://doi.org/10.1038/s41598-025-95511-y

[7] M. A. Murillo-Escobar, M. O. Meranza-Castillón, R. M. López-Gutiérrez, and C. Cruz-Hernández, “Suggested Integral Analysis for Chaos-Based Image Cryptosystems,” *Entropy*, vol. 21, no. 8, 815, 2019. https://doi.org/10.3390/e21080815

[8] M. Dworkin, “Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC,” NIST SP 800-38D, 2007. https://doi.org/10.6028/NIST.SP.800-38D
