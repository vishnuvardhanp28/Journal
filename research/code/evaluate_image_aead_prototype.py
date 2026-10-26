"""Run mode, round-trip, and fail-closed checks for image_aead_prototype."""
from __future__ import annotations
import csv, hashlib, json, secrets, statistics, tempfile, time
from pathlib import Path
from PIL import Image
from cryptography.exceptions import InvalidTag

from image_aead_prototype import open_image_file, open_pixels, seal_image_file, seal_pixels
from secure_image_bench import CIPHERS

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'benchmarks'/'usc_sipi'
OUT=ROOT/'results'/'image_aead_prototype_summary.json'
TIMING=ROOT/'results'/'image_aead_prototype_timing.csv'
REPEATS=9

def main():
    entries=list(csv.DictReader((DATA/'manifest.csv').open(newline='',encoding='utf-8')))
    rows=[]; roundtrips=0; tamper_rejected=0; wrong_key_rejected=0
    for entry in entries:
        path=ROOT/entry['relative_path']
        with Image.open(path) as im:
            if im.mode not in ('L','RGB'): raise ValueError(f'Unsupported mode: {path} {im.mode}')
            image=im.copy()
        raw=image.tobytes()
        for algorithm in CIPHERS:
            key=secrets.token_bytes(32)
            envelope=seal_pixels(raw,image.width,image.height,image.mode,key,algorithm)
            recovered,metadata=open_pixels(envelope,key)
            assert recovered==raw
            assert (metadata['width'],metadata['height'],metadata['mode'])==(image.width,image.height,image.mode)
            roundtrips+=1
            tampered=bytearray(envelope); tampered[-1]^=1
            try: open_pixels(bytes(tampered),key)
            except InvalidTag: tamper_rejected+=1
            else: raise AssertionError(f'tamper accepted: {path.name} {algorithm}')
            changed=bytearray(key); changed[0]^=1
            try: open_pixels(envelope,bytes(changed))
            except InvalidTag: wrong_key_rejected+=1
            else: raise AssertionError(f'wrong key accepted: {path.name} {algorithm}')
            rows.append({'image_id':path.stem,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                         'mode':image.mode,'width':image.width,'height':image.height,
                         'algorithm':algorithm,'plaintext_bytes':len(raw),'container_bytes':len(envelope),
                         'overhead_bytes':len(envelope)-len(raw)})

    # Verify the actual file API and measure full local file I/O plus encrypt/decrypt.
    file_roundtrips=0; timing_rows=[]; compression_levels=(6,1)
    scratch = ROOT / 'work'
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='image-aead-',dir=scratch) as td:
        tmp=Path(td)
        for entry in entries:
            source=ROOT/entry['relative_path']
            for algorithm in CIPHERS:
                key=secrets.token_bytes(32); sealed=tmp/(source.stem+'.imgenc'); restored=tmp/(source.stem+'_'+algorithm.replace('/','_')+'.png')
                with Image.open(source) as input_image: raw=input_image.tobytes(); width,height,mode=input_image.width,input_image.height,input_image.mode
                # Warm-up is excluded from each compression-level timing distribution.
                seal_image_file(source,sealed,key,algorithm)
                for compression_level in compression_levels:
                    open_image_file(sealed,restored,key,png_compress_level=compression_level)
                    enc_ms=[]; dec_ms=[]
                    for _ in range(REPEATS):
                        start=time.perf_counter_ns(); seal_image_file(source,sealed,key,algorithm); mid=time.perf_counter_ns()
                        open_image_file(sealed,restored,key,png_compress_level=compression_level); end=time.perf_counter_ns()
                        with Image.open(restored) as output_image:
                            assert output_image.mode==mode and output_image.size==(width,height) and output_image.tobytes()==raw
                        enc_ms.append((mid-start)/1e6); dec_ms.append((end-mid)/1e6)
                    mib=len(raw)/(1024*1024); med_enc=statistics.median(enc_ms); med_dec=statistics.median(dec_ms)
                    timing_rows.append({'image_id':source.stem,'mode':mode,'width':width,'height':height,
                        'raw_bytes':len(raw),'algorithm':algorithm,'png_compress_level':compression_level,'repeats':REPEATS,
                        'png_output_bytes':restored.stat().st_size,
                        'encrypt_median_ms':med_enc,'decrypt_median_ms':med_dec,
                        'encrypt_mib_s':mib/(med_enc/1000),'decrypt_mib_s':mib/(med_dec/1000)})
                file_roundtrips+=1

    with TIMING.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(timing_rows[0])); writer.writeheader(); writer.writerows(timing_rows)

    summary={'scope':'image-format and AEAD wrapper prototype checks; this is not a reproduction of any chaos-based paper.',
      'assets':len(entries),'grayscale_assets':sum(e['subset']=='grayscale' for e in entries),
      'rgb_assets':sum(e['subset']=='color' for e in entries),'algorithms':list(CIPHERS),
      'pixel_api_roundtrips':roundtrips,'tamper_rejections':tamper_rejected,
      'one_bit_wrong_key_rejections':wrong_key_rejected,'file_api_roundtrips':file_roundtrips,
      'file_timing_repeats_per_case':REPEATS,
      'file_timing_cases':len(timing_rows),
      'png_compression_levels':list(compression_levels),
      'mean_file_encrypt_mib_s':statistics.mean(r['encrypt_mib_s'] for r in timing_rows),
      'mean_file_decrypt_mib_s':statistics.mean(r['decrypt_mib_s'] for r in timing_rows),
      'mean_png_output_bytes_by_compression_level':{str(level):statistics.mean(r['png_output_bytes'] for r in timing_rows if r['png_compress_level']==level) for level in compression_levels},
      'all_checks_pass':roundtrips==len(entries)*len(CIPHERS) and tamper_rejected==roundtrips and wrong_key_rejected==roundtrips and file_roundtrips==len(entries)*len(CIPHERS),
      'key_management':'Caller supplies a 32-byte key; no key is derived from plaintext or stored in the envelope.',
      'metadata':'Width, height, pixel mode, dtype, algorithm, and version are authenticated as associated data.',
      'nonce':'A fresh cryptographic 96-bit nonce is generated for each sealing call.',
      'decrypted_output':'Lossless PNG; compression levels 6 and 1 compared, and output serialization is included in file-open timing.',
      'limits':['The file wrapper preserves L/RGB pixel data and dimensions, not EXIF or other container metadata.',
                'Any ciphertext corruption is rejected; it does not recover partially lost images.',
                'This uses standard AEAD primitives and is a reproducible security baseline, not a novel cipher.'],
      'per_image_cases':rows}
    OUT.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='per_image_cases'},indent=2))
    if not summary['all_checks_pass']: raise SystemExit('prototype checks failed')
if __name__=='__main__': main()
