# IMX519 — Orange Pi 4 Pro — bản ổn định 2026-09-10

**Tác giả: Lê Quốc Nam**  
**Tài liệu sử dụng:** [Hướng dẫn sử dụng tiếng Việt](HUONG_DAN_SU_DUNG_VI.md)

Gói chụp lại đúng phiên bản trên Pi sau khi khôi phục bản trước chỉnh chống xé hình. File thực thi preview và module IMX519 được giữ nguyên byte. Không bao gồm bản thử compositor/VSync hoặc sửa sharpen sau đó.

## Phần cứng và hệ điều hành đã kiểm chứng

- Orange Pi 4 Pro, A733 / sun60iw2, aarch64.
- Orange Pi OS 1.0.6 Bookworm, kernel **5.15.147-sun60iw2**, build `#1.0.6 SMP PREEMPT Wed Nov 26 03:21:10 UTC 2025`.
- Camera Sony IMX519 autofocus, cắm **CAM1**, sensor I²C8 `0x1a`, chip ID `0x0519`; motor AK7375 tại `0x0c`.
- Preview HDMI 1920×1080; tốc độ quan sát khoảng 25 FPS, khai báo luồng 30 FPS. Không cam kết đạt 30 FPS hoặc hết xé hình khi lia nhanh.
- Vị trí lens đã được người dùng xác nhận nét: **2200**. Đây là mã motor, không phải khoảng cách mm; vật ở khoảng cách khác có thể cần giá trị khác.

Installer kiểm tra cả SHA256 `/boot/uImage` để tránh nạp module vào bản kernel trùng tên nhưng khác build. Các phiên bản kernel/board khác cần port và kiểm thử riêng.

## Thành phần

- `modules/imx519.ko`: module đang được dùng; phụ thuộc VIN có sẵn trong hệ điều hành Orange Pi.
- `bin/imx519_live`: chương trình preview nguyên bản đã khôi phục, giữ màu và xử lý ảnh hiện tại.
- `boot/*.dtb`, `boot/*.dts`: device tree CAM1 đang hoạt động; TWI8 engine mode, sensor IMX519. Đây là DTB toàn bo mạch, đồng thời vô hiệu hóa các camera port khác theo cấu hình gốc.
- `source/linux-vin-source.tar.gz`: cây mã VIN hiện tại để sửa/build driver, kèm Makefile và bản quyền. Không bao gồm `.git` hoặc các module/object đã build.
- `source/imx519_live.c`: mã preview nguyên bản.
- `scripts/`: kiểm tra/cài/khôi phục, build, chạy preview và điều khiển focus.
- `metadata/`: nguồn gốc, hash bản gốc và log FPS thực tế; `SHA256SUMS`: kiểm tra tính toàn vẹn toàn bộ gói.

Cảm biến vẫn xuất Bayer10 ở tầng phần cứng. Chương trình hiện tại demosaic và xử lý màu bằng phần mềm, rồi đưa YUV420/Y4M sang MPV; hình hiển thị là ảnh đã xử lý màu.

## Cài trên Orange Pi 4 Pro cùng bản hệ điều hành

Tắt nguồn trước khi cắm/tháo cáp camera. Sau khi bật lại và đăng nhập desktop:

```bash
tar -xzf orangepi4pro-imx519-stable-20260910.tar.gz
cd orangepi4pro-imx519-stable-20260910
sudo apt install python3 mpv libgomp1 acl
sha256sum -c SHA256SUMS
python3 scripts/install.py
sudo python3 scripts/install.py --install --cam1-dtb
sudo reboot
```

`install.py` không tham số chỉ kiểm tra, không ghi vào hệ thống. Cài đặt sao lưu từng file trước khi thay, in đường dẫn `manifest.json`; không tự dừng camera hoặc tự reboot. Nếu Pi đã có DTB CAM1 đúng và muốn giữ DTB đó, bỏ `--cam1-dtb`. Không dùng DTB này cho một hệ thống có thay đổi device tree khác mà chưa đối chiếu.

Sau reboot, chạy từ terminal của tài khoản đang đăng nhập màn hình HDMI:

```bash
python3 /opt/orangepi4pro-imx519/scripts/preview.py
```

Đóng preview/MPV cũ trước khi mở. Trình chạy xin sudo cho nạp module và cấp quyền thiết bị cho tài khoản hiện tại; không lưu mật khẩu. Để dừng, nhấn Ctrl+C ở terminal. Không tự khởi động cửa sổ camera sau đăng nhập.

## Giữ đúng focus đã kiểm chứng

Binary nguyên bản có lỗi điều khiển motor; nó ghi mã cũ 250 khi khởi động. Wrapper chờ preview hoạt động rồi gửi đúng giao thức AK7375 để đặt lens **2200**, tái hiện cách ảnh đã được xác nhận nét trước khi thử chống xé.

Log nguyên bản vẫn ghi `Focus: 250`; đó là biến trong phần mềm cũ, không phải phép đo vị trí lens. Wrapper in riêng `Physical focus set to 2200`. Không ghi 2200 vào `/tmp/imx519_focus`: vòng lặp cũ sẽ ép về 1023 và gửi sai giao thức.

Đổi vị trí lens thủ công khi camera đang chạy:

```bash
python3 /opt/orangepi4pro-imx519/scripts/focus.py 2200
```

Dải hợp lệ 0–4095. Wrapper không thay gamma, cân bằng trắng, saturation, thời gian phơi sáng hay thuật toán hiển thị của binary.

## Kiểm tra và khôi phục

```bash
uname -r
/sbin/modinfo imx519
cat /sys/bus/i2c/devices/8-001a/name
sudo dmesg | grep -E 'IMX519|imx519|0x0519'
```

Khôi phục bằng manifest được in khi cài, sau khi đóng camera:

```bash
sudo python3 scripts/install.py --rollback /var/backups/orangepi4pro-imx519/THOI_DIEM_CAI/manifest.json
sudo reboot
```

File cũ được phục hồi; file do bộ cài tạo mới được gỡ. Thư mục rỗng có thể còn lại. Gói chỉ thay `imx519.ko`; các module VIN có sẵn trong image hệ điều hành được giữ nguyên.

## Build từ mã nguồn trên Pi

```bash
sudo apt install build-essential
test -d /lib/modules/5.15.147-sun60iw2/build
bash scripts/build.sh
```

Cần bộ kernel headers/BSP đúng image, đang có sẵn trên Pi nguồn. Kết quả nằm trong `build/`, không tự cài và không thay binary đóng gói. Biên dịch lại có thể cho hash khác do compiler/options; binary đi kèm mới là bản chụp chính xác đã kiểm chứng.

## Nguồn và bản quyền

VIN upstream: https://github.com/orangepi-xunlong/linux-orangepi, commit `3de7a14a69f9e1fcbfec914c972a5398f0abd6d9`, cộng các thay đổi hiện tại trên Pi. Nguồn tham khảo giao thức motor: https://github.com/ArduCAM/IMX519_AK7375/blob/main/AK7375/ak7375.c.

Giữ nguyên thông báo tác giả/SPDX trong source; driver IMX519 khai báo GPL-2.0-or-later. Bản GPL-2 kèm trong `LICENSES/`. Chương trình preview gốc không có tuyên bố giấy phép đầy đủ trong file; gói giữ nguyên mã và tác giả hiện có, không tự gán giấy phép mới cho phần đó.

## Phạm vi xác minh bộ đóng gói

Đã kiểm chứng camera/focus trên Pi nguồn và so khớp binary với bản khôi phục. Kiểm tra checksum, cú pháp và compatibility đã đạt trên Pi nguồn. Đã build thành công cả `imx519.ko` và preview từ mã nguồn trong gói; log nằm ở `metadata/build-validation.txt`. Quy trình cài/khôi phục trên một Pi sạch chưa được chạy; đóng gói không thay hay khởi động lại camera hiện tại.
