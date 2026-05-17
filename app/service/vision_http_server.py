from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


class VisionHttpServer:
    def __init__(self, vision_service, host: str = "127.0.0.1", port: int = 8765):
        self.vision_service = vision_service
        self.host = host
        self.port = int(port)
        self._server: ThreadingHTTPServer | None = None

    def start(self) -> None:
        handler = self._handler()
        self._server = ThreadingHTTPServer((self.host, self.port), handler)
        self._server.serve_forever()

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()

    def _handler(self):
        vision_service = self.vision_service

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                if self.path != "/plate-detections":
                    self._send(404, {"error": "not_found"})
                    return

                try:
                    payload = self._read_json()
                    sensor_id = payload.get("sensor_id")
                    if sensor_id is None:
                        raise ValueError("sensor_id is required.")

                    if payload.get("detected_plate"):
                        result = vision_service.process_plate_text(
                            sensor_id=int(sensor_id),
                            detected_plate=str(payload["detected_plate"]),
                            image_path=payload.get("image_path"),
                        )
                    else:
                        result = vision_service.process_image(
                            sensor_id=int(sensor_id),
                            image_path=str(payload["image_path"]),
                            save_result=bool(payload.get("save_result", True)),
                        )
                    self._send(200, result)
                except Exception as exc:
                    self._send(400, {"error": exc.__class__.__name__, "message": str(exc)})

            def log_message(self, format, *args):  # noqa: A002
                return

            def _read_json(self) -> dict[str, Any]:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length).decode("utf-8")
                return json.loads(body or "{}")

            def _send(self, status: int, payload: dict[str, Any]) -> None:
                body = json.dumps(payload, default=str).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        return Handler
