# Ứng dụng SDN và Network Virtualization trong Trường Đại học Thông minh (Smart Campus)

![Network Topology](/asset/image/sdn-and-nv-final-draft.png)

## Giới thiệu

Đề tài này triển khai một mô hình **Smart Campus** dựa trên công nghệ **Mạng điều khiển bằng phần mềm (SDN)** kết hợp với **ảo hóa mạng (Network Virtualization)** nhằm tối ưu hóa quản lý hạ tầng mạng, nâng cao khả năng giám sát, bảo mật, và hiệu năng trong môi trường học đường hiện đại.

---

## Kiến trúc hệ thống

Mạng được phân thành 3 mặt phẳng chính:

### 1. Management Plane (Mặt phẳng quản lý)
- **Chức năng:** Giám sát, trực quan hóa dữ liệu, giao tiếp với hệ thống quản lý đám mây thông qua API.
- **Công nghệ sử dụng:**
    - Grafana/Prometheus: Giám sát lưu lượng, hiệu năng.
    - Flask + HTML5: Giao diện web trực quan.
    
### 2. Control Plane (Mặt phẳng điều khiển)
- **Chức năng:** Điều phối hoạt động mạng, kiểm soát QoS, phát hiện mối đe dọa.
- **Công nghệ sử dụng:**
    - Ryu Controller: Bộ điều khiển SDN hỗ trợ OpenFlow 1.3.
    - QoS: Điều phối chất lượng dịch vụ.
    - Suricata: Phát hiện tấn công và bất thường mạng.
- **Giao tiếp:** Giao tiếp với Management Plane thông qua Northbound API.

### 3. Data Plane (Mặt phẳng dữ liệu)
- **Chức năng:** Chuyển tiếp gói dữ liệu, phân phối lưu lượng giữa các tòa nhà.
- **Thành phần:**
    - Open vSwitch (OVS): Làm nhiệm vụ switching, hỗ trợ OpenFlow.
    - VXLAN: Tầng ảo hóa mạng (Overlay Network) dùng để kết nối liên tòa nhà qua lớp hạ tầng vật lý.

---

## Mô hình mạng trong Campus

### ● Edge Layer (Tầng biên)
Các thiết bị và dịch vụ người dùng tại các tòa nhà:
- **Tòa nhà A:** Lớp học, phòng máy tính.
- **Tòa nhà B:** Thư viện, phòng tài chính, phòng hiệu trưởng.
- **Tòa nhà C:** Văn phòng giảng viên, phòng họp.
- **Tòa nhà D:** Web server.

### ● Distribution Layer (Tầng phân phối)
- Mỗi tòa nhà được kết nối với một switch OVS phân phối, đảm bảo tính linh hoạt và cô lập lưu lượng.

### ● Core Switch (Lõi chuyển mạch)
- Switch OVS trung tâm hỗ trợ OpenFlow 1.3 và VXLAN để quản lý phân phối lưu lượng giữa các node mạng.

---

## Kết nối ra Internet

- Core switch có kết nối trực tiếp với Internet để đảm bảo truy cập từ các máy trạm và dịch vụ như Web Server.

---

## Tính năng chính

- **Điều khiển mạng tập trung với SDN**
- **Ảo hóa mạng với VXLAN**
- **Giám sát mạng theo thời gian thực**
- **Quản lý chất lượng dịch vụ (QoS)**
- **Phát hiện tấn công mạng (IDS)**
- **Trực quan hóa dữ liệu và quản lý thông qua giao diện web**

---

## Công nghệ sử dụng

| Thành phần              | Công nghệ / Công cụ         |
|------------------------|-----------------------------|
| SDN Controller         | Ryu                         |
| Monitoring             | Prometheus + Grafana        |
| Threat Detection       | Suricata                    |
| Visualization Web      | Flask + HTML/CSS            |
| Virtual Switch         | Open vSwitch (OVS)          |
| Network Overlay        | VXLAN                       |
| Protocol               | OpenFlow 1.3                |

---

## Hướng phát triển

- Triển khai trên môi trường thực tế hoặc ảo hóa (Mininet + GNS3).
- Tích hợp AI cho phân tích dữ liệu mạng.
- Hỗ trợ mô hình mạng học trực tuyến, IoT, và thiết bị di động thông minh.

---

## Thành viên nhóm

- [Tên thành viên 1]
- [Tên thành viên 2]
- [Tên thành viên 3]

---

## Tài liệu tham khảo

- [Open vSwitch Documentation](https://docs.openvswitch.org)
- [Ryu SDN Framework](https://osrg.github.io/ryu/)
- [Suricata IDS](https://suricata.io)
- [VXLAN RFC 7348](https://tools.ietf.org/html/rfc7348)
