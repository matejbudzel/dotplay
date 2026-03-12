from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Protocol

from dotplay.core.framebuffer import FrameBuffer
from dotplay.output.base import OutputBackend

logger = logging.getLogger(__name__)


class _BleWriter(Protocol):
    async def write_gatt_char(self, char_specifier: str, data: bytes) -> None: ...


@dataclass
class BleIPixelOutput(OutputBackend):
    name_substring: str | None = None
    identifier: str | None = None
    mac: str | None = None
    service_uuid: str | None = None
    char_uuid: str | None = None
    _latest: bytes | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self._task: asyncio.Task[None] | None = None
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        while self._running:
            try:
                await self._connect_and_send_once()
            except Exception as exc:  # pragma: no cover - hardware path
                logger.warning("BLE cycle failed: %s", exc)
                await asyncio.sleep(2.0)

    async def _connect_and_send_once(self) -> None:
        from bleak import BleakClient, BleakScanner

        target = self.identifier or self.mac or self.name_substring
        if target is None:
            logger.warning("BLE backend disabled: no identifier configured")
            await asyncio.sleep(2.0)
            return
        logger.info("BLE target selector=%s", target)

        device = None
        if self.identifier or self.mac:
            try:
                async with BleakClient(target) as client:
                    await self._flush(client)
                    return
            except Exception:
                logger.info("Direct BLE connect failed, fallback to scan")

        discovered = await BleakScanner.discover(timeout=3.0)
        for candidate in discovered:
            name = candidate.name or ""
            address = candidate.address or ""
            if self.identifier and candidate.address == self.identifier:
                device = candidate
                break
            if self.mac and address.lower() == self.mac.lower():
                device = candidate
                break
            if self.name_substring and self.name_substring.lower() in name.lower():
                device = candidate
                break
        if device is None:
            logger.info("No matching BLE device found")
            await asyncio.sleep(2.0)
            return

        async with BleakClient(device) as client:
            await self._flush(client)

    async def _flush(self, client: _BleWriter) -> None:
        payload = self._latest
        if payload is None:
            await asyncio.sleep(0.2)
            return
        if self.char_uuid is None:
            logger.info("No BLE characteristic configured; dropping frame")
            await asyncio.sleep(0.2)
            return
        await client.write_gatt_char(self.char_uuid, payload)

    def push(self, framebuffer: FrameBuffer) -> None:
        self._latest = framebuffer.to_bytes()

    def close(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
