from pathlib import Path
import re,subprocess,json,numpy as np
ROOT=Path(__file__).resolve().parents[1];d=ROOT/'simulation_data/refinement';d.mkdir(exist_ok=True)
def crosses(t,y,sign):
 ix=np.flatnonzero((y[:-1]<0)&(y[1:]>=0)) if sign>0 else np.flatnonzero((y[:-1]>0)&(y[1:]<=0))
 return t[ix]-y[ix]*(t[ix+1]-t[ix])/(y[ix+1]-y[ix])
def metric(path,kind):
 a=np.loadtxt(path,skiprows=1);t,y=a[:,0],a[:,1];m=t>.6*t[-1] if kind in ['wien','astable'] else t>.005 if kind=='monostable' else t>=0;t,y=t[m],y[m];u=crosses(t,y,1);v=crosses(t,y,-1)
 if kind in ['wien','astable']:return float(np.mean(np.diff(u)))
 if kind=='monostable':return float(np.mean([u[u>x][0]-x for x in v if len(u[u>x])]))
 return float(v[0])
res={}
for kind in ['wien','astable','monostable','bistable']:
 name=kind+('_02' if kind=='bistable' else '_01');src=ROOT/'circuits'/kind/(name+'.cir');s=src.read_text();m=re.search(r'tran (\S+) (\S+) 0 (\S+)',s);step=float(m[1])/2
 s=s[:m.start()]+f'tran {step} {m[2]} 0 {step}'+s[m.end():];s=s.replace(str(ROOT/'simulation_data'/(name+'.txt')),str(d/(name+'.txt')))
 path=d/(name+'.cir');path.write_text(s);p=subprocess.run(['ngspice','-b',str(path)],capture_output=True,text=True);(d/(name+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0
 base=metric(ROOT/'simulation_data'/(name+'.txt'),kind);new=metric(d/(name+'.txt'),kind);err=abs(new-base)/abs(base)*100
 res[name]={'base_metric_s':base,'half_step_metric_s':new,'relative_difference_percent':err,'status':'PASS' if err<.5 else 'FAIL'}
 print(name,res[name],flush=True)
(ROOT/'calculations/timestep_refinement.json').write_text(json.dumps(res,indent=2))
