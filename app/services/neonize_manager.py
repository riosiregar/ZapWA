import asyncio
from typing import Optional, Dict
from sqlalchemy import select, update
from app.config.db import AsyncSessionLocal
from app.models.session import Session
from app.models.enums import SessionStatus

# TODO: ganti komentar ini dengan import client neonize sebenarnya
# from neonize import Client


class NeonizeClientWrapper:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._client = None
        self._qr_queue: asyncio.Queue[str] = asyncio.Queue()
        self.connected_info: Optional[dict] = None

    async def init_from_db(self):
        async with AsyncSessionLocal() as db:
            sess = (
                await db.execute(select(Session).where(Session.id == self.session_id))
            ).scalar_one_or_none()
            if not sess:
                db.add(Session(id=self.session_id, status=SessionStatus.disconnected))
                await db.commit()
            # if sess.session_blob:
            #     self._client = Client(state_blob=sess.session_blob)

    async def connect(self):
        # Pasang event handler Neonize di sini
        async def on_qr(qr_b64: str, expires_in: int):
            await self._qr_queue.put(qr_b64)
            await self._update_status(SessionStatus.qr)

        async def on_connected(info: dict, state_blob: bytes):
            await self._save_connected(info, state_blob)

        # await self._client.connect(on_qr=on_qr, on_connected=on_connected)
        await on_qr("data:image/png;base64,XXX", 60)  # mock untuk awal dev

    async def get_qr(self, timeout: int = 65) -> Optional[str]:
        try:
            return await asyncio.wait_for(self._qr_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def destroy(self):
        # if self._client: await self._client.logout_and_close()
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Session)
                .where(Session.id == self.session_id)
                .values(
                    status=SessionStatus.disconnected,
                    session_blob=None,
                    phone=None,
                    pushname=None,
                    device=None,
                )
            )
            await db.commit()

    async def ping(self):
        # if self._client: await self._client.send_presence()
        return True

    async def is_registered(self, phone_e164: str) -> bool:
        # TODO: ganti dengan API neonize/whatsmeow cek jid
        # sementara: parity mock
        n = int("".join(ch for ch in phone_e164 if ch.isdigit()))
        return n % 2 == 1

    async def _update_status(self, status: SessionStatus):
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Session)
                .where(Session.id == self.session_id)
                .values(status=status)
            )
            await db.commit()

    async def _save_connected(self, info: dict, state_blob: bytes):
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Session)
                .where(Session.id == self.session_id)
                .values(
                    status=SessionStatus.connected,
                    phone=info.get("phone"),
                    pushname=info.get("pushname"),
                    device=info.get("device"),
                    session_blob=state_blob,
                )
            )
            await db.commit()


class ClientRegistry:
    def __init__(self):
        self._clients: Dict[str, NeonizeClientWrapper] = {}
        self._lock = asyncio.Lock()

    async def get(self, session_id: str) -> NeonizeClientWrapper:
        async with self._lock:
            if session_id not in self._clients:
                c = NeonizeClientWrapper(session_id)
                await c.init_from_db()
                self._clients[session_id] = c
            return self._clients[session_id]


registry = ClientRegistry()
