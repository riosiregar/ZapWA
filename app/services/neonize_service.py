# app/services/neonize_service.py
import asyncio
import base64
import logging
from typing import Any, Dict, List

from neonize.aioze.client import ClientFactory, NewAClient  # async-friendly
from neonize.events import ConnectedEv, PairStatusEv
from neonize.utils import log
from neonize.utils.enum import Presence

from app.utils.ws_hub import ws_hub  # hub sederhana utk broadcast WS (lihat bawah)
from app.helpers.phone import normalize_msisdn  # normalisasi 62/8xx -> 62xxx

logger = logging.getLogger(__name__)


class NeonizeService:
    """
    Mengelola 1..N sesi WhatsApp Neonize (async).
    - QR broadcast via WebSocket
    - Tangkap siapa yang login (PairStatusEv)
    - Keep-alive presence (PING-PONG)
    - Verifikasi nomor lewat is_on_whatsapp
    """

    def __init__(self, db_name: str = "neonize.db"):
        self.factory = ClientFactory(db_name)
        self.clients: List[NewAClient] = []
        self._ping_task: asyncio.Task | None = None
        self._last_qr_png_b64: str | None = None
        self._last_logged_in_uid: str | None = None

    async def boot(self):
        # Buat client dari sesi yg sudah pernah login
        for device in self.factory.get_all_devices():
            self.factory.new_client(device.JID)
        # Atau buka slot baru (scan lagi) — beri uuid unik kalau perlu
        # from uuid import uuid4; self.factory.new_client(uuid=uuid4().hex[:6])

        # Event bindings (factory-wide)
        @self.factory.event(ConnectedEv)
        async def _on_connected(_: NewAClient, __: ConnectedEv):
            log.info("⚡ Connected")
            # Mulai keep-alive “pemanasan nomor”
            if not self._ping_task:
                self._ping_task = asyncio.create_task(self._presence_keepalive())

        @self.factory.event(PairStatusEv)
        async def _on_pair_status(_: NewAClient, ev: PairStatusEv):
            # nomor yg berhasil pair/login
            self._last_logged_in_uid = (
                ev.ID.User
            )  # contoh resmi. :contentReference[oaicite:3]{index=3}
            await ws_hub.broadcast_json(
                {"type": "pair_status", "user": ev.ID.User, "server": ev.ID.Server}
            )

        # Build semua client (thread dihandle lib, kita tunggu blocking di loop)
        await self.factory.run()  # contoh pola resmi async. :contentReference[oaicite:4]{index=4}
        # Simpan referensi klien untuk pemakaian API (ambil dari factory)
        self.clients = getattr(self.factory, "clients", []) or []

        # Bind QR per-klien (neonize exposes Event.qr via client.qr). :contentReference[oaicite:5]{index=5}
        for c in self.clients:

            @c.qr  # payload = bytes PNG QR dari core (dibungkus Event.qr) :contentReference[oaicite:6]{index=6}
            async def _on_qr(_: NewAClient, qr_png_bytes: bytes):
                self._last_qr_png_b64 = base64.b64encode(qr_png_bytes).decode()
                await ws_hub.broadcast_json(
                    {"type": "qr", "png_b64": self._last_qr_png_b64}
                )

    async def presence_now(self):
        # Kirim presence AVAILABLE utk "pemanasan nomor". :contentReference[oaicite:7]{index=7}
        for c in self.clients:
            try:
                await c.send_presence(Presence.AVAILABLE)
            except Exception as e:
                logger.warning(f"presence error: {e}")

    async def _presence_keepalive(self, interval_sec: int = 120):
        while True:
            await self.presence_now()
            await asyncio.sleep(interval_sec)

    def get_last_qr(self) -> str | None:
        return self._last_qr_png_b64

    def get_last_pair_user(self) -> str | None:
        return self._last_logged_in_uid

    async def destroy_sessions(self):
        # logout() akan melepas sesi; connect ulang nanti akan trigger QR baru. :contentReference[oaicite:8]{index=8}
        for c in self.clients:
            try:
                await c.logout()
                await c.disconnect()
            except Exception:
                pass
        self.clients.clear()
        self._last_qr_png_b64 = None
        self._last_logged_in_uid = None

    async def verify_numbers(self, raw_numbers: List[str]) -> Dict[str, Any]:
        """
        - Normalisasi msisdn (8xxx -> 62xxx)
        - Dedup
        - panggil is_on_whatsapp(*numbers)
        - hasil: {has_wa, no_wa, duplicate}
        """
        normalized = [normalize_msisdn(x) for x in raw_numbers if x and x.strip()]
        duplicates = sorted(list({n for n in normalized if normalized.count(n) > 1}))
        # de-dupe untuk query WA
        unique = sorted(list(dict.fromkeys(normalized)))

        if not self.clients:
            raise RuntimeError("Neonize belum siap / belum ada sesi aktif.")

        # Panggil ke satu klien saja (asumsi sama untuk semua device)
        client = self.clients[0]

        # is_on_whatsapp(*numbers) -> Sequence[IsOnWhatsAppResponse] :contentReference[oaicite:9]{index=9}
        # Robust parsing: field pada proto bisa berubah, jadi konversi ke dict.
        from google.protobuf.json_format import MessageToDict

        resp = await client.is_on_whatsapp(*unique)
        has_wa, no_wa = [], []
        for r in resp:
            d = MessageToDict(r, preserving_proto_field_name=True)
            # Cari indikasi “exists” / “is_in” di berbagai kemungkinan nama field
            exists = (
                d.get("exists")
                or d.get("is_in")
                or d.get("IsIn")
                or d.get("is_in_whatsapp")
            )
            # Ambil echo nomor yang dicek (biasanya ‘input’ atau ‘JID’)
            checked = (
                d.get("input")
                or d.get("number")
                or d.get("JID", {}).get("user")
                or d.get("jid", {}).get("user")
            )
            if exists:
                has_wa.append(checked)
            else:
                no_wa.append(checked)

        # Ada nomor unik yang mungkin tidak ikut terjawab (fallback ke no_wa)
        known = set([*has_wa, *no_wa])
        for n in unique:
            if n not in known:
                no_wa.append(n)

        return {
            "total_input": len(raw_numbers),
            "unique_checked": len(unique),
            "duplicate": duplicates,
            "has_wa": sorted(set(filter(None, has_wa))),
            "no_wa": sorted(set(filter(None, no_wa))),
        }


neonize = NeonizeService()
