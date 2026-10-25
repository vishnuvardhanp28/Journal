"""Check for undefined SHA-seed divisions in Geng et al. Eq. (14).

The paper's Eq. (14) divides by each XOR aggregate e2/e4/e6/e8 without a
stated zero case. This deterministic chosen-plaintext probe starts from a USC-SIPI
gray image and changes one pixel per query. It tests a documented edge condition,
not a confidentiality break.
"""
from __future__ import annotations
import csv, hashlib, json, random, time, math, sys
from pathlib import Path
import numpy as np
from PIL import Image

CODE=Path(__file__).resolve().parent
sys.path.insert(0,str(CODE))
from geng_eq17_variant_audit import seeds_from_plaintext

ROOT=Path(__file__).resolve().parents[1]
IMAGE=ROOT/'data'/'benchmarks'/'usc_sipi'/'grayscale'/'4.2.03_gray.tiff'
OUT=ROOT/'results'/'geng_seed_edge_case_audit.json'
QUERIES=10000
SEED=0x47534E47

def xor_groups(pixels: bytes):
    k=hashlib.sha256(pixels).digest()
    return k.hex(), [int(np.bitwise_xor.reduce(np.frombuffer(k[i:i+8],dtype=np.uint8))) for i in (0,8,16,24)]

def wilson(k,n,z=1.959963984540054):
    phat=k/n; den=1+z*z/n
    center=(phat+z*z/(2*n))/den
    half=z*math.sqrt(phat*(1-phat)/n+z*z/(4*n*n))/den
    return [center-half,center+half]

def main():
    manifest=ROOT/'data'/'benchmarks'/'usc_sipi'/'manifest.csv'
    corpus_checks=[]
    for entry in csv.DictReader(manifest.open(newline='',encoding='utf-8')):
        if entry['subset']!='grayscale': continue
        image_path=ROOT/entry['relative_path']
        with Image.open(image_path) as corpus_im: raw_corpus=corpus_im.convert('L').tobytes()
        try:
            seeds_from_plaintext(raw_corpus)
            corpus_checks.append({'image_id':entry['dataset_id'],'seed_derivation_ok':True})
        except Exception as err:
            digest,xors=xor_groups(raw_corpus)
            corpus_checks.append({'image_id':entry['dataset_id'],'seed_derivation_ok':False,
                                  'sha256_of_pixel_bytes':digest,'xor_aggregates_e2_e4_e6_e8':xors,
                                  'exception':f'{type(err).__name__}: {err}'})
    with Image.open(IMAGE) as im:
        if im.mode!='L': raise ValueError(f'Expected grayscale L image, got {im.mode}')
        original=np.asarray(im,dtype=np.uint8).copy()
    h,w=original.shape; flat=original.ravel(); rng=random.Random(SEED)
    seen=set(); failures=0; first=None; t=time.perf_counter()
    for q in range(1,QUERIES+1):
        idx=rng.randrange(flat.size); value=rng.randrange(256)
        if value==int(flat[idx]): value=(value+1)%256
        pair=(idx,value)
        while pair in seen:
            idx=rng.randrange(flat.size); value=rng.randrange(256)
            if value==int(flat[idx]): value=(value+1)%256
            pair=(idx,value)
        seen.add(pair)
        candidate=original.copy(); old=int(candidate.ravel()[idx]); candidate.ravel()[idx]=value
        raw=candidate.tobytes(); digest,xors=xor_groups(raw)
        zero_groups=[i+1 for i,x in enumerate(xors) if x==0]
        if zero_groups:
            failures+=1
            if first is None:
                try:
                    seeds_from_plaintext(raw)
                    exc=None
                except Exception as err:
                    exc=f'{type(err).__name__}: {err}'
                first={'seed_function_exception':exc,'query':q,'pixel_index':idx,'row':idx//w,'column':idx%w,'old_value':old,
                       'new_value':value,'sha256':digest,'xor_aggregates_e2_e4_e6_e8':xors,
                       'zero_denominator_groups_1_based':zero_groups}
    elapsed=time.perf_counter()-t
    p=1-(255/256)**4
    result={'scope':'chosen-input availability/definedness edge-case audit only; not a confidentiality attack',
      'source_image':IMAGE.name,'source_sha256':hashlib.sha256(IMAGE.read_bytes()).hexdigest(),
      'dimensions':[w,h],'queries':QUERIES,'queries_are_unique_single_pixel_changes':len(seen)==QUERIES,
      'prng_seed_for_probe_generation':SEED,'observed_zero_denominator_queries':failures,
      'curated_gray_corpus_checks':corpus_checks,
      'curated_gray_corpus_pass_count':sum(x['seed_derivation_ok'] for x in corpus_checks),
      'observed_failure_rate':failures/QUERIES,'observed_rate_wilson_95_ci':wilson(failures,QUERIES),
      'expected_failure_probability_if_SHA256_groups_are_uniform':p,
      'expected_failures_at_n':QUERIES*p,'elapsed_seconds':elapsed,
      'first_failure':first,
      'mechanism':'Eq. (14) contains e1/e2, e3/e4, e5/e6, and e7/e8; any zero XOR aggregate in groups 1-4 makes a denominator zero.',
      'interpretation':'This establishes that the published seed formula is undefined for some valid chosen plaintexts under the stated SHA-256 grouping. It does not establish plaintext recovery, key recovery, or a break of the remaining cipher.',
      'reproducibility':'The USC-SIPI source image, SHA-256, one-pixel query generator seed, query count, first failing input description, and output are recorded.'}
    OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()

