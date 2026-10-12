import json
from pathlib import Path
from agent import LABELS, PERCENT, MULTIPLE, DAYS
ROOT=Path(__file__).resolve().parent

def build():
 path=ROOT/'data/dashboard.json'
 payload=json.loads(path.read_text(encoding='utf-8')) if path.exists() else dict(company='GC메디아이 (구 유비케어)',updated_at=None,records=[],reports=[],coverage=[],labels=LABELS,percent=PERCENT,multiple=MULTIPLE,days=DAYS,peers=json.loads((ROOT/'peers.json').read_text(encoding='utf-8')))
 html=(ROOT/'dashboard.html').read_text(encoding='utf-8').replace('/*PAYLOAD*/',json.dumps(payload,ensure_ascii=False,allow_nan=False).replace('<','\\u003c'))
 out=ROOT/'docs';out.mkdir(exist_ok=True);(out/'index.html').write_text(html,encoding='utf-8')
 if path.exists():
  import shutil
  shutil.copy2(ROOT/'data/metrics.csv',out/'metrics.csv')
 print('Built docs/index.html; actual records:',len(payload['records']))
if __name__=='__main__': build()
