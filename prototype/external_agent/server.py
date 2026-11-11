"""
EKSTERNI AGENT - poseban mali web servis (kao da ga je napravio neko drugi).

Pokretanje (u POSEBNOM terminalu):
    python external_agent/server.py

Prima POST zahtev sa JSON-om na http://127.0.0.1:8001/run i vraca JSON.
Engine ga poziva preko HTTP-a kada je u config/agents.yaml kod
answer_grader postavljeno  type: remote_http.

Ovaj eksterni agent NE koristi LLM - ocenjuje jednostavnim pravilom
(duzina odgovora), samo da pokaze da sistem radi sa spoljnim servisom.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST, PORT = "127.0.0.1", 8001


class AgentHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")

        grades = {}
        for student_id, result in data.get("inputs", {}).items():
            if not student_id.startswith("student_test_") or not result:
                continue
            answers = result.get("answers", [])
            avg_len = sum(len(a.get("answer", "")) for a in answers) / max(len(answers), 1)
            score = min(100, round(avg_len))   # duzi odgovor = vise poena (namerno naivno)
            grades[student_id] = {"score": score, "comment": "ocenjeno eksternim servisom (pravilo: duzina odgovora)"}

        scores = [g["score"] for g in grades.values()]
        answer = {
            "message": "Zdravo, ja sam EKSTERNI agent za ocenjivanje!",
            "grades": grades,
            "average": round(sum(scores) / len(scores), 1) if scores else None,
            "_source": "external_http",
        }
        body = json.dumps(answer, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"Eksterni agent radi na http://{HOST}:{PORT}/run  (Ctrl+C za gasenje)")
    HTTPServer((HOST, PORT), AgentHandler).serve_forever()
