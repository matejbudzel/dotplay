You are building a small but well-engineered Python project called:

  dotplay

Project goal
Build a cross-platform Python application that renders a 32×32 RGB framebuffer and can be controlled through pluggable input backends and displayed through pluggable output backends.

Primary purpose
dotplay is a personal toy/status-display/game platform for a cheap BLE 32×32 LED board ("iPixel"-style board) and simple input devices. It must be pleasant to develop on macOS without requiring the real hardware, and it must run headless on very old Raspberry Pi Linux hardware with minimal changes (mostly via config).

IMPORTANT GLOBAL CONSTRAINT
Assume internet access is only guaranteed during the first setup/bootstrap phase; optimize the repository for offline iteration afterward.

Main target use cases

1. Development on macOS:
   - no LED board required
   - no HID mouse required
   - keyboard simulation input
   - desktop preview window output
   - optional terminal renderer
   - optionally real BLE LED board connected to the Mac

2. Deployment on Linux / Raspberry Pi:
   - headless
   - read from a real HID mouse-like input device
   - send frames to a BLE LED board
   - recover gracefully from missing hardware

3. Use cases:
   - small pixel-art UI
   - simple retro-style games
   - menus and status screens

Architecture overview

Use a clean architecture:

input backend → normalized input events → app/game logic → framebuffer → output backend

Core logic must not depend on concrete hardware implementations.

Technology and tooling requirements

Language/runtime:
- Python 3.12

Project structure:
- modern Python packaging
- pyproject.toml as canonical configuration
- src/ layout
- typed code everywhere practical

Tooling:
- Ruff for lint + formatting
- mypy for static typing
- pytest for tests
- PyYAML for config
- pygame for dev preview
- bleak for BLE
- evdev for Linux HID backend (optional dependency)

Create requirements.txt as a convenience deploy file, but keep pyproject.toml canonical.

Coding rules:
- comments in English only
- avoid heavy frameworks
- avoid unnecessary async complexity
- keep runtime dependencies small
- prefer readability over cleverness

Development environment constraint

Primary dev environment:
- Codex (web-based)
Backup:
- GitHub Codespaces

Important constraint:
Internet may only be available during initial setup.

Bootstrap/setup requirements

You MUST implement a working offline-ready bootstrap workflow in the first pass.

Create:

  scripts/setup.sh

It must:

1. Create or reuse a virtual environment.
2. Install project with dev dependencies.
3. Install all tooling needed for:
   - running app
   - tests
   - lint
   - format
   - typecheck
4. Verify setup by running:
   - imports
   - config load
   - tests
   - lint
   - typecheck
5. Leave environment usable offline afterward.

Also provide simple commands via:
- Makefile or justfile (optional but recommended)

Expected commands:

- make setup
- make run-dev
- make test
- make lint
- make format
- make typecheck

Input backends to implement

Define InputBackend abstraction.

Implement:

1. keyboard_sim
   - default dev backend
   - keys configurable
   - default mapping:
     A = left
     D = right
     W = rotate/up/confirm
     S = drop/down
     R = reset
     Space = primary/hard drop
     Esc = quit

2. hid_mouse_pygame
   - uses pygame mouse events
   - wheel + buttons → normalized actions

3. hid_mouse_evdev (Linux only)
   - use evdev
   - detect device by name substring
   - normalize to action model

4. noop_input (optional)

Normalized action model

Use normalized actions such as:

left, right, up, down, rotate, soft_drop, hard_drop,
confirm, cancel, reset, pause, quit

FrameBuffer

Implement a central FrameBuffer:

- size: 32×32
- RGB 0–255
- operations:
  - clear/fill
  - set_pixel/get_pixel
  - lines
  - rectangles
  - sprite blit

Also support:

- deterministic serialization for tests
- ascii representation
- PNG export for snapshot tests

Output backends

Define OutputBackend abstraction.

Implement:

1. pygame_window
   - dev preview
   - scalable LED size
   - optional grid

2. terminal_ascii
   - human-readable
   - ANSI if feasible

3. ble_ipixel (production backend)

BLE cross-platform requirements

The BLE backend must work on both:

- Linux (BlueZ)
- macOS (CoreBluetooth)

Implementation rules:

1. Use bleak.
2. Do NOT assume MAC address availability:
   - Linux: MAC works
   - macOS: identifier only

3. Support device config via:
   - MAC (Linux)
   - name substring
   - identifier

4. Discovery strategy:
   - attempt direct connect
   - fallback scan

5. Backend must:
   - fail gracefully
   - retry periodically
   - not block main loop

6. Log clearly which identifier is used.

Config

Use YAML runtime config.

Provide:

config.example.yaml

Suggested sections:

app:
input:
output:
logging:
dev:
gameplay:

Testing requirements

The project must include strong automated feedback loops.

Include:

1. Unit tests:
   - framebuffer ops
   - config loading
   - input normalization

2. Snapshot tests:

Provide many snapshots:

- blank framebuffer
- solid color
- checkerboard
- crosshair
- menu mock
- sample board state

Snapshots must be:

- human-readable ascii
- optionally PNG for selected cases

3. Integration tests:

- fake input backend
- fake output backend
- loop execution test

4. Backend contract tests

Fake backends:

- FakeInputBackend
- FakeOutputBackend
- NullOutputBackend

Initial functional scope

Do NOT start with full Tetris.

First implement:

- test pattern scene OR
- minimal menu scene OR
- simple Tic-Tac-Toe

Pick whichever best demonstrates architecture + testing.

Main loop requirements

Implement clean loop:

- input poll
- update
- render
- output push
- timing control
- logging
- graceful shutdown

Keep deterministic and simple.

Raspberry Pi deployment guideline (important)

Create:

docs/rpi-setup.md

It must include:

1. OS guidance:
   - recommend DietPi
   - fallback Raspberry Pi OS Lite
   - what to disable

2. apt baseline:

example:

sudo apt update
sudo apt install -y \
  python3 \
  python3-venv \
  python3-pip \
  git \
  bluetooth \
  bluez \
  bluez-tools \
  libbluetooth-dev

3. BLE sanity check:

bluetoothctl
power on
scan on

4. Performance tips:

- disable GUI
- low logging
- low FPS (~5–15)

5. systemd example

6. deploy steps

Design constraints for slow RPi

- avoid heavy deps
- avoid busy loops
- allow low FPS
- BLE must not block
- logging must be configurable

AGENTS.md

Create AGENTS.md explaining:

- project purpose
- architecture
- coding standards
- adding backends
- adding scenes
- snapshot philosophy
- strict separation of hardware concerns
- expectation of expanding automated tests

README.md

Must include:

- what dotplay is
- setup steps
- dev workflow
- switching configs
- test/lint/typecheck commands
- what exists vs planned

Definition of done (first pass)

Done when:

1. installs cleanly
2. runs on macOS with keyboard_sim + pygame_window
3. runs terminal_ascii
4. BLE backend exists (working or skeleton)
5. backend-agnostic architecture works
6. strong test suite exists
7. snapshot tests exist
8. lint/typecheck/tests pass
9. README + AGENTS present
10. ready for extension

Implementation strategy

Proceed in steps:

1. scaffold + tooling
2. config + logging
3. framebuffer + tests
4. fake backends + loop
5. pygame output
6. keyboard input
7. first scene
8. terminal output
9. BLE backend
10. docs + polish

General rules

- choose simplest good solution
- prioritize testability
- prioritize cross-platform dev
- avoid unnecessary async
- keep code small and clean

Expected output

Generate full project files and working code.
Prefer working slices over placeholders.
Include tests from the beginning.
