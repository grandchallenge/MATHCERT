from fractions import Fraction as Q
from itertools import combinations
from math import gcd
import json, pathlib, hashlib
ROOT=pathlib.Path(__file__).parent

def pairs_no_duplicate(items):
 d={}
 for k,v in items:
  if k in d: raise ValueError('duplicate key')
  d[k]=v
 return d

def validate(b,n):
 assert len(b)<=65536
 d=json.loads(b,object_pairs_hook=pairs_no_duplicate)
 assert set(d)=={'lines'} and len(d['lines'])==n
 norms=set()
 for line in d['lines']:
  assert len(line)==3 and all(type(v)==int and abs(v)<=10**30 for v in line)
  a,b,c=line; assert a or b
  g=gcd(gcd(abs(a),abs(b)),abs(c)); normal=tuple(v//g for v in line)
  if next(v for v in normal if v)!=abs(next(v for v in normal if v)):normal=tuple(-v for v in normal)
  assert normal not in norms; norms.add(normal)
 return d['lines']

def intersection(l,m):
 a,b,c=l;d,e,f=m;det=a*e-b*d
 return None if det==0 else (Q(b*f-c*e,det),Q(c*d-a*f,det))

def count(lines):
 triangles=[];stats={'parallel_support_triples':0,'concurrent_support_triples':0,'interior_crossed_triples':0,'accepted_with_vertex_touch':0}
 for triple in combinations(range(len(lines)),3):
  vertices=[intersection(lines[i],lines[j]) for i,j in combinations(triple,2)]
  if None in vertices:stats['parallel_support_triples']+=1;continue
  if len(set(vertices))<3:stats['concurrent_support_triples']+=1;continue
  touch=False
  for k,(a,b,c) in enumerate(lines):
   if k in triple:continue
   vals=[a*x+b*y+c for x,y in vertices]
   if min(vals)<0<max(vals):stats['interior_crossed_triples']+=1;break
   touch |= 0 in vals
  else:
   triangles.append(list(triple));stats['accepted_with_vertex_touch']+=int(touch)
 return {'triangles':len(triangles),'supporting_line_triples':triangles,'statistics':stats}
if __name__=='__main__':
 fixtures=[('unit_triangle',[[1,0,0],[0,1,0],[1,1,-1]],1),('parallel',[[1,0,0],[1,0,-1],[0,1,0]],0),('concurrent',[[1,0,0],[0,1,0],[1,1,0]],0),('vertex_touch',[[1,0,0],[0,1,0],[1,1,-1],[1,-1,0]],2),('side_subdivision',[[1,0,0],[0,1,0],[1,1,-1],[1,0,-1]],1)]
 checks=[]
 for name,lines,want in fixtures:
  result=count(lines);assert result['triangles']==want,(name,result);checks.append({'fixture':name,'expected':want,'observed':result})
 (ROOT/'degeneracy_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
 for name in ['candidate86','candidate93']:
  b=(ROOT/(name+'.json')).read_bytes();expected={'candidate86':('05a5f519433a0787a96a3f6c5a8cef17fc7f8ab093ccf0c9ab45a2d564ad11d5',86),'candidate93':('e606799ad6c1296deedb475440d1eecbe86daba8a3af625718f55726f93da4d5',93)}[name];assert hashlib.sha256(b).hexdigest()==expected[0],'candidate identity mismatch';result=count(validate(b,18));assert result['triangles']==expected[1],'count mismatch';result.update(candidate_sha256=hashlib.sha256(b).hexdigest(),line_count=18,predicate='affine strict opposite vertex signs',arithmetic='fractions.Fraction',indexing='zero-based')
  (ROOT/(name+'_ledger.json')).write_text(json.dumps(result,indent=2)+'\n');print(name,result['triangles'],result['statistics'])
