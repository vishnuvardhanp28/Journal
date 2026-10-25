"""Audit the literal real-domain behavior of Eqs. (20)-(21) in Zhu & Zhu (2024).

The paper prints sqrt((-2 ln D1) * cos(2 pi D2)) and the corresponding sine
expression. This script samples the stated uniform domain using a fixed PRNG
seed. It separately computes the usual Box-Muller expression as a comparator;
the comparator is not silently substituted into a reproduction.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "zhu_box_muller_domain_audit.json"
N = 1_000_000
SEED = 20251025

def main() -> None:
    rng = np.random.default_rng(SEED)
    u1 = rng.random(N)
    u2 = rng.random(N)
    radius_sq = -2.0 * np.log(u1)
    literal_rad1 = radius_sq * np.cos(2.0 * np.pi * u2)
    literal_rad2 = radius_sq * np.sin(2.0 * np.pi * u2)
    # Standard Box-Muller separates the radial square root from the trig factor.
    standard_z1 = np.sqrt(radius_sq) * np.cos(2.0 * np.pi * u2)
    standard_z2 = np.sqrt(radius_sq) * np.sin(2.0 * np.pi * u2)
    result = {
        "source": "Zhu & Zhu (2024), Scientific Reports 14, 15496, Eqs. (20)-(21)",
        "source_doi": "10.1038/s41598-024-66320-6",
        "scope": "Literal domain audit of printed equations; not a cipher reproduction or attack.",
        "sample_size": N,
        "numpy_generator": "PCG64 default_rng",
        "seed": SEED,
        "inputs": "Independent uniform U1,U2 in (0,1); U1 is sampled strictly above zero.",
        "printed_equation": "Z1=sqrt((-2*ln(U1))*cos(2*pi*U2)); Z2=sqrt((-2*ln(U1))*sin(2*pi*U2))",
        "negative_radicand_z1_count": int(np.count_nonzero(literal_rad1 < 0)),
        "negative_radicand_z1_rate": float(np.mean(literal_rad1 < 0)),
        "negative_radicand_z2_count": int(np.count_nonzero(literal_rad2 < 0)),
        "negative_radicand_z2_rate": float(np.mean(literal_rad2 < 0)),
        "at_least_one_negative_radicand_count": int(np.count_nonzero((literal_rad1 < 0) | (literal_rad2 < 0))),
        "at_least_one_negative_radicand_rate": float(np.mean((literal_rad1 < 0) | (literal_rad2 < 0))),
        "theoretical_rates_for_continuous_uniform_u2": {
            "z1_negative": 0.5,
            "z2_negative": 0.5,
            "at_least_one_negative": 0.75,
        },
        "standard_box_muller_comparator": {
            "expression": "Z1=sqrt(-2*ln(U1))*cos(2*pi*U2); Z2=sqrt(-2*ln(U1))*sin(2*pi*U2)",
            "all_values_finite": bool(np.isfinite(standard_z1).all() and np.isfinite(standard_z2).all()),
            "is_the_authors_intended_formula": "Unverified; this is only the standard comparator.",
        },
        "interpretation": "As printed, the equations do not produce real-valued Z1 and Z2 for much of the stated input domain. The paper may contain a typographical error or rely on an unstated implementation convention. Do not correct it silently; request author clarification or report both interpretations.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
