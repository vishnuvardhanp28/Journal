"""Equation-level Niu et al. key-schedule audit, not full cipher reproduction."""
from __future__ import annotations
import csv, hashlib, json, math, random
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/benchmarks/usc_sipi/manifest.csv'
OUT=ROOT/'results/niu_key_schedule_audit'
BASE=(.01,.01,.01,.01); PROBE='4.2.03'; PROBES=1000; SEED=0x4E495532

def matlab_round(x): return math.floor(x+.5) if x>=0 else math.ceil(x-.5)
def derive(a, mode='nearest'):
    a=np.asarray(a,dtype=np.uint8)
    if a.ndim!=2: raise ValueError('grayscale plane required')
    h,w=a.shape
    if w%4: raise ValueError('Eq. 8 requires width divisible by four')
    digest=hashlib.sha256(a.tobytes()).digest(); k=list(digest)
    alpha=[]
    for g in range(4):
        s=g*8; alpha.append(((k[s]^k[s+1]^k[s+2]^k[s+3])+sum(k[s+4:s+8]))/1280)
    col=a.mean(axis=0,dtype=np.float64); raw=[float(col[g*w//4:(g+1)*w//4].mean()) for g in range(4)]
    Q=[x-matlab_round(x) if mode=='nearest' else x-math.floor(x) for x in raw]
    init=[((Q[i]+Q[(i+1)%4]-alpha[i])%1.0)+BASE[i] for i in range(4)]
    return {'sha256':digest.hex(),'width':w,'height':h,'quarter_column_averages':raw,'alpha_beta_gamma_omega':alpha,'initial_values':init,'mode':mode}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with MANIFEST.open(newline='',encoding='utf-8') as f: entries=list(csv.DictReader(f))
    rows=[]
    for e in entries:
        if e['subset']!='grayscale': continue
        with Image.open(ROOT/e['relative_path']) as im: a=np.asarray(im.convert('L'),dtype=np.uint8)
        n=derive(a,'nearest'); fl=derive(a,'floor')
        rows.append({'image_id':e['dataset_id'],'width':a.shape[1],'height':a.shape[0],'sha256':n['sha256'],'nearest_initial_values':n['initial_values'],'floor_initial_values':fl['initial_values'],'interpretations_differ':n['initial_values']!=fl['initial_values']})
    entry=next(e for e in entries if e['dataset_id']==PROBE)
    with Image.open(ROOT/entry['relative_path']) as im: base=np.asarray(im.convert('L'),dtype=np.uint8)
    rng=random.Random(SEED); hashes=set(); nchange=fchange=0
    base_n=derive(base,'nearest')['initial_values']; base_f=derive(base,'floor')['initial_values']; flat=base.ravel()
    for _ in range(PROBES):
        idx=rng.randrange(flat.size); val=rng.randrange(256)
        if val==int(flat[idx]): val=(val+1)%256
        edit=base.copy(); edit.ravel()[idx]=val
        n=derive(edit,'nearest'); f=derive(edit,'floor'); hashes.add(n['sha256'])
        nchange += n['initial_values']!=base_n; fchange += f['initial_values']!=base_f
    result={'scope':'equation-level reproduction of Niu et al. Eqs. (8)-(10), not an end-to-end cipher reproduction','paper':'Niu et al., Scientific Reports 14, 7033 (2024), DOI 10.1038/s41598-024-57756-x','source_equations':'publisher article Eqs. (8)-(10); implementation assumption: SHA-256 over row-major grayscale pixel bytes; digest interpreted as 32 byte values K1..K32','external_base_key':list(BASE),'grayscale_corpus_cases':len(rows),'nearest_vs_floor_variant_differences':sum(x['interpretations_differ'] for x in rows),'variant_note':'The paper text calls the bracket a rounding function. Nearest-integer rounding is the primary transcription; floor is included only as a non-authoritative implementation variant, not an equally supported reading.','corpus_rows':rows,'chosen_input_probe':{'image':PROBE,'unique_one_pixel_edits':PROBES,'probe_seed':SEED,'unique_sha256_outputs':len(hashes),'derived_initial_values_changed_nearest':nchange,'derived_initial_values_changed_floor':fchange},'reproduction_gates':['The paper does not specify the byte serialization passed to SHA-256; row-major uint8 bytes are used here as an explicit assumption.','The article says decryption is the inverse of encryption but does not specify inverse steps.','The image-cipher ODE solver and integration step size are not stated.','Initial state depends on plaintext hash and column averages; the article does not specify how a decryptor obtains those plaintext-derived values without the original plaintext or transmitted auxiliary state.'],'interpretation':'The schedule is deterministic and input-dependent. The floor comparison is an implementation variant only. This audit does not implement ODE integration or image encryption and does not establish a confidentiality break.'}
    (OUT/'niu_key_schedule_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    with (OUT/'niu_key_schedule_corpus.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps({k:v for k,v in result.items() if k!='corpus_rows'},indent=2))
if __name__=='__main__': main()
