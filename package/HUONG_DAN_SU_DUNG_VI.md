# HƯỚNG DẪN SỬ DỤNG CAMERA IMX519 TRÊN ORANGE PI 4 PRO

**Tác giả: Lê Quốc Nam**  
**Phiên bản: Stable 20260910**  
**Ngày cập nhật: 10/09/2026**

## 1. Giới thiệu

Bộ phần mềm dùng để kết nối camera Sony IMX519 autofocus với cổng CAM1 của Orange Pi 4 Pro và xem hình trực tiếp trên màn hình HDMI.

Đây là phiên bản ổn định đã được khôi phục theo lựa chọn của người dùng, trước đợt chỉnh chống xé hình. Gói giữ cấu hình màu đã được xác nhận và cung cấp lệnh đặt vị trí lấy nét 2200.

Các chức năng chính:

- Nhận cảm biến IMX519 qua driver Linux.
- Hiển thị ảnh màu 1920 × 1080 trên màn hình HDMI.
- Điều khiển vị trí lấy nét của motor AK7375.
- Kiểm tra môi trường trước khi cài đặt.
- Sao lưu các file được thay thế và hỗ trợ khôi phục.
- Kèm mã nguồn để phát triển tiếp.

## 2. Thiết bị và hệ điều hành tương thích

| Thành phần | Yêu cầu |
| --- | --- |
| Bo mạch | Orange Pi 4 Pro, nền tảng A733 / sun60iw2 |
| Camera | Sony IMX519 autofocus, motor AK7375 |
| Cổng kết nối | CAM1 |
| Hệ điều hành đã thử | Orange Pi OS 1.0.6 Bookworm, 64 bit |
| Kernel | `5.15.147-sun60iw2`, đúng build được đóng gói |
| Màn hình | HDMI, có phiên desktop đang đăng nhập |
| Phần mềm | Python 3, MPV, libgomp1, acl |

Kiểm tra kernel bằng lệnh:

```bash
uname -r
```

Kết quả cần là `5.15.147-sun60iw2`. Bộ cài còn kiểm tra mã SHA256 của kernel để xác nhận đúng build. Chỉ trùng tên kernel chưa đủ bảo đảm tương thích.

## 3. Kết nối camera

1. Tắt hệ điều hành và ngắt nguồn Pi.
2. Gắn cáp camera vào cổng **CAM1**, đúng chiều tiếp điểm và khóa đầu nối chắc chắn.
3. Kết nối màn hình HDMI, bàn phím và chuột nếu sử dụng trực tiếp.
4. Cấp nguồn, chờ Pi khởi động và đăng nhập desktop.

Không tháo hoặc cắm cáp camera khi Pi đang có điện.

## 4. Cài đặt lần đầu

### 4.1. Chép bộ cài vào Pi

File cài đặt:

```text
orangepi4pro-imx519-stable-20260910.tar.gz
```

Trên Pi đang sử dụng, file đã được lưu tại `/home/onyx/`. Mở terminal và chạy:

```bash
cd /home/onyx
tar -xzf orangepi4pro-imx519-stable-20260910.tar.gz
cd orangepi4pro-imx519-stable-20260910
```

Nếu sử dụng tài khoản khác, chuyển đến thư mục nơi đã chép file bộ cài.

### 4.2. Cài các phần mềm cần thiết

```bash
sudo apt update
sudo apt install python3 mpv libgomp1 acl
```

Nhập mật khẩu tài khoản trên Pi khi được yêu cầu. Bộ cài không lưu mật khẩu.

### 4.3. Kiểm tra bộ cài và khả năng tương thích

```bash
sha256sum -c SHA256SUMS
python3 scripts/install.py
```

Các file phải báo `OK`. Khi môi trường phù hợp, chương trình kiểm tra sẽ báo `PASS`. Bước này chỉ đọc thông tin, chưa cài driver.

Nếu báo khác board, khác kernel build hoặc thiếu thư viện, xử lý lỗi đó trước khi cài tiếp.

### 4.4. Cài driver và cấu hình CAM1

Đóng cửa sổ camera trước khi cài:

```bash
sudo python3 scripts/install.py --install --cam1-dtb
```

Lưu lại đường dẫn `manifest.json` được in ra. Đây là thông tin để khôi phục file cũ nếu cần.

Tùy chọn `--cam1-dtb` cài toàn bộ device tree đã thử trên Pi nguồn. Cấu hình này dành cho CAM1 và vô hiệu hóa các camera port khác theo bản đã đóng gói. Nếu hệ thống có thay đổi device tree riêng, cần đối chiếu trước khi thay.

Nếu Pi đã có đúng cấu hình CAM1 và muốn giữ device tree hiện tại, dùng:

```bash
sudo python3 scripts/install.py --install
```

Sau khi cài thành công:

```bash
sudo reboot
```

**Pi đang chạy đúng phiên bản này không cần cài lại chỉ để xem camera.** Bộ đóng gói chưa được cài vào `/opt/` trên Pi nguồn; đường dẫn `/opt/` trong các mục tiếp theo có sau khi chạy bộ cài. Có thể chạy từ thư mục đã giải nén theo mục 5.2.

## 5. Mở và đóng camera

### 5.1. Mở camera sau khi đã cài bộ phần mềm

Đăng nhập desktop trên Pi, mở terminal bằng tài khoản người dùng thường và chạy:

```bash
python3 /opt/orangepi4pro-imx519/scripts/preview.py
```

Chương trình hiển thị camera toàn màn hình HDMI và đặt vị trí lens về **2200** sau khi camera khởi động. Trong lúc mở, chương trình có thể yêu cầu sudo để nạp module và cấp quyền thiết bị; không chạy toàn bộ lệnh bằng `sudo`.

### 5.2. Mở từ bộ đã giải nén trên Pi nguồn

Khi driver và CAM1 đã hoạt động trên Pi nguồn, có thể dùng:

```bash
cd /home/onyx/orangepi4pro-imx519-stable-20260910
python3 scripts/preview.py
```

Đóng camera/MPV đang chạy trước khi dùng lệnh này. Gói không tự mở thêm một camera khi phát hiện tiến trình cũ.

### 5.3. Mở qua SSH

Từ máy tính cùng mạng:

```bash
ssh onyx@192.168.0.170
```

Sau khi đăng nhập, nếu đã cài bộ phần mềm:

```bash
DISPLAY=:0 XAUTHORITY=/home/onyx/.Xauthority python3 /opt/orangepi4pro-imx519/scripts/preview.py
```

Ảnh xuất hiện trên **màn hình HDMI của Pi**, không phải trong cửa sổ SSH. Cần có phiên desktop của tài khoản `onyx` trên màn hình đó. Nếu địa chỉ IP hoặc tài khoản thay đổi, thay chúng trong lệnh.

### 5.4. Đóng camera

Trong terminal đã mở camera, nhấn **Ctrl+C** và chờ chương trình dừng. Đóng cửa sổ MPV còn lại nếu có trước khi mở lần tiếp theo.

Bộ cài nạp module khi khởi động hệ thống, nhưng không tự mở cửa sổ xem camera sau khi đăng nhập.

## 6. Sử dụng chức năng lấy nét

Vị trí **2200** đã được người dùng xác nhận nét trong cảnh thử. Đây là mã điều khiển motor, **không phải 2200 mm hoặc khoảng cách 2,2 m**. Khi thay khoảng cách từ vật đến camera, có thể cần chỉnh lại.

Đặt lại focus khi camera đang chạy:

```bash
python3 /opt/orangepi4pro-imx519/scripts/focus.py 2200
```

Nếu đang dùng trực tiếp bộ giải nén, mở terminal thứ hai:

```bash
cd /home/onyx/orangepi4pro-imx519-stable-20260910
python3 scripts/focus.py 2200
```

Dải điều khiển hợp lệ là **0–4095**. Có thể thử từng bước nhỏ quanh 2200, quan sát chữ hoặc cạnh vật thể rồi chọn vị trí rõ nhất. Không cần thay đổi nếu ảnh đang nét.

Muốn mở camera với một vị trí khác, ví dụ 2100:

```bash
python3 /opt/orangepi4pro-imx519/scripts/preview.py --focus 2100
```

Bộ chạy hiện tại đặt focus cố định, không tự lấy nét liên tục khi khoảng cách thay đổi.

**Lưu ý về log:** chương trình preview nguyên bản có thể vẫn in `Focus: 250`. Bộ chạy đặt lens bằng lệnh riêng sau khi mở và in `Physical focus set to 2200`. Con số trong log cũ không phản ánh vị trí lens đã đặt bằng lệnh riêng. Không dùng file `/tmp/imx519_focus` hoặc các lệnh focus cũ ngoài gói để chỉnh lens.

## 7. Kiểm tra khi không thấy hình

Chạy lần lượt:

```bash
uname -r
/sbin/modinfo imx519
ls -l /dev/video0 /dev/i2c-8
cat /sys/bus/i2c/devices/8-001a/name
sudo dmesg | grep -E 'IMX519|imx519|0x0519'
```

Trong cấu hình đã thử, tên cảm biến là `imx519`, chip ID trong log là `0x0519`. Việc có `/dev/video0` riêng lẻ chưa đủ xác nhận camera hoạt động; cần đối chiếu log nhận cảm biến và thử preview.

| Hiện tượng | Cách xử lý |
| --- | --- |
| `No such file` tại `/opt/orangepi4pro-imx519` | Chưa cài bộ phần mềm; cài theo mục 4 hoặc dùng đường dẫn bộ giải nén ở mục 5.2. |
| Báo camera/MPV đang chạy | Đóng tiến trình xem cũ trước khi mở lại. Có thể kiểm tra bằng `pgrep -a -x imx519_live` và `pgrep -a -x mpv`. |
| `Permission denied` khi chỉnh focus | Mở camera qua `preview.py` để chương trình cấp quyền thiết bị cho tài khoản hiện tại; kiểm tra gói `acl` đã cài. |
| Không tìm thấy `/dev/video0` | Kiểm tra cài module, reboot sau cài đặt và đọc log kernel. |
| Không nhận chip ID `0x0519` | Tắt nguồn rồi kiểm tra cổng CAM1, cáp và chiều tiếp điểm; kiểm tra DTB đã cài đúng. |
| Có kết nối SSH nhưng không hiện cửa sổ | Kiểm tra màn hình HDMI và phiên desktop đang đăng nhập; tham khảo lệnh mục 5.3. |
| Ảnh mờ sau khi thay vị trí camera/vật | Đặt lại 2200; nếu khoảng cách đã thay đổi, chỉnh từng bước nhỏ và quan sát. |
| Log vẫn ghi `Focus: 250` | Xem giải thích tại mục 6; dùng lệnh focus của bộ đóng gói. |
| Ảnh bị xé hoặc nhòe khi lia nhanh | Đây là giới hạn còn lại của bản ổn định đã chọn; bộ này không chứa các thay đổi thử nghiệm chống xé. |

## 8. Khôi phục sau khi cài

Đóng camera, vào thư mục bộ cài và tìm manifest:

```bash
ls /var/backups/orangepi4pro-imx519/
```

Dùng đúng đường dẫn đã được in khi cài; thay `THOI_DIEM_CAI` bằng thư mục thực tế:

```bash
sudo python3 scripts/install.py --rollback /var/backups/orangepi4pro-imx519/THOI_DIEM_CAI/manifest.json
sudo reboot
```

Thao tác phục hồi các file trước lần cài tương ứng và gỡ các file mới do lần cài đó tạo ra. Giữ lại bộ cài và thư mục backup nếu muốn có khả năng khôi phục.

## 9. Tóm tắt các lệnh thường dùng

| Nhu cầu sau khi cài | Lệnh |
| --- | --- |
| Mở camera, focus 2200 | `python3 /opt/orangepi4pro-imx519/scripts/preview.py` |
| Đặt focus 2200 khi đang xem | `python3 /opt/orangepi4pro-imx519/scripts/focus.py 2200` |
| Mở với focus tùy chọn | `python3 /opt/orangepi4pro-imx519/scripts/preview.py --focus 2100` |
| Kiểm tra kernel | `uname -r` |
| Xem thông tin driver | `/sbin/modinfo imx519` |
| Dừng camera | Ctrl+C trong terminal đã mở camera |

## 10. Ghi chú phiên bản và nguồn gốc

Ảnh hiển thị đã được xử lý màu. Bayer10 vẫn là định dạng ở tầng cảm biến; chương trình chuyển dữ liệu thành ảnh màu để hiển thị. Không cần chỉnh lại màu khi sử dụng theo hướng dẫn này.

Gói đã qua kiểm tra checksum, tương thích và biên dịch lại module/preview trên Pi nguồn. Chưa thử toàn bộ quá trình cài và khôi phục trên một Pi sạch. Các thông số và file gốc nằm trong `metadata/`; hướng dẫn build và nguồn mã chi tiết nằm trong `README_VI.md`.

**Tác giả: Lê Quốc Nam.** Thông báo bản quyền và giấy phép của các thành phần nguồn gốc được giữ trong mã nguồn và thư mục `LICENSES/`.
