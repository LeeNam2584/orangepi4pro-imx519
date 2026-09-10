#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
KERNEL=5.15.147-sun60iw2
test "$(uname -r)" = "$KERNEL"
mkdir -p build
tar -xzf source/linux-vin-source.tar.gz -C build
make -C "/lib/modules/$KERNEL/build" M="$PWD/build/bsp/drivers/vin/modules/sensor" -j2 imx519.ko
# Keep the original archived source exact; use a portable include in build only.
sed 's|"/home/onyx/linux-vin/bsp/drivers/vin/vin_test/sunxi_camera_v2.h"|"sunxi_camera_v2.h"|' source/imx519_live.c >build/imx519_live.c
gcc -O3 -fopenmp -pthread -Ibuild/bsp/drivers/vin/vin_test build/imx519_live.c -o build/imx519_live -lm
echo 'Built into build/. Shipped modules and binary were not replaced.'
