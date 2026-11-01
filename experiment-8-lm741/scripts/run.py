#!/usr/bin/env python3
import pathlib, json, subprocess, os, argparse, numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('--only',default='all'); args=p.parse_args()
cfg=ROOT/'trials.json'
if not cfg.exists():
 cfg.write_text(json.dumps({'wien':[[10000,1e-7],[1000,2.2e-7],[4700,1e-7]],'astable':[[4700,1e-7],[10000,1e-7],[22000,1e-7]],'monostable':[[15000,1e-7],[22000,1e-7],[33000,1e-7]],'bistable':[[100,1e-7],[220,1e-7],[470,1e-7]]},indent=2))
trials=json.loads(cfg.read_text())
for kind, pairs in trials.items():
 for i,(r,c) in enumerate(pairs,1):
  name=f'{kind}_{i:02}';
  if args.only not in ['all',name]: continue
  d=ROOT/'circuits'/kind; d.mkdir(exist_ok=True)
  common=f'''{name} - original lab topology; National Semiconductor LM741 macromodel
.include {ROOT}/models/LM741_ngspice.lib
Vpos vp 0 15
Vneg vn 0 -15
.model D4148 D(Is=2.52n Rs=0.568 N=1.752 Cjo=4p M=0.4 Tt=20n)
'''
  if kind=='wien':
   rf=2010
   circuit=f'Rin minus 0 1k\nRF out minus {rf}\nR1 plus 0 {r}\nC1 plus 0 {c} IC=0.05\nR2 out series {r}\nC2 series plus {c}\nXU plus minus vp vn out LM741/NS\n'
   stop=5000*r*c; step=r*c/120; nodes='v(out) v(plus)'; init=''
   circuit += '.ic v(plus)=0.05\n'
  elif kind=='astable':
   circuit=f'R1 plus 0 10k\nR2 out plus 10k\nR out minus {r}\nC minus 0 {c} IC=0.05\nXU plus minus vp vn out LM741/NS\n'
   stop=50*r*c; step=min(r*c/200,1e-6); nodes='v(out) v(minus)'; init='uic'
  elif kind=='monostable':
   circuit=f'R1 out plus 10k\nR2 plus 0 10k\nR out minus {r}\nC minus 0 {c}\nD1 minus 0 D4148\nCd trigger diff 10n\nRd diff 0 470\nD2 plus diff D4148\nVtrigger trigger 0 PULSE(0 -15 10m 50u 1u 0.1m 20m)\nXU plus minus vp vn out LM741/NS\n'
   stop=.07; step=1e-6; nodes='v(out) v(trigger) v(minus) v(plus)'; init=''
  else:
   # Figure 4: trigger source at unspecified left terminal of C.
   circuit=f'R1 out plus 10k\nR2 plus 0 10k\nC trigger minus {c}\nR minus 0 {r}\nVtrigger trigger 0 PWL(0 0 1m 0 1.0002m 12 1.2m 12 1.2002m 0 3m 0 3.0002m -12 3.2m -12 3.2002m 0 5m 0 5.0002m 12 5.2m 12 5.2002m 0 7m 0 7.0002m -12 7.2m -12 7.2002m 0 9m 0)\nXU plus minus vp vn out LM741/NS\n'
   circuit += '.nodeset v(out)=11 v(plus)=5.5\n'
   stop=.009; step=1e-7; nodes='v(out) v(trigger) v(minus) v(plus)'; init=''
  net=common+circuit+f'''.options reltol=1e-5 abstol=1e-10 method=gear maxord=2
.control
set wr_singlescale
set wr_vecnames
tran {step} {stop} 0 {step} {init}
wrdata {ROOT}/simulation_data/{name}.txt {nodes}
quit
.endc
.end
'''
  path=d/(name+'.cir');path.write_text(net)
  q=subprocess.run(['ngspice','-b',str(path)],capture_output=True,text=True)
  (ROOT/'simulation_data'/(name+'.log')).write_text(q.stdout+q.stderr)
  log=q.stdout+q.stderr
  data=ROOT/'simulation_data'/(name+'.txt')
  complete=False
  if data.exists():
   try: complete=abs(float(data.read_text().splitlines()[-1].split()[0])-stop)<max(1e-9,stop*1e-6)
   except Exception: pass
  print(name, 'TRANSIENT COMPLETE' if q.returncode==0 and complete and 'timestep too small' not in log.lower() else 'FAIL: incomplete transient', flush=True)
  if q.returncode or not (ROOT/'simulation_data'/(name+'.txt')).exists(): print(q.stderr,flush=True)
