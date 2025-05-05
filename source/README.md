# Custom Mininet Topology with VLAN Mapping

## Mô tả Topology

Topology này được xây dựng bằng Python sử dụng thư viện Mininet, gồm:

- **4 switch**: `s1`, `s2`, `s3`, `s4`
- **16 host**: mỗi switch kết nối với 4 host
- **Liên kết giữa các switch**:
  - `s1 <-> s2`
  - `s2 <-> s3`
  - `s3 <-> s4`

### Tốc độ và độ trễ các liên kết:
- Host <-> Switch: `10 Mbps`, `1ms`
- Switch <-> Switch: `20 Mbps`, `2ms`

---

## Cấu trúc IP và MAC

Mỗi host được gán:
- IP: `10.0.0.X/24`
- MAC: `00:00:00:00:00:XX`, với `XX` là số hex tương ứng với số thứ tự của host

---

## Phân chia VLAN theo MAC Address

Topology này sử dụng bảng ánh xạ MAC-to-VLAN như sau:

### VLAN 10
- `00:00:00:00:00:01` (h1 - s1)
- `00:00:00:00:00:05` (h5 - s2)
- `00:00:00:00:00:09` (h9 - s3)
- `00:00:00:00:00:0d` (h13 - s4)

### VLAN 20
- `00:00:00:00:00:02` (h2 - s1)
- `00:00:00:00:00:06` (h6 - s2)
- `00:00:00:00:00:0a` (h10 - s3)
- `00:00:00:00:00:0e` (h14 - s4)

### VLAN 30
- `00:00:00:00:00:03` (h3 - s1)
- `00:00:00:00:00:07` (h7 - s2)
- `00:00:00:00:00:0b` (h11 - s3)
- `00:00:00:00:00:0f` (h15 - s4)

### VLAN 40
- `00:00:00:00:00:04` (h4 - s1)
- `00:00:00:00:00:08` (h8 - s2)
- `00:00:00:00:00:0c` (h12 - s3)
- `00:00:00:00:00:10` (h16 - s4)

---

## 🎮 Cách chạy topology

1. Cài đặt Mininet (nếu chưa có).
2. Chạy file Python:
   ```bash
   sudo python3 topo.py

