"""Probe the published cyclic-XOR diffusion equations in Zhang et al. (2024).

This is an equation-level chosen-plaintext collision audit, not a complete
Qiskit or chaotic-cipher reproduction. It transcribes Eqs. (11)--(16) from
the supplied PDF. Under fixed keys, all inputs other than A1 are held fixed.
"""
from __future__ import annotations

import json
import hashlib
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "zhang_diffusion_collision_audit"
SEED = 20261025
SIZES = [(2, 2), (4, 4), (8, 8), (16, 12), (32, 32)]
TRIALS_PER_SIZE = 100


def rotate_right(values: list[int], amount: int) -> list[int]:
    amount %= len(values)
    return values[-amount:] + values[:-amount] if amount else values[:]


def diffusion(a1: list[int], a2: list[int], b1: list[int], b2: list[int]) -> tuple[list[int], list[int]]:
    """Apply the paper's Eqs. (11)--(16) to bit sequences (0/1 values)."""
    length = len(a1)
    if not (length == len(a2) == len(b1) == len(b2)):
        raise ValueError("all bit sequences must have the same length")
    a11 = rotate_right(a1, sum(a2))  # Eq. (11) shift
    out1 = [0] * length
    out1[0] = a11[0] ^ a11[-1] ^ a2[0] ^ b1[0]  # Eq. (12)
    for i in range(1, length):
        out1[i] = a11[i] ^ a11[i - 1] ^ a2[i] ^ b1[i]  # Eq. (13)

    a22 = rotate_right(a2, sum(out1))  # Eq. (14), then right shift
    out2 = [0] * length
    out2[0] = a22[0] ^ a22[-1] ^ out1[0] ^ b2[0]  # Eq. (15)
    for i in range(1, length):
        out2[i] = a22[i] ^ a22[i - 1] ^ out1[i] ^ b2[i]  # Eq. (16)
    return out1, out2


def image_groups(rng: random.Random, height: int, width: int) -> tuple[list[int], list[int]]:
    """Encode an 8-bit image using upper 4 planes for A1, lower for A2."""
    pixels = [rng.randrange(256) for _ in range(height * width)]
    a1 = [(pixel >> bit) & 1 for bit in range(7, 3, -1) for pixel in pixels]
    a2 = [(pixel >> bit) & 1 for bit in range(3, -1, -1) for pixel in pixels]
    return a1, a2


def run() -> dict:
    rng = random.Random(SEED)
    rows = []
    total = 0
    for height, width in SIZES:
        length = 4 * height * width
        matches = 0
        for _ in range(TRIALS_PER_SIZE):
            a1, a2 = image_groups(rng, height, width)
            b1 = [rng.randrange(2) for _ in range(length)]
            b2 = [rng.randrange(2) for _ in range(length)]
            c1, c2 = diffusion(a1, a2, b1, b2)
            complemented = [bit ^ 1 for bit in a1]
            c1_prime, c2_prime = diffusion(complemented, a2, b1, b2)
            if c1 == c1_prime and c2 == c2_prime:
                matches += 1
            else:
                raise AssertionError(f"collision identity failed at {height}x{width}")
        rows.append({"height": height, "width": width, "trials": TRIALS_PER_SIZE,
                     "ciphertext_diffusion_collisions": matches,
                     "all_trials_collide": matches == TRIALS_PER_SIZE})
        total += matches

    # Exhaust every possible A1, A2, b1, and b2 at the smallest valid
    # diffusion length (L=4), rather than relying only on random probes.
    exhaustive_length = 4
    exhaustive_limit = 1 << exhaustive_length
    exhaustive_cases = 0
    exhaustive_collisions = 0
    for a1_value in range(exhaustive_limit):
        a1 = [(a1_value >> bit) & 1 for bit in range(exhaustive_length - 1, -1, -1)]
        complemented = [bit ^ 1 for bit in a1]
        for a2_value in range(exhaustive_limit):
            a2 = [(a2_value >> bit) & 1 for bit in range(exhaustive_length - 1, -1, -1)]
            for b1_value in range(exhaustive_limit):
                b1 = [(b1_value >> bit) & 1 for bit in range(exhaustive_length - 1, -1, -1)]
                for b2_value in range(exhaustive_limit):
                    b2 = [(b2_value >> bit) & 1 for bit in range(exhaustive_length - 1, -1, -1)]
                    out = diffusion(a1, a2, b1, b2)
                    paired_out = diffusion(complemented, a2, b1, b2)
                    exhaustive_cases += 1
                    exhaustive_collisions += out == paired_out
    if exhaustive_collisions != exhaustive_cases:
        raise AssertionError("exhaustive L=4 diffusion collision check failed")
    corpus = ROOT / "data" / "benchmarks" / "usc_sipi" / "grayscale"
    corpus_rows = []
    for image_path in sorted(corpus.glob("*.tiff")):
        with Image.open(image_path) as im:
            if im.mode != "L":
                continue
            width, height = im.size
            pixels = list(im.get_flattened_data())
        a1 = [(pixel >> bit) & 1 for bit in range(7, 3, -1) for pixel in pixels]
        a2 = [(pixel >> bit) & 1 for bit in range(3, -1, -1) for pixel in pixels]
        paired_pixels = [pixel ^ 240 for pixel in pixels]
        a1_paired = [(pixel >> bit) & 1 for bit in range(7, 3, -1) for pixel in paired_pixels]
        a2_paired = [(pixel >> bit) & 1 for bit in range(3, -1, -1) for pixel in paired_pixels]
        if a1_paired != [bit ^ 1 for bit in a1] or a2_paired != a2:
            raise AssertionError(f"pixel-mask mapping failed: {image_path.name}")
        length = 4 * height * width
        b1 = [rng.randrange(2) for _ in range(length)]
        b2 = [rng.randrange(2) for _ in range(length)]
        c1, c2 = diffusion(a1, a2, b1, b2)
        c1_prime, c2_prime = diffusion(a1_paired, a2_paired, b1, b2)
        same = c1 == c1_prime and c2 == c2_prime
        if not same:
            raise AssertionError(f"corpus collision identity failed: {image_path.name}")
        corpus_rows.append({"file": image_path.name, "sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
                            "paired_plaintext_sha256": hashlib.sha256(bytes(paired_pixels)).hexdigest(),
                            "height": height, "width": width, "plaintext_pair": "P and P XOR 240 at every pixel",
                            "same_post_diffusion_sequences": same})
    if not corpus_rows:
        raise FileNotFoundError(
            f"No grayscale USC-SIPI TIFFs found in {corpus}. "
            "Obtain the licensed/source-appropriate assets listed in the benchmark manifest and place them here."
        )

    result = {
        "paper": "Zhang, Zhou, and Luo (2024), Nonequal-length image encryption based on bitplane chaotic mapping",
        "source": "supplied PDF s41598-024-58612-8.pdf, journal pp. 6-7, Eqs. (11)-(16), (17), (20)-(29)",
        "scope": "Equation-level chosen-plaintext collision audit of the binary diffusion stage; not a complete Qiskit/chaotic-cipher implementation.",
        "assumptions": [
            "fixed secret keys and deterministic key streams, as described in the published steps",
            "A1 is the concatenation of four higher bitplanes and A2 of four lower bitplanes; complementing all A1 bits corresponds to XORing each 8-bit pixel with 240",
            "the subsequent confusion and Arnold stages are deterministic functions of the diffusion outputs and the fixed key/shape"
        ],
        "identity": "For cyclic binary difference D(x)[0]=x[0] XOR x[L-1], D(x)[i]=x[i] XOR x[i-1], complementing every bit leaves D(x) unchanged. Thus A1 and NOT(A1) produce identical B1; A2, sum(B1), B2, and downstream deterministic ciphertext remain identical.",
        "probe_seed": SEED,
        "trials_per_size": TRIALS_PER_SIZE,
        "sizes": rows,
        "total_collisions": total,
        "total_trials": TRIALS_PER_SIZE * len(SIZES),
        "exhaustive_small_sequence_check": {
            "sequence_length": exhaustive_length,
            "cases_over_all_A1_A2_b1_b2": exhaustive_cases,
            "collisions": exhaustive_collisions,
            "all_cases_collide": exhaustive_collisions == exhaustive_cases
        },
        "usc_sipi_grayscale_assets_checked": len(corpus_rows),
        "usc_sipi_asset_records": corpus_rows,
        "usc_sipi_pair_collisions": sum(row["same_post_diffusion_sequences"] for row in corpus_rows),
        "interpretation": "The published deterministic mapping is non-injective under the stated assumptions. A correct decryptor cannot recover both distinct plaintexts from the same ciphertext. This is an equation-derived collision, not key recovery, and would be avoided if the paper's implemented algorithm contains an unreported input-dependent operation or randomization."
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "zhang_diffusion_collision_audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (OUT / "zhang_diffusion_collision_audit.md").write_text(
        "# Zhang et al. (2024) cyclic-XOR collision audit\n\n"
        "The probe transcribes Eqs. (11)--(16) from the supplied PDF. In the first diffusion stage, each output bit is the cyclic XOR difference of the shifted `A1` bit and its predecessor, XORed with values from `A2` and key stream `b1`. The same cyclic-difference operation appears in the second stage.\n\n"
        "For any binary sequence `x`, complementing every bit leaves its cyclic difference unchanged: `(x[i] XOR 1) XOR (x[i-1] XOR 1) = x[i] XOR x[i-1]`, including the wraparound first element. Holding `A2`, keys, and dimensions fixed therefore makes the first-stage output `B1` identical for `A1` and its complement. The later seed `s0 = mod(sum(B1)/L, 1)` is then also identical, so deterministic confusion and the Arnold permutation receive identical inputs and produce identical ciphertexts. With four upper bitplanes assigned to `A1`, the two source images differ by XOR mask `240` at every pixel.\n\n"
        f"An exhaustive check of every $(A_1,A_2,b_1,b_2)$ tuple at $L=4$ confirmed the identity in {exhaustive_collisions}/{exhaustive_cases} cases. The seeded probe also checked {TRIALS_PER_SIZE * len(SIZES)} cases over five synthetic image sizes; all {total} paired diffusion outputs collided. A separate check applied the same complement to {len(corpus_rows)} grayscale USC-SIPI assets and found {len(corpus_rows)} matching post-diffusion output pairs. Source hashes and dimensions are in `zhang_diffusion_collision_audit.json`.\n\n"
        "**Scope:** this is a mathematical chosen-plaintext collision argument plus a direct test of the transcribed diffusion equations. It is not an end-to-end reproduction of the Lorenz sequence generation, quantum circuit, or image cipher, and it does not recover a key. It assumes the later stages are deterministic functions of the listed diffusion outputs and fixed keys. The authors should clarify whether an omitted operation or per-message randomization is used.\n",
        encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
