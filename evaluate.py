import json, time, hashlib, platform
from agent import Agent, ROOT
a=Agent(); cases=[]
for d in a.docs:
    cases += [{'query':q,'expected':d['topic']} for q in d['test']]
cases += [{'query':q,'expected':None} for q in ['明天香港天气怎样','帮我订火车票','今天食堂有什么','我的银行卡密码是什么','宿舍水费在哪里交','推荐一部电影']]
results={}
for mode in ['retrieval_only','full','no_reject']:
    rows=[]; start=time.perf_counter()
    for c in cases:
        r=a.run(c['query'],mode); pred=r.get('document') if r['status']=='answered' else None
        rows.append(dict(c, prediction=pred,correct=pred==c['expected'],result=r))
    tp=sum(x['correct'] and x['expected'] is not None for x in rows)
    answered=sum(x['prediction'] is not None for x in rows)
    f=[]
    for d in a.docs:
        label=d['topic']; t=sum(x['prediction']==label and x['expected']==label for x in rows)
        fp=sum(x['prediction']==label and x['expected']!=label for x in rows);fn=sum(x['prediction']!=label and x['expected']==label for x in rows)
        f.append(2*t/(2*t+fp+fn) if 2*t+fp+fn else 0)
    results[mode]={'task_accuracy':sum(x['correct'] for x in rows)/len(rows),'macro_f1':sum(f)/len(f),'answer_precision':tp/answered if answered else 0,'coverage':answered/len(rows),'ood_rejection':sum(x['prediction'] is None for x in rows if x['expected'] is None)/6,'mean_ms':1000*(time.perf_counter()-start)/len(rows),'rows':rows}
checks={'blank':a.run('')['status']=='invalid','long':a.run('a'*501)['status']=='invalid','nonstring':a.run(None)['status']=='invalid','trace':len(a.run('过拟合怎么办')['trace'])==5}
assert all(checks.values())
out={'environment':platform.python_version(),'data_sha256':hashlib.sha256((ROOT/'data.json').read_bytes()).hexdigest(),'test_note':'人工编写的小型教学验证集；与训练样例不重复，但由同一作者构造，不代表真实使用分布。阈值0.12为预设启发式，未进行独立验证集调参。','checks':checks,'results':results}
(ROOT/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'demo_run.json').write_text(json.dumps(a.run('过拟合怎么办'),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:{m:v for m,v in r.items() if m!='rows'} for k,r in results.items()},indent=2))
