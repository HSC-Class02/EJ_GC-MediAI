import unittest, json
from pathlib import Path
from agent import number, div, extract, analyze, MAP

class FinancialTests(unittest.TestCase):
 def test_amount(self):
  self.assertEqual(number('(1,200)'),-1200)
  self.assertIsNone(number('-'))
  self.assertEqual(number('0'),0)
 def test_denominator(self):
  self.assertIsNone(div(2,0));self.assertIsNone(div(2,-1));self.assertIsNone(div(None,2))
 def test_income_ytd(self):
  rows=[dict(sj_div='IS',account_id='ifrs-full_Revenue',account_nm='매출액',thstrm_amount='30',thstrm_add_amount='90',currency='KRW')]
  v,e,p=extract(rows,'11014');self.assertEqual(v['revenue'],90)
  rows.append(dict(rows[0],thstrm_add_amount='100'))
  self.assertIsNone(extract(rows,'11014')[0]['revenue'])
 def test_nonkrw(self):
  self.assertIsNone(extract([dict(sj_div='BS',account_id='ifrs-full_Assets',thstrm_amount='100',currency='USD')],'11011')[0]['assets'])
 def test_no_invented_capex(self):
  r=self.row('11011',12,100,10);r['cumulative']['capex_ppe']=4
  v=analyze([r])[0]['values'];self.assertIsNone(v['capex']);self.assertIsNone(v['fcf'])
 def row(self,code,month,revenue,cfo):
  v={k:None for k in MAP};v.update(revenue=revenue,cfo=cfo,assets=200,equity=100,net_income=10)
  return dict(year=2025,month=month,code=code,basis='CFS',cumulative=v,prior={'assets':100,'equity':50})
 def test_quarter_difference(self):
  half=self.row('11012',6,60,12);q=self.row('11014',9,100,20)
  analyzed=analyze([half,q]);self.assertEqual(analyzed[1]['values']['revenue'],40);self.assertEqual(analyzed[1]['values']['cfo'],8)
  self.assertEqual(analyzed[1]['days'],92)
 def test_quarter_missing_previous(self):
  self.assertIsNone(analyze([self.row('11014',9,100,20)])[0]['values']['cfo'])
 def test_average_equity(self):
  v=analyze([self.row('11011',12,100,10)])[0]['values'];self.assertAlmostEqual(v['roe'],10/75)
 def test_workflow_structure(self):
  import yaml
  root=Path(__file__).resolve().parents[1]
  # BaseLoader keeps YAML 1.1 from coercing GitHub's `on` key to boolean.
  obj=yaml.load((root/'workflow_templates/dart-update.yml').read_text(),Loader=yaml.BaseLoader)
  self.assertEqual(obj['on']['schedule'][0]['cron'],'0 0 1 * *')
  self.assertEqual(obj['permissions']['pages'],'write')
  self.assertIn('workflow_dispatch',obj['on'])
  self.assertEqual(obj['jobs']['deploy']['needs'],'update')
  self.assertEqual(obj['jobs']['update']['steps'][-1]['with']['path'],'docs')
if __name__=='__main__': unittest.main()
