import json,urllib.request,urllib.parse
from pathlib import Path
out=Path('/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/_publication_worktrees/ntn-resilience-sim/paper/submission/verification')
for key,doi in [('lin2021','10.1109/MCOMSTD.011.2100038'),('rinaldi2020','10.1109/ACCESS.2020.3022981'),('azari2022','10.1109/COMST.2022.3199901'),('sedin2020','10.1109/GLOBECOM42002.2020.9347998'),('figaro2026','10.1038/s44459-026-00029-y')]:
 url='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')
 try:
  data=json.load(urllib.request.urlopen(url)); (out/(key+'_crossref.json')).write_text(json.dumps(data,indent=2)+'\n'); m=data['message']; print(key,m['title'],m.get('volume'),m.get('issue'),m.get('page'),m.get('published'))
 except Exception as e: print(key,type(e).__name__,str(e))
