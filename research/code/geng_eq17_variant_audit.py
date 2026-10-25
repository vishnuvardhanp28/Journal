"""Partial keystream reproduction for the Geng et al. image cipher.

Implements the published SHA-256 seed equations (13)-(15) and the 4-D ODE
(Eq. 2) with explicit illustrative numerical choices. It does NOT implement the
full cipher. The paper does not specify the ODE solver/time step and Eq. 17
conflicts with its surrounding prose, so both W1 interpretations are reported.
"""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
IMAGE=ROOT/'data'/'images'/'PIA00123.jpg'
OUT=ROOT/'results'/'geng_eq17_variant_audit.json'
SIZE=(64,64)
DT=0.001
DISCARD=1000
PARAMS=(28.0,17.0,13.0,21.8,5.0)  # parameter example reported with system phase diagrams

def seeds_from_plaintext(pixels: bytes):
    digest=hashlib.sha256(pixels).digest()
    k=list(digest)
    e=[]
    for j in range(4):
        group=k[8*j:8*j+8]
        e.extend((sum(group), np.bitwise_xor.reduce(np.array(group,dtype=np.uint8)).item()))
    h=[0.0]*8
    for j in range(4):
        s,xor=e[2*j],e[2*j+1]
        if xor==0:
            raise ValueError('Published Eq. 14 divides by XOR group value 0 for this input.')
        h[j]=(xor*k[j]*k[j+8]*k[j+16]*k[j+24])/256.0+s/xor
    h[4]=(e[1]+e[3])/256.0+e[0]/e[1]
    h[5]=(e[3]+e[5])/256.0+e[2]/e[3]
    h[6]=(e[5]+e[7])/256.0+e[4]/e[5]
    h[7]=(e[7]+e[1])/256.0+e[6]/e[7]
    states=[((h[j]+h[j+4])*1e4)%256/256 for j in range(4)]
    return digest.hex(), tuple(float(s) for s in states)

def rhs(q, params):
    x,y,z,w=q; a,b,c,d,e=params
    return np.array([a*(y-x)+w, b*x*z-x*z*z+c*y, x*x+y*y-d*z, x*z+y*z-e*w],dtype=np.float64)

def generate(n, initial, params, dt):
    q=np.array(initial,dtype=np.float64)
    seq=np.empty((n,4),dtype=np.float64)
    for i in range(n):
        k1=rhs(q,params); k2=rhs(q+0.5*dt*k1,params)
        k3=rhs(q+0.5*dt*k2,params); k4=rhs(q+dt*k3,params)
        q=q+(dt/6.0)*(k1+2*k2+2*k3+k4)
        if not np.all(np.isfinite(q)) or np.max(np.abs(q))>1e100:
            raise FloatingPointError(f'ODE became unstable/non-finite at iteration {i+1}; review dt/parameters.')
        seq[i]=q
    return seq

def main():
    image=Image.open(IMAGE).convert('L').resize(SIZE,Image.Resampling.LANCZOS)
    pixels=np.asarray(image,dtype=np.uint8).tobytes()
    digest,initial=seeds_from_plaintext(pixels)
    seq=generate(DISCARD+len(pixels),initial,PARAMS,DT)[DISCARD:]
    y=seq[:,1]; w=seq[:,3]
    w1_equation=(np.floor(y*1e4).astype(np.int64)%256)+1
    w1_prose=(np.floor(w*1e4).astype(np.int64)%256)+1
    different=np.count_nonzero(w1_equation!=w1_prose)
    result={
      'scope':'partial keystream reproduction only; not full cipher reproduction or security attack',
      'source_image':IMAGE.name,'source_image_sha256':hashlib.sha256(IMAGE.read_bytes()).hexdigest(),
      'grayscale_test_dimensions':list(SIZE),'plaintext_pixel_sha256':digest,
      'ode':{'method':'fixed-step classical RK4','step_size':DT,'transient_discard':DISCARD,'parameters':{'a':PARAMS[0],'b':PARAMS[1],'c':PARAMS[2],'d':PARAMS[3],'e':PARAMS[4]},'note':'step size and solver are not specified by the paper; parameters are an example in the paper, not verified encryption settings'},
      'eq17_variants':{
        'literal_displayed_equation':'W1 = mod(floor(y(i)*10^4),256)+1',
        'surrounding_prose':'W1 = mod(floor(w(i)*10^4),256)+1',
        'sample_count':int(len(w1_equation)),
        'different_positions':int(different),
        'different_fraction':float(different/len(w1_equation)),
        'equation_variant_unique_values':int(np.unique(w1_equation).size),
        'prose_variant_unique_values':int(np.unique(w1_prose).size),
      },
      'reproducibility_caveats':['The article does not state an ODE solver or step size.','This test uses one grayscale NASA smoke-test image resized to 64x64, not the paper dataset.','Only SHA seed derivation and chaotic sequence generation were implemented; scrambling, DNA encoding/diffusion, inverse, and key exchange were not.','Results characterize the effect of two conflicting Eq. 17 interpretations under one explicit numerical setting; they are not claimed as the authors original output.']
    }
    OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
