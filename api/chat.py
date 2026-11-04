from http.server import BaseHTTPRequestHandler
import json, os, urllib.request

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api/chat":
            self.send_response(404); self.end_headers(); return
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n))
        q = body.get("q", "")
        ctx = body.get("ctx", "")[:12000]
        if not GROQ_KEY:
            self.send_response(500); self.send_header("Content-Type","application/json"); self.end_headers()
            self.wfile.write(json.dumps({"error":"GROQ_API_KEY not set on server"}).encode()); return
        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role":"system","content":"You answer questions about a PDF. Use only provided text. Be concise, cite pages."},
                {"role":"user","content": f"Document text:\n{ctx}\n\nQuestion: {q}"}
            ],
            "temperature": 0.2, "max_tokens": 800
        }).encode()
        req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions",
            data=payload, headers={"Authorization":"Bearer "+GROQ_KEY,"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                j = json.loads(r.read())
            ans = j["choices"][0]["message"]["content"]
        except Exception as e:
            ans = "Error: " + str(e)
        self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps({"answer": ans}).encode())
    def do_OPTIONS(self):
        self.send_response(200); self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
