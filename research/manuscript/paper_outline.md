# Working manuscript outline (not yet submission-ready)

## Working title
Beyond Image Statistics: Reproducible Attack-Driven Evaluation of Chaos-Based Image Encryption

## Intended venue
IEEE Transactions on Information Forensics and Security (T-IFS), Q1 in Vishnu's IEEE journal list. Continue with this target only if the work produces substantive attack evidence or a rigorous security-evaluation contribution. The present AEAD benchmark is supporting infrastructure, not the paper's novelty.

## Abstract
**Do not complete until results exist.** The final abstract must state the question, evaluated schemes, attacker model, actual attacks/findings, measured costs, and limits. No result values are to be invented.

## 1. Introduction
- Explain the role of image encryption and the volume of recent chaos-based proposals.
- Identify the evaluation gap: statistical image measures are frequently used to support strong security language.
- State the precise research questions, selected papers, attack model, and contributions after cryptanalysis is complete.
- Avoid claiming all chaotic ciphers are insecure; findings must be scoped to tested schemes and implementations.

## 2. Background and related work
- Summarize the six supplied schemes and distinguish their algorithmic ideas.
- Review cryptanalysis of chaotic image ciphers and limitations of image-statistic-only evaluation.
- Define the relation between descriptive metrics and security notions.

## 3. Threat model and evaluation protocol
- Define known/chosen plaintext and ciphertext capabilities, key reuse, image metadata, and success criteria.
- Specify exact software numeric precision, parameter generation, nonce/state handling, and excluded assumptions.
- Separate confidentiality, integrity, image-quality recovery, and channel robustness.

## 4. Reproduction and attack methods
- Reimplement schemes only from published descriptions; document ambiguities and independent validation.
- Describe each attack in reproducible steps, assumptions, complexity, and what constitutes success.
- Include AES-GCM and ChaCha20-Poly1305 as standard authenticated-encryption references, not as proposed novelty.

## 5. Results
- First show reproduction agreement or divergence from author-reported values.
- Report attack success/failure with inputs, outputs, runtime, key/precision conditions, and confidence bounds.
- Report image statistics only as secondary descriptive evidence.
- Report runtime/memory by image mode and size on a named machine.

## 6. Discussion
- Explain which claims the experiments support and which they do not.
- Explain implications for image-encryption evaluation and for the specific schemes tested.
- Separate performance/robustness trade-offs from cryptographic security.

## 7. Limitations and responsible use
- State limits of the reproduction, datasets, machines, attack budget, and schemes selected.
- Do not generalize to untested algorithms.
- Record image credits/terms and code/data availability.

## 8. Conclusion
- Answer each research question directly using measured evidence only.
