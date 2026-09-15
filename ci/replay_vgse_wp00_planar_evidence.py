#!/usr/bin/env python3
"""Independent exact/interval replay for VGSE-C05.

Uses only the MATHCERT C00/C01/C04 exact replay. No MATHSOLVE VGSE code,
numerical roots, or generated coordinates are consumed.
"""
from __future__ import annotations
import hashlib, importlib.util, itertools, json
from collections import defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("vgse_exact",ROOT/"ci"/"replay_vgse_wp00_exact_evidence.py")
assert spec and spec.loader
base=importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
x,y,t=base.x,base.y,base.t; I=sp.I

# Fixed labeled dual-cell combinatorics reconstructed from Figure 16 pattern 1.
P0,P1,P2,P3,P4,P5="P0 P1 P2 P3 P4 P5".split(); A,D,C="A D C".split()
POINTS=[P0,P1,P2,P3,P4,P5,A,D,C]
FACES={
 "F01":[A,P2,P1],"F02":[P0,A,P1],"F03":[P4,C,D],"F04":[A,D,C,P2],
 "F05":[P2,C,P3],"F06":[P3,C,P4],"F07":[A,P0,P5,D],"F08":[P4,D,P5],
}
# (id, white, black, sign, exact weight, oriented dual start, oriented dual end)
EDGES=[
 ("F01|F04","F01","F04", 1,sp.Rational(1),A,P2),
 ("F01|F02","F01","F02", 1,sp.Rational(1),P1,A),
 ("F07|F02","F07","F02", 1,sp.Rational(1),A,P0),
 ("F03|F06","F03","F06",-1,sp.Rational(1),P4,C),
 ("F03|F04","F03","F04", 1,sp.Rational(2,7),C,D),
 ("F03|F08","F03","F08", 1,sp.Rational(25,7),D,P4),
 ("F07|F04","F07","F04",-1,sp.Rational(6,7),D,A),
 ("F05|F04","F05","F04", 1,sp.Rational(3,25),P2,C),
 ("F05|F06","F05","F06", 1,sp.Rational(2,25),C,P3),
 ("F07|F08","F07","F08", 1,sp.Rational(9,7),P5,D),
 ("B1","F07","U1",1,sp.Rational(1),P0,P5),
 ("B2","U2","F02",1,sp.Rational(1),P0,P1),
 ("B3","F01","U3",1,sp.Rational(1),P2,P1),
 ("B4","F05","U4",1,sp.Rational(1),P3,P2),
 ("B5","U5","F06",1,sp.Rational(1),P3,P4),
 ("B6","U6","F08",1,sp.Rational(1),P4,P5),
]
COLORS={**base.COLORS,"U1":"black","U2":"white","U3":"black","U4":"black","U5":"white","U6":"white"}
KAWASAKI={A:([P0,P1,P2,D],-sp.Rational(6,7)),D:([A,C,P4,P5],-sp.Rational(3,25)),C:([P2,P3,P4,D],-sp.Rational(4,21))}
CENTERS=[
 (F(-643258615714007,500000000000000),F(-209351489834101,125000000000000)),
 (F(-565695992298869,10**15),F(-2083580087894511,10**15)),
 (F(1268914500001,20000000000000),F(-367278724452119,10**15)),
 (F(76048389833163,10**15),F(-339351844508339,500000000000000)),
 (F(365042265789951,500000000000000),F(-158630455064113,500000000000000)),
]
RAD=F(1,10**10)

def saturated():
 nx,ny,Dv=base.master_equations(); g=sp.groebner([nx,ny,1-t*Dv],t,y,x,order="lex",domain=sp.QQ_I)
 bs=[p.as_expr() for p in g.polys]
 q=sp.Poly(next(b for b in bs if not b.has(t) and not b.has(y)),x,domain=sp.QQ_I).monic()
 r=sp.Poly(next(b for b in bs if not b.has(t) and sp.Poly(b,y).degree()==1),y,x,domain=sp.QQ_I)
 lc=r.coeff_monomial(y); p=sp.cancel(-sp.Poly(r.as_expr().subs(y,0),x,domain=sp.QQ_I).as_expr()/lc)
 tri=sp.groebner([y-p,q.as_expr()],y,x,order="lex",domain=sp.QQ_I)
 return q,p,tri

def zero_mod(expr,tri):
 num,_=sp.fraction(sp.cancel(expr)); rem=tri.reduce(sp.Poly(sp.expand(num),y,x,domain=sp.QQ_I).as_expr())[1]
 return sp.simplify(rem)==0

def exact_positions(q,p,tri):
 whites=sorted(v for v,c in COLORS.items() if c=="white"); blacks=sorted(v for v,c in COLORS.items() if c=="black")
 wi={v:i for i,v in enumerate(whites)}; bi={v:i for i,v in enumerate(blacks)}
 b=base.BOUNDARY; dz=[]
 for i in range(6):
  cx,cy=b[i]; px,py=b[i-1]; dz.append((cx-px)+I*(cy-py))
 zeta=base.ALPHAS; zt=[sp.cancel(dz[i]/zeta[i]) for i in range(6)]
 pf=[(-1)**i*zeta[i] for i in range(6)]; pt=[(-1)**i*zt[i] for i in range(6)]
 mf=[]; rf=[]
 for black in sorted(v for v in blacks if not v.startswith("U")):
  row=[sp.Rational(0)]*7
  for _,w,bb,s,wt,_,_ in EDGES:
   if bb==black: row[wi[w]]+=s*wt
  mf.append(row); rf.append(0)
 for j in range(6):
  _,w,bb,s,wt,_,_=EDGES[10+j]; row=[sp.Rational(0)]*7; u=f"U{j+1}"
  if COLORS[u]=="white": row[wi[u]]=-1
  else: row[wi[base.BOUNDARY_OWNERS[j]]]=-s*wt
  mf.append(row); rf.append(pf[j])
 MF=sp.Matrix(mf); RF=sp.Matrix(rf); piv=MF.T.rref()[1]; assert piv==(0,1,2,3,4,5,7)
 fs=MF[list(piv),:].inv()*RF[list(piv),:]; assert all(sp.simplify(v)==0 for v in MF*fs-RF)
 fv={v:sp.cancel(fs[i]) for i,v in enumerate(whites)}
 mt=[]; rt=[]
 for white in sorted(v for v in whites if not v.startswith("U")):
  row=[sp.Rational(0)]*7
  for _,ww,bb,s,wt,_,_ in EDGES:
   if ww==white: row[bi[bb]]+=s*wt
  mt.append(row); rt.append(0)
 for j in range(6):
  _,w,bb,s,wt,_,_=EDGES[10+j]; row=[sp.Rational(0)]*7; u=f"U{j+1}"
  if COLORS[u]=="black": row[bi[u]]=1
  else: row[bi[base.BOUNDARY_OWNERS[j]]]=-s*wt
  mt.append(row); rt.append(pt[j])
 MT=sp.Matrix(mt); RT=sp.Matrix(rt); piv=MT.T.rref()[1]; assert piv==(0,1,2,3,4,5,6)
 ts=MT[list(piv),:].inv()*RT[list(piv),:]; assert all(zero_mod(v,tri) for v in MT*ts-RT)
 tv={v:sp.cancel(ts[i]) for i,v in enumerate(blacks)}
 adj=defaultdict(list)
 for _,w,bb,s,wt,a,bp in EDGES:
  inc=sp.cancel(fv[w]*s*wt*tv[bb]); adj[a].append((bp,inc)); adj[bp].append((a,-inc))
 pos={P0:sp.Integer(0)}; Q=deque([P0]); closures=[]
 while Q:
  a=Q.popleft()
  for b2,inc in adj[a]:
   cand=sp.cancel(pos[a]+inc)
   if b2 not in pos: pos[b2]=cand; Q.append(b2)
   else: closures.append(sp.cancel(pos[b2]-cand))
 assert set(pos)==set(POINTS) and all(zero_mod(v,tri) for v in closures)
 targets=dict(zip([P0,P1,P2,P3,P4,P5],[u+I*v for u,v in b]))
 shift=sp.cancel(targets[P0]-pos[P0]); pos={k:sp.cancel(v+shift) for k,v in pos.items()}
 assert all(zero_mod(pos[k]-targets[k],tri) for k in targets)
 px={k:sp.cancel(v.subs(y,p)) for k,v in pos.items()}
 ks=[]
 for k,(order,want) in KAWASAKI.items():
  rays=[sp.cancel(px[v]-px[k]) for v in order]; cr=sp.cancel(rays[1]*rays[3]/(rays[0]*rays[2]))
  assert cr==want and want<0; ks.append({"vertex":k,"cross_ratio":str(want)})
 h=hashlib.sha256("|".join(sp.sstr(px[k]) for k in sorted(px)).encode()).hexdigest()
 return px,{"f_system_rank":7,"tilde_system_rank":7,"f_all_equations_exact":True,"tilde_all_equations_zero_mod_saturated_ideal":True,"primitive_closure_zero_mod_saturated_ideal":True,"prescribed_boundary_exact_mod_saturated_ideal":True,"kawasaki_cross_ratios":ks,"position_expression_sha256":h}

@dataclass(frozen=True)
class Iv:
 lo:F; hi:F
 def __post_init__(self): assert self.lo<=self.hi
 @staticmethod
 def p(v): v=F(v); return Iv(v,v)
 def __add__(self,o): o=o if isinstance(o,Iv) else Iv.p(o); return Iv(self.lo+o.lo,self.hi+o.hi)
 __radd__=__add__
 def __neg__(self): return Iv(-self.hi,-self.lo)
 def __sub__(self,o): return self+(-(o if isinstance(o,Iv) else Iv.p(o)))
 def __rsub__(self,o): return Iv.p(o)-self
 def __mul__(self,o):
  o=o if isinstance(o,Iv) else Iv.p(o); a=(self.lo*o.lo,self.lo*o.hi,self.hi*o.lo,self.hi*o.hi); return Iv(min(a),max(a))
 __rmul__=__mul__
 def inv(self): assert not self.lo<=0<=self.hi; return Iv(min(1/self.lo,1/self.hi),max(1/self.lo,1/self.hi))
 def __truediv__(self,o): o=o if isinstance(o,Iv) else Iv.p(o); return self*o.inv()
 def inside(self,o): return self.lo<o.lo and o.hi<self.hi

def sq(a):
 if a.lo>=0:return Iv(a.lo*a.lo,a.hi*a.hi)
 if a.hi<=0:return Iv(a.hi*a.hi,a.lo*a.lo)
 return Iv(F(0),max(a.lo*a.lo,a.hi*a.hi))

@dataclass(frozen=True)
class CI:
 re:Iv; im:Iv
 @staticmethod
 def p(a,b=0): return CI(Iv.p(a),Iv.p(b))
 def __add__(self,o): o=o if isinstance(o,CI) else CI.p(o); return CI(self.re+o.re,self.im+o.im)
 __radd__=__add__
 def __neg__(self): return CI(-self.re,-self.im)
 def __sub__(self,o): return self+(-(o if isinstance(o,CI) else CI.p(o)))
 def __rsub__(self,o): return CI.p(o)-self
 def __mul__(self,o): o=o if isinstance(o,CI) else CI.p(o); return CI(self.re*o.re-self.im*o.im,self.re*o.im+self.im*o.re)
 __rmul__=__mul__
 def inv(self): d=sq(self.re)+sq(self.im); assert d.lo>0; return CI(self.re/d,(-self.im)/d)
 def __truediv__(self,o): o=o if isinstance(o,CI) else CI.p(o); return self*o.inv()
 def inside(self,o): return self.re.inside(o.re) and self.im.inside(o.im)

def parts(z):
 a,b=sp.re(sp.cancel(z)),sp.im(sp.cancel(z)); return F(int(sp.numer(a)),int(sp.denom(a))),F(int(sp.numer(b)),int(sp.denom(b)))
def ce(z): a,b=parts(z); return CI.p(a,b)
def pc(poly,Z):
 out=ce(poly.all_coeffs()[0])
 for c in poly.all_coeffs()[1:]: out=out*Z+ce(c)
 return out
def inv_exact(z): a,b=parts(z); d=a*a+b*b; return CI.p(a/d,-b/d)
def eval_ci(e,Z):
 n,d=sp.fraction(sp.cancel(e)); return pc(sp.Poly(n,x,domain=sp.QQ_I),Z)/pc(sp.Poly(d,x,domain=sp.QQ_I),Z)
def cross(a,b): return a.re*b.im-a.im*b.re
def orient(a,b,c): return cross(b-a,c-a)
def sgn(a): return 1 if a.lo>0 else (-1 if a.hi<0 else 0)

def root_box(q,c):
 u,v=c; Z=CI(Iv(u-RAD,u+RAD),Iv(v-RAD,v+RAD)); z=sp.Rational(u.numerator,u.denominator)+I*sp.Rational(v.numerator,v.denominator)
 C0=CI.p(u,v); inv=inv_exact(q.diff().as_expr().subs(x,z)); K=C0-inv*ce(q.as_expr().subs(x,z))+(CI.p(1)-inv*pc(q.diff(),Z))*(Z-C0)
 assert Z.inside(K); return Z

def boundary_convex():
 b=base.BOUNDARY; out=[]
 for i,p in enumerate(b):
  a=b[i-1]; c=b[(i+1)%6]; out.append(sp.cancel((p[0]-a[0])*(c[1]-p[1])-(p[1]-a[1])*(c[0]-p[0])))
 assert all(v>0 for v in out) or all(v<0 for v in out); return [str(v) for v in out]

def validate(q,px):
 boxes=[root_box(q,c) for c in CENTERS]
 for a,b in itertools.combinations(boxes,2): assert a.re.hi<b.re.lo or b.re.hi<a.re.lo or a.im.hi<b.im.lo or b.im.hi<a.im.lo
 reports=[]; Abox=[]
 for i,Z in enumerate(boxes,1):
  p={k:eval_ci(e,Z) for k,e in px.items()}
  for face in FACES.values():
   signs=[sgn(cross(p[face[(j+1)%len(face)]]-p[face[j]],p[face[(j+2)%len(face)]]-p[face[(j+1)%len(face)]])) for j in range(len(face))]
   assert 0 not in signs and len(set(signs))==1
  seg=[(a,b) for *_,a,b in EDGES]
  for j,(a,b) in enumerate(seg):
   for c,d in seg[j+1:]:
    if len({a,b,c,d})<4: continue
    s=(sgn(orient(p[a],p[b],p[c])),sgn(orient(p[a],p[b],p[d])),sgn(orient(p[c],p[d],p[a])),sgn(orient(p[c],p[d],p[b])))
    assert 0 not in s and not (s[0]*s[1]<0 and s[2]*s[3]<0)
  bb=[CI.p(F(u),F(v)) for u,v in base.BOUNDARY]
  for k in (A,D,C):
   s=[sgn(orient(bb[j],bb[(j+1)%6],p[k])) for j in range(6)]; assert 0 not in s and len(set(s))==1
  Abox.append(p[A]); reports.append({"pattern_index":i,"root_box_center":[str(CENTERS[i-1][0]),str(CENTERS[i-1][1])],"root_box_radius":str(RAD),"krawczyk_unique_root":True,"eight_faces_strictly_convex":True,"no_nonadjacent_edge_crossings":True,"all_internal_vertices_strictly_inside_prescribed_boundary":True,"boundary_angle_inequalities":"strict convex planar cellulation inside strictly convex prescribed boundary"})
 for a,b in itertools.combinations(Abox,2): assert a.re.hi<b.re.lo or b.re.hi<a.re.lo or a.im.hi<b.im.lo or b.im.hi<a.im.lo
 return reports

def build_evidence():
 q,p,tri=saturated(); px,exact=exact_positions(q,p,tri); reports=validate(q,px)
 return {"schema_version":"1.0.0","evidence_id":"MC-VGSE-WP00-CERT-001-PLANAR-001","route_id":"MC-ROUTE-VGSE-001","campaign_id":"VGSE-001","workset_id":"VGSE-WP00-CERT-001","claim_id":"VGSE-C05","dependencies":["MC-VGSE-WP00-CERT-001-EXACT-ALGEBRAIC-GRAPH-001"],"independence":{"solve_code_imported_or_executed":False,"solve_numerical_roots_consumed":False,"solve_numerical_embeddings_consumed":False,"interval_arithmetic":"exact Fraction endpoint arithmetic","root_existence_uniqueness":"complex Krawczyk inclusion on five disjoint rational rectangles"},"exact_replay":exact,"prescribed_boundary":{"coordinate_semantics":"rounded Figure 16 source-vector boundary interpreted as exact rationals at 1e-6 PDF-point resolution","strictly_convex":True,"corner_cross_products":boundary_convex()},"validated_branches":reports,"conclusion":{"certified_root_boxes":5,"five_discrete_holomorphic_extensions":True,"five_primitives_exactly_closed":True,"prescribed_boundary_exact":True,"five_planar_embeddings_strictly_convex_and_noncrossing":True,"kawasaki_equalities_exact":True,"boundary_angle_inequalities_certified":True,"five_embeddings_distinct":True},"trust":{"modality":"INTERVAL_CERTIFICATE_PLUS_EXACT_SYMBOLIC_REPLAY","trust_boundary":"script_replayed_exact_arithmetic","adjudication_effect":"none","may_adjudicate_after_this_record_alone":False,"certificate_output":None},"scope_exclusions":["VGSE-C06 is not discharged by this record","continuous rigid foldability","collision freedom","finite thickness","manufacturability","product performance","commercial value"]}

def main():
 import argparse
 ap=argparse.ArgumentParser(); ap.add_argument("--write",type=Path); ap.add_argument("--check",type=Path); a=ap.parse_args(); text=json.dumps(build_evidence(),indent=2,sort_keys=True)+"\n"
 if a.write: a.write.parent.mkdir(parents=True,exist_ok=True); a.write.write_text(text,encoding="utf-8")
 if a.check and a.check.read_text(encoding="utf-8")!=text: print("VGSE planar evidence record does not match replay"); return 1
 print("VGSE planar replay: five unique roots; exact extensions/closure/boundary/Kawasaki; interval-certified strict convex noncrossing embeddings"); return 0
if __name__=="__main__": raise SystemExit(main())
