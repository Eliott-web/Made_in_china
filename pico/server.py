import socket
import network
import ujson
import db


_game_state = {
    "distance": "—",
    "time":     "—",
    "state":    "idle",
    "game_over": False,
    "j1_score": 0,
    "j2_score": 0,
}

_on_start = None
_on_stop  = None
_on_reset = None
_sock     = None


def set_callbacks(on_start, on_stop, on_reset):
    global _on_start, _on_stop, _on_reset
    _on_start = on_start
    _on_stop  = on_stop
    _on_reset = on_reset


def update_game_state(**kwargs):
    _game_state.update(kwargs)


def _setup_ap():
    import time
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    time.sleep_ms(1000)
    ap.active(True)
    ap.config(essid="MadeInChina", password="12345678", channel=6)
    for _ in range(100):
        if ap.active():
            break
        time.sleep_ms(100)
    # Attendre que l'IP soit assignée (sinon 0.0.0.0)
    for _ in range(100):
        if ap.ifconfig()[0] != "0.0.0.0":
            break
        time.sleep_ms(100)
    print("AP ready, IP:", ap.ifconfig()[0])


def _parse_request(raw):
    header_part, _, body_raw = raw.partition("\r\n\r\n")
    lines = header_part.split("\r\n")
    method, path, _ = lines[0].split(" ", 2)
    headers = {}
    for line in lines[1:]:
        if ": " in line:
            k, v = line.split(": ", 1)
            headers[k.lower()] = v
    content_length = int(headers.get("content-length", 0))
    body = ujson.loads(body_raw[:content_length]) if content_length > 0 else {}
    return method, path, body


def _respond_json(conn, body, status="200 OK"):
    payload = ujson.dumps(body).encode()
    conn.send(
        "HTTP/1.1 {}\r\n"
        "Content-Type: application/json\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Content-Length: {}\r\n\r\n".format(status, len(payload))
    )
    conn.send(payload)


def _serve_file(conn, filepath):
    import os
    ext  = filepath.rsplit(".", 1)[-1]
    mime = {"html": "text/html", "css": "text/css", "js": "text/javascript"}.get(ext, "text/plain")
    try:
        size = os.stat(filepath)[6]
        conn.send(
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: {}; charset=utf-8\r\n"
            "Cache-Control: no-store\r\n"
            "Content-Length: {}\r\n\r\n".format(mime, size)
        )
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(512)
                if not chunk:
                    break
                conn.write(chunk)
    except OSError:
        conn.send("HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n")


def _handle(conn):
    raw = b""
    while True:
        chunk = conn.recv(512)
        if not chunk:
            break
        raw += chunk
        if b"\r\n\r\n" in raw:
            break

    if b"\r\n\r\n" not in raw:
        conn.close()
        return
    raw_lower = raw.lower()
    remaining_length = int(raw_lower.split(b"content-length: ")[1].split(b"\r\n")[0]) if b"content-length: " in raw_lower else 0
    body_start = raw.index(b"\r\n\r\n") + 4
    while len(raw) - body_start < remaining_length:
        raw += conn.recv(256)

    method, path, body = _parse_request(raw.decode())

    if method == "OPTIONS":
        conn.send(
            "HTTP/1.1 204 No Content\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Access-Control-Allow-Methods: GET, POST\r\n"
            "Access-Control-Allow-Headers: Content-Type\r\n\r\n"
        )
    elif method == "GET" and path == "/":
        _serve_file(conn, "pico/site/site.html")
    elif method == "GET" and path == "/script_site.js":
        _serve_file(conn, "pico/site/script_site.js")
    elif method == "GET" and path == "/style.css":
        _serve_file(conn, "pico/site/style.css")
    elif method == "GET" and path == "/data":
        _respond_json(conn, _game_state)
    elif method == "GET" and path == "/db":
        _respond_json(conn, {"profiles": {p["name"]: p for p in db.get_all_profiles()}})
    elif method == "POST" and path == "/profile/create":
        ok = db.create_profile(body.get("name", ""))
        _respond_json(conn, {"ok": ok})
    elif method == "POST" and path == "/profile/delete":
        db.delete_profile(body.get("name", ""))
        _respond_json(conn, {"ok": True})
    elif method == "POST" and path == "/stats/update":
        db.update_stats(body["name"], body["games_won"], body["rounds_won"], body["rounds_played"])
        _respond_json(conn, {"ok": True})
    elif method == "POST" and path == "/start":
        if _on_start:
            _on_start(body.get("rounds", 3))
        _respond_json(conn, {"ok": True})
    elif method == "POST" and path == "/stop":
        if _on_stop:
            _on_stop()
        _respond_json(conn, {"ok": True})
    elif method == "POST" and path == "/reset":
        if _on_reset:
            _on_reset()
        _respond_json(conn, {"ok": True})
    else:
        conn.send("HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n")


def init():
    global _sock
    _setup_ap()
    _sock = socket.socket()
    _sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _sock.bind(("", 80))
    _sock.listen(1)
    _sock.setblocking(False)


def poll():
    if _sock is None:
        return
    try:
        conn, _ = _sock.accept()
        conn.settimeout(2.0)
        try:
            _handle(conn)
        except Exception as e:
            print("handler error:", e)
        finally:
            conn.close()
    except OSError:
        pass
