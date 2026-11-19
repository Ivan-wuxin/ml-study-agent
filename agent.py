"""Offline study agent: character TF-IDF retrieval and multinomial Naive Bayes.
Run: python agent.py --query "过拟合怎么办" or python agent.py --serve
"""
import argparse, collections, json, math, re
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
ROOT = Path(__file__).resolve().parent
def tokens(s):
    s = re.sub(r'\s+', '', s.lower())
    return list(s) + [s[i:i+2] for i in range(len(s)-1)]
class Agent:
    def __init__(self, data_path=None):
        self.load_error = None
        try:
            self.docs=json.loads(Path(data_path or ROOT/'data.json').read_text(encoding='utf-8'))
            if not isinstance(self.docs,list) or not self.docs: raise ValueError('empty database')
            seen=set()
            for d in self.docs:
                if not isinstance(d,dict): raise ValueError('invalid document')
                for key in ('topic','title','answer','source'):
                    if not isinstance(d.get(key),str) or not d[key].strip(): raise ValueError('invalid field')
                if d['topic'] in seen or not d['source'].startswith('https://'): raise ValueError('invalid topic/source')
                seen.add(d['topic'])
                if not isinstance(d.get('train'),list) or not d['train'] or not all(isinstance(s,str) and s.strip() for s in d['train']): raise ValueError('invalid training examples')
        except (OSError, UnicodeError, ValueError, TypeError):
            self.docs=[]; self.load_error='知识库无法加载或格式不正确，请检查data.json后重启服务。'
            return
        self.counts={}; self.totals={}; self.priors={}; vocab=set()
        for d in self.docs:
            c=d['topic']; cnt=collections.Counter(tokens(' '.join(d['train'])))
            self.counts[c]=cnt; self.totals[c]=sum(cnt.values()); self.priors[c]=len(d['train']); vocab.update(cnt)
        self.vocab=vocab
        self.df=collections.Counter()
        for d in self.docs: self.df.update(set(tokens(d['title']+d['answer'])))
        self.vectors=[self.vector(d['title']+d['answer']) for d in self.docs]
    def vector(self,s):
        cnt=collections.Counter(tokens(s))
        v={t:(1+math.log(n))*(math.log((1+len(self.docs))/(1+self.df.get(t,0)))+1) for t,n in cnt.items()}
        norm=math.sqrt(sum(x*x for x in v.values())) or 1
        return {t:x/norm for t,x in v.items()}
    def classify(self,q):
        ts=[t for t in tokens(q) if t in self.vocab]
        scores={c:math.log(self.priors[c]/sum(self.priors.values()))+sum(math.log((cnt[t]+1)/(self.totals[c]+len(self.vocab))) for t in ts) for c,cnt in self.counts.items()}
        return max(scores,key=scores.get)
    def run(self,q,mode='full', threshold=0.12):
        if not isinstance(q,str) or not q.strip() or len(q)>500:
            return {'status':'invalid','answer':'请输入1—500字的学习问题','trace':['输入校验失败']}
        normalized=re.sub(r'\s+','',q.lower())
        risk_groups=[('医疗',('用药','剂量','诊断','治疗','吃什么药')),('金融',('银行卡密码','转账','买哪只股票','贷款审批')),('法律',('法律判决','起诉','合同效力')),('隐私与权限',('他人密码','破解密码','身份证号'))]
        for category,terms in risk_groups:
            if any(term in normalized for term in terms):
                return {'status':'review','reason':'high_impact','answer':'此问题涉及'+category+'，超出课程资料范围。请由相应专业人员或有权限的负责人核实；本系统不执行操作。','source':None,'trace':['校验输入','高影响关键词检查','转交人工复核']}
        if self.load_error:
            return {'status':'error','reason':'knowledge_unavailable','answer':self.load_error,'source':None,'trace':['校验输入','知识库加载失败','停止回答']}
        if mode not in ('full','retrieval_only','no_reject','improved'):
            return {'status':'invalid','answer':'不支持的运行模式','trace':['模式校验失败']}
        try:
            if mode=='improved':
                aliases={'overfitting':'过拟合','data leakage':'数据泄漏','precision':'精确率','recall':'召回率','naive bayes':'朴素贝叶斯','laplace':'拉普拉斯平滑','k-means':'K均值','kmeans':'K均值','cosine':'余弦相似度'}
                q=q.lower()
                for term,replacement in aliases.items(): q=q.replace(term,replacement)
            return self._retrieve(q,mode,threshold)
        except (OSError, ValueError, KeyError, TypeError, ArithmeticError):
            return {'status':'error','reason':'retrieval_failed','answer':'检索工具暂时不可用，请检查知识库或重启；当前不返回猜测答案。','source':None,'trace':['校验输入','检索工具失败','停止回答']}
    def _retrieve(self,q,mode,threshold=0.12):
        route=self.classify(q); v=self.vector(q)
        scores=[sum(w*self.vectors[i].get(t,0) for t,w in v.items()) for i in range(len(self.docs))]
        candidates=list(range(len(self.docs)))
        if mode in ('full','no_reject'): candidates=[i for i,d in enumerate(self.docs) if d['topic']==route]
        best=max(candidates,key=lambda i:scores[i]); d=self.docs[best]; score=scores[best]
        reject=mode!='no_reject' and score<threshold
        return {'status':'review' if reject else 'answered','topic':route,'document':d['topic'],'similarity':round(score,4),'answer':'资料不足，请补充课程上下文并请教师复核。' if reject else d['answer'],'source':None if reject else d['source'],'trace':['校验输入','朴素贝叶斯主题分类：'+route,'TF-IDF余弦检索','阈值检查：'+str(threshold),'请求人工复核' if reject else '返回资料摘要及来源']}
def main():
    p=argparse.ArgumentParser(); p.add_argument('--query'); p.add_argument('--serve',action='store_true'); p.add_argument('--mode',choices=['full','retrieval_only','no_reject','improved'],default='full'); p.add_argument('--threshold',type=float,default=None); p.add_argument('--port',type=int,default=8765); a=p.parse_args(); agent=Agent()
    threshold=a.threshold if a.threshold is not None else (0.08 if a.mode=='improved' else 0.12)
    if a.serve:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body=(ROOT/'demo.html').read_bytes(); self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(body)
            def do_POST(self):
                try:
                    size=int(self.headers.get('Content-Length','0'))
                    if size<0 or size>10000: raise ValueError('请求过大')
                    payload=json.loads(self.rfile.read(size))
                    if not isinstance(payload,dict): raise ValueError('请求须为JSON对象')
                    result=agent.run(payload.get('query'),a.mode,threshold)
                    body=json.dumps(result,ensure_ascii=False).encode();self.send_response(200)
                except Exception:
                    body=b'{"status":"invalid"}';self.send_response(400)
                self.send_header('Content-Type','application/json; charset=utf-8');self.end_headers();self.wfile.write(body)
        print('Open http://127.0.0.1:'+str(a.port));HTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
    else: print(json.dumps(agent.run(a.query if a.query is not None else '过拟合怎么办',a.mode,threshold),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
