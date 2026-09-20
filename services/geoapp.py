"""Mini app Telegram: legge il GPS e lo rimanda al bot come una città."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any
from urllib.parse import unquote

logger = logging.getLogger(__name__)

GEO_PURPOSES = frozenset(
    {
        "cielo",
        "sole",
        "meteo",
        "osserva",
        "skyq",
        "luna",
        "natev",
        "gps",
        "compass",
        "brfrom",
        "brto",
        "watch",
    }
)

PinHandler = Callable[
    [int, float, float, str | None, float | None, float | None],
    Awaitable[str],
]

_pin_handler: PinHandler | None = None

GEO_PAGE = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>La tua posizione</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  :root { color-scheme: dark; }
  html, body { height: 100%; }
  body {
    margin: 0; font-family: system-ui, sans-serif;
    background: var(--tg-theme-bg-color, #0f1419);
    color: var(--tg-theme-text-color, #f4f1ea);
    display: flex; align-items: center; justify-content: center;
    text-align: center; padding: 28px 22px;
  }
  main { max-width: 22rem; }
  h1 { font-size: 1.2rem; margin: 0 0 10px; }
  p { margin: 0; line-height: 1.45; opacity: .92; }
  .muted { margin-top: 12px; font-size: .92rem; opacity: .7; }
</style>
</head>
<body>
<main>
  <h1>📍 La tua posizione</h1>
  <p id="stato">Leggo il GPS e la uso come città, senza scriverla.</p>
  <p class="muted" id="nota"></p>
</main>
<script>
const tg = window.Telegram && window.Telegram.WebApp;
if (tg) { tg.ready(); tg.expand(); }
const stato = document.getElementById("stato");
const nota = document.getElementById("nota");
const purpose = new URLSearchParams(location.search).get("p") || "";

function fail(msg) {
  stato.textContent = msg;
  nota.textContent = "Chiudi e scrivi la città nel bot, oppure Italia / Mondo.";
}

async function sendPin(lat, lon, accuracy, heading) {
  stato.textContent = "Trovata. La uso come se l'avessi scritta…";
  try {
    const res = await fetch("/geo/pin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        initData: tg ? tg.initData : "",
        lat, lon, accuracy, heading, purpose
      })
    });
    const data = await res.json().catch(function () { return {}; });
    if (!res.ok || !data.ok) {
      fail(data.error || "Non ho trovato il luogo.");
      return;
    }
    stato.textContent = data.name ? ("Uso " + data.name + ".") : "Posizione ricevuta.";
    nota.textContent = "Puoi chiudere.";
    setTimeout(function () { if (tg) tg.close(); }, 500);
  } catch (err) {
    fail("Rete assente. Riprova o scrivi la città.");
  }
}

function viaBrowser() {
  if (!navigator.geolocation) {
    fail("Questo Telegram non dà il GPS.");
    return;
  }
  navigator.geolocation.getCurrentPosition(
    function (pos) {
      sendPin(
        pos.coords.latitude,
        pos.coords.longitude,
        pos.coords.accuracy,
        pos.coords.heading
      );
    },
    function () {
      fail("Serve il permesso per la posizione.");
    },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 20000 }
  );
}

function viaTelegram() {
  const lm = tg && tg.LocationManager;
  if (!lm || typeof lm.init !== "function") {
    viaBrowser();
    return;
  }
  lm.init(function () {
    if (lm.isLocationAvailable === false) {
      viaBrowser();
      return;
    }
    lm.getLocation(function (loc) {
      if (!loc || loc.latitude == null || loc.longitude == null) {
        viaBrowser();
        return;
      }
      sendPin(loc.latitude, loc.longitude, loc.horizontal_accuracy, loc.course);
    });
  });
}

viaTelegram();
</script>
</body>
</html>
"""


def geo_web_url(purpose: str | None = None) -> str | None:
    base = (os.getenv("WEBHOOK_URL") or "").strip().rstrip("/")
    if not base:
        return None
    if purpose and purpose in GEO_PURPOSES:
        return f"{base}/geo?p={purpose}"
    return f"{base}/geo"


def parse_webapp_user(token: str, init_data: str) -> int | None:
    if not token or not init_data:
        return None
    pairs: dict[str, str] = {}
    for part in init_data.split("&"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        pairs[key] = value
    given = pairs.pop("hash", "")
    if not given:
        return None
    check = "\n".join(f"{key}={value}" for key, value in sorted(pairs.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    expect = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expect, given):
        return None
    try:
        user = json.loads(unquote(pairs.get("user", "")))
        return int(user["id"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def clean_purpose(raw: str | None) -> str | None:
    value = (raw or "").strip()
    return value if value in GEO_PURPOSES else None


def register_pin_handler(handler: PinHandler) -> None:
    global _pin_handler
    _pin_handler = handler


def install_geo_http() -> None:
    """Aggiunge GET /geo e POST /geo/pin al server webhook di PTB (Tornado)."""
    try:
        from telegram.ext._utils.webhookhandler import WebhookAppClass
        import tornado.web
    except ImportError:
        logger.warning("Webhook non disponibile: la mini app GPS resta spenta")
        return
    if getattr(WebhookAppClass, "_botsquad_geo", False):
        return

    original = WebhookAppClass.__init__

    def patched(
        self: Any,
        webhook_path: str,
        bot: Any,
        update_queue: Any,
        secret_token: str | None = None,
    ) -> None:
        original(self, webhook_path, bot, update_queue, secret_token)
        self.add_handlers(
            r".*$",
            [
                (r"/geo/?", _GeoPageHandler),
                (r"/geo/pin", _GeoPinHandler),
            ],
        )

    WebhookAppClass.__init__ = patched  # type: ignore[method-assign]
    WebhookAppClass._botsquad_geo = True  # type: ignore[attr-defined]
    logger.info("Mini app GPS su /geo")


class _GeoPageHandler:
    """Placeholder sostituito dopo l'import di tornado."""

    pass


class _GeoPinHandler:
    pass


def _bind_tornado_handlers() -> None:
    global _GeoPageHandler, _GeoPinHandler
    try:
        import tornado.web
    except ImportError:
        return

    class GeoPageHandler(tornado.web.RequestHandler):
        def get(self) -> None:
            self.set_header("Content-Type", "text/html; charset=utf-8")
            self.set_header("Cache-Control", "no-store")
            self.write(GEO_PAGE)

    class GeoPinHandler(tornado.web.RequestHandler):
        def set_default_headers(self) -> None:
            self.set_header("Content-Type", "application/json; charset=utf-8")
            self.set_header("Cache-Control", "no-store")

        async def post(self) -> None:
            try:
                payload = json.loads(self.request.body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self.set_status(400)
                self.write({"ok": False, "error": "richiesta non valida"})
                return
            if not isinstance(payload, dict):
                self.set_status(400)
                self.write({"ok": False, "error": "richiesta non valida"})
                return
            token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
            user_id = parse_webapp_user(token, str(payload.get("initData") or ""))
            if user_id is None:
                self.set_status(403)
                self.write({"ok": False, "error": "Apri il tasto da Telegram, non dal browser."})
                return
            try:
                lat = float(payload.get("lat"))
                lon = float(payload.get("lon"))
            except (TypeError, ValueError):
                self.set_status(400)
                self.write({"ok": False, "error": "coordinate assenti"})
                return
            if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
                self.set_status(400)
                self.write({"ok": False, "error": "coordinate non valide"})
                return
            purpose = clean_purpose(str(payload.get("purpose") or ""))
            try:
                accuracy_m = float(payload["accuracy"]) if payload.get("accuracy") is not None else None
            except (TypeError, ValueError):
                accuracy_m = None
            try:
                heading = float(payload["heading"]) if payload.get("heading") is not None else None
            except (TypeError, ValueError):
                heading = None
            handler = _pin_handler
            if handler is None:
                self.set_status(503)
                self.write({"ok": False, "error": "bot non pronto"})
                return
            try:
                name = await handler(user_id, lat, lon, purpose, accuracy_m, heading)
            except Exception:
                logger.exception("GPS ricevuto ma non applicato")
                self.set_status(500)
                self.write({"ok": False, "error": "non ho trovato il luogo"})
                return
            self.write({"ok": True, "name": name})

    _GeoPageHandler = GeoPageHandler
    _GeoPinHandler = GeoPinHandler


_bind_tornado_handlers()
