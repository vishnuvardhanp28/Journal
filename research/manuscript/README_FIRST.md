# Overleaf-ready IEEE journal research draft

This package follows the IEEE Transactions template you supplied. The sample declares `lettersize`, but the included `IEEEtran.cls` does not define that option; this source uses the class-supported `letterpaper,journal` options for the same US letter journal layout. It contains the manuscript, BibTeX references, the supplied `IEEEtran.cls`, and the study-methodology, image-comparison, metric-comparison, color, and grayscale figures.

## Import and compile

1. In Overleaf, create a blank project and upload this ZIP.
2. Set `main.tex` as the main document.
3. Compile with pdfLaTeX and BibTeX (Overleaf's standard IEEE setup).

The malformed math delimiters in the old workflow diagram are fixed. The methods overview is a parallel-path flow diagram (`fig:workflow`). The study-methodology figure is placed in Methods. The image montage (`fig:image-montage`) follows the image-results discussion and mirrors your reference layout: original, display-only ciphertext preview, and decryption columns. Separate RGB and grayscale figures (`fig:color-demo`, `fig:gray-demo`) show their histograms beside those examples. The literature comparison chart and attack/metric tables are placed in Results near the related text; figures and tables are placed near the paragraphs that discuss them, with flexible float placement to avoid unnecessary float-only pages.

## Figures and scope

The ciphertext panels are visual previews made by reshaping encrypted pixel-body bytes. They are not ciphertext files and cannot be decrypted. The actual authenticated encrypted files use the binary `.imgenc` format and are in the separate image-demo package. The grayscale visual examples are luminance conversions of the two USC-SIPI photographs 4.1.07 and 4.1.08; decryption was verified pixel-for-pixel.

The paper reports control tests using AES-256-GCM and ChaCha20-Poly1305, plus bounded equation-level audits. It does not claim complete implementations or attacks on all six custom schemes. The added citations to P. Vishnu Vardhan's coauthored work are relevant context and do not change the six-paper audit set.

The author is listed as **P. Vishnu Vardhan**, with the Department of Computer Science, SRM University AP, Amaravati 522240, Andhra Pradesh, India; email `vishnuvardhan_p@srmap.edu.in`; ORCID `0009-0007-5130-4011`. This package remains a research draft and is not submission-ready or a guarantee of journal acceptance. Current IEEE/TIFS requirements, source rights for all data, citations, affiliation details, and successful compilation must be checked before submission.

The revised manuscript includes (1) a six-paper comparison of reported entropy and NPCR/UACI results, (2) a paper-by-paper matrix for entropy/histogram, correlation, noise/cropping, CPA, KPA/COA, timing, brute-force/key sensitivity, and scrambling-only coverage, and (3) clear separation between source-paper claims and tests actually run here. Published values use different data and protocols, so the tables are descriptive and do not rank cipher strength. The supplement also includes `results/published_paper_metric_comparison.csv`.

This is a reproducibility-audit manuscript, not a newly proposed chaos-based encryption algorithm. It does not include a new chaotic-system graph because the reviewed generators are not independently reproduced end to end; plotting one without its complete system and numeric settings would misrepresent the study. The manuscript montage includes all 10 original grayscale and all 10 original color benchmark images, each alongside a ciphertext-byte preview and exact decrypted image. The 22-image quantitative corpus also includes two grayscale transformations. USC-SIPI notes that copyright is unknown for many images; clear reproduction rights for all displayed assets before submission.
