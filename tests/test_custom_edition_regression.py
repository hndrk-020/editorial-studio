"""Synthetic 19-page proof; no personal guide or real photograph is bundled."""
import hashlib
import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from PIL import Image,ImageDraw
import pymupdf
from finalized_edition import document_digest,inspect_edition,publish_edition


class CustomEditionRegression(unittest.TestCase):
    def test_nineteen_pages_twelve_images_and_changed_approval_block(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);assets=[];approvals={}
            pdf=pymupdf.open()
            for number in range(19):
                page=pdf.new_page()
                page.insert_text((40,40),f'SYNTHETIC TEST EDITION page {number+1}')
                if number<12:
                    image=Image.new('RGB',(320,200),(30+number*10,80,110))
                    ImageDraw.Draw(image).text((8,20),f'SYNTHETIC TEST IMAGE {number+1}',fill='white')
                    stream=BytesIO();image.save(stream,format='JPEG');data=stream.getvalue()
                    name=f'test-{number}.jpg';(root/name).write_bytes(data)
                    digest=hashlib.sha256(data).hexdigest();identifier=f'image-{number}'
                    approvals[identifier]=digest
                    assets.append(dict(id=identifier,file=name,approved=True,sha256=digest))
                    page.insert_image(pymupdf.Rect(40,80,360,280),stream=data)
            pdf.save(root/'reviewed.pdf');pdf.close()
            original=(root/'reviewed.pdf').read_bytes()
            doc={'human_image_approval':{'assets':approvals},'style':{'selected':'field-notes'}}
            spec=dict(pdf='reviewed.pdf',pdf_sha256=hashlib.sha256(original).hexdigest(),manifest_sha256=document_digest(doc),pages=19,photo_pages=list(range(1,13)),assets=assets)
            (root/'finalized-edition.json').write_text(json.dumps(spec))
            checked=inspect_edition(root,doc)
            result=publish_edition(checked,doc,root/'export.pdf')
            self.assertEqual(result['pages'],19)
            self.assertEqual(result['photo_pages_verified'],12)
            self.assertEqual((root/'export.pdf').read_bytes(),original)
            (root/'reviewed.pdf').write_bytes(original+b'changed')
            with self.assertRaisesRegex(ValueError,'fingerprint'):inspect_edition(root,doc)
            (root/'reviewed.pdf').write_bytes(original)
            approvals['image-0']='changed'
            with self.assertRaises(ValueError):inspect_edition(root,doc)

    def test_custom_registration_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);doc={}
            (root/'finalized-edition.json').write_text(json.dumps({'manifest_sha256':document_digest(doc),'pdf':'../outside.pdf'}))
            with self.assertRaisesRegex(ValueError,'inside the project'):inspect_edition(root,doc)
