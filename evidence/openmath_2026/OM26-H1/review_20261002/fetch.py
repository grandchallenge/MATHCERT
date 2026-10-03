import subprocess,json,pathlib,base64,hashlib
root=pathlib.Path(__file__).parent

def fetch(repo,ref,path,name):
 d=json.loads(subprocess.check_output(['gh','api',f'repos/grandchallenge/{repo}/contents/{path}?ref={ref}']));b=base64.b64decode(d['content']);(root/name).write_bytes(b);print(name,'blob',d['sha'],'sha256',hashlib.sha256(b).hexdigest());return b
if __name__=='__main__':
 sha='8a2610215989bec15474f0a088945c0a1b6d8172'
 for f in ['INTAKE.json','INDEPENDENT_REVIEW_BOOTSTRAP.md']:
  b=fetch('MATHCERT',sha,'evidence/openmath_2026/OM26-H1/RH_BADER93/'+f,'RH_'+f); print(b.decode())
 a=json.loads((root/'evidence__openmath_2026__OM26-H1__INTAKE.json').read_text())
 b=fetch('MATHFORGE',a['source_authority']['forge_commit'],a['source_authority']['statement']['path'],'STATEMENT.md');print(b.decode())
