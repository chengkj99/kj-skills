import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('render',ROOT/'scripts/render.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class ReaderTests(unittest.TestCase):
    def setUp(self): self.d=json.loads((ROOT/'examples/sample.json').read_text())
    def test_complete_sample(self):
        self.assertEqual(r.validate(self.d),[])
        out=r.render(self.d)
        for p in self.d['paragraphs']:
            for mode in ('quick','deep','language'):
                self.assertIn(f'id="{mode}-{p["id"]}"',out)
            self.assertIn(r.e(p['original']),out)
        self.assertIn('role="tablist"',out)
        self.assertNotIn('<script src=',out)
        self.assertNotIn('<link ',out)
    def test_reject_missing_deep_and_broken_reference(self):
        self.d['paragraphs'][0]['deep']={}
        self.d['language']['sentences'][0]['paragraph_id']='p999'
        self.assertTrue(r.validate(self.d))
    def test_reject_changed_training_quote(self):
        self.d['language']['sentences'][0]['original']='Invented sentence.'
        self.assertTrue(any('verbatim' in e for e in r.validate(self.d)))
    def test_reject_lost_chunk(self):
        self.d['language']['sentences'][0]['chunks'][0]['text']='changed'
        self.assertTrue(any('reconstruct' in e for e in r.validate(self.d)))
    def test_reject_invalid_choice(self):
        q=next(q for q in self.d['language']['exercises'] if q['type']=='choice')
        q['answer']='Not an option'
        self.assertTrue(r.validate(self.d))
    def test_escape_article_and_script_payload(self):
        attack='</script><script>alert("x")</script> @@JS@@'
        self.d['paragraphs'][0]['original']+=attack
        self.d['title']=attack
        out=r.render(self.d)
        self.assertNotIn('<script>alert',out)
        self.assertIn('&lt;/script&gt;',out)
        self.assertIn('\\u003c/script\\u003e',out)
        self.assertIn('@@JS@@',out)
    def test_preserve_multiline_list_code(self):
        self.d['paragraphs'][-1]['original']='First\n- item\nif (x < 2) { return "yes"; }'
        out=r.render(self.d)
        self.assertIn('First\n- item\nif (x &lt; 2)',out)
    def test_cli_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'reader.html';dest.write_text('existing')
            result=subprocess.run(['python3',str(ROOT/'scripts/render.py'),str(ROOT/'examples/sample.json'),'--output',str(dest)],capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(dest.read_text(),'existing')
    def test_malformed_input_returns_errors(self):
        self.assertTrue(r.validate({'paragraphs':[None],'conclusions':[None],'language':{}}))

if __name__=='__main__': unittest.main()
