from pathlib import Path
import json, subprocess, hashlib, zipfile, re
import fitz
from PIL import Image
root=Path(__file__).resolve().parents[1];qc={}
rows=json.loads((root/'calculations/observations.json').read_text());assert len(rows)==13
passes=[r for r in rows if r['status'].startswith('PASS')];fails=[r for r in rows if not r['status'].startswith('PASS')];assert len(passes)==12 and len(fails)==1 and fails[0]['circuit']=='bistable' and fails[0]['trial']==1
qc['behavior']={'final_trials':13,'passes':12,'failures':[{'name':'bistable_01','reason':fails[0]['blocker']}],'successful_trials_per_circuit':{k:sum(r['circuit']==k for r in passes) for k in ['wien','astable','monostable','bistable']}}
for r in rows:
 name=f"{r['circuit']}_{r['trial']:02}";p=root/'simulation_data'/(name+'.log');s=p.read_text().lower();assert 'no. of data rows' in s and 'timestep too small' not in s and 'error:' not in s
 # analyze.py additionally checks the requested stop time and the waveform behavior
qc['logs']='PASS: 13 final transient logs; no timestep-too-small or error; missing-spinit warning retained'
orig=(root/'models/LM741.model').read_text();expected=orig.replace('EOS 7 1 POLY(1) 16 49 1E-3 1','BEOS 7 1 V=1e-3+v(16,49)').replace('F6 50 99 POLY(1) V6 450U 1','BF6 50 99 I=450u+i(V6)');working=(root/'models/LM741_ngspice.lib').read_text().split('\n',1)[1];assert working==expected
qc['model']={'status':'PASS exact two-source algebraic compatibility translation','source_sha256':hashlib.sha256((root/'models/LM741.model').read_bytes()).hexdigest(),'validation':json.loads((root/'calculations/model_validation.json').read_text()),'limitation':'manufacturer-attributed mirrored macromodel; no hardware validation or comparison to current TI release'}
images=sorted((root/'waveforms').glob('*.png'));assert len(images)==13
for f in images:
 with Image.open(f) as im:im.load();assert im.size==(2481,3507) and min(im.info['dpi'])>299;assert im.convert('RGB').getpixel((0,0))==(255,255,255)
qc['PNG']={'total':13,'successful_waveforms':12,'failed_baseline_diagnostic':1,'DPI':300,'decode_white_background':'PASS'}
for f in (root/'reports').glob('*.pdf'):
 d=fitz.open(f);assert len(d)>0
 if 'Printouts' in f.name:assert len(d)==12
 if 'Failure' in f.name:assert len(d)==1
 for page in d:
  assert abs(page.rect.width-595)<1 and abs(page.rect.height-842)<1
  for b in page.get_text('blocks'):assert b[0]>=0 and b[2]<=page.rect.width and b[1]>=0 and b[3]<=page.rect.height,(f.name,page.number,b[:4])
 qc[f.name]={'pages':len(d),'A4_text_bounds':'PASS'}
with zipfile.ZipFile(root/'reports/Experiment_8_Complete_Report.docx') as z:assert z.testzip() is None and 'word/document.xml' in z.namelist()
qc['DOCX']='PASS XML/ZIP integrity; PDF is print-layout reference'
ref=json.loads((root/'calculations/timestep_refinement.json').read_text());assert all(v['status']=='PASS' for v in ref.values());qc['refinement']=ref
status=subprocess.check_output(['git','-C','/workspace/circuit-lab','--no-optional-locks','status','--porcelain=v1'],text=True);assert status==''
qc['repository']={'status':'clean including untracked','commit':subprocess.check_output(['git','-C','/workspace/circuit-lab','rev-parse','HEAD'],text=True).strip()}
qc['delivery']='Cloud workspace only per user instruction; no external upload'
(root/'QC.json').write_text(json.dumps(qc,indent=2));files=sorted(f for f in root.rglob('*') if f.is_file() and f.name!='SHA256SUMS.txt')
(root/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(root)) for f in files)+'\n');print(json.dumps(qc,indent=2))
