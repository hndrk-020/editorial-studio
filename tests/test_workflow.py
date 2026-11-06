"""Creative intake, style selection, image researcher and rights-gate regression tests."""
from __future__ import annotations

from io import BytesIO
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import engine
from creative import propose_directions,candidate_queries,normalize_brief
from photo_researcher import safe_photo_url,import_public_image

BRIEF={
 'subject':'Modern bridges in Europe',
 'purpose':'Present a beautiful design story',
 'audience':'Design-conscious readers',
 'preferred_style':'Understated photographic editorial with unusual typography',
 'reference_url':'https://example.com/inspiration',
 'category':'architecture',
 'distribution':'private',
}

def image_bytes(color=(50,90,150)):
    image=Image.new('RGB',(1500,1000),color)
    b=BytesIO();image.save(b,format='PNG');return b.getvalue()

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.p=Path(self.temp.name)
        self.prev_projects,self.prev_outputs=engine.PROJECTS,engine.OUTPUTS
        engine.PROJECTS=self.p/'projects';engine.OUTPUTS=self.p/'outputs'
    def tearDown(self):
        engine.PROJECTS,self.temp_projects= self.prev_projects,None
        engine.OUTPUTS=self.prev_outputs
        self.temp.cleanup()
    def new(self,brief=BRIEF,kind='onepager'):
        return engine.create_project('Future infrastructure',kind,'A design issue about the built world','Issue 01',brief)
    def test_upload_rejects_other_decoder_formats(self):
        doc=self.new();engine.select_style(doc['slug'],'field-notes')
        payload=BytesIO();Image.new('RGB',(10,10),'white').save(payload,format='BMP')
        with self.assertRaises(engine.PublicationError):
            engine.import_image(doc['slug'],'hero',payload.getvalue(),'synthetic test','test','own')

    def test_same_title_projects_export_to_distinct_paths(self):
        from unittest.mock import patch
        first=self.new();second=self.new()
        with patch.object(engine,'render_pdf',side_effect=lambda doc,path:path) as render:
            one=engine.export(first['slug']);two=engine.export(second['slug'])
        self.assertNotEqual(one,two)
        self.assertIn(second['slug'],two.name)

    def test_changed_provenance_revokes_approval(self):
        doc=self.new();engine.select_style(doc['slug'],'field-notes')
        engine.import_image(doc['slug'],'hero',image_bytes(),'synthetic test','test','own')
        engine.set_image_metadata(doc['slug'],'hero',{'approved':True})
        engine.set_image_metadata(doc['slug'],'hero',{'credit':'Updated test credit'})
        self.assertFalse(engine.load(doc['slug'])['hero']['approved'])

    def test_brief_then_two_distinct_directions(self):
        doc=self.new()
        ideas=propose_directions(doc['brief'])
        self.assertEqual(len(ideas),2)
        self.assertNotEqual(ideas[0]['palette'],ideas[1]['palette'])
        self.assertNotEqual(ideas[0]['typography'],ideas[1]['typography'])
        self.assertIn('Modern bridges',ideas[0]['rationale'])
        self.assertFalse(doc['style']['selected'])
        with self.assertRaises(engine.PublicationError):engine.add_story(doc['slug'],'Three bridges')
        self.assertTrue(any('Select' in x for x in engine.preflight(doc)['errors']))
        engine.select_style(doc['slug'],'bold-perspective')
        item=engine.add_story(doc['slug'],'Three bridges')
        self.assertEqual(item['title'],'Three bridges')
    def test_change_brief_requires_new_style_choice(self):
        doc=self.new();engine.select_style(doc['slug'],'field-notes')
        doc=engine.update_brief(doc['slug'],{'preferred_style':'Brutalist and expressive'})
        self.assertIsNone(doc['style']['selected'])
        with self.assertRaises(engine.PublicationError):engine.add_story(doc['slug'],'Bridge')
    def test_research_is_general_not_restaurant_specific(self):
        doc=self.new();engine.select_style(doc['slug'],'field-notes')
        story=engine.add_story(doc['slug'],'Pont de Normandie')
        fresh=engine.load(doc['slug'])
        sources=candidate_queries(fresh,story['id'])
        self.assertEqual(sources['category'],'architecture')
        self.assertIn('Pont de Normandie',sources['query'])
        self.assertEqual(len(sources['sources']),4)
        for s in sources['sources']:
            self.assertTrue(s['url'].startswith('https://'))
    def test_import_from_https_is_unapproved_and_traceable(self):
        doc=self.new();engine.select_style(doc['slug'],'field-notes')
        engine.add_story(doc['slug'],'Bridge')
        photo=import_public_image(doc['slug'],'hero','https://images.example.com/original.png',
                'https://example.com/press','Test photographer','licensed',evidence='https://example.com/license',
                downloader=lambda url:image_bytes())
        self.assertFalse(photo['approved'])
        saved=engine.load(doc['slug'])['hero']
        self.assertEqual(saved['download_url'],'https://images.example.com/original.png')
        self.assertEqual(saved['evidence'],'https://example.com/license')
        self.assertTrue((engine.path_for(doc['slug'])/'assets'/'hero.jpg').exists())
    def test_reject_private_fetch_targets(self):
        for bad in ('http://example.com/img.jpg','https://127.0.0.1/photo.jpg','https://localhost/1.png',
                    'https://192.168.1.10/image.png','https://[::1]/1.png','https://a.local/photo.jpg',
                    'https://user:pass@example.com/image.jpg','https://public.example.com:8443/photo.jpg'):
            with self.subTest(bad=bad):
                with self.assertRaises((engine.PublicationError,ValueError)):
                    safe_photo_url(bad)
    def test_public_cannot_ship_private_reference_photography(self):
        public=dict(BRIEF,distribution='public')
        doc=self.new(brief=public)
        engine.select_style(doc['slug'],'bold-perspective')
        engine.add_story(doc['slug'],'Bridge')
        for slot in ('hero','bridge'):
            engine.import_image(doc['slug'],slot,image_bytes(), 'https://example.com/source', 'Example photographer','private_reference')
            engine.set_image_metadata(doc['slug'],slot,{'approved':True})
        pf=engine.preflight(engine.load(doc['slug']))
        self.assertFalse(pf['pass'])
        self.assertTrue(any('cannot be publicly distributed' in e for e in pf['errors']))
    def test_onepager_renders_both_selected_art_styles(self):
        doc=self.new();engine.select_style(doc['slug'],'field-notes')
        engine.add_story(doc['slug'],'Bridge')
        for slot in ('hero','bridge'):
            engine.import_image(doc['slug'],slot,image_bytes(), 'https://example.com/source', 'My photo','own')
            engine.set_image_metadata(doc['slug'],slot,{'approved':True})
        engine.update_story(doc['slug'],'bridge',{'description':'A gracefully engineered bridge connecting people and places.','website':'https://example.com/bridge'})
        d=engine.load(doc['slug'])
        self.assertTrue(engine.preflight(d)['pass'],engine.preflight(d))
        d1=engine.export(d['slug'])
        one=Path(d1['file']).read_bytes()
        engine.select_style(doc['slug'],'bold-perspective')
        d2=engine.export(doc['slug'])
        two=Path(d2['file']).read_bytes()
        self.assertNotEqual(one,two)
        self.assertEqual(d2['pages'],1)
        self.assertEqual(d2['photo_pages_verified'],1)

if __name__=='__main__':unittest.main()
