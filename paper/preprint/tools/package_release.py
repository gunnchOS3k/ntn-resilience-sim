from pathlib import Path
import shutil,json,hashlib,zipfile,subprocess,re
p=Path('paper/preprint/v0.1');e=p/'evidence';s=Path('paper/submission');dist=p/'dist';dist.mkdir(exist_ok=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
prov={'version':'0.1','experimental_source_sha':'05aaa9aec16882f58bac6ce4ff47618d9812f69f','journal_manuscript_source_sha':'f55c06aee3fbc0664dc8aac0c63f3ca5e030d2a7','candidate_source_sha':head,'seeds':list(range(1,31)),'steps_per_seed':48,'evidence_class':'SYNTHETIC_SIM','publication_authorization':False,'human_scientific_approval':False,'article_license_approval':False,'originality_verified':False}
for path in [p/'PROVENANCE.json',e/'PROVENANCE.json']:path.write_text(json.dumps(prov,indent=2)+'\n')
shutil.copy2(s/'verification/tests_full.txt',e/'verification/tests_full.txt')
# Explicit traceable references to retained records, not implicit current working directories.
(e/'CLAIM_TO_EVIDENCE.md').write_text('''# Claim-to-evidence links (archive relative)

| Claim | Retained evidence | Bound |
|---|---|---|
| TN.7375; NTN-aware.8292 | [raw JSON](artifacts/rq3_gary_failover_sweeps.json), policies[].runs/statistics; [table](tables/base.csv) | 30 synthetic timelines |
| Gain.09166; CI[.07575726,.10756274], dz2.15223274 | [independent stats](verification/statistics_audit.json), independent_statistics.adaptive.paired_vs_tn | Paired Monte Carlo uncertainty |
| Three NTN-aware policies equal | raw JSON, policies[].statistics.seed_min_service; preprint Eq14 | Both paths qualify; no switch cost |
| Harmful.1083 versus retained.7375 | raw JSON, delay_class_contrast/stress_probes; [negative table](tables/negative.csv) |550ms or.5Mbps; same qualification bit/stream |
| Shared-power expectation ceiling.85 | [eight-state audit](verification/statistics_audit.json), exact_8_state_expectation_check; [experiment source](source/src/ntn_resilience/experiment.py); preprint Eq17 | Population only; finite sample can exceed |
| Latency grid20/40/60; capacity1/5/20 | raw JSON, decision_grids; [plot source](scripts/generate_artifacts.py) | Flat within qualifying region |
| Full37 focused9 tests | [full log](verification/tests_full.txt), [focused log](verification/tests_rq3.txt) | Historical software checks with sibling fixtures; not standalone suite |
| Frozen source/protocol | [original snapshot manifest](source/MANIFEST.json), [protocol](artifacts/experiment_protocol.yaml), [execution YAML](source/configs/experiments/rq3_gary_failover_sweeps.yaml) | No retrospective registration claim |

No physical NTN, adaptive superiority, validated local/peer path, externally calibrated parameters or established originality is claimed. The source/stats verifier operates from clean extraction with generated outputs separate from retained records.
''')
# Verify original snapshot bytes against both retained manifest and exact Git source.
m=json.loads((e/'source/MANIFEST.json').read_text());assert m['source_sha']==prov['experimental_source_sha']
for rel,h in m['sha256'].items():
 raw=(e/'source'/rel).read_bytes();assert hashlib.sha256(raw).hexdigest()==h
 assert raw==subprocess.check_output(['git','show',prov['experimental_source_sha']+':'+rel])
qa={'pdf_sha256':hashlib.sha256((p/'preprint.pdf').read_bytes()).hexdigest(),'pages':9,'every_page_visually_inspected':True,'neutral_article_class':True,'no_ieee_template_assets':True,'no_unresolved_references':not re.search('undefined|^!',(p/'preprint.log').read_text(),re.M),'source_snapshot_files_verified_against_git':len(m['sha256']),'human_scientific_approval':False}
assert qa['no_unresolved_references']
(p/'verification/VISUAL_AND_SOURCE_CHECK.json').write_text(json.dumps(qa,indent=2)+'\n')
# Durable local packager; use fixed zip member timestamp and validate manifests after extraction.
def writezip(name,root,files):
 files=sorted(files);lines=[hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(root)) for f in files]
 manifest='\n'.join(lines)+'\n'
 with zipfile.ZipFile(dist/name,'w',zipfile.ZIP_DEFLATED) as z:
  for f in files:
   info=zipfile.ZipInfo(str(f.relative_to(root)),(2026,10,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,f.read_bytes())
  info=zipfile.ZipInfo('SHA256SUMS',(2026,10,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,manifest)
 return len(files)
sourcefiles=[f for f in p.rglob('*') if f.is_file() and f.relative_to(p).parts[0] not in ['evidence','dist','verification'] and f.suffix not in ['.aux','.log','.out','.blg','.pdf']]
# Include required vector figure PDFs, but keep manuscript PDF in its separate deliverable.
sourcefiles += list((p/'figures').glob('*.pdf'))
a=writezip('paper-iii-v0.1-source.zip',p,sourcefiles)
b=writezip('paper-iii-v0.1-evidence.zip',e,[f for f in e.rglob('*') if f.is_file() and '__pycache__' not in f.parts])
index={f.name:{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in dist.glob('*.zip')};index['preprint.pdf']={'sha256':qa['pdf_sha256'],'bytes':(p/'preprint.pdf').stat().st_size};index['source_payload_files']=a;index['evidence_payload_files']=b
(p/'ARTIFACT_HASHES.json').write_text(json.dumps(index,indent=2)+'\n')
print(json.dumps(index,indent=2))
