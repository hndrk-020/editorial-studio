"""Local-host and CSRF protections for desktop dashboard's JSON API."""
from __future__ import annotations
import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import engine
from studio import Handler
from http.server import ThreadingHTTPServer

class LocalServerSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=5)
    def setUp(self):
        self.port=self.server.server_port
    def request(self,method,path,body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        c.request(method,path,body=body,headers=headers or {})
        response=c.getresponse();status=response.status
        content=response.read();c.close()
        return status,json.loads(content)
    def test_untrusted_host_cannot_get_session_token(self):
        status,_=self.request('GET','/api/session',headers={'Host':'evil.example'})
        self.assertEqual(status,403)
    def test_mutation_requires_csrf_token_and_correct_origin(self):
        status,sess=self.request('GET','/api/session')
        self.assertEqual(status,200)
        self.assertGreater(len(sess['token']),30)
        data=json.dumps({'title':'A magazine'}).encode()
        status,_=self.request('POST','/api/create',body=data,headers={'Content-Type':'application/json'})
        self.assertEqual(status,403)
        status,_=self.request('POST','/api/create',body=data,
            headers={'Content-Type':'text/plain','X-Editorial-Studio-Token':sess['token']})
        self.assertEqual(status,415)
        status,_=self.request('POST','/api/create',body=data,
            headers={'Content-Type':'application/json','X-Editorial-Studio-Token':sess['token'],
                     'Origin':'https://evil.example'})
        self.assertEqual(status,403)

if __name__=='__main__':unittest.main()
