"""Make an enlarged figure of published image-level mean NPCR/UACI results."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/'results'/'published_paper_metric_comparison.csv'
OUT=ROOT/'manuscript'/'figures'/'reported_npcr_uaci_comparison.png'
# Values are transcribed/recalculated from the named source-paper tables.
labels=['Niu et al.','Geng et al.','Al-Dayel et al.']
npcr=[99.6082,99.6184,99.6143]
uaci=[33.4733,33.4734,33.4983]
plt.rcParams.update({'font.size':12,'axes.titlesize':16,'axes.labelsize':13,'xtick.labelsize':12,'ytick.labelsize':11})
fig,axs=plt.subplots(1,2,figsize=(12.5,4.9),constrained_layout=True)
colors=['#6c63a8','#3883a5','#628c5a']
for ax,vals,title,ylab,ylim,fmt in [(axs[0],npcr,'NPCR','Reported mean NPCR (%) (zoomed axis)',(99.55,99.67),'{:.4f}'),(axs[1],uaci,'UACI','Reported mean UACI (%) (zoomed axis)',(33.35,33.57),'{:.4f}')]:
 bars=ax.bar(labels,vals,color=colors,width=.6,edgecolor='#263746',linewidth=.65)
 ax.set_title(title,fontweight='bold',pad=10);ax.set_ylabel(ylab);ax.set_ylim(*ylim)
 ax.grid(axis='y',alpha=.22);ax.set_axisbelow(True);ax.tick_params(axis='x',rotation=0,pad=7)
 for b,v in zip(bars,vals):
  ax.annotate(fmt.format(v)+'%',(b.get_x()+b.get_width()/2,v),xytext=(0,8),textcoords='offset points',ha='center',va='bottom',fontsize=12,fontweight='bold',color='#111111',clip_on=False)
fig.suptitle('Published differential-image metrics (source protocols differ)',fontsize=17,fontweight='bold',color='#183b5b')
fig.savefig(OUT,dpi=300,bbox_inches='tight',facecolor='white')
plt.close(fig)
print(OUT.resolve())
