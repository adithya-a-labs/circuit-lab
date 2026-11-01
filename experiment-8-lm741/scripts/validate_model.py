from pathlib import Path
import subprocess,json,numpy as np
root=Path(__file__).resolve().parents[1]
p=subprocess.run(['ngspice','-b',str(root/'circuits/validation/model_check.cir')],capture_output=True,text=True)
(root/'simulation_data/model_check.log').write_text(p.stdout+p.stderr)
assert p.returncode==0 and 'timestep too small' not in (p.stdout+p.stderr).lower()
a=np.loadtxt(root/'simulation_data/model_dc.txt',skiprows=1); b=np.loadtxt(root/'simulation_data/model_slew.txt',skiprows=1)
m=(b[:,0]>50e-6)&(b[:,0]<80e-6)&(b[:,1]>-4)&(b[:,1]<4)
slope=float(np.polyfit(b[m,0],b[m,1],1)[0]/1e6)
r={'follower_max_error_V':float(np.max(abs(a[:,0]-a[:,1]))),'positive_open_loop_saturation_V':float(a[-1,2]),'negative_open_loop_saturation_V':float(a[0,2]),'slew_V_per_us':slope,'pin_order':'noninverting,inverting,+supply,-supply,out','supply_V':'+15/-15','model':'National Semiconductor LM741/NS'}
assert r['follower_max_error_V']<.005 and a[-1,2]>10 and a[0,2]<-10 and .2<slope<1
r['status']='PASS (macromodel validation; not physical hardware)'
(root/'calculations/model_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
