"""Verify representative ciphertext attacks against all 20 numbered image containers.

All disclosed keys are DEMO ONLY. This script checks fail-closed behavior; it
never manufactures a decrypted image for a rejected attack.
"""
from __future__ import annotations
import csv, hashlib, json, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from cryptography.exceptions import InvalidTag
from secure_image_bench import MAGIC, NONCE_SIZE, TAG_SIZE, decrypt, parse_envelope

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'/'ten_by_ten_montage'
CSV_OUT=ROOT/'results'/'attack_evidence_samples.csv'
FIGURE=ROOT/'manuscript'/'figures'/'attack_evidence.png'

def reject(blob: bytes, key: bytes):
    try:
        decrypt(blob,key)
        return False,'Accepted'
    except Exception as e:
        return True,type(e).__name__

def main():
    rows=[]
    cases={}
    for serial in range(1,21):
        stem=f'image_{serial:02d}'
        container=(RESULTS/'encrypted'/f'{stem}.imgenc').read_bytes()
        key=bytes.fromhex((RESULTS/'demo_keys'/f'{stem}_DEMO_ONLY.key.txt').read_text().strip())
        header,nonce,cttag,meta=parse_envelope(container)
        body,tag=cttag[:-TAG_SIZE],cttag[-TAG_SIZE:]
        tests={}
        bitflip=bytearray(container); bitflip[-1]^=1; tests['tag_bit_flip']=bytes(bitflip)
        rng=random.Random(int(hashlib.sha256(f'attack:{serial}'.encode()).hexdigest()[:16],16))
        noised=bytearray(body)
        count=max(1,len(noised)//100)
        for idx in rng.sample(range(len(noised)),count): noised[idx]=rng.choice((0,255))
        tests['ciphertext_byte_noise_1pct']=MAGIC+len(header).to_bytes(2,'big')+header+nonce+bytes(noised)+tag
        tests['container_truncation_1pct']=container[:max(1,len(container)-max(1,len(container)//100))]
        wrong=bytearray(key); wrong[0]^=1
        tests['one_bit_wrong_key']=container
        for attack,altered in tests.items():
            used_key=bytes(wrong) if attack=='one_bit_wrong_key' else key
            rejected,exc=reject(altered,used_key)
            rows.append({'paper_image_no':serial,'attack':attack,'container_bytes':len(altered),'rejected':rejected,'result':exc,'recovered_image_produced':not rejected})
            if serial in (1,11): cases.setdefault(serial,[]).append((attack,rejected,exc))
    CSV_OUT.parent.mkdir(parents=True,exist_ok=True)
    with CSV_OUT.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    if len(rows)!=80 or not all(r['rejected'] for r in rows): raise AssertionError('attack run failed')
    # Build a transparent figure: actual image IO samples, with rejected attacks
    # shown as text outcomes because authenticated decryption returns no image.
    font_path=Path('C:/Windows/Fonts/arial.ttf'); bold_path=Path('C:/Windows/Fonts/arialbd.ttf')
    normal=ImageFont.truetype(str(font_path),25) if font_path.exists() else ImageFont.load_default()
    bold=ImageFont.truetype(str(bold_path),29) if bold_path.exists() else ImageFont.load_default()
    W,H=3200,1040; fig=Image.new('RGB',(W,H),'white');draw=ImageDraw.Draw(fig)
    draw.text((40,20),'Attack evidence: valid image recovery and fail-closed ciphertext probes',font=bold,fill='#183b5b')
    colx=[40,550,1060]; widths=[470,470,470]
    heads=['Original input','Ciphertext-byte preview','Valid decryption']
    for k,x in enumerate(colx): draw.text((x,85),heads[k],font=bold,fill='#263746')
    testx=1600;draw.text((testx,85),'Attack probes (no output image)',font=bold,fill='#263746')
    attacks=['Tag bit flip','1% ciphertext-byte noise','1% truncation','One-bit wrong key']
    row_y=[170,590]
    for n,y in zip((1,11),row_y):
        stem=f'image_{n:02d}'
        paths=[RESULTS/f'{stem}_original.png',RESULTS/f'{stem}_cipher_preview.png',RESULTS/f'{stem}_decrypted.png']
        draw.text((40,y-33),f'Image {n} (grayscale)' if n==1 else f'Image {n} (color)',font=bold,fill='#183b5b')
        for x,w,path in zip(colx,widths,paths):
            with Image.open(path) as src: tile=src.convert('RGB');tile.thumbnail((440,365),Image.Resampling.LANCZOS)
            frame=(x,y,x+w,y+375);draw.rectangle(frame,outline='#aebbc6',width=2)
            fig.paste(tile,(x+(w-tile.width)//2,y+(375-tile.height)//2))
        # Failed authentication returns no image; outcomes are listed below.
        for j,label in enumerate(attacks):
            item=cases[n][j]
            draw.text((testx,y+52+j*62),f'{label}: REJECTED ({item[2]}); no output image',font=normal,fill='#176b47')
    draw.text((40,H-45),'Ciphertext previews are display-only. Each attack was applied to the saved binary .imgenc container; exact plaintext was produced only for valid authenticated decryption.',font=normal,fill='#4a5965')
    FIGURE.parent.mkdir(parents=True,exist_ok=True);fig.save(FIGURE,dpi=(300,300),optimize=True)
    print(f'attack tests rejected: {sum(r["rejected"] for r in rows)}/{len(rows)}; figure={FIGURE}')

if __name__=='__main__': main()
