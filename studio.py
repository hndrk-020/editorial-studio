"""Editorial Studio local dashboard. Local-only; remote photo URLs fetched ONLY when explicitly supplied."""
from __future__ import annotations
import argparse
import base64
import json
import secrets
import mimetypes
import os
import re
import sys
import traceback
import webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlsplit, unquote
from threading import Timer

from engine import (ROOT, OUTPUTS, PROJECTS, PublicationError, add_story, create_project,
                    export, import_image, list_projects, load, path_for, preflight,
                    set_image_metadata, update_project, update_story, update_brief, select_style)
from creative import propose_directions, candidate_queries
from photo_researcher import import_public_image

PORT = 8765
MAX_BODY=20_000_000
SESSION_TOKEN=secrets.token_urlsafe(32)

class Handler(BaseHTTPRequestHandler):
    server_version="EditorialStudio/0.3"

    def log_message(self, fmt, *args):
        print("[studio]", fmt % args)

    def _response(self,code,data,kind="application/json; charset=utf-8",download=False):
        raw = data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type",kind)
        self.send_header("Content-Length",str(len(raw)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("X-Frame-Options","DENY")
        self.send_header("Referrer-Policy","no-referrer")
        self.send_header("Content-Security-Policy","default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        if download:self.send_header("Content-Disposition",f'attachment; filename="{download}"')
        self.end_headers();self.wfile.write(raw)

    def _file(self, filepath,kind,download=False):
        if not filepath.exists():return self._response(404,{"error":"File not found"})
        self._response(200,filepath.read_bytes(),kind,download)

    def _reject_cross_origin(self):
        origin=self.headers.get("Origin","")
        port=self.server.server_port
        return origin and origin not in (f"http://127.0.0.1:{port}",f"http://localhost:{port}")

    def _trusted_local_host(self):
        port=self.server.server_port
        return self.headers.get("Host","") in (f"127.0.0.1:{port}",f"localhost:{port}")

    def do_GET(self):
        if not self._trusted_local_host():
            return self._response(403,{"error":"Invalid local Host header"})
        try:
            p=urlsplit(self.path)
            q={k:v[0] for k,v in parse_qs(p.query).items()}
            if p.path=="/": return self._file(ROOT/"static"/"index.html","text/html; charset=utf-8")
            if p.path=="/static/studio.css":return self._file(ROOT/"static"/"studio.css","text/css; charset=utf-8")
            if p.path=="/static/studio.js":return self._file(ROOT/"static"/"studio.js","application/javascript; charset=utf-8")
            if p.path=="/api/projects":return self._response(200,{"projects":list_projects()})
            if p.path=="/api/session":return self._response(200,{"token":SESSION_TOKEN})
            if p.path=="/api/project":
                doc=load(q['slug'])
                return self._response(200,{"project":doc,"preflight":preflight(doc),
                                          "directions":propose_directions(doc.get('brief',{}))})
            if p.path=="/api/research":
                doc=load(q['slug'])
                return self._response(200,candidate_queries(doc,q['slot']))
            if p.path=="/api/preflight":return self._response(200,preflight(load(q["slug"])))
            if p.path.startswith("/assets/"):
                pieces=p.path.split("/")
                if len(pieces)!=4:return self._response(404,{"error":"Invalid path"})
                _,_,slug,name=pieces
                if not re.fullmatch(r"[a-z0-9_-]+\.jpg",name):raise PublicationError("Invalid photo filename")
                return self._file(path_for(slug)/"assets"/name,"image/jpeg")
            if p.path.startswith("/output/"):
                name=p.path[len("/output/"):]
                if not re.fullmatch(r"[a-z0-9-]+-(?:magazine|onepager)\.pdf",name):raise PublicationError("Invalid PDF filename")
                return self._file(OUTPUTS/name,"application/pdf",name)
            return self._response(404,{"error":"Not found"})
        except (KeyError,PublicationError,ValueError) as ex:self._response(400,{"error":str(ex)})
        except Exception as ex:
            traceback.print_exc()
            self._response(500,{"error":"Unexpected server error; check the terminal"})

    def do_POST(self):
        if not self._trusted_local_host() or self._reject_cross_origin():
            return self._response(403,{"error":"Untrusted request origin"})
        if self.headers.get('Content-Type','').split(';')[0].strip().lower()!='application/json':
            return self._response(415,{"error":"Expected application/json"})
        if not secrets.compare_digest(self.headers.get('X-Editorial-Studio-Token',''),SESSION_TOKEN):
            return self._response(403,{"error":"Missing or invalid studio session token"})
        try:
            n=int(self.headers.get("Content-Length", "0"))
            if n<=0 or n>MAX_BODY:return self._response(413,{"error":"Invalid request size (20 MB max)"})
            data=json.loads(self.rfile.read(n).decode("utf-8"))
            p=urlsplit(self.path).path
            if p=="/api/create":
                project=create_project(str(data.get("title","")),str(data.get("kind","magazine")),str(data.get("description","")),str(data.get("edition","")),data.get('brief',{}))
                return self._response(200,{"project":project})
            if p=="/api/project/update":return self._response(200,{"project":update_project(data["slug"],data.get("changes",{}))})
            if p=="/api/brief/update":return self._response(200,{"project":update_brief(data['slug'],data.get('changes',{}))})
            if p=="/api/style/select":return self._response(200,{"style":select_style(data['slug'],data['style_id'])})
            if p=="/api/story/add":return self._response(200,{"story":add_story(data["slug"],str(data["title"]))})
            if p=="/api/story/update":return self._response(200,{"story":update_story(data["slug"],data["story_id"],data.get("changes",{}))})
            if p=="/api/image/upload":
                rawdata=str(data.get("data", ""))
                if "," in rawdata:rawdata=rawdata.split(",",1)[1]
                try:payload=base64.b64decode(rawdata,validate=True)
                except Exception as ex:raise PublicationError("Invalid image encoding") from ex
                im=import_image(data["slug"],data["slot"],payload,data.get("source", ""),data.get("credit", ""),data.get("rights", ""))
                return self._response(200,{"image":im})
            if p=="/api/image/from-url":
                result=import_public_image(data['slug'],data['slot'],str(data['image_url']),
                                           str(data.get('source','')),str(data.get('credit','')),
                                           str(data.get('rights','')))
                return self._response(200,{"image":result,'message':'Candidate imported; verify subject and approve separately'})
            if p=="/api/image/meta":
                im=set_image_metadata(data["slug"],data["slot"],data.get("changes", {}))
                return self._response(200,{"image":im})
            if p=="/api/export":
                audit=export(data["slug"])
                return self._response(200,{"audit":audit,"url":"/output/"+Path(audit["file"]).name})
            return self._response(404,{"error":"Unknown action"})
        except (KeyError,PublicationError,ValueError,UnicodeDecodeError,json.JSONDecodeError) as ex:self._response(400,{"error":str(ex)})
        except Exception:
            traceback.print_exc()
            self._response(500,{"error":"Unexpected server error; check the terminal"})


def main():
    parser=argparse.ArgumentParser(prog="editorial-studio",description="Creative brief, two directions, photo research, magazine and onepager PDF publishing")
    sub=parser.add_subparsers(dest="command")
    run=sub.add_parser("serve",help="Open local dashboard")
    run.add_argument("--port",type=int,default=PORT)
    p=sub.add_parser("preflight",help="Validate photo assets and links")
    p.add_argument("slug")
    e=sub.add_parser("export",help="Generate strictly verified offline PDF")
    e.add_argument("slug")
    args=parser.parse_args()
    try:
        if args.command=="preflight":
            result=preflight(load(args.slug))
            print(json.dumps(result,ensure_ascii=False,indent=2))
            return 0 if result["pass"] else 2
        if args.command=="export":
            result=export(args.slug)
            print(json.dumps(result,ensure_ascii=False,indent=2))
            return 0
        if args.command in (None,"serve"):
            port=args.port if args.command=="serve" else PORT
            with ThreadingHTTPServer(("127.0.0.1",port),Handler) as server:
                print(f"\nEditorial Studio is running: http://127.0.0.1:{port}\nOnly accessible on this computer. Press Ctrl+C to stop.\n",flush=True)
                Timer(1.2,lambda:webbrowser.open(f"http://127.0.0.1:{port}")).start()
                server.serve_forever()
            return 0
    except PublicationError as ex:
        print(f"ERROR: {ex}",file=sys.stderr)
        return 2
    except OSError as ex:
        print(f"ERROR: Could not start the local server ({ex}). Close any older Editorial Studio window using port 8765 and retry.",file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nStudio stopped")
        return 0

if __name__=="__main__":raise SystemExit(main())
