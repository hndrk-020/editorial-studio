"""Engine regression suite. Synthetic assets never represent actual photography."""
from __future__ import annotations
import tempfile
import unittest
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw
import fitz
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import engine

BRIEF={'subject':'Architecture field guide','purpose':'Test a photo-led story',
       'audience':'Design readers','preferred_style':'Warm editorial',
       'category':'architecture','distribution':'private'}

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.base=Path(self.temp.name)
        self.old_projects=engine.PROJECTS
        self.old_outputs=engine.OUTPUTS
        engine.PROJECTS=self.base/'projects'
        engine.OUTPUTS=self.base/'output'
        self.doc=engine.create_project('Test architecture issue','magazine',
              'Ten scenes about built environments and the people who shape them.',
              'Issue 01',BRIEF)
        engine.select_style(self.doc['slug'],'field-notes')
        for i in range(10):
            e=engine.add_story(self.doc['slug'],f'Building {i+1:02d}')
            engine.update_story(self.doc['slug'],e['id'],{
                  'description':f'A short and grounded story about building {i+1}.',
                  'website':'https://example.org/source','maps':'https://example.org/map'})
        self.doc=engine.load(self.doc['slug'])
        self.photos_folder=engine.path_for(self.doc['slug'])/'assets'
        self.photos_folder.mkdir(parents=True,exist_ok=True)
    def tearDown(self):
        engine.PROJECTS=self.old_projects
        engine.OUTPUTS=self.old_outputs
        self.temp.cleanup()

    def add_synthetic_images(self, doc):
        """Synthetic TEST ONLY fixtures; never ship as original subject photographs."""
        for i,(slot,label,photo) in enumerate(engine.photo_slots(doc)):
            color=(90+i*12 % 135,110+i*8%115,95+i*17%105)
            im=Image.new('RGB',(1900,1280),color)
            dr=ImageDraw.Draw(im)
            dr.text((70,70),f'TEST FIXTURE ONLY - NOT AN ACTUAL PHOTO: {slot}',fill=(255,255,255))
            path=self.photos_folder/('hero.jpg' if slot=='hero' else slot+'.jpg')
            im.save(path,quality=92)
            photo.update({'file':path.name,'sha256':sha256(path.read_bytes()).hexdigest(),
                          'source':'synthetic test fixture','credit':'Unittest synthetic',
                          'rights':'own','approved':True,'width':1900,'height':1280})
        engine.store(doc['slug'],doc)

    def test_preflight_blocks_missing_images(self):
        pf=engine.preflight(self.doc)
        self.assertFalse(pf['pass'])
        self.assertEqual(pf['total_photos'],11)
        self.assertEqual(pf['ready_photos'],0)
        with self.assertRaises(engine.PublicationError):engine.export(self.doc['slug'])

    def test_verified_pdf_with_embedded_images_and_paginated_credits(self):
        self.add_synthetic_images(self.doc)
        pf=engine.preflight(self.doc)
        self.assertTrue(pf['pass'],pf)
        out=engine.export(self.doc['slug'])
        self.assertTrue(out['pass'],out)
        self.assertEqual(out['pages'],16)
        self.assertEqual(out['photo_pages_verified'],11)
        self.assertGreaterEqual(out['links'],20)
        pdf=Path(out['file'])
        self.assertGreater(pdf.stat().st_size,80000)
        with fitz.open(pdf) as document:
            self.assertEqual(len(document),16)
            self.assertTrue(document[0].get_images(full=True))
            self.assertTrue(document[3].get_images(full=True))
            self.assertIn('Source:',document[-1].get_text())
        self.assertTrue(Path(out['snapshot']).exists())

    def test_onepager_template(self):
        self.doc['kind']='onepager'
        self.doc['stories']=self.doc['stories'][:3]
        self.add_synthetic_images(self.doc)
        out=engine.export(self.doc['slug'])
        self.assertEqual(out['pages'],1)
        with fitz.open(out['file']) as pdf:
            self.assertGreaterEqual(len(pdf[0].get_images(full=True)),4)

    def test_upload_resets_approval_and_creates_hash(self):
        im=Image.new('RGB',(1200,900),(50,100,180))
        buf=BytesIO();im.save(buf,format='PNG')
        slot=self.doc['stories'][0]['id']
        obj=engine.import_image(self.doc['slug'],slot,buf.getvalue(),
                                'https://example.org/source','Photographer','permission')
        self.assertFalse(obj['approved'])
        self.assertEqual(obj['file'],slot+'.jpg')
        self.assertEqual(len(obj['sha256']),64)
        obj=engine.set_image_metadata(self.doc['slug'],slot,{'approved':True})
        self.assertTrue(obj['approved'])
        self.assertFalse(engine.preflight(engine.load(self.doc['slug']))['pass'])

    def test_reject_path_traversal(self):
        with self.assertRaises(engine.PublicationError):engine.load('../outside')
        with self.assertRaises(engine.PublicationError):engine.load('a/b')

    def test_approved_image_fingerprint_detects_replaced_bytes(self):
        self.add_synthetic_images(self.doc)
        path=self.photos_folder/'hero.jpg'
        Image.new('RGB',(1900,1280),(30,30,200)).save(path)
        errors=engine.preflight(engine.load(self.doc['slug']))['errors']
        self.assertTrue(any('changed after import' in e for e in errors),errors)

    def test_overflowing_text_blocks_publication(self):
        self.add_synthetic_images(self.doc)
        engine.update_story(self.doc['slug'],self.doc['stories'][0]['id'],
                             {'description':'Very long text. '*500})
        self.assertFalse(engine.preflight(engine.load(self.doc['slug']))['pass'])

    def test_generic_editorial_default_has_no_restaurant_suggestion(self):
        self.assertEqual(self.doc['stories'][0]['best_for'],'')
        self.assertEqual(self.doc['stories'][0]['order'],'')

    def test_public_edition_footer_is_not_marked_private(self):
        self.add_synthetic_images(self.doc)
        self.doc['brief']['distribution']='public'
        engine.store(self.doc['slug'],self.doc)
        out=engine.export(self.doc['slug'])
        with fitz.open(out['file']) as pdf:
            self.assertIn('PUBLICEDITION',pdf[0].get_text().replace(' ',''))

    def test_title_tags_are_not_printed_as_source(self):
        self.assertEqual(engine.clean_headline('Magazine<br>Issue'),'Magazine Issue')

if __name__=='__main__':unittest.main()
