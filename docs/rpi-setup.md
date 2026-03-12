# Raspberry Pi setup guide

## OS guidance

- Recommended: DietPi (minimal footprint)
- Fallback: Raspberry Pi OS Lite
- Disable desktop GUI, unused services, and high-volume logging.

## apt baseline

```bash
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
```

## BLE sanity checks

```bash
bluetoothctl
power on
scan on
```

## Performance tips

- Run headless
- Keep logging at INFO/WARN for production
- Set low FPS (5-15)
- Avoid unnecessary background services

## systemd example

```ini
[Unit]
Description=dotplay service
After=network.target bluetooth.target

[Service]
Type=simple
WorkingDirectory=/opt/dotplay
ExecStart=/opt/dotplay/.venv/bin/dotplay --config /opt/dotplay/config.yaml
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

## Deploy steps

1. Clone repository on Pi.
2. Run `bash scripts/setup.sh`.
3. Copy and edit config for Pi hardware.
4. Validate with terminal output backend first.
5. Enable/start systemd service.
