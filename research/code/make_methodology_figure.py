from pathlib import Path
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Create the manuscript methodology flow diagram.')
parser.add_argument('--output',type=Path,default=root/'manuscript'/'figures'/'methodology_overview.png')
out=parser.parse_args().output
out.parent.mkdir(parents=True,exist_ok=True)
fig,ax=plt.subplots(figsize=(13.5,4.2))
ax.set_xlim(0,13.5); ax.set_ylim(0,4.2); ax.axis('off')
boxes={
 'papers':(0.35,2.55,3.0,1.05,'Paper track','Six supplied papers\nReported methods and metrics\nImplementation details'),
 'images':(0.35,0.65,3.0,1.05,'Image/control track','22 USC-SIPI images\nAES-256-GCM and\nChaCha20-Poly1305'),
 'eq':(4.55,2.55,3.1,1.05,'Equation audit','Recheck published equations\nChosen-input tests and\ndomain checks'),
 'aead':(4.55,0.65,3.1,1.05,'AEAD measurements','Round trips, integrity probes,\nimage statistics, and timing'),
 'report':(9.3,1.6,3.75,1.15,'Evidence synthesis','Separate measured controls from\ntarget-paper findings\nState limitations'),
}
for key,(x,y,w,h,title,body) in boxes.items():
    patch=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.12,rounding_size=0.12',linewidth=1.6,edgecolor='#244a73',facecolor='#eef5fb')
    ax.add_patch(patch)
    ax.text(x+w/2,y+h*0.69,title,ha='center',va='center',fontsize=13,fontweight='bold',color='#163a5c')
    ax.text(x+w/2,y+h*0.34,body,ha='center',va='center',fontsize=9,color='#222222',linespacing=1.25)
def arrow(a,b):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=18,linewidth=1.6,color='#405d78',connectionstyle='arc3,rad=0'))
arrow((3.42,3.08),(4.48,3.08))
arrow((3.42,1.18),(4.48,1.18))
arrow((7.75,3.02),(9.18,2.42))
arrow((7.75,1.18),(9.18,1.95))
ax.text(6.1,3.93,'Parallel review paths',ha='center',va='center',fontsize=15,fontweight='bold',color='#163a5c')
ax.text(6.1,0.12,'The AEAD controls are not presented as implementations or attacks against the six custom ciphers.',ha='center',va='center',fontsize=9,color='#444444')
fig.tight_layout(pad=0.3)
fig.savefig(out,dpi=300,bbox_inches='tight',facecolor='white')
plt.close(fig)
print(out.resolve())
