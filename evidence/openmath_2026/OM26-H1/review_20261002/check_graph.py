from verify import *

def graph_triples(lines):
 vertices=[set() for _ in lines]
 for i,j in combinations(range(len(lines)),2):
  p=intersection(lines[i],lines[j])
  if p is not None: vertices[i].add(p);vertices[j].add(p)
 triples=[]
 for t in combinations(range(len(lines)),3):
  i,j,k=t;p=intersection(lines[i],lines[j]);q=intersection(lines[i],lines[k]);r=intersection(lines[j],lines[k])
  if None in (p,q,r) or len({p,q,r})<3:continue
  good=True
  for s,u,v in [(i,p,q),(j,p,r),(k,q,r)]:
   axis=0 if u[0]!=v[0] else 1;lo,hi=sorted([u[axis],v[axis]])
   if any(lo<w[axis]<hi for w in vertices[s]):good=False;break
  if good:triples.append(list(t))
 return triples
if __name__=='__main__':
 checks=[]
 for path in [ROOT/'candidate86.json',ROOT/'candidate93.json']:
  lines=validate(path.read_bytes(),18);a=count(lines)['supporting_line_triples'];b=graph_triples(lines);assert a==b;checks.append({'candidate':path.name,'count':len(b),'exact_triples_equal':True})
 # This graph checker was written AFTER reading FACE_CRITERION; it is a corroborating check,
 # and does not replace the pre-proof independent sign predicate.
 fixtures=json.loads((ROOT/'degeneracy_checks.json').read_text())
 cases=[[[1,0,0],[0,1,0],[1,1,-1]],[[1,0,0],[1,0,-1],[0,1,0]],[[1,0,0],[0,1,0],[1,1,0]],[[1,0,0],[0,1,0],[1,1,-1],[1,-1,0]],[[1,0,0],[0,1,0],[1,1,-1],[1,0,-1]],[[1,0,0],[0,1,0],[1,1,-2],[1,-1,0]],[[1,0,0],[0,1,0],[1,1,-2],[1,0,-1]],[[1,0,0],[0,1,0],[1,1,-2],[1,1,0]]]
 for lines in cases:assert graph_triples(lines)==count(lines)['supporting_line_triples']
 checks.append({'degeneracy_arrangements':len(cases),'exact_triples_equal':True})
 (ROOT/'graph_crosscheck.json').write_text(json.dumps(checks,indent=2)+'\n');print(checks)
