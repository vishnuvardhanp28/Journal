"""Build a compact, monochrome IEEE-style study-method diagram."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript'/'figures'/'methodology_overview'
fig,ax=plt.subplots(figsize=(7.16,3.4))
ax.set_xlim(0,100); ax.set_ylim(0,46); ax.axis('off')
ink='#111111'; border='#292929'; light='#f2f2f2'; white='#ffffff'; mid='#e7e7e7'

def box(x,y,w,h,title,body,fill=white):
    ax.add_patch(Rectangle((x,y),w,h,linewidth=.85,edgecolor=border,facecolor=fill,zorder=1))
    ax.text(x+w/2,y+h-.85,title,ha='center',va='top',fontsize=7.4,fontweight='bold',color=ink,linespacing=1.05,zorder=2)
    ax.text(x+w/2,y+h-2.75,body,ha='center',va='top',fontsize=6.2,color=ink,linespacing=1.18,zorder=2)

def arrow(start,end):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=8.5,
        linewidth=.8,color=ink,shrinkA=2,shrinkB=2,zorder=0))

ax.text(1,43.5,'PAPER-AUDIT TRACK',ha='left',va='center',fontsize=7.2,fontweight='bold',color=ink)
ax.text(1,27.5,'REFERENCE-CONTROL TRACK',ha='left',va='center',fontsize=7.2,fontweight='bold',color=ink)

box(1,30,22,11,'Source papers','Six supplied papers; reported\nalgorithms, metrics, and tests',light)
box(26,30,23,11,'Protocol / equation audit','Compare reported tests; inspect\nselected equations and domain\nassumptions')
box(52,30,22,11,'Paper-audit outputs','Test-coverage matrix; bounded\nequation findings; reproduction\ngaps',light)
arrow((23,35.5),(26,35.5)); arrow((49,35.5),(52,35.5))

box(1,14,22,11,'Evaluation images','20 in the montage (10 grayscale,\n10 RGB); 2 additional grayscale\ntransforms in the control set',light)
box(26,14,23,11,'AEAD reference controls','AES-256-GCM and\nChaCha20-Poly1305;\n22 images per algorithm\n(44 image-algorithm cases)')
box(52,14,22,11,'Control measurements','Exact recovery; tamper and wrong-key\nchecks; image statistics and timing;\nselected CPA/KPA probes',light)
arrow((23,19.5),(26,19.5)); arrow((49,19.5),(52,19.5))

box(78,21,21,15,'Evidence synthesis','Compare source-paper\nclaims with equation\naudits and AEAD controls.\nState assumptions and\nlimits; no full target-\ncipher reproduction.',mid)
arrow((74,35.5),(78,32.5)); arrow((74,19.5),(78,24.5))

ax.text(50,4.7,'AEAD measurements are reference controls, not implementations or attacks against the six source ciphers.',
        ha='center',va='center',fontsize=7.1,color=ink)
fig.subplots_adjust(left=.01,right=.99,top=.99,bottom=.03)
OUT.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(OUT.with_suffix('.pdf'),bbox_inches='tight',facecolor='white')
fig.savefig(OUT.with_suffix('.png'),dpi=400,bbox_inches='tight',facecolor='white')
plt.close(fig)
print(OUT.with_suffix('.pdf').resolve())
