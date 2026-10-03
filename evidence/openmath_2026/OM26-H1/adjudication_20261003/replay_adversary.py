from pathlib import Path
import json, importlib.util, tempfile, shutil, subprocess
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'review_evidence'
spec=importlib.util.spec_from_file_location('h1review',SOURCE/'verify.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
for name,lines,want in [('vertex_only_touch',[[1,0,0],[0,1,0],[1,1,-1],[1,1,0]],1),('vertex_entry',[[1,0,0],[0,1,0],[1,1,-1],[1,-1,0]],2),('concurrent',[[1,0,0],[0,1,0],[1,1,0]],0),('parallel',[[1,0,0],[1,0,-1],[0,1,0]],0)]:
 got=m.count(lines)['triangles'];assert got==want;checks.append({'name':name,'expected':want,'observed':got,'result':'PASS'})
for name,lines in [('coincident_scaled',[[1,0,0],[2,0,0],[0,1,0]]),('boolean',[[True,0,0],[0,1,0],[1,1,-1]]),('zero_normal',[[0,0,1],[0,1,0],[1,1,-1]]),('integer_bound',[[10**30+1,0,0],[0,1,0],[1,1,-1]])]:
 try:m.validate(json.dumps({'lines':lines}).encode(),3)
 except (AssertionError,ValueError):checks.append({'name':name,'result':'REJECTED_AS_REQUIRED'})
 else:raise AssertionError(name)
with tempfile.TemporaryDirectory() as d:
 t=Path(d)
 for f in ['verify.py','candidate86.json','candidate93.json']:shutil.copy2(SOURCE/f,t/f)
 data=json.loads((t/'candidate86.json').read_text());data['lines'][0][2]+=1;(t/'candidate86.json').write_text(json.dumps(data))
 run=subprocess.run(['python',str(t/'verify.py')],capture_output=True,text=True)
 assert run.returncode!=0 and 'candidate identity mismatch' in run.stderr
 checks.append({'name':'candidate_coordinate_mutation','result':'REJECTED_BEFORE_REPLAY_BY_SHA256'})
for n in [86,93]:
 lines=m.validate((SOURCE/f'candidate{n}.json').read_bytes(),18);now=m.count(lines);ledger=json.loads((SOURCE/f'candidate{n}_ledger.json').read_text())
 assert ledger['supporting_line_triples']==now['supporting_line_triples']
 bad=dict(ledger);bad['triangles']+=1;assert bad['triangles']!=now['triangles']
 checks.append({'name':f'candidate{n}_ledger_count_mutation','result':'DETECTED_BY_EXACT_REGENERATED_COUNT'})
assert checks==json.loads((ROOT/'ADVERSARY_CHECKS.json').read_text())
print(json.dumps(checks,indent=2))
