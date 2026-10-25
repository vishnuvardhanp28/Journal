"""Arithmetic and key-material classification audit for Al-Dayel et al. (2025).

This script verifies internal exponents in the article's key-space calculation.
It does not assert the effective security level, because several values called
keys may be derived states and their secrecy/provisioning is not sufficiently
specified in the paper.
"""
from __future__ import annotations
import json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'/'aldayel_keyspace_audit.json'
per_value=10**15
components={'CDS':8,'KSGP':42,'decimal_diffusion':3,'decimal_conversion':3}
expected_exponents={name:count*15 for name,count in components.items()}
correct_total_exponent=sum(expected_exponents.values())
prose_total_exponent=120+630+48+48
assert components['CDS']+components['KSGP']+components['decimal_diffusion']+components['decimal_conversion']==56
assert expected_exponents=={'CDS':120,'KSGP':630,'decimal_diffusion':45,'decimal_conversion':45}
assert correct_total_exponent==840 and prose_total_exponent==846

result={
 'paper':'Al-Dayel et al., Scientific Reports (2025), DOI 10.1038/s41598-025-95511-y',
 'scope':'internal key-space arithmetic and key-material classification; not a cryptanalysis',
 'published_breakdown':components,
 'paper_prose_component_exponents':{'CDS':120,'KSGP':630,'decimal_diffusion':48,'decimal_conversion':48},
 'recomputed_component_exponents':expected_exponents,
 'paper_final_product_exponents':[120,630,45,45],
 'verified_total_exponent':correct_total_exponent,
 'literal_prose_product_exponent':prose_total_exponent,
 'arithmetic_observation':'Each three-value component contributes 10^45 under the stated 10^15-per-value assumption; the text says 10^48, while its final product correctly uses 10^45.',
 'key_material_audit':{
   'paper_identifies_56_values_as_keys':True,
   'scheme_text_names_additional_or_unmapped_key_symbols':['u','eta','sigma_1','sigma_2','sigma_3','key1','key2'],
   'mapping_caveat':'The paper does not clearly map these named secret parameters to the 56-value key-space enumeration; p,q,r,s are system parameters in Eq. 1 but omitted from the 8-value CDS count (they may be fixed public constants).',
   'six_decimal_diffusion_and_conversion_values_described_as_derived_from_channel_pixel_values':True,
   'classification':'Data-derived/intermediate values are not automatically independent secret-key choices. Their contribution to effective secret entropy requires an explicit key-generation and adversary model.',
   'conditional_exponent_if_only_those_six_are_removed':750,
   'conditional_warning':'10^750 is only an illustrative upper-bound calculation assuming the other 50 values are independent secrets with 10^15 valid choices each; that assumption is not verified.',
 },
 'limitations':['Decimal precision is not effective secret entropy.','The paper must distinguish independently chosen secret keys from plaintext-dependent, ciphertext-dependent, or intermediate values.','This audit establishes a mismatch in component arithmetic, not a weakness enabling key recovery.']
}
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
