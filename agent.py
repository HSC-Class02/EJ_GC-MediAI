"""OpenDART collector. Never log URLs containing credentials."""
import csv, io, json, os, re, time, zipfile, hashlib, calendar
from pathlib import Path
from datetime import date, datetime, timezone
import xml.etree.ElementTree as ET
import requests

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
CODES = {'11011': ('annual',12), '11012': ('Half-year',6), '11013': ('quarterly',3), '11014': ('quarterly',9)}
# Exact aliases only: ambiguous/custom accounts require review instead of guessing.
MAP = {
 'assets': ('BS',['ifrs-full_Assets'],['자산총계']),
 'cash': ('BS',['ifrs-full_CashAndCashEquivalents'],['현금및현금성자산','현금 및 현금성자산']),
 'receivables': ('BS',[],['매출채권']), 'inventory': ('BS',['ifrs-full_Inventories'],['재고자산']),
 'ppe': ('BS',['ifrs-full_PropertyPlantAndEquipment'],['유형자산']),
 'liabilities': ('BS',['ifrs-full_Liabilities'],['부채총계']),
 'equity': ('BS',['ifrs-full_Equity'],['자본총계']),
 'parent_equity': ('BS',['ifrs-full_EquityAttributableToOwnersOfParent'],['지배기업 소유주지분','지배기업의 소유주에게 귀속되는 자본']),
 'current_assets': ('BS',['ifrs-full_CurrentAssets'],['유동자산']),
 'current_liabilities': ('BS',['ifrs-full_CurrentLiabilities'],['유동부채']),
 'payables': ('BS',[],['매입채무']),
 'debt': ('BS',[],['이자부차입금']),
 'revenue': ('IS',['ifrs-full_Revenue','ifrs-full_RevenueFromContractsWithCustomers'],['매출액','수익(매출액)','영업수익']),
 'cogs': ('IS',['ifrs-full_CostOfSales'],['매출원가']),
 'gross_profit': ('IS',['ifrs-full_GrossProfit'],['매출총이익']),
 'sga': ('IS',[],['판매비와관리비','판매비와 관리비']),
 'operating_profit': ('IS',['dart_OperatingIncomeLoss'],['영업이익','영업이익(손실)','영업손익']),
 'pretax_profit': ('IS',['ifrs-full_ProfitLossBeforeTax'],['법인세비용차감전순이익','법인세비용차감전순이익(손실)']),
 'net_income': ('IS',['ifrs-full_ProfitLoss'],['당기순이익','당기순이익(손실)','분기순이익','반기순이익']),
 'parent_income': ('IS',['ifrs-full_ProfitLossAttributableToOwnersOfParent'],['지배기업 소유주지분 순이익','지배기업의 소유주에게 귀속되는 당기순이익']),
 'interest_expense': ('IS',[],['이자비용']),
 'cfo': ('CF',['ifrs-full_CashFlowsFromUsedInOperatingActivities'],['영업활동현금흐름','영업활동으로 인한 현금흐름']),
 'cfi': ('CF',['ifrs-full_CashFlowsFromUsedInInvestingActivities'],['투자활동현금흐름','투자활동으로 인한 현금흐름']),
 'cff': ('CF',['ifrs-full_CashFlowsFromUsedInFinancingActivities'],['재무활동현금흐름','재무활동으로 인한 현금흐름']),
 'capex_ppe': ('CF',['ifrs-full_PurchaseOfPropertyPlantAndEquipment','ifrs-full_PurchasesOfPropertyPlantAndEquipment'],['유형자산의 취득','유형자산 취득']),
 'capex_intangible': ('CF',['ifrs-full_PurchaseOfIntangibleAssets','ifrs-full_PurchasesOfIntangibleAssets'],['무형자산의 취득','무형자산 취득']),
 'depreciation': ('CF',[],['감가상각비']), 'amortization': ('CF',[],['무형자산상각비']),
 'quick_assets': ('BS',[],['당좌자산'])
}
LABELS = {'assets':'총자산','cash':'현금및현금성자산','receivables':'매출채권','inventory':'재고자산','ppe':'유형자산','liabilities':'총부채','equity':'자본총계','parent_equity':'지배주주자본','debt':'이자부차입금','current_assets':'유동자산','current_liabilities':'유동부채','payables':'매입채무','revenue':'매출액','cogs':'매출원가','gross_profit':'매출총이익','sga':'판매비와관리비','operating_profit':'영업이익','pretax_profit':'세전이익','net_income':'당기순이익','parent_income':'지배주주순이익','interest_expense':'이자비용','cfo':'영업활동현금흐름','cfi':'투자활동현금흐름','cff':'재무활동현금흐름','capex_ppe':'유형자산 취득 현금','capex_intangible':'무형자산 취득 현금','depreciation':'감가상각비','amortization':'무형상각비','quick_assets':'당좌자산','capex':'CAPEX','fcf':'FCF','net_debt':'순차입금','ebitda':'EBITDA(영업이익+상각비)','gross_margin':'매출총이익률','operating_margin':'영업이익률','net_margin':'순이익률','ebitda_margin':'EBITDA 마진','roa':'ROA(기간수익률)','roe':'ROE(기간수익률)','parent_roe':'지배주주 ROE(기간수익률)','roic':'ROIC','current_ratio':'유동비율','quick_ratio':'당좌비율','debt_ratio':'부채비율','equity_ratio':'자기자본비율','debt_dependency':'차입금의존도','interest_coverage':'이자보상배율','net_debt_ebitda':'순차입금/연간 EBITDA','asset_turnover':'총자산회전율','dso':'DSO','dio':'DIO','dpo':'DPO','ccc':'CCC','revenue_growth':'매출증가율(YoY)','cfo_net_income':'CFO/순이익','per':'PER','pbr':'PBR','ev_ebitda':'EV/EBITDA','fcf_yield':'FCF 수익률','roic_wacc':'ROIC-WACC'}
PERCENT = ['gross_margin','operating_margin','net_margin','ebitda_margin','roa','roe','parent_roe','roic','current_ratio','quick_ratio','debt_ratio','equity_ratio','debt_dependency','revenue_growth','fcf_yield','roic_wacc']
MULTIPLE = ['interest_coverage','net_debt_ebitda','asset_turnover','cfo_net_income','per','pbr','ev_ebitda']
DAYS = ['dso','dio','dpo','ccc']

def dump(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def number(v):
 if v is None or str(v).strip() in ('','-','—'): return None
 s=str(v).replace(',','').strip(); s=re.sub(r'^\((.*)\)$',r'-\1',s)
 try: return int(s)
 except ValueError: return None

class Dart:
 def __init__(self,key): self.key=key; self.session=requests.Session()
 def call(self,endpoint,binary=False,**params):
  params['crtfc_key']=self.key
  for attempt in range(5):
   try:
    time.sleep(.15)
    r=self.session.get('https://opendart.fss.or.kr/api/'+endpoint,params=params,timeout=(15,90))
    if r.status_code==429 or r.status_code>=500: raise RuntimeError('temporary HTTP failure')
    if r.status_code!=200: raise ValueError('DART HTTP status '+str(r.status_code))
    if binary and r.content[:2]==b'PK':
     with zipfile.ZipFile(io.BytesIO(r.content)) as z: z.testzip()
     return r.content
    if binary:
     root=ET.fromstring(r.content); j={e.tag:e.text for e in root}
    else: j=r.json()
    status=j.get('status')
    if status=='000': return j
    if status in ('013','014'): return None
    if status in ('800','900'): raise RuntimeError('temporary DART status '+status)
    raise ValueError('DART status '+str(status)+'; check API key, permissions, IP or quota')
   except (requests.RequestException,RuntimeError) as e:
    if attempt==4: raise RuntimeError('DART request failed after retries; credentials/URL omitted') from None
    time.sleep(2**attempt)
  raise RuntimeError('unreachable')
 def corp(self):
  blob=self.call('corpCode.xml',binary=True)
  if not blob: raise ValueError('Corporation list unavailable')
  with zipfile.ZipFile(io.BytesIO(blob)) as z:
   root=ET.fromstring(z.read('CORPCODE.xml'))
  matches=[x for x in root.findall('list') if x.findtext('stock_code','').strip()=='032620']
  if len(matches)!=1: raise ValueError('Cannot uniquely resolve stock code 032620')
  return matches[0].findtext('corp_code'),matches[0].findtext('corp_name')

def extract(rows,code):
 values={}; evidence={}; prior={}
 for key,(section,ids,names) in MAP.items():
  allowed={section} if section!='IS' else {'IS','CIS'}
  pool=[x for x in rows if x.get('sj_div') in allowed and x.get('currency','KRW')=='KRW']
  hits=[x for x in pool if x.get('account_id') in ids] if ids else []
  if not hits: hits=[x for x in pool if x.get('account_nm','').strip() in names]
  if section=='IS' and any(x.get('sj_div')=='IS' for x in hits): hits=[x for x in hits if x.get('sj_div')=='IS']
  # No summation or fuzzy match; duplicates with different values are unresolved.
  field='thstrm_add_amount' if section=='IS' and code!='11011' else 'thstrm_amount'
  candidates={number(x.get(field)) for x in hits}
  candidates.discard(None)
  values[key]=next(iter(candidates)) if len(candidates)==1 else None
  evidence[key]=[{'account_id':x.get('account_id'),'account_nm':x.get('account_nm'),'sj_div':x.get('sj_div'),'field':field,'raw':x.get(field)} for x in hits]
  p={number(x.get('frmtrm_amount')) for x in hits}; p.discard(None)
  prior[key]=next(iter(p)) if section=='BS' and len(p)==1 else None
 return values,evidence,prior

def div(a,b): return a/b if a is not None and b is not None and b>0 else None

def sub(a,b): return a-b if a is not None and b is not None else None

def add(a,b): return a+b if a is not None and b is not None else None

def analyze(records):
 lookup={(r['year'],r['code'],r['basis']):r for r in records}
 for r in records:
  v=dict(r['cumulative']); m=r['month']; code=r['code']; basis=r['basis']; yr=r['year']
  # Quarterly reports are Q1/Q3; convert YTD IS and CF to a single quarter.
  start_month=1
  if code=='11014':
   previous=lookup.get((yr,'11012',basis)); start_month=7
   for k,(s,_,__) in MAP.items():
    if s in ('IS','CF'): v[k]=sub(v.get(k),previous['cumulative'].get(k) if previous else None)
  prev_code='11012' if code=='11014' else '11011'
  prev_year=yr if code=='11014' else yr-1
  opening=lookup.get((prev_year,prev_code,basis))
  def avg(k):
   a=opening['cumulative'].get(k) if opening else (r.get('prior',{}).get(k) if code!='11014' else None)
   b=v.get(k)
   return (a+b)/2 if a is not None and b is not None else None
  days=(date(yr,m,calendar.monthrange(yr,m)[1])-date(yr,start_month,1)).days+1
  v['capex']=add(abs(v['capex_ppe']) if v.get('capex_ppe') is not None else None,abs(v['capex_intangible']) if v.get('capex_intangible') is not None else None)
  v['fcf']=sub(v.get('cfo'),v['capex']); v['net_debt']=sub(v.get('debt'),v.get('cash'))
  v['ebitda']=add(v.get('operating_profit'),add(v.get('depreciation'),v.get('amortization')))
  for out,a in [('gross_margin','gross_profit'),('operating_margin','operating_profit'),('net_margin','net_income'),('ebitda_margin','ebitda')]: v[out]=div(v.get(a),v.get('revenue'))
  for out,a,b in [('current_ratio','current_assets','current_liabilities'),('quick_ratio','quick_assets','current_liabilities'),('debt_ratio','liabilities','equity'),('equity_ratio','equity','assets'),('debt_dependency','debt','assets'),('interest_coverage','operating_profit','interest_expense'),('cfo_net_income','cfo','net_income')]: v[out]=div(v.get(a),v.get(b))
  v['roa']=div(v.get('net_income'),avg('assets')); v['roe']=div(v.get('net_income'),avg('equity')); v['parent_roe']=div(v.get('parent_income'),avg('parent_equity'))
  v['asset_turnover']=div(v.get('revenue'),avg('assets'))
  v['dso']=div(avg('receivables'),v.get('revenue')); v['dio']=div(avg('inventory'),v.get('cogs'))
  for k in ('dso','dio'): v[k]=v[k]*days if v[k] is not None else None
  for k in ('dpo','ccc','roic','roic_wacc','per','pbr','ev_ebitda','fcf_yield'): v[k]=None
  v['net_debt_ebitda']=div(v['net_debt'],v['ebitda']) if code=='11011' else None
  prev=lookup.get((yr-1,code,basis)); old=prev['cumulative'].get('revenue') if prev else None
  if code=='11014' and prev:
   half=lookup.get((yr-1,'11012',basis)); old=sub(old,half['cumulative'].get('revenue') if half else None)
  growth=div(v.get('revenue'),old); v['revenue_growth']=growth-1 if growth is not None else None
  r['values']=v; r['days']=days
  r['missing']={k:'계정 미매핑/중복/비교기간 또는 양의 분모 미확보' for k in LABELS if v.get(k) is None}
  for k in ('roic','roic_wacc'): r['missing'][k]='NOPAT·투하자본·세율·WACC 검증 필요'
  for k in ('per','pbr','ev_ebitda','fcf_yield'): r['missing'][k]='동일 기준일 주가·시가총액·주식수 등 시장 데이터 미제공'
  for k in ('dpo','ccc'): r['missing'][k]='외상매입액 미제공; 매출원가로 대체하지 않음'
 return records

def collect():
 key=os.environ.get('DART_API_KEY','').strip()
 if len(key)!=40: raise ValueError('DART_API_KEY must be a 40-character GitHub Actions secret')
 api=Dart(key); corp,name=api.corp(); today=date.today(); reports=[]
 DATA.mkdir(exist_ok=True)
 # Full list rescan includes old restatements, never only latest-year disclosures.
 for year in range(2010,today.year+1):
  page=1
  while True:
   j=api.call('list.json',corp_code=corp,bgn_de=f'{year}0101',end_de=min(f'{year}1231',today.strftime('%Y%m%d')),pblntf_ty='A',last_reprt_at='N',page_count=100,page_no=page,sort='date',sort_mth='asc')
   if not j: break
   for r in j['list']:
    if not any(x in r['report_nm'] for x in ('사업보고서','반기보고서','분기보고서')): continue
    match=re.search(r'\((\d{4})\.(\d{2})\)',r['report_nm'])
    if not match or int(match[1])<2010: continue
    month=int(match[2]); code={12:'11011',6:'11012',3:'11013',9:'11014'}.get(month)
    if not code: continue
    r.update(year=int(match[1]),month=month,code=code)
    r['url']='https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+r['rcept_no']
    archive=DATA/'reports'/(r['rcept_no']+'.zip')
    if not archive.exists():
     blob=api.call('document.xml',binary=True,rcept_no=r['rcept_no'])
     if blob:
      if len(blob)>90*1024*1024: raise ValueError('Report exceeds safe GitHub file size; use external archive')
      archive.parent.mkdir(exist_ok=True); archive.write_bytes(blob)
    r['archive_available']=archive.exists(); reports.append(r)
   if page>=int(j['total_page']): break
   page+=1
 latest={}
 for r in sorted(reports,key=lambda x:x['rcept_no']): latest[(r['year'],r['code'])]=r
 records=[]; coverage=[]
 for (year,code),report in sorted(latest.items()):
  if year<2015:
   coverage.append(dict(year=year,code=code,status='원문 보관; 수치 수동 검증 필요',receipt=report['rcept_no']))
   continue
  for basis in ('CFS','OFS'):
   j=api.call('fnlttSinglAcntAll.json',corp_code=corp,bsns_year=year,reprt_code=code,fs_div=basis)
   if not j:
    coverage.append(dict(year=year,code=code,basis=basis,status='API 수치 없음')); continue
   raw=json.dumps(j,ensure_ascii=False,sort_keys=True).encode(); sha=hashlib.sha256(raw).hexdigest()
   dump(DATA/'raw'/f'{year}_{code}_{basis}_{sha[:16]}.json',j)
   v,e,p=extract(j['list'],code)
   receipts=sorted({x.get('rcept_no') for x in j['list'] if x.get('rcept_no')})
   records.append(dict(year=year,month=CODES[code][1],code=code,category=CODES[code][0],basis=basis,period=f'{year}-{CODES[code][1]:02d}',cumulative=v,prior=p,evidence=e,receipts=receipts,source=report['url'],source_mismatch=bool(receipts and report['rcept_no'] not in receipts)))
 # Verified overrides, including historical numbers. Blank remains unknown, not zero.
 manual=ROOT/'manual'/'verified_metrics.csv'
 with manual.open(encoding='utf-8-sig',newline='') as f:
  for row in csv.DictReader(f):
   year=int(row['year']); code=row['code']; basis=row['basis']; field=row['field']
   if field not in MAP or code not in CODES or basis not in ('CFS','OFS') or not row['source_url'] or not row['reviewer']: raise ValueError('Invalid verified manual row')
   found=next((r for r in records if (r['year'],r['code'],r['basis'])==(year,code,basis)),None)
   if found is None:
    found=dict(year=year,month=CODES[code][1],code=code,category=CODES[code][0],basis=basis,period=f'{year}-{CODES[code][1]:02d}',cumulative={k:None for k in MAP},prior={},evidence={},receipts=[],source=row['source_url'],source_mismatch=False); records.append(found)
   amount=number(row['amount_krw'])
   if amount is None: raise ValueError('Manual amount must be integer KRW')
   found['cumulative'][field]=amount; found['evidence'][field]=[dict(manual=True,source=row['source_url'],reviewer=row['reviewer'],note=row['note'])]
 records=analyze(sorted(records,key=lambda r:(r['period'],r['basis'])))
 payload=dict(company=name,stock_code='032620',corp_code=corp,updated_at=datetime.now(timezone.utc).isoformat(),records=records,reports=reports,coverage=coverage,labels=LABELS,percent=PERCENT,multiple=MULTIPLE,days=DAYS,peers=json.loads((ROOT/'peers.json').read_text(encoding='utf-8')))
 dump(DATA/'dashboard.json',payload)
 with (DATA/'metrics.csv').open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=['period','category','basis',*LABELS]); writer.writeheader()
  for r in records: writer.writerow({'period':r['period'],'category':r['category'],'basis':r['basis'],**{k:r['values'].get(k) for k in LABELS}})
 dump(DATA/'manifest.json',dict(updated_at=payload['updated_at'],reports=len(reports),records=len(records),historical_pending=[x for x in coverage if x['year']<2015]))
 print(f'Collected {len(reports)} disclosures and {len(records)} financial statements')

if __name__=='__main__':
 try: collect()
 except Exception as e:
  print('Collection stopped:',str(e) if isinstance(e,(ValueError,RuntimeError)) else type(e).__name__)
  raise SystemExit(1)
