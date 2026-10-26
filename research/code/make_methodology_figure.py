"""Render the study workflow. It explicitly keeps target-paper audits separate
from AES-GCM/ChaCha control experiments."""
from pathlib import Path
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=root/'manuscript'/'figures'/'methodology_overview.png')
out=parser.parse_args().output
fig,ax=plt.subplots(figsize=(15.5,6.0))
ax.set_xlim(0,15.5);ax.set_ylim(0,6);ax.axis('off')
navy='#173f68'; blue='#edf4fb'; teal='#eaf6f4'; pale='#f7f9fc'; line='#42688d'; ink='#213547'

def box(x,y,w,h,title,body,fill=blue,fs=11):
    patch=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.12,rounding_size=0.12',linewidth=1.6,edgecolor=navy,facecolor=fill)
    ax.add_patch(patch)
    ax.text(x+w/2,y+h*0.72,title,ha='center',va='center',fontsize=14,fontweight='bold',color=navy)
    ax.text(x+w/2,y+h*0.38,body,ha='center',va='center',fontsize=fs,color=ink,linespacing=1.35)

def arrow(a,b,rad=0):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=18,linewidth=1.6,color=line,connectionstyle=f'arc3,rad={rad}'))

ax.text(7.75,5.68,'Study workflow and separation of evidence',ha='center',va='center',fontsize=19,fontweight='bold',color=navy)
# Three first-stage evidence sources
box(.35,3.75,3.0,1.25,'Six source papers','Reported algorithms, equations,\nmetrics, and implementation details',fill=blue)
box(.35,2.05,3.0,1.25,'Twenty numbered images','10 grayscale (1–10) and\n10 color (11–20)',fill=teal)
box(.35,.35,3.0,1.25,'Threat probes','Ciphertext edits, noise, truncation,\nwrong keys, CPA/KPA diagnostics',fill=pale)
# Independent analysis lanes
box(4.45,3.75,3.25,1.25,'Paper / equation audits','Transcribe equations; test bounded\ninput, domain, and collision claims',fill=blue)
box(4.45,1.2,3.25,1.45,'AEAD control experiments','AES-256-GCM and ChaCha20-Poly1305;\nexact round trips, per-image metrics,\nauthenticated tamper rejection',fill=teal,fs=10.5)
# Explicit separate diagnostics then synthesis
box(8.75,1.2,2.8,1.45,'Measured outputs','Per-image CSV; timing; NPCR/UACI;\nentropy; attack outcomes',fill=teal,fs=10.5)
box(12.1,2.45,3.05,1.6,'Evidence synthesis','Compare reported claims with\nreproduced controls and audits;\nstate assumptions and limits',fill=pale)
arrow((3.45,4.36),(4.35,4.36))
arrow((3.45,2.68),(4.35,2.1))
arrow((3.45,.96),(4.35,1.65))
arrow((7.8,1.93),(8.65,1.93))
arrow((7.8,4.36),(11.85,3.3),rad=-.12)
arrow((11.65,1.94),(12.0,2.75),rad=.12)
ax.text(7.75,.38,'The AEAD results are reference controls, not implementations or attacks against the six custom ciphers.',ha='center',va='center',fontsize=11,color='#4a5965')
fig.tight_layout(pad=.35)
out.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(out,dpi=300,bbox_inches='tight',facecolor='white')
plt.close(fig)
print(out.resolve())
