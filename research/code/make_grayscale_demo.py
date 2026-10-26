from pathlib import Path
import sys, json, hashlib, secrets, shutil, argparse
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Create grayscale AEAD demonstration images and histogram figure.')
parser.add_argument('--input-dir',type=Path,default=ROOT/'data'/'benchmarks'/'usc_sipi'/'color',help='Folder containing 4.1.07.tiff and 4.1.08.tiff')
parser.add_argument('--output-dir',type=Path,default=ROOT/'results'/'grayscale_demo')
parser.add_argument('--figure',type=Path,default=None,help='Optional separate figure destination')
args=parser.parse_args()
src_dir=args.input_dir
out=args.output_dir
fig_out=args.figure or (out/'figures'/'grayscale_original_ciphertext_decrypted_histograms.png')
for d in [out/'original',out/'encrypted',out/'ciphertext_views',out/'decrypted',out/'demo_keys']:
    d.mkdir(parents=True,exist_ok=True)
# The supplement code directory contains the shared authenticated-encryption wrapper.
sys.path.insert(0,str(Path(__file__).resolve().parent))
vendor_candidates=[ROOT/'work'/'python_vendor',Path(__file__).resolve().parents[3]/'work'/'python_vendor']
for local_vendor in vendor_candidates:
    if local_vendor.exists():
        sys.path.insert(0,str(local_vendor))
        break
from secure_image_bench import canonical_header, encrypt, decrypt, parse_envelope

cases=[]
records=[]
for example_no,(image_id,color_serial) in enumerate([('4.1.07',15),('4.1.08',16)],start=1):
    src=src_dir/f'{image_id}.tiff'
    with Image.open(src) as im:
        rgb=im.convert('RGB')
        gray=rgb.convert('L')
        arr=np.asarray(gray,dtype=np.uint8).copy()
        w,h=gray.size
    original_path=out/'original'/f'{image_id}_grayscale.png'
    gray.save(original_path)
    raw=arr.tobytes()
    key=secrets.token_bytes(32)
    keypath=out/'demo_keys'/f'{image_id}_AES-256-GCM_DEMO_ONLY.key.txt'
    keypath.write_text(key.hex()+'\n',encoding='ascii')
    header=canonical_header('AES-256-GCM',w,h,'L')
    envelope=encrypt(raw,header,key,'AES-256-GCM')
    encpath=out/'encrypted'/f'{image_id}_AES-256-GCM.imgenc'
    encpath.write_bytes(envelope)
    _,_,body,_=parse_envelope(envelope)
    cipher=Image.frombytes('L',(w,h),np.frombuffer(body[:-16],dtype=np.uint8).copy().tobytes())
    cipherpath=out/'ciphertext_views'/f'{image_id}_AES-256-GCM_ciphertext_bytes.png'
    cipher.save(cipherpath)
    plain,meta=decrypt(envelope,key)
    decarr=np.frombuffer(plain,dtype=np.uint8).reshape(h,w).copy()
    decpath=out/'decrypted'/f'{image_id}_AES-256-GCM_decrypted.png'
    Image.fromarray(decarr,'L').save(decpath)
    assert np.array_equal(arr,decarr)
    cases.append((example_no,color_serial,arr,np.asarray(cipher),decarr))
    records.append({'figure_example_no':example_no,'derived_from_color_image_no':color_serial,'source_asset_id':image_id,'source_file':src.name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'grayscale_transform':'Pillow RGB-to-L conversion','mode':'L','width':w,'height':h,'algorithm':'AES-256-GCM','encrypted_binary':str(encpath.relative_to(out)),'ciphertext_display_png':str(cipherpath.relative_to(out)),'decrypted_png':str(decpath.relative_to(out)),'demo_key_sidecar':str(keypath.relative_to(out)),'exact_pixel_match':True,'warning':'Illustration only; demonstration key is exposed and must never be reused.'})

fig,axes=plt.subplots(4,3,figsize=(10.3,10.8),gridspec_kw={'height_ratios':[1.05,.65,1.05,.65]})
coltitles=('Original grayscale image','Ciphertext-byte visualization','Decrypted grayscale image')
for j,t in enumerate(coltitles): axes[0,j].set_title(t,fontsize=11,weight='bold')
for i,(example_no,color_serial,orig,cipher,dec) in enumerate(cases):
    row=2*i
    for j,(im,title) in enumerate([(orig,f'Grayscale example {example_no} — original'),(cipher,'AES-256-GCM ciphertext bytes\nreshaped as grayscale (display only)'),(dec,f'Grayscale example {example_no} — exact decryption')]):
        ax=axes[row,j]; ax.imshow(im,cmap='gray',vmin=0,vmax=255); ax.set_title(title,fontsize=8.5); ax.axis('off')
        hist=axes[row+1,j]; hist.hist(np.asarray(im).ravel(),bins=np.arange(257),color='#4d5ddd',linewidth=0)
        hist.set_xlim(0,255); hist.set_xlabel('Gray value',fontsize=8); hist.set_ylabel('Count',fontsize=8); hist.grid(alpha=.18); hist.tick_params(labelsize=7)
        hist.set_title(f'Histogram: grayscale example {example_no} ({("original", "ciphertext preview", "decrypted")[j]})',fontsize=8)
fig.suptitle('Authenticated image encryption: grayscale examples and histograms',fontsize=14,weight='bold',y=.995)
fig.text(.5,.005,'Examples 1 and 2 are grayscale conversions of color images 15 and 16. Ciphertext preview is display-only; both decryptions match exactly.',ha='center',fontsize=8)
fig.tight_layout(rect=(0,.025,1,.97),h_pad=1.5,w_pad=.65)
fig_out.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(fig_out,dpi=260,bbox_inches='tight')
plt.close(fig)
(out/'visual_manifest_grayscale.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print('FIGURE',fig_out)
print('CASES',json.dumps(records,indent=2))
