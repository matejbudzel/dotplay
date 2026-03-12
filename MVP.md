# dotplay MVP checklist

This checklist tracks the first-version work needed to satisfy the original project goals.

## 1) Core architecture and runtime

- [x] Keep strict backend-agnostic pipeline: input → normalized events → scene logic → framebuffer → output.
- [x] Maintain a deterministic fixed-size 32×32 framebuffer with draw primitives and serialization.
- [x] Keep a simple main loop with polling, update, render, push, timing control, and graceful shutdown.
- [x] Add explicit scene protocol typing (instead of runtime `hasattr`) for cleaner contracts.

## 2) Config and environment

- [x] YAML-based runtime config with sample configuration.
- [x] Offline-first bootstrap script (`scripts/setup.sh`) that installs and validates tests/lint/typecheck.
- [x] Add a production Pi config preset (`config.rpi.yaml`) with low FPS and BLE defaults.
- [ ] Add config validation schema with user-friendly error messages for invalid values.

## 3) Input backends

- [x] `keyboard_sim` for local development without hardware.
- [x] `hid_mouse_pygame` for dev mouse simulation.
- [x] `hid_mouse_evdev` module exists with basic normalization helper.
- [ ] Complete full evdev runtime integration (device discovery by substring + non-blocking read loop).
- [ ] Add integration tests for evdev behavior using mocked events.

## 4) Output backends

- [x] `pygame_window` preview backend.
- [x] `terminal_ascii` backend.
- [x] `ble_ipixel` first-pass resilient backend skeleton.
- [ ] Implement concrete iPixel packet formatting/protocol and chunking strategy.
- [ ] Add BLE reconnect/backoff configuration and metrics in logs.
- [ ] Add backend contract/integration tests for BLE using stubs.

## 5) MVP app behavior

- [x] Add `color_toggle` scene to verify input/output end-to-end.
- [x] Bind simple actions:
  - on: Confirm / Hard Drop / Up / Rotate
  - off: Cancel / Soft Drop / Down
  - left: turn red
  - right: turn blue
- [ ] Add tiny on-screen help overlay (pygame and terminal variants) for controls.
- [ ] Add one additional scene (menu or simple game) behind config switch.

## 6) Testing and quality gates

- [x] Unit tests for framebuffer and config loading.
- [x] Snapshot tests for multiple framebuffer shapes.
- [x] Integration test for loop execution with fake backends.
- [x] Lint + typecheck + tests in setup verification.
- [x] Add deterministic tests for `color_toggle` scene behavior.
- [x] Add a small smoke test that runs CLI with terminal backend and bounded ticks.

## 7) Docs and deployment

- [x] README with setup, commands, and backend switching.
- [x] Raspberry Pi deployment guide with apt baseline and systemd sample.
- [x] AGENTS.md project guidance.
- [x] Add troubleshooting matrix (pygame missing, BLE unavailable, evdev permissions).
- [ ] Add release checklist for first deploy to Pi.
