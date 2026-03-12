# dotplay

`dotplay` is a small, backend-agnostic 32x32 RGB framebuffer platform for toy games, UI experiments, and BLE LED boards.

## What exists now

- 32x32 framebuffer core (draw ops + deterministic serialization + ASCII + PNG export)
- Pluggable input backends (`keyboard_sim`, `hid_mouse_pygame`, `hid_mouse_evdev` stub, `noop_input`)
- Pluggable output backends (`pygame_window`, `terminal_ascii`, `ble_ipixel` resilient skeleton)
- Clean app loop with normalized actions
- Test pattern scene for first playable/renderable slice
- Unit, snapshot, integration, and backend contract tests

## Planned

- More scenes/games
- Full Linux evdev runtime backend
- Device-specific BLE protocol tuning for iPixel variants

## Setup (offline-ready after bootstrap)

```bash
make setup
```

This creates/reuses `.venv`, installs project + dev tools, and verifies imports/config/tests/lint/typecheck.

## Dev workflow

```bash
make run-dev
make test
make lint
make format
make typecheck
```

## Switching config/backends

Edit `config.example.yaml`:

- Input: `input.backend`
- Output: `output.backend`
- FPS: `app.fps`

Run with custom file:

```bash
dotplay --config path/to/config.yaml
```
