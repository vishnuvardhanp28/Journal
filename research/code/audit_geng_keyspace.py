"""Audit the nominal key-space arithmetic in Geng et al. (2025).

This is not a cryptanalysis or a reproduction of their cipher. It formalizes one
conditional accounting issue: the paper derives four initial conditions from a
SHA-256 hash of the plaintext, yet includes those four values in its 9-value
key-space product. If the remaining five control parameters are independent,
secret, and each truly selectable at 10^15 points, their nominal product is
10^75. The paper does not fully specify the parameter provisioning/ranges, so
that conditional count is not asserted as the actual security level.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "geng_keyspace_audit.json"

precision_points_per_value = 10**15
paper_counted_values = 9  # x0,y0,z0,w0,a,b,c,d,e
plaintext_derived_initial_values = 4
remaining_control_parameters = paper_counted_values - plaintext_derived_initial_values

claimed_points = precision_points_per_value**paper_counted_values
conditional_control_parameter_points = precision_points_per_value**remaining_control_parameters
removed_bits = plaintext_derived_initial_values * math.log2(precision_points_per_value)

result = {
    "paper": "Geng et al., Scientific Reports (2025), DOI 10.1038/s41598-025-95263-9",
    "scope": "nominal key-space accounting only; not a cipher reproduction or attack",
    "published_description": {
        "initial_state_source": "SHA-256 of plaintext image pixels; four states x0,y0,z0,w0 derived from digest",
        "key_space_count": "(10^15)^9 = 10^135, counting four initial states plus five control parameters",
    },
    "conditional_audit": {
        "assumption": "only five control parameters are independently selectable secret values, each with 10^15 valid choices",
        "nominal_points": str(conditional_control_parameter_points),
        "nominal_bits": round(math.log2(conditional_control_parameter_points), 6),
        "difference_from_published_count_bits": round(removed_bits, 6),
        "factor_by_which_published_count_exceeds_conditional_count": str(precision_points_per_value**plaintext_derived_initial_values),
    },
    "interpretation": [
        "A deterministic function of the plaintext is not an independent secret key choice.",
        "This does not establish that the scheme is brute-forceable: the conditional five-parameter count remains large if those parameters are secret and independently chosen.",
        "The paper must specify whether the five control parameters are secret, their allowed ranges and quantization, and how sender and receiver establish them.",
        "The actual effective key entropy cannot be inferred from decimal precision alone or from this arithmetic audit.",
    ],
}
assert paper_counted_values == 9 and remaining_control_parameters == 5
assert int(result["conditional_audit"]["nominal_points"]) == 10**75
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
