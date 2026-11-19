"""HTTP assertions executed by upstream webapp-testing lifecycle helper."""
import json, urllib.request
from pathlib import Path
rows=[]
for q,expected in [('过拟合怎么办','answered'),('帮我订火车票','review'),('','invalid')]:
    req=urllib.request.Request('http://127.0.0.1:8766/query',data=json.dumps({'query':q}).encode(),headers={'Content-Type':'application/json'})
    actual=json.load(urllib.request.urlopen(req,timeout=5))
    rows.append({'query':q,'expected':expected,'actual':actual,'pass':actual['status']==expected})
assert all(x['pass'] for x in rows)
Path('skill_test_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('Three HTTP skill assertions passed')
