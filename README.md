# agent-assembly-line
Build agents in Python.
A library for developers.

## Build

/usr/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install service

cp agent-assembly-line-service.service /etc/systemd/system/agent-assembly-line.service
sudo systemctl enable agent-assembly-line.service
systemctl is-enabled agent-assembly-line.service


journalctl -u agent-assembly-line.service

# Test

python -m unittest tests/test.py
