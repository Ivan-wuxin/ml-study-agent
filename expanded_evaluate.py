"""Validation-selected threshold, fixed extended tests, all rows retained."""
import json, hashlib
from agent import Agent, ROOT

dev=[('overfitting怎么缓解','overfit'),('data leakage是什么意思','split'),('precision与recall','metrics'),('naive bayes分类','bayes'),('cosine检索','retrieve'),('k-means簇数','cluster'),('推荐旅游路线',None),('帮我买午饭',None),('计算一下我明天运气',None),('用药剂量怎么选',None),('你好',None),('想听音乐',None)]
test=[('overfitting在验证集有什么现象','overfit'),('只会记住训练答案怎么办','overfit'),('模型在训练数据好换数据就差','overfit'),('为什么需要正则化约束','overfit'),('data leakage会让分数虚高吗','split'),('先全量标准化再拆分行吗','split'),('测试数据也参与特征选择可以吗','split'),('按时间先后如何留出测试','split'),('precision分母是什么','metrics'),('recall低表示什么','metrics'),('全猜多数类别准确率很高合理吗','metrics'),('混淆矩阵怎样反映漏判','metrics'),('naive bayes为何假设独立','bayes'),('laplace避免什么零概率问题','bayes'),('没见过的词怎样平滑','bayes'),('词频分类的类别先验是什么','bayes'),('cosine比较两段文本','retrieve'),('高频常见字如何降低权重','retrieve'),('检索遇到同义词为什么失败','retrieve'),('归一化后点积是什么','retrieve'),('kmeans为什么需要选K','cluster'),('k-means更新质心的步骤','cluster'),('球形簇适合什么方法','cluster'),('轮廓系数越大表示什么','cluster'),('帮我预订机票',None),('生成今天的天气预报',None),('解释量子纠缠的实验细节',None),('写一首春天的诗',None),('帮我转账100元',None),('告诉我他人密码',None)]
boundaries=[('', 'invalid'),(' '*5,'invalid'),('字'*501,'invalid'),(None,'invalid'),(123,'invalid'),('治疗要用什么药','review'),('贷款审批直接通过吗','review'),('合同效力如何判定','review'),('过拟合和聚类都讲讲','review'),('这个怎么弄','review'),('🙂🙂🙂','review'),('a'*500,'review')]
a=Agent()
def evaluate(cases,mode,threshold):
 rows=[]
 for q,label in cases:
  r=a.run(q,mode,threshold); pred=r.get('document') if r['status']=='answered' else None
  rows.append({'query':q,'expected':label,'prediction':pred,'correct':pred==label,'result':r})
 answered=sum(x['prediction'] is not None for x in rows); correct_answer=sum(x['correct'] and x['expected'] is not None for x in rows)
 f=[]
 for d in a.docs:
  c=d['topic'];tp=sum(x['prediction']==c and x['expected']==c for x in rows);fp=sum(x['prediction']==c and x['expected']!=c for x in rows);fn=sum(x['prediction']!=c and x['expected']==c for x in rows)
  f.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
 return {'accuracy':sum(x['correct'] for x in rows)/len(rows),'macro_f1':sum(f)/len(f),'answer_precision':correct_answer/answered if answered else 0,'coverage':answered/len(rows),'rows':rows}
validation={str(t):evaluate(dev,'improved',t) for t in [.08,.12,.18,.24]}
threshold=max([.08,.12,.18,.24],key=lambda t:(validation[str(t)]['accuracy'],t))
results={m:evaluate(test,m,threshold if m=='improved' else .12) for m in ['full','retrieval_only','improved']}
boundary_rows=[]
for q,expected in boundaries:
 r=a.run(q,'improved',threshold);boundary_rows.append({'query':q,'expected_status':expected,'actual_status':r['status'],'pass':r['status']==expected,'result':r})
out={'provenance':'AI辅助人工构造；非真实用户日志。验证和测试在脚本中固定，术语映射先于本轮测试结果编写；并非独立外部评估。混合主题要求复核，用于揭示单主题设计限制。','validation_n':len(dev),'test_n':len(test),'boundary_n':len(boundaries),'selected_threshold':threshold,'validation':validation,'results':results,'boundaries':boundary_rows}
(ROOT/'expanded_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('threshold',threshold)
for m,r in results.items(): print(m,{k:v for k,v in r.items() if k!='rows'})
print('boundaries',sum(x['pass'] for x in boundary_rows),'/',len(boundary_rows))
if __name__=='__main__': pass
