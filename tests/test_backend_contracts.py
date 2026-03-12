from dotplay.core.framebuffer import FrameBuffer
from dotplay.fakes import FakeInputBackend, FakeOutputBackend, NullOutputBackend


def test_fake_input_contract() -> None:
    backend = FakeInputBackend(batches=[[]])
    assert backend.poll() == []


def test_fake_output_contract() -> None:
    fb = FrameBuffer()
    backend = FakeOutputBackend()
    backend.push(fb)
    assert len(backend.frames) == 1


def test_null_output_contract() -> None:
    fb = FrameBuffer()
    backend = NullOutputBackend()
    backend.push(fb)
