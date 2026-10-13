from pathlib import Path
import json,csv,hashlib,subprocess,sys,math,platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import t
base=Path('/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/_publication_worktrees/ntn-resilience-sim')
s=base/'paper/submission'; r=json.loads((s/'artifacts/rq3_gary_failover_sweeps.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
labels={'terrestrial_baseline':'TN only','static_ntn':'NTN first','fallback':'TN first','adaptive':'Adaptive'}
def save(fig,name):
 fig.savefig(s/'figures'/f'{name}.pdf',bbox_inches='tight'); fig.savefig(s/'figures'/f'{name}.png',dpi=300,bbox_inches='tight'); plt.close(fig)
def table(name,caption,header,rows,spec):
 text='\\begin{table}[t]\n\\centering\n\\caption{'+caption+'}\n\\label{tab:'+name+'}\n\\footnotesize\n\\begin{tabular}{'+spec+'}\\toprule\n'+header+r' \\ \midrule'+'\n'+'\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n\\bottomrule\\end{tabular}\n\\end{table}\n'
 (s/'tables'/f'{name}.tex').write_text(text)
 with (s/'tables'/f'{name}.csv').open('w') as f: csv.writer(f).writerows([header.split(' & ')]+rows)
rows=[]
for p in r['policies']:
 st=p['statistics']; ci=st['ci95_min_service']; rows.append([labels[p['policy']],f"{st['mean_min_service']:.4f}",f"[{ci['low']:.4f}, {ci['high']:.4f}]",f"{st['mean_ntn_path_fraction']:.4f}"])
table('base','Compound base case; 30 seed means, 48 steps each. Intervals describe simulation variability.','Policy & Service & 95\\% interval & NTN fraction',rows,'lccc')
rows=[]
for p in r['policies']:
 k=p['policy']; d=next(x for x in r['delay_class_contrast'] if x['policy']==k); c=next(x for x in r['stress_probes'] if x['policy']==k); rows.append([labels[k],f"{d['leo_tr38821']['mean_min_service']:.4f}",f"{d['geo_configured']['mean_min_service']:.4f}",f"{c['mean_min_service']:.4f}"])
table('negative','Minimum-useful-service counterexamples. GEO means configured 550 ms; thin NTN means 0.5 Mbps.','Policy & LEO base & GEO & Thin NTN',rows,'lccc')
rows=[]
for p in r['compound_contrast']:
 rows.append([labels[p['policy']],f"{p['simple']['mean_min_service']:.4f}",f"{p['compound']['mean_min_service']:.4f}",f"{p['delta_min_service_compound_minus_simple']:.4f}"])
table('compound','Power contrast on shared random streams. Simple removes the power constraint; compound disables both paths when power is lost.','Policy & Simple & Compound & Difference',rows,'lccc')
rows=[]
for p in r['policies']:
 st=p['statistics'];rows.append([labels[p['policy']],f"{st['mean_on_path_latency_ms']:.2f}",f"{st['mean_offline_steps']:.2f}",f"{st['mean_recovery_steps_to_min_service']:.2f}"])
table('secondary','Descriptive secondary metrics. Delay averages only selected online paths; recovery is first-miss-to-first-restoration in abstract steps.','Policy & Delay (ms) & Offline steps & Recovery',rows,'lccc')
fig,ax=plt.subplots(figsize=(3.45,2.3))
vals=[p['statistics']['mean_min_service'] for p in r['policies']]; errors=[p['statistics']['ci95_min_service']['high']-p['statistics']['mean_min_service'] for p in r['policies']]
ax.bar(range(4),vals,yerr=errors,color=['#666666','#4e79a7','#59a14f','#f28e2b'],capsize=3);ax.set_xticks(range(4),[labels[p['policy']] for p in r['policies']],rotation=15);ax.set_ylabel('Minimum-useful-service fraction');ax.set_ylim(0,1);ax.axhline(.85,color='#444444',ls='--',lw=.7);ax.text(3.45,.862,'power ceiling',ha='right',fontsize=7);save(fig,'base_service')
fig,axs=plt.subplots(1,2,figsize=(7.0,2.55),sharey=True)
vis=[.5,.85,.99]
for ax,dim,values in [(axs[0],'ntn_latency_ms',[20,40,60]),(axs[1],'ntn_capacity_mbps',[1,5,20])]:
 grid=r['decision_grids']['latency_x_visibility' if dim=='ntn_latency_ms' else 'capacity_x_visibility']; arr=np.array([[next(x['mean_min_service'] for x in grid if x['policy']=='adaptive' and x[dim]==d and x['ntn_visibility']==v)-vals[0] for v in vis] for d in values]); im=ax.imshow(arr,vmin=0,vmax=.12,cmap='Blues',origin='lower',aspect='auto');ax.set_xticks(range(3),vis);ax.set_yticks(range(3),values);ax.set_xlabel('NTN visibility probability');ax.set_ylabel('Latency (ms)' if dim=='ntn_latency_ms' else 'Capacity (Mbps)')
 for i in range(3):
  for j in range(3):ax.text(j,i,f'{arr[i,j]:.4f}',ha='center',va='center',color='white' if arr[i,j]>.08 else '#111111',fontsize=8)
axs[1].tick_params(labelleft=True);fig.colorbar(im,ax=axs,shrink=.85,label='Adaptive minus TN service');save(fig,'decision_grids')
fig,ax=plt.subplots(figsize=(3.45,2.45));x=np.arange(4);w=.24
for i,(name,key,col) in enumerate([('LEO base','leo_tr38821','#4e79a7'),('Configured GEO','geo_configured','#e15759'),('Thin NTN','stress','#b07aa1')]):
 ys=[next(z for z in (r['stress_probes'] if key=='stress' else r['delay_class_contrast']) if z['policy']==p['policy']) for p in r['policies']];ys=[z['mean_min_service'] if key=='stress' else z[key]['mean_min_service'] for z in ys];ax.bar(x+(i-1)*w,ys,w,label=name,color=col)
ax.set_xticks(x,[labels[p['policy']] for p in r['policies']],rotation=15);ax.set_ylim(0,1);ax.set_ylabel('Minimum-useful-service fraction');ax.legend(fontsize=7,loc='upper left');save(fig,'negative_cases')
fig,ax=plt.subplots(figsize=(3.45,2.45));tn=r['policies'][0]['runs'];ad=r['policies'][3]['runs'];ds=[a['min_service_fraction']-b['min_service_fraction'] for a,b in zip(ad,tn)];ax.plot(r['seeds'],ds,'o',ms=3,color='#4e79a7');ax.axhline(np.mean(ds),color='#222222',lw=.8,label='Mean paired gain');ax.axhline(0,color='#777777',ls='--',lw=.6);ax.set_xlabel('Shared seed');ax.set_ylabel('Adaptive minus TN service');ax.set_ylim(-.01,.23);ax.legend(fontsize=7);save(fig,'paired_seed_gain')
fig,ax=plt.subplots(figsize=(7.0,2.4));ax.axis('off');blocks=[(.02,'Shared power\nP = 0 → both paths unavailable'),(.36,'Service qualification\nC ≥ 1 Mbps and L ≤ 500 ms'),(.70,'30 shared seeds\nLEO gain; GEO/thin NTN counterexamples')]
for x,txt in blocks:ax.text(x,.7,txt,transform=ax.transAxes,va='center',fontsize=10,bbox={'boxstyle':'round,pad=.6','fc':'#eaf1f7','ec':'#4e79a7'})
ax.text(.5,.15,'Synthetic threshold benchmark • no field NTN or local/peer validation',ha='center',transform=ax.transAxes,fontsize=10);save(fig,'graphical_abstract')
# Independent statistics + exact input/output hashes; no source changes.
checks=[]
for p in r['policies']:
 a=np.array([x['min_service_fraction'] for x in p['runs']]);m=a.mean();sd=a.std(ddof=1);half=t.ppf(.975,len(a)-1)*sd/np.sqrt(len(a));st=p['statistics'];checks.append({'policy':p['policy'],'mean_from_seed_records':float(m),'sd':float(sd),'ci_low':float(m-half),'ci_high':float(m+half),'max_ci_error':float(max(abs(st['ci95_min_service']['low']-(m-half)),abs(st['ci95_min_service']['high']-(m+half))))})
paths=['src/ntn_resilience/experiment.py','src/ntn_resilience/fallback_policy.py','src/ntn_resilience/stats.py','configs/experiments/rq3_gary_failover_sweeps.yaml','paper/artifacts/experiment_protocol.yaml','config/assumption_registry.yaml']
record={'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=base,text=True).strip(),'source_hashes':{p:hashlib.sha256((base/p).read_bytes()).hexdigest() for p in paths},'output_hash':hashlib.sha256((s/'artifacts/rq3_gary_failover_sweeps.json').read_bytes()).hexdigest(),'python':sys.version,'platform':platform.platform(),'scipy_check':checks,'evidence_class':'SYNTHETIC_SIM','n_seeds':30,'steps_per_seed':48,'claim_firewall':r['claim_firewall'],'analytic_expectations':{'tn_compound':.85*.88,'ntn_feasible_compound':.85*(.88+.12*.85),'static_unqualified_compound':.85*.88*.15,'shared_power_ceiling':.85}}
(s/'verification/reproduction_audit.json').write_text(json.dumps(record,indent=2)+'\n')
(s/'artifacts/environment.lock.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
print('Generated 6 figures, 4 tables and independent CI audit; maximum CI discrepancy',max(x['max_ci_error'] for x in checks))
