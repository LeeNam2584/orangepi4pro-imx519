#!/usr/bin/env python3
"""Set AK7375 lens position without changing the legacy preview mailbox."""
import argparse
import fcntl
import os
import time

def set_focus(position):
    if not 0 <= position <= 4095:
        raise ValueError('AK7375 position must be 0..4095')
    fd = os.open('/dev/i2c-8', os.O_RDWR)
    try:
        fcntl.ioctl(fd, 0x0703, 0x0c)
        if os.write(fd, bytes([2, 0])) != 2:
            raise OSError('Short write enabling VCM')
        time.sleep(.015)
        if os.write(fd, bytes([0, position >> 4, (position & 15) << 4])) != 3:
            raise OSError('Short write setting VCM')
    finally:
        os.close(fd)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('position', type=int, nargs='?', default=2200)
    a = p.parse_args()
    set_focus(a.position)
    print('Physical lens position:', a.position)
