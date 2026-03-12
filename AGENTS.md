# dotplay AGENTS guide

## Project purpose

dotplay is a lightweight, testable 32x32 RGB framebuffer app framework with pluggable input/output backends for local development and Raspberry Pi/BLE deployment.

## Architecture

Strict flow:

1. input backend
2. normalized input events
3. scene/app logic
4. framebuffer
5. output backend

Core logic must remain hardware-agnostic.

## Coding standards

- Python 3.12, typed code
- English comments only
- Keep logic readable and small
- Avoid heavy frameworks and unnecessary async complexity
- Prefer deterministic behavior for tests

## Adding backends

- Implement `InputBackend` or `OutputBackend` contracts.
- Keep hardware access isolated in backend modules.
- Fail gracefully when optional dependencies or devices are missing.

## Adding scenes

- Scene objects should expose `update()` and `render(framebuffer)` and optional `reset()`.
- Keep scene logic independent from hardware.

## Snapshot philosophy

- Prefer human-readable ASCII snapshots first.
- Use PNG snapshots for selected visual checks.
- Keep snapshot generation deterministic.

## Testing expectations

- Expand unit and integration tests with each feature.
- Add contract tests for any new backend.
- Preserve strict separation of hardware concerns.
