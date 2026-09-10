# IMX519 cho Orange Pi 4 Pro

**Tác giả: Lê Quốc Nam**  
**Phiên bản: Stable 20260910**

Driver, cấu hình CAM1 và chương trình xem camera Sony IMX519 autofocus trên Orange Pi 4 Pro (A733 / sun60iw2).

## Tải về

- [Bộ cài ZIP](downloads/orangepi4pro-imx519-stable-20260910.zip)
- [Bộ cài TAR.GZ](downloads/orangepi4pro-imx519-stable-20260910.tar.gz)
- [Hướng dẫn sử dụng tiếng Việt](package/HUONG_DAN_SU_DUNG_VI.md)
- [Hướng dẫn kỹ thuật, cài đặt và khôi phục](package/README_VI.md)

## Tương thích

- Orange Pi 4 Pro, camera IMX519 gắn **CAM1**, motor AK7375.
- Orange Pi OS 1.0.6 Bookworm, kernel **5.15.147-sun60iw2**, đúng build được kiểm tra trong bộ cài.
- Hiển thị HDMI 1920×1080, tốc độ quan sát khoảng 25 FPS.
- Vị trí lấy nét đã kiểm chứng: **2200**, là mã motor chứ không phải khoảng cách mm.

Đây là bản ổn định đã khôi phục trước đợt chỉnh chống xé hình. Màu sắc và binary preview được giữ nguyên; không cam kết hết xé hình khi lia nhanh. Đã kiểm tra checksum, tương thích và build trên Pi nguồn; chưa thử cài/khôi phục trên Pi sạch.

## Cài đặt

Đọc hướng dẫn trước khi thay device tree. Bộ cài sao lưu các file được thay, chỉ hỗ trợ đúng board/kernel và không tự reboot.

```bash
tar -xzf orangepi4pro-imx519-stable-20260910.tar.gz
cd orangepi4pro-imx519-stable-20260910
sudo apt install python3 mpv libgomp1 acl
sha256sum -c SHA256SUMS
python3 scripts/install.py
sudo python3 scripts/install.py --install --cam1-dtb
sudo reboot
```

Sau khi đăng nhập desktop trên Pi:

```bash
python3 /opt/orangepi4pro-imx519/scripts/preview.py
```

## Mã nguồn và bản quyền

Mã nguồn VIN nằm trong [source archive](package/source/linux-vin-source.tar.gz); mã preview và công cụ cài đặt nằm trong `package/source/` và `package/scripts/`.

Giữ nguyên thông báo tác giả và giấy phép của nguồn gốc. Driver IMX519 khai báo GPL-2.0-or-later; xem [GPL-2](package/LICENSES/GPL-2.txt) và thông báo trong từng file. Không áp dụng một giấy phép mới chung cho chương trình preview gốc.
