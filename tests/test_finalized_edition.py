import tempfile,json,hashlib,unittest
from pathlib import Path
import fitz
from finalized_edition import inspect_edition,document_digest,publish_edition
class FinalizedEditionTests(unittest.TestCase):
 def test_reviewed_copy_and_changed_content_block(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);doc={'human_image_approval':{'assets':{}}};(root/'image.bin').write_bytes(b'approved test fixture')
   digest=hashlib.sha256((root/'image.bin').read_bytes()).hexdigest();doc['human_image_approval']['assets']['test']=digest
   pdf=fitz.open();page=pdf.new_page();page.insert_text((40,40),'Synthetic test fixture');pdf.save(root/'reviewed.pdf');pdf.close()
   spec=dict(pdf='reviewed.pdf',pdf_sha256=hashlib.sha256((root/'reviewed.pdf').read_bytes()).hexdigest(),manifest_sha256=document_digest(doc),pages=1,photo_pages=[],assets=[dict(id='test',file='image.bin',approved=True,sha256=digest)])
   (root/'finalized-edition.json').write_text(json.dumps(spec))
   result=inspect_edition(root,doc);audit=publish_edition(result,doc,root/'out.pdf');self.assertEqual(audit['pages'],1);self.assertEqual((root/'out.pdf').read_bytes(),(root/'reviewed.pdf').read_bytes())
   with self.assertRaises(ValueError):inspect_edition(root,dict(doc,title='Changed'))
   (root/'image.bin').write_bytes(b'changed')
   with self.assertRaises(ValueError):inspect_edition(root,doc)
 def test_unregistered_project_uses_standard_renderer(self):
  with tempfile.TemporaryDirectory() as tmp:self.assertIsNone(inspect_edition(Path(tmp),{}))
