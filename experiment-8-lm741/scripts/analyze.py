import pathlib, json, csv, hashlib, re
import numpy as np
from scipy.signal import find_peaks
import matplotlib, matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
assert matplotlib.get_backend().lower()=='agg'
plt.rcParams.update({'figure.facecolor':'white','axes.facecolor':'white','font.size':10,'axes.grid':True,'grid.color':'0.85','grid.linewidth':.5,'savefig.facecolor':'white'})
trials=json.loads((ROOT/'trials.json').read_text()); rows=[]
def crossing(t,y,level=0,direction=1):
 z=y-level; ix=np.flatnonzero((z[:-1]<0)&(z[1:]>=0)) if direction==1 else np.flatnonzero((z[:-1]>0)&(z[1:]<=0))
 return t[ix]-z[ix]*(t[ix+1]-t[ix])/(z[ix+1]-z[ix])
with PdfPages(ROOT/'reports/Experiment_8_Waveform_Printouts.pdf') as pdf:
 for kind,pairs in trials.items():
  for i,(r,c) in enumerate(pairs,1):
   name=f'{kind}_{i:02}'; path=ROOT/'simulation_data'/(name+'.txt'); a=np.loadtxt(path,skiprows=1); t,y=a[:,0],a[:,1]
   log=(ROOT/'simulation_data'/(name+'.log')).read_text()
   assert not re.search(r'(?im)^(error|fatal)|timestep too small',log),name
   assert np.isfinite(a).all() and np.all(np.diff(t)>0)
   net=(ROOT/'circuits'/kind/(name+'.cir')).read_text();stop=float(re.search(r'tran \S+ (\S+)',net)[1]);assert abs(t[-1]-stop)<1e-6*stop,name
   m=t>t[-1]*.6 if kind in ['wien','astable'] else t>.005 if kind=='monostable' else t>=0
   tt,yy=t[m],y[m]; low=float(yy.min());high=float(yy.max());up=crossing(tt,yy);dn=crossing(tt,yy,direction=-1)
   row={'circuit':kind,'trial':i,'R_ohm':r,'C_F':c,'supply_V':15,'Vmax':high,'Vmin':low,'Vpp':high-low,'model':'National Semiconductor LM741/NS macromodel','status':'PASS (LM741 macromodel behavior)'}
   annotation=''
   if kind in ['wien','astable']:
    assert len(up)>=5,name
    periods=np.diff(up);T=float(np.mean(periods)); f=1/T; row.update(period_s=T,frequency_Hz=f,cycles_measured=len(periods),period_std_s=float(np.std(periods)))
    theo=1/(2*np.pi*r*c) if kind=='wien' else 1/(2*r*c*np.log(3))
    row.update(theoretical_Hz=theo,error_percent=abs(f-theo)/theo*100)
    # late-window amplitude stationarity
    early=y[(t>.6*t[-1])&(t<.8*t[-1])]; late=y[t>.8*t[-1]]
    row['amplitude_drift_percent']=abs(np.ptp(early)-np.ptp(late))/np.ptp(late)*100
    assert row['amplitude_drift_percent']<1,name
    if kind=='astable':
     ons=[float(dn[dn>u][0]-u) for u in up[:-1] if len(dn[dn>u])];on=float(np.mean(ons));row.update(Ton_s=on,Toff_s=T-on,duty_percent=100*on/T,Vhigh_plateau=float(np.median(yy[yy>.8*high])),Vlow_plateau=float(np.median(yy[yy<.8*low])))
    else:
     # Fit steady integer-cycle window; harmonic distortion indicator through fifth harmonic.
     fit=(tt>=up[0])&(tt<=up[-1]);x=tt[fit];z=yy[fit];mat=np.column_stack([np.ones(len(x))]+[g(2*np.pi*k*f*x) for k in range(1,6) for g in [np.sin,np.cos]])
     coeff=np.linalg.lstsq(mat,z,rcond=None)[0]; amps=np.hypot(coeff[1::2],coeff[2::2]);row['THD_2to5_percent']=float(100*np.linalg.norm(amps[1:])/amps[0]);row['duty_percent']='N/A (sinusoidal)'
     row['shape_note']='Saturation-limited; inspect harmonic distortion and waveform before calling it a sine'
    plotmask=t>t[-1]-5*T;annotation=f'T = {T*1e3:.4f} ms; f = {f:.3f} Hz; Vpp = {high-low:.3f} V'
   elif kind=='monostable':
    widths=[]
    for d in dn:
     nextup=up[up>d]
     if len(nextup): widths.append(float(nextup[0]-d))
    assert len(widths)==3,(name,widths)
    width=float(np.mean(widths)); nominal=13.9;vd=.6;theo=r*c*np.log((nominal+vd)/(nominal*(1-.5)))
    row.update(pulse_width_s=width,pulse_width_std_s=float(np.std(widths)),pulses_measured=len(widths),theoretical_pulse_s=theo,ideal_diode_pulse_s=r*c*np.log(2),error_percent=abs(width-theo)/theo*100,trigger_frequency_Hz=50,trigger_period_s=.02,duty_percent=width/.02*100,Vhigh_plateau=float(np.median(yy[yy>.8*high])),Vlow_plateau=float(np.median(yy[yy<.8*low])),stable_state='HIGH',quasi_stable_state='LOW')
    assert np.all(y[(t>.006)&(t<.009)]>5)
    plotmask=(t>=.008)&(t<=.016);annotation=f'LOW pulse = {width*1e3:.4f} ms; trigger = 50 Hz (external)'
   else:
    # State retention well after triggers have returned to zero.
    states=[float(np.median(y[(t>lo)&(t<hi)])) for lo,hi in [(.0002,.0008),(.0015,.0028),(.0035,.0048),(.0055,.0068),(.0075,.0088)]]
    events=np.sort(np.r_[up,dn]);assert min(abs(v) for v in states)>5
    if len(events)<4 or len(up)==0 or len(dn)==0:
     row['status']='FAIL: no demonstrated bistable switching'
     row['blocker']='12 V / 0.2 us trigger edges decay through R*C before LM741 output changes state; no topology change made.'
    row.update(initial_state='HIGH' if states[0]>0 else 'LOW',final_state='HIGH' if states[-1]>0 else 'LOW',retained_levels_V=states,switch_times_s=events.tolist(),frequency_Hz='N/A',period_s='N/A',duty_percent='N/A',trigger_conditions='0 to +12 or -12 V pulses, 0.2 ms wide, edges 0.2 us; positive edge resets, negative edge sets',threshold_V=high*.5)
    plotmask=t>=0;annotation='Both states switch and persist; f, T, duty: N/A' if row['status'].startswith('PASS') else 'FAIL: output did not switch with the specified trigger. f, T, duty: N/A'
   rows.append(row)
   fig=plt.figure(figsize=(8.27,11.69));gs=fig.add_gridspec(2 if kind in ['monostable','bistable'] else 1,1,left=.12,right=.95,bottom=.32,top=.80,hspace=.2)
   fig.text(.1,.94,'EC3091D - Experiment 8',fontsize=15,weight='bold');fig.text(.1,.90,f'{kind.title()} - Trial {i} / Figure {list(trials).index(kind)+1}',fontsize=13)
   fig.text(.1,.865,f'R = {r:g} ohm; C = {c*1e6:g} uF; supplies = +/-15 V',fontsize=11)
   fig.text(.1,.835,'NATIONAL SEMICONDUCTOR LM741 MACROMODEL',fontsize=10,weight='bold')
   x=t[plotmask]*1e3
   ax=fig.add_subplot(gs[0]);ax.plot(x,y[plotmask],color='black',lw=1,label='Output V(out)');ax.set(ylabel='Voltage (V)');ax.legend(loc='upper right',fontsize=8);ax.set_ylim(low-2,high+2)
   if kind in ['monostable','bistable']:
    ax2=fig.add_subplot(gs[1],sharex=ax);ax2.plot(x,a[plotmask,2],color='0.2',lw=1,ls='--',label='Applied trigger V(in)');ax2.plot(x,a[plotmask,3],color='black',lw=.8,label='Inverting input V(C)');ax2.set(xlabel='Time (ms)',ylabel='Voltage (V)');ax2.legend(fontsize=8,loc='upper right')
   else: ax.set_xlabel('Time (ms)')
   fig.text(.1,.255,annotation,fontsize=9);fig.text(.1,.22,'Measured from ngspice numerical transient data; 0 V output crossings.',fontsize=9)
   fig.text(.1,.185,f'Data: simulation_data/{name}.txt',fontsize=9)
   fig.text(.1,.13,'Observation / handwritten notes: __________________________________',fontsize=10)
   fig.text(.1,.085,'________________________________________________________________',fontsize=10)
   fig.savefig(ROOT/'waveforms'/(name+'.png'),dpi=300)
   if row['status'].startswith('PASS'): pdf.savefig(fig)
   else: fig.savefig(ROOT/'reports/Bistable_Baseline_Failure.pdf')
   plt.close(fig)
   with Image.open(ROOT/'waveforms'/(name+'.png')) as im: im.verify()
(ROOT/'calculations/observations.json').write_text(json.dumps(rows,indent=2))
keys=list(dict.fromkeys(k for row in rows for k in row))
with (ROOT/'calculations/observations.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
print(json.dumps(rows,indent=2))
