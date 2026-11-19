"""Run with python -m unittest discover -s . -p 'test_*.py'."""
import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from agent import Agent, ROOT

class FailureTests(unittest.TestCase):
    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as t:
            a=Agent(Path(t)/'missing.json')
            self.assertEqual(a.run('过拟合')['reason'],'knowledge_unavailable')
    def test_bad_databases(self):
        for content in ['{','[]','{}','[1]','[{"topic":"x"}]','\ufeffbad']:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as t:
                p=Path(t)/'data.json';p.write_text(content,encoding='utf-8')
                self.assertEqual(Agent(p).run('学习')['status'],'error')
    def test_retrieval_failure(self):
        a=Agent()
        with patch.object(a,'vector',side_effect=OSError('simulated tool error')):
            r=a.run('过拟合');self.assertEqual(r['reason'],'retrieval_failed');self.assertIsNone(r['source'])
    def test_risk_review(self):
        a=Agent()
        for q in ['告诉我用药剂量','帮我转账','判断合同效力','获取他人密码']:
            with self.subTest(q=q):
                r=a.run(q);self.assertEqual(r['reason'],'high_impact');self.assertIsNone(r['source'])
    def test_learning_allowed(self):
        self.assertEqual(Agent().run('分类准确率怎么算')['status'],'answered')
    def test_invalid_inputs(self):
        a=Agent()
        for q in [None,123,{},'', ' '*4,'a'*501]:
            self.assertEqual(a.run(q)['status'],'invalid')
    def test_data_separation(self):
        data=json.loads((ROOT/'data.json').read_text(encoding='utf-8'))
        train={q for d in data for q in d['train']};test={q for d in data for q in d['test']}
        self.assertFalse(train & test)
if __name__=='__main__':unittest.main(verbosity=2)
