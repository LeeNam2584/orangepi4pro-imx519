#!/usr/bin/env python3
"""Install the pinned Orange Pi 4 Pro snapshot, without restarting the camera."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
KERNEL = '5.15.147-sun60iw2'
IMAGE_SHA = '0e39fea01d864931f75fd82a36c11a5fa1b965fcdb0606063ed3b8ba88c71951'
DTB = Path('/boot/dtb-' + KERNEL + '/allwinner/sun60i-a733-orangepi-4-pro.dtb')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check():
    for line in (ROOT / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        if digest(ROOT / name) != expected:
            raise RuntimeError('Checksum mismatch: ' + name)
    if platform.machine() != 'aarch64' or platform.release() != KERNEL:
        raise RuntimeError('Requires aarch64 kernel ' + KERNEL)
    env = Path('/boot/orangepiEnv.txt').read_text().splitlines()
    if 'fdtfile=allwinner/sun60i-a733-orangepi-4-pro.dtb' not in env:
        raise RuntimeError('Orange Pi 4 Pro boot configuration not found')
    if digest('/boot/uImage') != IMAGE_SHA:
        raise RuntimeError('Kernel build differs from tested image; rebuild before installation')
    if not DTB.is_file():
        raise RuntimeError('Expected DTB is missing')
    for executable in ('mpv', 'python3', 'sudo', 'setfacl'):
        if not shutil.which(executable):
            raise RuntimeError('Missing runtime dependency: ' + executable)
    result = subprocess.run(['ldd', str(ROOT / 'bin/imx519_live')], capture_output=True, text=True)
    if result.returncode or 'not found' in result.stdout:
        raise RuntimeError('Missing preview libraries: ' + result.stdout + result.stderr)
    print('PASS: checksums, board boot configuration, exact kernel build, runtime libraries')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--cam1-dtb', action='store_true', help='install tested full DTB (disables other camera ports)')
    parser.add_argument('--rollback', type=Path, help='manifest.json printed by a prior installation')
    args = parser.parse_args()
    if args.rollback:
        if os.geteuid():
            raise RuntimeError('Rollback requires sudo')
        manifest = args.rollback.resolve()
        records = json.loads(manifest.read_text())
        for record in reversed(records):
            target = Path(record['target'])
            if record['existed']:
                shutil.copy2(manifest.parent / record['backup'], target)
            else:
                target.unlink(missing_ok=True)
        subprocess.run(['/sbin/depmod', '-a', KERNEL], check=True)
        print('Restored files. Reboot manually to activate the restored kernel/DTB state.')
        return
    check()
    if not args.install:
        print('Read-only check. Use --install [--cam1-dtb] to install.')
        return
    if os.geteuid():
        raise RuntimeError('Installation requires sudo')
    mappings = [
        (ROOT/'modules/imx519.ko', Path('/lib/modules/'+KERNEL+'/kernel/bsp/drivers/vin/modules/sensor/imx519.ko'), 0o644),
        (ROOT/'config/imx519-cam1.conf', Path('/etc/modprobe.d/imx519-cam1.conf'), 0o644),
        (ROOT/'config/imx519-load.conf', Path('/etc/modules-load.d/imx519-cam1.conf'), 0o644),
    ]
    if args.cam1_dtb:
        mappings.append((ROOT/'boot'/DTB.name, DTB, 0o644))
    for item in ('bin/imx519_live', 'scripts/preview.py', 'scripts/focus.py'):
        mappings.append((ROOT/item, Path('/opt/orangepi4pro-imx519')/item, 0o755))
    backup = Path('/var/backups/orangepi4pro-imx519') / time.strftime('%Y%m%d-%H%M%S')
    backup.mkdir(parents=True, exist_ok=False)
    records = []
    for index, (source, target, mode) in enumerate(mappings):
        target.parent.mkdir(parents=True, exist_ok=True)
        record = {'target': str(target), 'existed': target.exists(), 'backup': str(index)}
        if target.exists():
            shutil.copy2(target, backup / str(index))
        records.append(record)
        (backup/'manifest.json').write_text(json.dumps(records, indent=2))
        temporary = target.with_name(target.name+'.imx519-install')
        shutil.copyfile(source, temporary)
        temporary.chmod(mode)
        os.replace(temporary, target)
    subprocess.run(['/sbin/depmod', '-a', KERNEL], check=True)
    print('Installed. Backup manifest:', backup/'manifest.json')
    print('Reboot manually, then run: python3 /opt/orangepi4pro-imx519/scripts/preview.py')

if __name__ == '__main__':
    main()
