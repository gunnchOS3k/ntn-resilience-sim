from pathlib import Path
import json,hashlib,sys,subprocess,statistics
import numpy as np
from scipy.stats import t
root=Path(__file__).resolve().parents[3];s=root/'paper/submission'
sys.path.insert(0,str(root/'src'))
from ntn_resilience.experiment import run_experiment
fresh=run_experiment('rq3_gary_failover_sweeps',out_dir=s/'verification'/'fresh_reproduction')
old=json.loads((s/'artifacts/rq3_gary_failover_sweeps.json').read_text())
for obj in (fresh,old):
 for k in ('wrote','statistical_artifacts'): obj.pop(k,None)
assert fresh==old,'Reproduced numerical payload mismatch'
def summary(a):
 a=np.asarray(a,dtype=float);m=a.mean();sd=a.std(ddof=1);half=t.ppf(.975,len(a)-1)*sd/len(a)**.5
 return {'n':len(a),'mean':float(m),'sample_sd':float(sd),'ci95':[float(m-half),float(m+half)]}
pol={p['policy']:p for p in fresh['policies']};baseline=pol['terrestrial_baseline']['runs'];checks={}
for k,p in pol.items():
 a=[x['min_service_fraction'] for x in p['runs']];d=[x['min_service_fraction']-y['min_service_fraction'] for x,y in zip(p['runs'],baseline)]
 checks[k]={'service':summary(a),'paired_vs_tn':summary(d)}
 checks[k]['paired_vs_tn']['dz']=None if statistics.stdev(d)==0 else statistics.mean(d)/statistics.stdev(d)
 st=p['statistics'];c=checks[k]['service']['ci95']
 assert max(abs(c[0]-st['ci95_min_service']['low']),abs(c[1]-st['ci95_min_service']['high']))<1e-10
assert pol['static_ntn']['statistics']['seed_min_service']==pol['fallback']['statistics']['seed_min_service']==pol['adaptive']['statistics']['seed_min_service']
assert all(x['min_service_fraction']>y['min_service_fraction'] for x,y in zip(pol['adaptive']['runs'],baseline))
# Enumerate the raw sampler state space independently of simulator calls.
q,r,v=.85,.88,.85
expect={}
for gt in (0,1):
 for gn in (0,1):
  total=dict.fromkeys(pol,0.)
  for P in (0,1):
   for R in (0,1):
    for V in (0,1):
     prob=(q if P else 1-q)*(r if R else 1-r)*(v if V else 1-v)
     at,an=P*R,P*V
     m={'terrestrial_baseline':at*gt,'static_ntn':an*gn+(1-an)*at*gt,'fallback':at*gt+(1-at)*an*gn,'adaptive':int(bool(at*gt or an*gn))}
     for k,x in m.items(): total[k]+=prob*x
  formula={'terrestrial_baseline':q*r*gt,'static_ntn':q*(v*gn+(1-v)*r*gt),'fallback':q*(r*gt+(1-r)*v*gn),'adaptive':q*(r*gt+v*gn-r*v*gt*gn)}
  assert max(abs(total[k]-formula[k]) for k in total)<1e-12
  expect[f'g_t={gt},g_n={gn}']=total
record={'source_sha':'05aaa9aec16882f58bac6ce4ff47618d9812f69f','fresh_payload_equal':True,'excluded_machine_dependent_keys':['wrote','statistical_artifacts'],'independent_statistics':checks,'exact_8_state_expectation_check':expect,'n_seeds':30,'steps_per_seed':48,'seed_unit':'synthetic timeline','python':sys.version}
(s/'verification/statistics_audit.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'numerical_payload_equal':True,'paired_adaptive':checks['adaptive']['paired_vs_tn'],'source_sha':record['source_sha']},indent=2))
