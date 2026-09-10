#!/usr/bin/env python3
"""Run the unchanged stable preview; apply the verified optical focus afterward."""
import argparse
import os
from pathlib import Path
import signal
import subprocess
import time
from focus import set_focus

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--focus', type=int, default=2200)
a = p.parse_args()
if not 0 <= a.focus <= 4095:
    p.error('focus must be 0..4095')
if os.geteuid() == 0:
    p.error('Run as the logged-in desktop user; sudo is requested only for hardware access')
for entry in Path('/proc').iterdir():
    if entry.name.isdigit():
        try:
            comm = (entry/'comm').read_text().strip()
        except OSError:
            continue
        # The legacy binary terminates mpv on startup, so refuse other players.
        if comm in ('imx519_live', 'mpv'):
            p.error('Close the existing camera/mpv window first (PID '+entry.name+')')
subprocess.run(['sudo', '/sbin/modprobe', 'imx519'], check=True)
subprocess.run(['sudo', '/sbin/modprobe', 'vin_v4l2'], check=True)
subprocess.run(['sudo', '/sbin/modprobe', 'i2c-dev'], check=True)
subprocess.run(['sudo', 'setfacl', '-m', 'u:'+str(os.getuid())+':rw', '/dev/video0', '/dev/i2c-8'], check=True)
root = Path(__file__).resolve().parent.parent
env = os.environ.copy()
env.setdefault('DISPLAY', ':0')
env.setdefault('XAUTHORITY', str(Path.home()/'.Xauthority'))
proc = subprocess.Popen([str(root/'bin/imx519_live'), '--focus', '250', '--fps', '30', '--sharp', '180', '--coring', '8'], env=env)
try:
    time.sleep(3)
    if proc.poll() is not None:
        raise RuntimeError('Preview exited during initialization')
    set_focus(a.focus)
    print('Physical focus set to', a.focus, '(legacy log still displays 250)', flush=True)
    proc.wait()
except KeyboardInterrupt:
    pass
finally:
    if proc.poll() is None:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
