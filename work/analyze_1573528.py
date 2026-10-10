import wave,json,math
import numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).parent
with wave.open(str(root/'music/1573528.wav')) as w:
 sr=w.getframerate();audio=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
hop=220;n=2048
frames=np.lib.stride_tricks.sliding_window_view(audio,n)[::hop]
w=np.hanning(n).astype(np.float32);freq=np.fft.rfftfreq(n,1/sr)
bands=[];flux=[];prev=np.zeros(n//2+1)
for a in range(0,len(frames),1024):
 f=frames[a:a+1024];spec=np.abs(np.fft.rfft(f*w,axis=1));log=np.log1p(spec*10)
 delta=np.maximum(0,log-np.vstack([prev,log[:-1]]));prev=log[-1]
 flux.extend(np.mean(delta[:,freq>120],axis=1).tolist())
 bands.extend(np.stack([np.sqrt(np.mean(f*f,axis=1)),np.mean(spec[:,(freq>25)&(freq<160)],axis=1),np.mean(spec[:,(freq>200)&(freq<5000)],axis=1)],axis=1).tolist())
times=(np.arange(len(frames))*hop+n/2)/sr;flux=np.array(flux);bands=np.array(bands)
# Robust local contrast, without confusing a sustained loud note for an onset.
mean=np.convolve(flux,np.ones(101)/101,mode='same');contrast=np.maximum(0,flux-mean)
peaks=[i for i in range(2,len(flux)-2) if contrast[i]==max(contrast[i-2:i+3]) and contrast[i]>.035]
peaks=sorted(peaks,key=lambda i:contrast[i],reverse=True);chosen=[];taken=np.zeros(len(flux),bool)
for i in peaks:
 if taken[i]:continue
 chosen.append(i);taken[max(0,i-8):min(len(flux),i+9)]=True
chosen.sort()
onsets=[{'time':round(float(times[i]),5),'strength':round(float(contrast[i]),5),'bass':round(float(bands[i,1]),5)} for i in chosen]
# Score an onset comb against candidate tempos and phases across both drops.
active=(times>10)&(times<220);tt=times[active];ff=contrast[active]
best=[]
for bpm in np.arange(80,201,.1):
 phase=np.angle(np.sum(ff*np.exp(2j*np.pi*tt/(60/bpm))))/(2*np.pi)*(60/bpm)
 strength=abs(np.sum(ff*np.exp(2j*np.pi*tt/(60/bpm))))
 best.append((strength,bpm,phase%(60/bpm)))
score,bpm,phase=max(best)
print('duration',len(audio)/sr,'BPM',bpm,'phase',phase,'onsets',len(onsets))
for t in np.arange(0,250,5):
 mask=(times>=t)&(times<t+5)
 print(round(t),*[round(float(q),3) for q in bands[mask].mean(0)])
plan={'song':1573528,'duration':len(audio)/sr,'bpm':float(bpm),'phase':float(phase),'onsets':onsets,'analysis':'spectral flux and onset-comb estimation from cached original MP3; no claim of manual listening'}
(root/'music-1573528-analysis.json').write_text(json.dumps(plan,indent=2))
np.savez_compressed(root/'music/features-1573528.npz',time=times,bands=bands,flux=flux,contrast=contrast)
im=Image.new('RGB',(1600,1050),(12,16,25));d=ImageDraw.Draw(im)
for row,(start,end) in enumerate([(0,80),(80,160),(160,240)]):
 ybase=320+row*350;mask=(times>=start)&(times<end)
 for k,col in [(0,(228,195,239)),(1,(255,133,56)),(2,(132,101,240))]:
  vals=bands[mask,k];vals=vals/max(np.percentile(bands[:,k],99),.00001)
  pts=[(40+(t-start)/(end-start)*1520,ybase-min(1,v)*260) for t,v in zip(times[mask][::10],vals[::10])]
  d.line(pts,fill=col,width=1)
 for t in range(start,end+1,5):
  x=40+(t-start)/(end-start)*1520;d.line((x,ybase,x,ybase+5),fill='white');d.text((x-8,ybase+9),str(t),fill='white')
 d.text((40,ybase-290),'SONG 1573528 / white: amplitude, orange: bass, violet: mid-high energy',fill='white')
im.save(root/'music/timeline-1573528.png')
