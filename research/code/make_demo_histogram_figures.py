"""Rebuild the two demonstration figures from saved image outputs, without re-encrypting."""
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
COLOR=ROOT/'results'/'expanded_color_demo'
GRAY=ROOT/'results'/'grayscale_demo'
FIGS=ROOT/'manuscript'/'figures'
FIGS.mkdir(parents=True,exist_ok=True)

def read(path,mode):
    with Image.open(path) as im:
        return np.asarray(im.convert(mode)).copy()

def color_hist(ax,arr):
    x=np.arange(256)
    for c,color,label in [(0,'red','R'),(1,'green','G'),(2,'blue','B')]:
        ax.plot(x,np.bincount(arr[:,:,c].ravel(),minlength=256),color=color,lw=.8,label=label)
    ax.set(xlim=(0,255),xlabel='Pixel value',ylabel='Count')
    ax.grid(alpha=.18); ax.legend(fontsize=6,ncol=3,loc='upper right',frameon=False)

fig,axes=plt.subplots(4,3,figsize=(12,14))
for j,title in enumerate(('Original image','Ciphertext-byte preview','Decrypted image')):
    axes[0,j].set_title(title,fontsize=12,weight='bold')
for i,(asset,serial) in enumerate([('4.1.07',15),('4.1.08',16)]):
    imgs=[read(COLOR/'original'/f'{asset}.tiff','RGB'),
          read(COLOR/'ciphertext_views'/f'{asset}_aes_gcm_ciphertext_bytes.png','RGB'),
          read(COLOR/'decrypted'/f'{asset}_AES-256-GCM_decrypted.png','RGB')]
    for col,arr in enumerate(imgs):
        ax=axes[2*i,col]; ax.imshow(arr); ax.axis('off')
        label=('original','ciphertext preview','decrypted')[col]
        ax.set_title(f'Color image {serial} — {label}',fontsize=9)
        color_hist(axes[2*i+1,col],arr)
        axes[2*i+1,col].set_title(f'Histogram: color image {serial} ({label})',fontsize=8)
fig.suptitle('Authenticated image encryption: color images 15 and 16 with channel histograms',fontsize=15,weight='bold')
fig.text(.5,.018,'Ciphertext preview is encrypted pixel-body bytes reshaped as RGB; the .imgenc artifact is binary. Decrypted pixels match exactly.',ha='center',fontsize=8)
fig.subplots_adjust(left=.08,right=.98,top=.94,bottom=.055,hspace=.52,wspace=.22)
fig.savefig(FIGS/'color_original_ciphertext_decrypted_histograms.png',dpi=240,bbox_inches='tight')
plt.close(fig)

fig,axes=plt.subplots(4,3,figsize=(10.3,10.8),gridspec_kw={'height_ratios':[1.05,.65,1.05,.65]})
for j,title in enumerate(('Original grayscale image','Ciphertext-byte preview','Decrypted grayscale image')):
    axes[0,j].set_title(title,fontsize=11,weight='bold')
for i,(asset,example,color_serial) in enumerate([('4.1.07',1,15),('4.1.08',2,16)]):
    imgs=[read(GRAY/'original'/f'{asset}_grayscale.png','L'),
          read(GRAY/'ciphertext_views'/f'{asset}_AES-256-GCM_ciphertext_bytes.png','L'),
          read(GRAY/'decrypted'/f'{asset}_AES-256-GCM_decrypted.png','L')]
    for col,arr in enumerate(imgs):
        ax=axes[2*i,col]; ax.imshow(arr,cmap='gray',vmin=0,vmax=255); ax.axis('off')
        label=('original','ciphertext preview','decrypted')[col]
        ax.set_title(f'Grayscale example {example} — {label}',fontsize=8.5)
        hist=axes[2*i+1,col]; hist.hist(arr.ravel(),bins=np.arange(257),color='#4d5ddd',linewidth=0)
        hist.set_xlim(0,255); hist.set_xlabel('Gray value',fontsize=8); hist.set_ylabel('Count',fontsize=8)
        hist.grid(alpha=.18); hist.tick_params(labelsize=7)
        hist.set_title(f'Histogram: grayscale example {example} ({label})',fontsize=8)
fig.suptitle('Authenticated image encryption: grayscale examples 1 and 2',fontsize=14,weight='bold',y=.995)
fig.text(.5,.005,'Grayscale examples 1 and 2 are conversions of color images 15 and 16. Ciphertext previews are display-only; decryptions match exactly.',ha='center',fontsize=8)
fig.tight_layout(rect=(0,.025,1,.97),h_pad=1.5,w_pad=.65)
fig.savefig(FIGS/'grayscale_original_ciphertext_decrypted_histograms.png',dpi=260,bbox_inches='tight')
plt.close(fig)
print('Rebuilt color image 15/16 and grayscale example 1/2 histogram figures from saved outputs.')
