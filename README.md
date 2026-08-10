# dotplay

`dotplay` is a small, backend-agnostic RGB framebuffer platform for toy games, UI experiments, and BLE LED boards. It supports 8×8, 16×16, and 32×32 grids.

## What exists now

- 32x32 framebuffer core (draw ops + deterministic serialization + ASCII + PNG export)
- Pluggable input backends (`keyboard_sim`, `terminal_tui`, `hid_mouse_pygame`, `hid_mouse_evdev` stub, `noop_input`)
- Pluggable output backends (`pygame_window`, `terminal_tui`, `terminal_ascii`, `ble_ipixel` resilient skeleton)
- Clean app loop with normalized actions
- Explicit typed `Scene` protocol contract for scene lifecycle methods
- MVP `color_toggle` scene that demonstrates input → render → output behavior
- Test pattern scene for renderer testing
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

## First app demo: color toggle controls

Default scene is `color_toggle`.

Keyboard controls (with `keyboard_sim`):

- **Space/W**: turn panel on
- **S**: turn panel off
- **A**: turn panel red
- **D**: turn panel blue
- **R**: reset/off
- **Esc**: quit

To run in terminal preview instead of pygame window, set in config:

```yaml
output:
  backend: terminal_ascii
```

For an interactive full-screen terminal grid, pair the TUI input and output backends:

```yaml
input:
  backend: terminal_tui
output:
  backend: terminal_tui
  show_grid: false
```

The TUI uses Left/Right or A/D to move, Up/W to rotate, Down/S to soft drop,
Space to hard drop, R to reset, P to pause, and Q or Esc to quit. `tui` is also
accepted as a shorter backend alias.

Press **M** to cycle between mini-app modes, or use **1**–**9** to select one directly.
The footer shows the active mode and its short control hint. The bundled modes are Test,
Pattern, and Animation; within Animation, use Left/Right to switch between Fireworks and
Waves.

### Run the terminal UI

```bash
make setup
make run-tui
```

This uses [`config.tui.yaml`](config.tui.yaml). The terminal needs at least twice the
grid size in columns and three more rows than the grid size (64×35 for 32×32). The UI
will show its required dimensions if it is too small. Quit with **Q** or **Esc** and the
terminal will be restored normally.

Choose an 8×8 or 16×16 grid without changing configuration:

```bash
make run-tui GRID_SIZE=8
make run-tui GRID_SIZE=16
```

For other launch commands, use `dotplay --config config.tui.yaml --grid-size 8`.
GNU Make variables use `GRID_SIZE=8`; `make run-tui --grid-size=8` is not valid Make syntax.

The Pygame preview supports the same values: `make run-dev GRID_SIZE=8` or
`make run-dev GRID_SIZE=16`. Its window remains the same size, so each grid cell is
automatically enlarged to fill it.

## Switching config/backends

Edit `config.example.yaml` (or use `config.rpi.yaml` for Raspberry Pi defaults):

- Input: `input.backend`
- Output: `output.backend`
- Scene: `gameplay.mode`
- FPS: `app.fps`

Run with custom file:

```bash
dotplay --config path/to/config.yaml
```


## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: pygame` or pygame window fails to open | `pygame` not installed in active environment | Run `make setup` (or `pip install -e .[dev]`) and use `output.backend: terminal_ascii` when running headless. |
| BLE output cannot connect (`ble_ipixel`) | Device out of range, identifier mismatch, or BLE stack unavailable | Verify adapter with `bluetoothctl`, set `output.name_substring` / `output.identifier` / `output.mac` correctly, and keep `terminal_ascii` as fallback for offline debugging. |
| `hid_mouse_evdev` receives no input on Linux | Missing permissions or wrong device match substring | Confirm event device path and grant access (group/udev), then set the configured device-name substring to match your mouse-like device. |
