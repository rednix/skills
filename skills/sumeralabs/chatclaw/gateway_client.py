"""
Local OpenClaw Gateway Client — authenticated connection using device identity.

Implements:
  - Ed25519 challenge-response signing for the WebSocket auth handshake
  - HTTP SSE streaming via /v1/chat/completions for all chat traffic
    (WebSocket chat.send is NOT used — see OpenClaw Issue #16427)

Cross-platform path resolution:
  Checks /data/.openclaw first (Docker/VPS layout), then ~/.openclaw (standard install).
  Override with OPENCLAW_DATA_DIR environment variable.
"""

import asyncio
import base64
import json
import logging
import os
import time
import uuid
from pathlib import Path

import aiohttp
import websockets
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_private_key,
    load_pem_public_key,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path resolution — exported so main.py can use the same base
# ---------------------------------------------------------------------------
def _resolve_openclaw_dir() -> Path:
    """
    Returns the OpenClaw data directory, in priority order:
      1. OPENCLAW_DATA_DIR environment variable (explicit override)
      2. /data/.openclaw  (Docker / VPS layout — present on Hostinger/Contabo)
      3. ~/.openclaw      (standard macOS / Linux install)
    """
    if env := os.environ.get("OPENCLAW_DATA_DIR"):
        return Path(env)
    docker_path = Path("/data/.openclaw")
    if docker_path.exists():
        return docker_path
    return Path.home() / ".openclaw"


OPENCLAW_DATA_DIR    = _resolve_openclaw_dir()
DEVICE_IDENTITY_PATH = OPENCLAW_DATA_DIR / "identity" / "device.json"
DEVICE_AUTH_PATH     = OPENCLAW_DATA_DIR / "identity" / "device-auth.json"
OPENCLAW_CONFIG_PATH = OPENCLAW_DATA_DIR / "openclaw.json"

logger.debug(f"OpenClaw data dir resolved to: {OPENCLAW_DATA_DIR}")

# ---------------------------------------------------------------------------
# Gateway WebSocket constants
# ---------------------------------------------------------------------------
GATEWAY_URL  = "ws://localhost:18789"
CLIENT_ID    = "cli"
CLIENT_MODE  = "cli"
ROLE         = "operator"
SCOPES       = ["operator.admin", "operator.approvals", "operator.pairing"]


# ---------------------------------------------------------------------------
# Identity helpers
# ---------------------------------------------------------------------------
def load_device_identity() -> dict:
    try:
        identity = json.loads(DEVICE_IDENTITY_PATH.read_text())
        auth     = json.loads(DEVICE_AUTH_PATH.read_text())
    except FileNotFoundError as e:
        raise RuntimeError(
            f"OpenClaw identity files not found: {e}. "
            f"Expected at: {OPENCLAW_DATA_DIR / 'identity'}. "
            "Set OPENCLAW_DATA_DIR if your installation uses a different path."
        ) from e

    token = auth.get("tokens", {}).get("operator", {}).get("token")
    if not identity.get("deviceId") or not token:
        raise RuntimeError(
            "Missing deviceId or operator token in OpenClaw identity files. "
            "Re-run 'openclaw wizard' to regenerate them."
        )
    return {
        "device_id":       identity["deviceId"],
        "private_key_pem": identity["privateKeyPem"].encode(),
        "public_key_pem":  identity["publicKeyPem"].encode(),
        "token":           token,
    }


def derive_public_key_base64(public_key_pem: bytes) -> str:
    pub = load_pem_public_key(public_key_pem)
    raw = pub.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)[-32:]
    return base64.b64encode(raw).decode()


def build_auth_payload(device_id: str, token: str, signed_at_ms: int, nonce: str) -> str:
    scopes_str = ",".join(SCOPES)
    parts = ["v2", device_id, CLIENT_ID, CLIENT_MODE, ROLE,
             scopes_str, str(signed_at_ms), token, nonce]
    return "|".join(parts)


def sign_payload(payload: str, private_key_pem: bytes) -> str:
    private_key = load_pem_private_key(private_key_pem, password=None)
    sig = private_key.sign(payload.encode("utf-8"))
    return base64.urlsafe_b64encode(sig).rstrip(b"=").decode()


# ---------------------------------------------------------------------------
# GatewayClient
# ---------------------------------------------------------------------------
class GatewayClient:
    def __init__(self):
        self.url          = GATEWAY_URL
        self.ws           = None
        self._request_id  = 1
        self._queue       = asyncio.Queue()
        self._reader_task = None

    def _next_id(self) -> str:
        rid = f"skill-{self._request_id}"
        self._request_id += 1
        return rid

    async def connect(self):
        backoff = 5
        while True:
            try:
                logger.info(f"Connecting to local gateway: {self.url}...")
                self.ws = await websockets.connect(
                    self.url,
                    ping_interval=30,
                    ping_timeout=10,
                    close_timeout=5,
                )
                await self._authenticate()
                logger.info("Gateway authenticated ✓")
                if self._reader_task:
                    self._reader_task.cancel()
                # Single reader coroutine owns all recv() calls — prevents concurrent recv conflicts
                self._reader_task = asyncio.create_task(self._reader_loop())
                backoff = 5
                return
            except RuntimeError:
                # Identity file errors are not transient — surface immediately
                raise
            except Exception as e:
                logger.warning(f"Gateway connection failed: {e}. Retrying in {backoff}s...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)

    async def _reader_loop(self):
        """Drains the WebSocket into the internal queue. One task only."""
        try:
            async for raw in self.ws:
                msg = json.loads(raw)
                await self._queue.put(msg)
        except Exception as e:
            logger.warning(f"Gateway reader stopped: {e}")
        finally:
            await self._queue.put(None)  # Signal disconnect to any awaiting receive()

    async def _authenticate(self):
        """Performs the Ed25519 challenge-response handshake with the OpenClaw gateway."""
        while True:
            raw = await self.ws.recv()
            msg = json.loads(raw)

            # Skip health/tick events that may arrive before the challenge
            if msg.get("event") in ("health", "tick"):
                continue

            if msg.get("type") == "event" and msg.get("event") == "connect.challenge":
                nonce     = msg["payload"]["nonce"]
                signed_at = int(time.time() * 1000)
                identity  = load_device_identity()

                payload   = build_auth_payload(
                    identity["device_id"], identity["token"], signed_at, nonce
                )
                signature = sign_payload(payload, identity["private_key_pem"])
                pub_key   = derive_public_key_base64(identity["public_key_pem"])

                await self.ws.send(json.dumps({
                    "type": "req", "id": "auth-init", "method": "connect",
                    "params": {
                        "minProtocol": 3,
                        "maxProtocol": 3,
                        "client": {
                            "id": CLIENT_ID, "version": "1.0.0",
                            "platform": "linux", "mode": CLIENT_MODE,
                        },
                        "role":   ROLE,
                        "scopes": SCOPES,
                        "auth":   {"token": identity["token"]},
                        "device": {
                            "id":        identity["device_id"],
                            "publicKey": pub_key,
                            "signature": signature,
                            "signedAt":  signed_at,
                            "nonce":     nonce,
                        },
                    },
                }))

            elif msg.get("type") == "res" and msg.get("id") == "auth-init":
                if msg.get("ok"):
                    return
                raise RuntimeError(f"Gateway auth rejected: {msg.get('error')}")

    async def receive(self) -> dict:
        """Returns the next message from the gateway queue. Raises on disconnect."""
        msg = await self._queue.get()
        if msg is None:
            raise websockets.ConnectionClosed(None, None)
        return msg

    def _read_gateway_token(self) -> str:
        """Reads the gateway bearer token from openclaw.json."""
        try:
            cfg = json.loads(OPENCLAW_CONFIG_PATH.read_text())
            token = cfg["gateway"]["auth"]["token"]
            if not token:
                raise ValueError("gateway.auth.token is empty")
            return token
        except FileNotFoundError:
            raise RuntimeError(
                f"openclaw.json not found at {OPENCLAW_CONFIG_PATH}. "
                "Ensure OpenClaw has been initialised and set OPENCLAW_DATA_DIR if needed."
            )
        except (KeyError, ValueError) as e:
            raise RuntimeError(
                f"Could not read gateway.auth.token from openclaw.json: {e}"
            )

    async def stream_chat(self, text: str, session_key: str):
        """
        POST to /v1/chat/completions and yield SSE delta text chunks.

        Uses the standard OpenAI-compatible SSE format:
          data: {"choices":[{"delta":{"content":"..."}}]}
          data: [DONE]

        The session key is passed via x-openclaw-session-key header, which tells
        OpenClaw to route the request to a specific conversation thread and maintain
        history across turns (session_key = task_id from the dashboard).
        """
        url           = "http://localhost:18789/v1/chat/completions"
        gateway_token = self._read_gateway_token()

        headers = {
            "Authorization":           f"Bearer {gateway_token}",
            "x-openclaw-session-key":  f"agent:main:{session_key}",
            "Content-Type":            "application/json",
            "Accept":                  "text/event-stream",
        }
        body = {
            "model":    "auto",
            "messages": [{"role": "user", "content": text}],
            "stream":   True,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as resp:
                if not resp.ok:
                    body_bytes = await resp.read()
                    raise RuntimeError(
                        f"Gateway HTTP {resp.status}: "
                        f"{body_bytes[:400].decode('utf-8', errors='replace')}"
                    )

                # Parse SSE line-by-line using readline() — required because aiohttp's
                # async-for iterates raw bytes, not logical SSE lines
                while True:
                    line_bytes = await resp.content.readline()
                    if not line_bytes:
                        break
                    line = line_bytes.decode("utf-8").strip()
                    if not line or not line.startswith("data: "):
                        continue

                    data_str = line[6:]
                    if data_str == "[DONE]":
                        return

                    try:
                        chunk = json.loads(data_str)
                        # Primary: OpenAI-style choices[0].delta.content
                        delta = (
                            chunk.get("choices", [{}])[0]
                                 .get("delta", {})
                                 .get("content", "")
                        ) or ""
                        # Fallback: non-OpenAI format (top-level text / delta.text)
                        if not delta:
                            delta = (
                                chunk.get("text")
                                or chunk.get("delta", {}).get("text")
                                or ""
                            )
                        # Strip stray <final>…</final> wrapper emitted on first-message SSE quirk
                        if delta:
                            delta = delta.replace("<final>", "").replace("</final>", "")
                        if delta:
                            yield delta
                    except json.JSONDecodeError as e:
                        logger.warning(f"SSE JSON decode error: {e} — line: {data_str[:100]}")
                        continue

    async def close(self):
        if self._reader_task:
            self._reader_task.cancel()
        if self.ws:
            await self.ws.close()
        logger.info("Gateway connection closed")