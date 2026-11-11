"""
EKSTERNI AGENT - poseban mali web servis (kao da ga je napravio neko drugi).

Pokretanje (u POSEBNOM terminalu):
    python external_agent/server.py

Prima POST zahtev sa JSON-om na http://127.0.0.1:8001/run
i vraća JSON odgovor. Engine ga poziva preko HTTP-a.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST, PORT = "127.0.0.1", 8001


class AgentHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")

        # --- "logika" eksternog agenta: ocenjuje odgovore ucenika ---
        inputs = data.get("inputs", {})
        grades = {}
        for student_id in ("student_beginner", "student_intermediate", "student_advanced"):
            student = inputs.get(student_id) or {}
            grades[student_id] = 5 if "Nisam siguran" in student.get("answer", "") else 9

        answer = {"message": "Zdravo, ja sam EKSTERNI agent za ocenjivanje!", "grades": grades}

        body = json.dumps(answer, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"Eksterni agent radi na http://{HOST}:{PORT}/run  (Ctrl+C za gasenje)")
    HTTPServer((HOST, PORT), AgentHandler).serve_forever()
