"""Cross-paper security-test battery adapted to the USC-SIPI AEAD controls.

This tests AES-256-GCM and ChaCha20-Poly1305 reference implementations only.
It is not a reproduction or cryptanalysis of the six uploaded chaos-based ciphers.
Image-level statistics are descriptive; they do not establish cryptographic security.
"""
from __future__ import annotations
import csv, hashlib, json, math, os, platform, random, statistics, struct, sys, time
from pathlib import Path
import numpy as np
from PIL import Image
from cryptography.exceptions import InvalidTag

CODE=Path(__file__).resolve().parent
sys.path.insert(0,str(CODE))
from secure_image_bench import (CIPHERS, MAGIC, NONCE_SIZE, TAG_SIZE, canonical_header,
    encrypt, decrypt, parse_envelope, entropy_u8, npcr_uaci)

ROOT=CODE.parent
DATA=ROOT/'data'/'benchmarks'/'usc_sipi'
OUT=ROOT/'results'
REPEATS=9
DIFF_TRIALS=5
ALPHA_CHI2_CRITICAL_255DF=293.2478


def read_asset(entry):
    path=ROOT/Path(entry['relative_path'])
    with Image.open(path) as im:
        expected='L' if entry['subset']=='grayscale' else 'RGB'
        if im.mode!=expected: raise ValueError(f'{path}: expected {expected}, got {im.mode}')
        im=im.copy()
    return path,im.tobytes(),im.width,im.height,im.mode


def array_channels(raw,w,h,mode):
    a=np.frombuffer(raw,dtype=np.uint8)
    return a.reshape((h,w)) if mode=='L' else a.reshape((h,w,3))


def correlations(a):
    if a.ndim==2: a=a[:,:,None]
    out={}
    pairs={'horizontal':(a[:,:-1,:],a[:,1:,:]),'vertical':(a[:-1,:,:],a[1:,:,:]),
           'diagonal_down':(a[:-1,:-1,:],a[1:,1:,:]),'diagonal_up':(a[1:,:-1,:],a[:-1,1:,:])}
    for d,(x,y) in pairs.items():
        for c in range(a.shape[2]):
            xx=x[:,:,c].ravel().astype(np.float64); yy=y[:,:,c].ravel().astype(np.float64)
            out[f'corr_{d}_c{c}']=float(np.corrcoef(xx,yy)[0,1]) if xx.size>1 and xx.std()>0 and yy.std()>0 else 0.0
    return out


def image_stats(raw,cipher,w,h,mode):
    # Strip the AEAD tag: only the length-preserving ciphertext body becomes a raster.
    a=array_channels(cipher[:len(raw)],w,h,mode)
    channels=a[:,:,None] if a.ndim==2 else a
    result={'ciphertext_entropy_bits_per_byte':entropy_u8(np.frombuffer(cipher[:len(raw)],dtype=np.uint8))}
    result.update(correlations(a))
    entropies=[]; chi=[]; max_devs=[]; local=[]
    for c in range(channels.shape[2]):
        plane=channels[:,:,c]
        counts=np.bincount(plane.ravel(),minlength=256).astype(np.float64)
        expected=plane.size/256
        chi2=float(np.sum((counts-expected)**2/expected))
        chi.append(chi2); max_devs.append(float(np.max(np.abs(counts-expected))/expected))
        probs=counts[counts>0]/plane.size
        entropies.append(float(-np.sum(probs*np.log2(probs))))
        # Local Shannon entropy over non-overlapping 16x16 tiles; partial edge tiles included.
        for y in range(0,plane.shape[0],16):
            for x in range(0,plane.shape[1],16):
                tile=plane[y:y+16,x:x+16]
                hist=np.bincount(tile.ravel(),minlength=256).astype(np.float64)
                q=hist[hist>0]/tile.size
                local.append(float(-np.sum(q*np.log2(q))))
    spectral_flatness=[]; spectral_entropy=[]
    for c in range(channels.shape[2]):
        plane=channels[:,:,c].astype(np.float64)
        mag=np.abs(np.fft.fftshift(np.fft.fft2(plane))).ravel()
        # Remove the DC coefficient so mean intensity does not dominate the summary.
        mag=np.delete(mag,mag.size//2)+1e-12
        spectral_flatness.append(float(np.exp(np.mean(np.log(mag)))/np.mean(mag)))
        probs=mag/np.sum(mag); h=-float(np.sum(probs*np.log2(probs)))
        spectral_entropy.append(h/math.log2(len(probs)) if len(probs)>1 else 0.0)
    result.update({'spectrum_flatness_mean_excluding_dc':statistics.mean(spectral_flatness),
                   'spectrum_entropy_normalized_mean_excluding_dc':statistics.mean(spectral_entropy),
                   'channel_entropy_mean_bits':statistics.mean(entropies),
                   'histogram_chi2_mean':statistics.mean(chi),
                   'histogram_chi2_max':max(chi),
                   'histogram_max_relative_bin_deviation_mean':statistics.mean(max_devs),
                   'histogram_chi2_below_293_2478_all_channels':all(v<=ALPHA_CHI2_CRITICAL_255DF for v in chi),
                   'local_entropy_mean_16px_bits':statistics.mean(local),
                   'local_entropy_min_16px_bits':min(local),
                   'local_entropy_max_16px_bits':max(local)})
    # Descriptive visual-difference metrics only; ciphertext rasterization is arbitrary.
    x=np.frombuffer(raw,dtype=np.uint8).astype(np.int16)
    y=np.frombuffer(cipher[:len(raw)],dtype=np.uint8).astype(np.int16)
    mse=float(np.mean((x-y)**2))
    result['plaintext_ciphertext_mse']=mse
    result['plaintext_ciphertext_psnr_db']=float(20*math.log10(255/math.sqrt(mse))) if mse else float('inf')
    return result


def make_envelope(header,nonce,body):
    return MAGIC+struct.pack('>H',len(header))+header+nonce+body


def rejects(envelope,key):
    try: decrypt(envelope,key)
    except (InvalidTag,ValueError,KeyError,struct.error,IndexError): return True
    return False


def attack_rows(envelope,key,header,nonce,body,raw,w,h,mode,seed):
    rng=random.Random(seed)
    rows=[]
    def add(name,damaged): rows.append({'attack':name,'rejected':rejects(damaged,key)})
    # Ciphertext and authentication-tag modification.
    if len(body)>TAG_SIZE:
        b=bytearray(body); b[len(b)//2]^=1; add('ciphertext_single_bit_flip',make_envelope(header,nonce,bytes(b)))
    b=bytearray(body); b[-1]^=1; add('authentication_tag_single_bit_flip',make_envelope(header,nonce,bytes(b)))
    # Authenticated metadata edits.
    altered=json.loads(header.decode()); altered['width']=int(altered['width'])+1
    bad_header=json.dumps(altered,sort_keys=True,separators=(',',':')).encode()
    add('authenticated_width_metadata_change',make_envelope(bad_header,nonce,body))
    # Central image-plane occlusion with white fill, preserving the serialized length.
    channels=1 if mode=='L' else 3
    for frac in (1/64,1/16,1/4):
        raster=np.frombuffer(body[:len(raw)],dtype=np.uint8).copy().reshape(h,w,channels)
        rh=max(1,int(round(h*math.sqrt(frac)))); rw=max(1,int(round(w*math.sqrt(frac))))
        y0=(h-rh)//2; x0=(w-rw)//2
        raster[y0:y0+rh,x0:x0+rw,:]=255
        damaged=raster.tobytes()+body[len(raw):]
        add(f'ciphertext_center_occlusion_whitefill_area_{frac:g}',make_envelope(header,nonce,damaged))
    # Salt-and-pepper style substitutions in serialized ciphertext bytes.
    for density in (.001,.01,.1,.2):
        b=bytearray(body); flips=max(1,int(len(b)*density))
        for pos in rng.sample(range(len(b)),min(flips,len(b))): b[pos]=0 if rng.getrandbits(1)==0 else 255
        add(f'ciphertext_salt_pepper_density_{density:g}',make_envelope(header,nonce,bytes(b)))
    # Truncated container and wrong/one-bit-different keys.
    add('container_truncated_1_byte',envelope[:-1])
    return rows


def run_one(path,raw,w,h,mode,algorithm):
    header=canonical_header(algorithm,w,h,mode)
    key=__import__('secrets').token_bytes(32)
    nonce=__import__('secrets').token_bytes(NONCE_SIZE)
    first=encrypt(raw,header,key,algorithm,nonce=nonce)
    body=parse_envelope(first)[2]
    assert len(body)==len(raw)+TAG_SIZE
    opened,meta=decrypt(first,key)
    assert opened==raw and meta['mode']==mode
    wrong=__import__('secrets').token_bytes(32)
    flipped=bytearray(key); flipped[0]^=1
    tests=attack_rows(first,key,header,nonce,body,raw,w,h,mode,int.from_bytes(hashlib.sha256(path.name.encode()).digest()[:8],'big'))
    tests += [{'attack':'wrong_random_key','rejected':rejects(first,wrong)},
              {'attack':'one_bit_key_change','rejected':rejects(first,bytes(flipped))}]

    # Fresh-nonce NPCR/UACI controls (same plaintext and chosen one-byte change).
    changed=bytearray(raw); changed[len(changed)//2]^=1
    same=[]; differential=[]
    for _ in range(DIFF_TRIALS):
        a=encrypt(raw,header,key,algorithm); b=encrypt(raw,header,key,algorithm)
        c=encrypt(bytes(changed),header,key,algorithm)
        same.append(npcr_uaci(parse_envelope(a)[2][:-TAG_SIZE],parse_envelope(b)[2][:-TAG_SIZE]))
        differential.append(npcr_uaci(parse_envelope(a)[2][:-TAG_SIZE],parse_envelope(c)[2][:-TAG_SIZE]))
    # Same nonce under two different keys is valid: key-sensitivity diagnostic.
    changed_key=bytes(flipped)
    ek=encrypt(raw,header,changed_key,algorithm,nonce=nonce)
    key_npcr,key_uaci=npcr_uaci(body[:-TAG_SIZE],parse_envelope(ek)[2][:-TAG_SIZE])

    # Timing with warm-up and median of 9 paired operations.
    warm=encrypt(raw,header,key,algorithm); decrypt(warm,key)
    enc=[]; dec=[]
    for _ in range(REPEATS):
        t=time.perf_counter_ns(); env=encrypt(raw,header,key,algorithm); t1=time.perf_counter_ns()
        plain,_=decrypt(env,key); t2=time.perf_counter_ns(); assert plain==raw
        enc.append((t1-t)/1e6); dec.append((t2-t1)/1e6)
    mib=len(raw)/(1024*1024)
    trow={'image_id':path.stem,'mode':mode,'width':w,'height':h,'raw_bytes':len(raw),
          'algorithm':algorithm,'timing_repeats':REPEATS,
          'encrypt_median_ms':statistics.median(enc),'decrypt_median_ms':statistics.median(dec),
          'encrypt_mib_s':mib/(statistics.median(enc)/1000),
          'decrypt_mib_s':mib/(statistics.median(dec)/1000),
          'roundtrip_ok':True,'nominal_key_bits':256}
    srow={'image_id':path.stem,'mode':mode,'algorithm':algorithm}
    srow.update(image_stats(raw,body,w,h,mode))
    for label,vals in [('same_plain_fresh_nonce',same),('one_byte_change_fresh_nonce',differential)]:
        srow[label+'_npcr_mean_pct']=statistics.mean(v[0] for v in vals)
        srow[label+'_npcr_min_pct']=min(v[0] for v in vals); srow[label+'_npcr_max_pct']=max(v[0] for v in vals)
        srow[label+'_uaci_mean_pct']=statistics.mean(v[1] for v in vals)
    srow.update({'one_bit_key_change_npcr_pct':key_npcr,'one_bit_key_change_uaci_pct':key_uaci,
                 'all_integrity_and_wrong_key_attacks_rejected':all(x['rejected'] for x in tests),
                 'attack_cases':len(tests)})
    return trow,srow,tests


def linear_fit(rows,algorithm):
    group=[r for r in rows if r['algorithm']==algorithm]
    x=np.array([r['raw_bytes'] for r in group],dtype=float); y=np.array([r['encrypt_median_ms'] for r in group],dtype=float)
    slope,intercept=np.polyfit(x,y,1); pred=intercept+slope*x
    ss_res=float(np.sum((y-pred)**2)); ss_tot=float(np.sum((y-y.mean())**2))
    return {'algorithm':algorithm,'intercept_ms':float(intercept),'slope_ms_per_byte':float(slope),
            'r_squared':1-ss_res/ss_tot if ss_tot else 1.0,'n_images':len(group),
            'interpretation':'Descriptive linear fit over this corpus; not a formal algorithmic complexity proof.'}


def main():
    entries=list(csv.DictReader((DATA/'manifest.csv').open(newline='',encoding='utf-8')))
    if sum(e['subset']=='grayscale' for e in entries)<10 or sum(e['subset']=='color' for e in entries)<10:
        raise SystemExit('Need at least 10 grayscale and 10 color assets')
    timing=[]; stats=[]; attacks=[]
    for e in entries:
        path,raw,w,h,mode=read_asset(e)
        for alg in CIPHERS:
            tr,sr,ar=run_one(path,raw,w,h,mode,alg)
            timing.append(tr); stats.append(sr)
            for row in ar: attacks.append({'image_id':path.stem,'mode':mode,'algorithm':alg,**row})
            print(f"{path.stem} {mode} {alg}: round-trip OK; rejected {sum(a['rejected'] for a in ar)}/{len(ar)} corruption/key tests; {tr['encrypt_mib_s']:.1f} MiB/s")
    OUT.mkdir(exist_ok=True)
    for name,rows in [('paper_test_timing.csv',timing),('paper_test_image_statistics.csv',stats),('paper_test_integrity_attacks.csv',attacks)]:
        with (OUT/name).open('w',newline='',encoding='utf-8') as f:
            fields=list(dict.fromkeys(k for row in rows for k in row)); wri=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); wri.writeheader(); wri.writerows(rows)
    summary={'scope':'AEAD reference baselines only; no supplied chaos-based cipher was implemented or attacked.',
      'dataset_assets':len(entries),'grayscale_assets':sum(e['subset']=='grayscale' for e in entries),
      'rgb_assets':sum(e['subset']=='color' for e in entries),'image_cipher_cases':len(timing),
      'algorithms':list(CIPHERS),'all_roundtrips_pass':all(r['roundtrip_ok'] for r in timing),
      'integrity_attack_cases':len(attacks),'all_integrity_and_wrong_key_attacks_rejected':all(a['rejected'] for a in attacks),
      'nominal_key_bits':256,'fresh_nonce_differential_repeats_per_image_cipher':DIFF_TRIALS,
      'runtime_repeats_per_image_cipher':REPEATS,
      'runtime_scaling_fits':[linear_fit(timing,a) for a in CIPHERS],
      'environment':{'python':platform.python_version(),'platform':platform.platform(),'machine':platform.machine(),'processor':platform.processor()},
      'warnings':['NPCR/UACI on fresh-nonce AEAD outputs are dominated by nonce randomization; do not interpret as intrinsic plaintext diffusion.',
        'Chi-square, entropy, histograms, local entropy, correlation, MSE, and PSNR are descriptive image statistics, not security proofs.',
        'Chaos-specific Lyapunov/bifurcation/fractal/NIST tests are inapplicable to these standard AEAD primitives.',
        'Noise/crop tests for AEAD measure fail-closed integrity, not graceful image recovery.',
        'Timing cannot be ranked against the six articles unless hardware, software, image sizes, and timing boundaries are matched.']}
    (OUT/'paper_test_suite_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()







