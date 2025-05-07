# Ứng dụng SDN và Network Virtualization trong Trường Đại học Thông minh (Smart Campus)

![Network Topology](/asset/image/final_sdn_project.png)

## Giới thiệu

Đề tài này triển khai một mô hình **Smart Campus** với quy mô nhỏ và đơn giản dựa trên công nghệ **Mạng điều khiển bằng phần mềm (SDN-Software Defined Network)** kết hợp với công nghệ **ảo hóa mạng (Network Virtualization)** nhằm tối ưu hóa quản lý hạ tầng mạng, nâng cao khả năng mở rộng, linh hoạt và đảm bảo hiệu năng trong môi trường học đường hiện đại.

---

## Kiến trúc hệ thống

Mạng được phân thành 2 mặt phẳng chính:
    
### 1. Control Plane (Mặt phẳng điều khiển)
- **Chức năng:** Điều phối hoạt động mạng, kiểm soát QoS,
- **Công nghệ sử dụng:**
    - Ryu Controller: Bộ điều khiển SDN hỗ trợ OpenFlow 1.3.
    - QoS: Điều phối chất lượng dịch vụ.
- **Giao tiếp:** Quyết định chính sách và định tuyến giũa các host trong Data Plane.

### 2. Data Plane (Mặt phẳng dữ liệu)
- **Chức năng:** Chuyển tiếp gói dữ liệu, phân phối lưu lượng giữa các tòa nhà.
- **Thành phần:**
    - Open vSwitch (OVS): Làm nhiệm vụ switching, hỗ trợ OpenFlow.
    - Một web server được viết bằng thư viện Flask của Python  dùng để mô phỏng phân biệt người dùng và kiểm tra băng thông.

---

## Mô hình mạng trong Campus

### Edge Layer (Tầng biên)
Các thiết bị và dịch vụ người dùng tại các tòa nhà:
- **Tòa nhà A (Building A - S1):** 
    - VLAN 10: Student (student_A).
    - VLAN 20: Teacher (teacher_A).
    - VLAN 30: Staff (staff_A).
- **Tòa nhà B (Building B - S2):** 
    - VLAN 10: Student (student_B).
    - VLAN 20: Teacher (teacher_B).
    - VLAN 30: Staff (staff_B).
- **Tòa nhà C:** 
    - Web Server (Server).

### Distribution Layer (Tầng phân phối)
- Mỗi tòa nhà được kết nối với một switch OVS phân phối (S1, S2, S3), đảm bảo tính linh hoạt và cô lập lưu lượng giữa các VLAN.

- Các switch hỗ trợ OpenFlow 1.3 để quản lý lưu lượng dựa trên chính sách QoS.

### Core Switch (Lõi chuyển mạch)
- Switch trung tâm (Controller - C0) đóng vai trò điều phối toàn bộ mạng.

-Controller sử dụng giao thức OpenFlow để quản lý các switch phân phối và định tuyến lưu lượng giữa các VLAN.

---

## Tính năng chính

- **Điều khiển mạng tập trung với SDN**: Quản lý toàn bộ mạng thông qua Ryu Controller.

- **Phân chia VLAN**: Cô lập lưu lượng giữa các nhóm người dùng (Student, Teacher, Staff).

- **Quản lý chất lượng dịch vụ (QoS)**: Giới hạn băng thông dựa trên VLAN.

- **Giám sát mạng theo thời gian thực**: Theo dõi trạng thái mạng và lưu lượng.

- **Trực quan hóa dữ liệu:** Giao diện web hiển thị thông tin mạng.

---

## Công nghệ sử dụng

| Thành phần              | Công nghệ / Công cụ         |
|------------------------|-----------------------------|
| SDN Controller         | Ryu                         |
| Monitoring             | Prometheus + Grafana        |
| Virtual Switch         | Open vSwitch (OVS)          |
| Protocol               | OpenFlow 1.3                |

---

## Hướng phát triển

- Triển khai trên môi trường thực tế hoặc ảo hóa (Mininet + GNS3).
- Tích hợp AI cho phân tích dữ liệu mạng.
- Hỗ trợ mô hình mạng học trực tuyến, IoT, và thiết bị di động thông minh.

---

## Thành viên nhóm

- Đinh Huỳnh Gia Bảo - 22520101
- Dương Bá Cần - 22520143
- Trần Gia Bảo - 22520117
- Nguyễn Minh Thư - 22521441

---

## Tài liệu tham khảo

- [Open vSwitch Documentation](https://docs.openvswitch.org)
- [Ryu SDN Framework](https://osrg.github.io/ryu/)
- [VXLAN RFC 7348](https://tools.ietf.org/html/rfc7348)