# ruff: noqa: E501
from __future__ import annotations

import base64
import json
import logging
import socket
import threading
from collections import deque
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, ClassVar

from dotplay.core.framebuffer import FrameBuffer
from dotplay.output.base import OutputBackend
from dotplay.types import Action, InputEvent

logger = logging.getLogger(__name__)

_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>dotplay</title><style>
:root { color-scheme: dark; font-family: system-ui, sans-serif; background: #111217; color: #e8e8ef; }
body { margin: 0; display: grid; justify-items: center; gap: 12px; padding: 14px; }
#menu { width: min(92vw, 512px); font-size: 14px; color: #cfd0da; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
canvas { width: min(92vw, 512px); aspect-ratio: 1; image-rendering: pixelated; background: #000; border: 1px solid #333541; }
#controls { width: min(92vw, 512px); display: grid; gap: 8px; }
.row { display: flex; justify-content: center; gap: 8px; }
button { min-width: 48px; min-height: 44px; border: 1px solid #464957; border-radius: 8px; background: #292b35; color: inherit; font-size: 18px; touch-action: manipulation; }
button:active { background: #565a6c; }
#help { position: fixed; inset: 0; display: none; place-items: center; background: #0009; padding: 20px; }
#help.visible { display: grid; }
#help-box { min-width: min(80vw, 340px); max-width: 90vw; padding: 18px; border: 1px solid #606575; border-radius: 10px; background: #1c1e27; }
#help-lines { display: grid; gap: 10px; white-space: pre-wrap; }
</style></head><body>
<div id="menu">dotplay</div>
<canvas id="grid" width="32" height="32"></canvas>
<div id="controls">
<div class="row"><button data-action="mode_1">1</button><button data-action="mode_2">2</button><button data-action="mode_3">3</button><button data-action="mode_4">4</button><button data-action="next_mode">M</button><button data-action="next_style">G</button><button data-action="help">?</button></div>
<div class="row"><button data-action="up">↑</button></div>
<div class="row"><button data-action="left">←</button><button data-action="hard_drop">●</button><button data-action="right">→</button></div>
<div class="row"><button data-action="down">↓</button><button data-action="reset">R</button></div>
</div>
<div id="help"><div id="help-box"><div id="help-lines"></div><div class="row"><button data-action="escape">Esc</button></div></div></div>
<script>
const canvas = document.querySelector('#grid'), ctx = canvas.getContext('2d'), menu = document.querySelector('#menu'), help = document.querySelector('#help'), helpLines = document.querySelector('#help-lines');
const send = action => fetch('/input', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({action})});
document.querySelectorAll('button').forEach(button => button.addEventListener('click', () => send(button.dataset.action)));
const keys = {ArrowLeft:'left', ArrowRight:'right', ArrowUp:'up', ArrowDown:'down', Escape:'escape', '?':'help', ' ':'hard_drop', r:'reset', m:'next_mode', g:'next_style', 1:'mode_1', 2:'mode_2', 3:'mode_3', 4:'mode_4', 5:'mode_5', 6:'mode_6', 7:'mode_7', 8:'mode_8', 9:'mode_9'};
addEventListener('keydown', event => { const action = keys[event.key]; if (action && (action !== 'escape' || help.classList.contains('visible'))) { event.preventDefault(); send(action); } });
function renderHelp(lines) { helpLines.replaceChildren(...(lines || []).map(line => { const node = document.createElement('div'); node.textContent = line; return node; })); help.classList.toggle('visible', Boolean(lines)); }
async function refresh() { try { const response = await fetch('/state', {cache:'no-store'}); if (!response.ok) throw new Error(`state request: ${response.status}`); const state = await response.json(); if (!state.pixels) return; const cellSize = Math.max(1, Math.floor(512 / state.width)); if (canvas.width !== state.width * cellSize) { canvas.width = state.width * cellSize; canvas.height = state.height * cellSize; } const rgb = atob(state.pixels); ctx.fillStyle = '#12141b'; ctx.fillRect(0, 0, canvas.width, canvas.height); for (let y = 0, source = 0; y < state.height; y++) { for (let x = 0; x < state.width; x++, source += 3) { const red = rgb.charCodeAt(source), green = rgb.charCodeAt(source + 1), blue = rgb.charCodeAt(source + 2); if (red || green || blue) { const centerX = x * cellSize + cellSize / 2, centerY = y * cellSize + cellSize / 2, brightness = Math.max(red, green, blue), radius = 12 + brightness * 52 / 255, gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius); gradient.addColorStop(0, `rgb(${red}, ${green}, ${blue})`); gradient.addColorStop(.25, `rgba(${red}, ${green}, ${blue}, .8)`); gradient.addColorStop(.7, `rgba(${red}, ${green}, ${blue}, .24)`); gradient.addColorStop(1, `rgba(${red}, ${green}, ${blue}, .04)`); ctx.fillStyle = gradient; ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize); } } } ctx.strokeStyle = '#2a2d39'; for (let x = 0; x <= state.width; x++) { ctx.beginPath(); ctx.moveTo(x * cellSize + .5, 0); ctx.lineTo(x * cellSize + .5, canvas.height); ctx.stroke(); } for (let y = 0; y <= state.height; y++) { ctx.beginPath(); ctx.moveTo(0, y * cellSize + .5); ctx.lineTo(canvas.width, y * cellSize + .5); ctx.stroke(); } menu.textContent = `dotplay  •  ${state.status || ''}`; renderHelp(state.help); } catch (error) { menu.textContent = `Connection error: ${error.message || 'reconnecting'}`; } }
setInterval(refresh, 75); refresh();
</script></body></html>"""


class WebSession:
    """Thread-safe shared state and HTTP lifecycle for the web backends."""

    _instance: ClassVar[WebSession | None] = None

    def __init__(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        self.host = host
        self.port = port
        self._lock = threading.Lock()
        self._events: deque[InputEvent] = deque()
        self._pixels = b""
        self._width = 0
        self._height = 0
        self._status = ""
        self._help: list[str] | None = None
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @classmethod
    def shared(cls, host: str, port: int) -> WebSession:
        if cls._instance is None:
            cls._instance = cls(host, port)
        return cls._instance

    def start(self) -> None:
        if self._server is not None:
            return
        def handler(*args: Any) -> _WebRequestHandler:
            return _WebRequestHandler(*args, session=self)

        self._server = ThreadingHTTPServer((self.host, self.port), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        logger.info("Web preview available at %s", self.url)

    @property
    def url(self) -> str:
        port = self.port if self._server is None else self._server.server_address[1]
        host = self.host
        if host == "0.0.0.0":
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
                    connection.connect(("8.8.8.8", 80))
                    host = connection.getsockname()[0]
            except OSError:
                host = "localhost"
        return f"http://{host}:{port}"

    def close(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join()
        self._server = None
        self._thread = None

    def update_frame(self, framebuffer: FrameBuffer) -> None:
        with self._lock:
            self._pixels = framebuffer.to_bytes()
            self._width = framebuffer.width
            self._height = framebuffer.height

    def set_status(self, status: str) -> None:
        with self._lock:
            self._status = status

    def set_help(self, lines: list[str] | None) -> None:
        with self._lock:
            self._help = lines

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                "width": self._width,
                "height": self._height,
                "pixels": base64.b64encode(self._pixels).decode("ascii"),
                "status": self._status,
                "help": self._help,
            }

    def add_event(self, event: InputEvent) -> None:
        with self._lock:
            self._events.append(event)

    def drain_events(self) -> list[InputEvent]:
        with self._lock:
            events = list(self._events)
            self._events.clear()
        return events


class WebOutput(OutputBackend):
    """Publish framebuffer and scene status for a browser canvas client."""

    def __init__(
        self, host: str = "0.0.0.0", port: int = 8000, session: WebSession | None = None
    ) -> None:
        self.session = session or WebSession.shared(host, port)
        self.session.start()

    def set_status(self, status: str) -> None:
        self.session.set_status(status)

    def set_help(self, lines: list[str] | None) -> None:
        self.session.set_help(lines)

    def push(self, framebuffer: FrameBuffer) -> None:
        self.session.update_frame(framebuffer)

    def close(self) -> None:
        self.session.close()


class _WebRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args: Any, session: WebSession) -> None:
        self.session = session
        super().__init__(*args)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/":
            self._respond(HTTPStatus.OK, _PAGE.encode(), "text/html; charset=utf-8")
        elif self.path == "/state":
            payload = json.dumps(self.session.snapshot()).encode()
            self._respond(HTTPStatus.OK, payload, "application/json")
        else:
            self._respond(HTTPStatus.NOT_FOUND, b"Not found", "text/plain")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/input":
            self._respond(HTTPStatus.NOT_FOUND, b"Not found", "text/plain")
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length))
            action = Action(payload["action"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            self._respond(HTTPStatus.BAD_REQUEST, b"Invalid action", "text/plain")
            return
        self.session.add_event(InputEvent(action))
        self._respond(HTTPStatus.NO_CONTENT, b"", "text/plain")

    def log_message(self, format: str, *args: object) -> None:
        _ = format, args

    def _respond(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
