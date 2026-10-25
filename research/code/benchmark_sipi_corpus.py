"""Run mode-preserving AEAD controls on the curated USC-SIPI grayscale + RGB set.

This benchmarks standard reference AEADs, not the chaos-based papers' ciphers.
Nonce reuse is exercised only as an explicitly unsafe, isolated control to show
why image-difference scores are not security proofs.
"""
from __future__ import annotations
import csv, hashlib, json, secrets, statistics, struct, sys, time
from pathlib import Path
from PIL import Image
from cryptography.exceptions import InvalidTag

CODE=Path(__file__).resolve().parent
sys.path.insert(0,str(CODE))
from secure_image_bench import (CIPHERS,MAGIC,NONCE_SIZE,TAG_SIZE,canonical_header,
    encrypt,decrypt,parse_envelope,body_bytes,entropy_u8,npcr_uaci)

ROOT=CODE.parent
DATA=ROOT/'data'/'benchmarks'/'usc_sipi'
OUT=ROOT/'results'
REPEATS=9

def read_image(path):
    with Image.open(path) as im:
        if path.parent.name=='grayscale':
            if im.mode not in ('1','L','I;16','I','F'): raise ValueError(f'not grayscale: {path} mode={im.mode}')
            im=im.convert('L')
        else:
            if im.mode not in ('RGB','RGBA'): raise ValueError(f'not color: {path} mode={im.mode}')
            im=im.convert('RGB')
        arr=im.copy()
        return arr.tobytes(),arr.width,arr.height,arr.mode

def metadata_tamper_rejected(envelope,key):
    header,nonce,body,meta=parse_envelope(envelope)
    meta['width']=int(meta['width'])+1
    altered=json.dumps(meta,sort_keys=True,separators=(',',':')).encode()
    frame=MAGIC+struct.pack('>H',len(altered))+altered+nonce+body
    try: decrypt(frame,key)
    except InvalidTag: return True
    return False

def ciphertext_tamper_rejected(envelope,key):
    corrupted=bytearray(envelope); corrupted[-1]^=1
    try: decrypt(bytes(corrupted),key)
    except InvalidTag: return True
    return False

def benchmark(path,algorithm):
    raw,width,height,mode=read_image(path)
    header=canonical_header(algorithm,width,height,mode)
    key=secrets.token_bytes(32)
    first=encrypt(raw,header,key,algorithm)
    recovered,meta=decrypt(first,key)
    assert recovered==raw and (meta['width'],meta['height'],meta['mode'])==(width,height,mode)
    assert ciphertext_tamper_rejected(first,key)
    assert metadata_tamper_rejected(first,key)
    try: decrypt(first,secrets.token_bytes(32))
    except InvalidTag: wrong_key=True
    else: wrong_key=False
    assert wrong_key

    enc_ms=[]; dec_ms=[]
    for _ in range(REPEATS):
        t0=time.perf_counter_ns(); env=encrypt(raw,header,key,algorithm); t1=time.perf_counter_ns()
        opened,_=decrypt(env,key); t2=time.perf_counter_ns()
        assert opened==raw
        enc_ms.append((t1-t0)/1e6); dec_ms.append((t2-t1)/1e6)
    mib=len(raw)/(1024*1024)
    timing={'image_id':path.stem,'mode':mode,'width':width,'height':height,'raw_bytes':len(raw),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'algorithm':algorithm,'repeats':REPEATS,'roundtrip_ok':True,'ciphertext_tamper_rejected':True,'metadata_tamper_rejected':True,'wrong_key_rejected':True,'encrypt_median_ms':statistics.median(enc_ms),'decrypt_median_ms':statistics.median(dec_ms),'encrypt_mib_s':mib/(statistics.median(enc_ms)/1000),'decrypt_mib_s':mib/(statistics.median(dec_ms)/1000)}

    fresh_same=encrypt(raw,header,key,algorithm)
    fresh_other=encrypt(raw,header,key,algorithm)
    same_npcr,same_uaci=npcr_uaci(body_bytes(fresh_same),body_bytes(fresh_other))
    changed=bytearray(raw); changed[len(changed)//2]^=1
    changed_env=encrypt(bytes(changed),header,key,algorithm)
    ch_npcr,ch_uaci=npcr_uaci(body_bytes(fresh_same),body_bytes(changed_env))
    cipher=body_bytes(first)
    metrics={'image_id':path.stem,'mode':mode,'algorithm':algorithm,'ciphertext_entropy_bits_per_byte':entropy_u8(__import__('numpy').frombuffer(cipher,dtype='uint8')),'same_plain_fresh_nonce_npcr_pct':same_npcr,'same_plain_fresh_nonce_uaci_pct':same_uaci,'one_byte_change_fresh_nonce_npcr_pct':ch_npcr,'one_byte_change_fresh_nonce_uaci_pct':ch_uaci}

    # Deliberately unsafe misuse control; never use nonce reuse operationally.
    fixed=b'\xA5'*NONCE_SIZE
    e0=encrypt(raw,header,key,algorithm,nonce=fixed)
    e1=encrypt(bytes(changed),header,key,algorithm,nonce=fixed)
    xor_leak=bytes(a^b for a,b in zip(body_bytes(e0),body_bytes(e1)))
    plain_xor=bytes(a^b for a,b in zip(raw,changed))
    assert xor_leak==plain_xor
    unsafe_npcr,unsafe_uaci=npcr_uaci(body_bytes(e0),body_bytes(e1))
    metrics.update({'nonce_reuse_one_byte_change_npcr_pct_UNSAFE':unsafe_npcr,'nonce_reuse_one_byte_change_uaci_pct_UNSAFE':unsafe_uaci,'nonce_reuse_plaintext_xor_leak_reproduced_UNSAFE':True})
    return timing,metrics

def main():
    manifest=DATA/'manifest.csv'
    with manifest.open(newline='',encoding='utf-8') as f: entries=list(csv.DictReader(f))
    if len(entries)<20: raise SystemExit('Need at least 20 manifest entries')
    gray=sum(x['subset']=='grayscale' for x in entries); color=sum(x['subset']=='color' for x in entries)
    if gray<10 or color<10: raise SystemExit(f'Need >=10 per mode; found gray={gray}, color={color}')
    timing_rows=[]; metric_rows=[]
    for entry in entries:
        path=ROOT/Path(entry['relative_path'])
        for algorithm in CIPHERS:
            timing,metrics=benchmark(path,algorithm)
            timing_rows.append(timing); metric_rows.append(metrics)
            print(f"{path.stem} {timing['mode']} {algorithm}: checks OK, {timing['encrypt_mib_s']:.1f} MiB/s")
    OUT.mkdir(exist_ok=True)
    for name,rows in [('sipi_aead_timing.csv',timing_rows),('sipi_metric_diagnostics.csv',metric_rows)]:
        with (OUT/name).open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    summary={
      'dataset':f'USC-SIPI Volume 3, curated {gray} grayscale + {color} RGB images',
      'image_counts':{'grayscale':gray,'color':color},'algorithm_rows':len(timing_rows),
      'ciphers':list(CIPHERS),'timing_repeats_per_image_cipher':REPEATS,
      'all_roundtrips_ok':all(x['roundtrip_ok'] for x in timing_rows),
      'all_tamper_checks_ok':all(x['ciphertext_tamper_rejected'] and x['metadata_tamper_rejected'] and x['wrong_key_rejected'] for x in timing_rows),
      'all_unsafe_nonce_xor_controls_reproduced':all(x['nonce_reuse_plaintext_xor_leak_reproduced_UNSAFE'] for x in metric_rows),
      'mean_entropy_bits_per_byte':statistics.mean(x['ciphertext_entropy_bits_per_byte'] for x in metric_rows),
      'mean_encrypt_mib_s':statistics.mean(x['encrypt_mib_s'] for x in timing_rows),
      'note':'Exploratory reference-cipher measurements only; no supplied chaos-based cipher is reproduced here. Metrics/throughput are not universal security claims. Rights notes are in the dataset manifest.'}
    (OUT/'sipi_aead_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()

