# Giao thức VXLAN 

## VXLAN là gì?

- **VXLAN (Virtual Extensible LAN)** là một giao thức **tunnel-based** được thiết kế để **mở rộng mạng Layer 2 (Ethernet)** qua **mạng Layer 3 (IP)**.

- Được chuẩn hóa trong [RFC 7348](https://datatracker.ietf.org/doc/html/rfc7348).

- **Mục tiêu**: Cho phép tạo ra nhiều mạng ảo (Virtual Network) độc lập chạy trên cùng một hạ tầng vật lý mà không bị giới hạn bởi số lượng VLAN truyền thống.

## Vì sao cần VXLAN?

### Hạn chế của VLAN truyền thống:

- Mạng Layer 2 mở rộng bị giới hạn về quy mô do số VLAN chỉ có tối đa 4096 ID (12-bit).

- Mạng vật lý khó linh hoạt khi muốn di chuyển VM (virtual machine) giữa các rack, data center, hay cloud khác nhau.

- VLAN bị phụ thuộc chặt vào topology vật lý.

### VXLAN giải quyết:
- Hỗ trợ tới **16 triệu mạng ảo** với VNI (VXLAN Network Identifier) 24-bit.

- **Decouple Layer 2 khỏi Layer 3**: chạy mạng ảo L2 xuyên suốt qua mạng vật lý L3/IP.

- Dễ dàng mở rộng, cô lập và di chuyển VM mà không cần thay đổi cấu trúc mạng vật lý.

## Cách hoạt động của VXLAN (Overlay Network)

VXLAN sử dụng mô hình **Overlay Network** với 2 thành phần chính:

| Thành phần     | Vai trò                                                                 |
|----------------|-------------------------------------------------------------------------|
| **VTEP**        | (VXLAN Tunnel Endpoint): Thiết bị thực hiện encapsulate/decapsulate VXLAN |
| **Underlay**    | Mạng vật lý IP (Layer 3) – truyền tải các gói VXLAN đã được encapsulated   |

### Cơ chế Encapsulation:
1. Gói Ethernet từ VM được **bọc trong UDP**.

2. Gói UDP mang địa chỉ IP của **VTEP đích**, truyền qua mạng IP.

3. VTEP bên kia **bóc gói**, trả về gói Ethernet gốc cho VM đích.

> [!NOTE]
>  VXLAN sử dụng **UDP port 4789**.

## VXLAN "Decouple" khỏi mạng vật lý như thế nào?

| Trước VXLAN                             | Với VXLAN                                                      |
|----------------------------------------|----------------------------------------------------------------|
| Mạng ảo bị gắn chặt với thiết bị vật lý | Mạng ảo hoạt động **độc lập với mạng vật lý**                  |
| Phải cấu hình VLAN trên từng switch    | VXLAN hoạt động trên **mạng IP tiêu chuẩn**                   |
| Di chuyển VM gặp rào cản địa lý        | VM có thể **di chuyển tự do** mà không thay đổi cấu trúc mạng |

> **Decouple** nghĩa là VXLAN **không cần mạng vật lý hiểu về mạng ảo**, chỉ cần mạng IP có thể truyền UDP là đủ.

## Lợi ích của VXLAN

- Cho phép **nhiều mạng ảo độc lập** chạy trên cùng một mạng vật lý.

- **Không bị giới hạn 4096 VLAN** như trước (VXLAN hỗ trợ ~16 triệu VNI).

- Mạng vật lý **không cần biết** chi tiết mạng logic bên trong.

- **Tách biệt (decouple)** hoàn toàn cấu trúc mạng logic khỏi mạng vật lý.

## Ứng dụng thực tế của VXLAN

- **Data Center (Leaf-Spine)**: VXLAN phân tách các tenant logic.

- **SDN và NFV**: VXLAN thường dùng làm cơ sở cho network slicing, traffic isolation.

- **Multi-tenant Cloud**: AWS, Azure, OpenStack… dùng VXLAN để cô lập traffic giữa khách hàng.

- **Kubernetes CNI Plugins**: Một số plugin (Flannel, Calico) dùng VXLAN để tạo overlay network.

## Ví dụ:

### Tình huống: Gửi thư trong tòa nhà văn phòng

Hãy tưởng tượng chúng ta làm việc trong một tòa nhà văn phòng lớn, nơi có nhiều công ty thuê không gian. Tất cả công ty đều dùng chung hệ thống chuyển thư nội bộ. Bạn muốn gửi thư đến đồng nghiệp ở công ty khác tầng, nhưng đảm bảo thư đến **đúng người, đúng công ty**, không bị lạc.

### So sánh giữa VLAN và VXLAN

- Cách truyền thống: VLAN

    - Mỗi công ty dùng **một màu phong bì riêng** để phân biệt (vàng cho công ty A, xanh cho công ty B…).

    - Tuy nhiên, hệ thống chỉ hỗ trợ tối đa **4096 màu** (giới hạn VLAN ID).

    - Các tầng (switch) **phải biết và hỗ trợ màu đó** ⇒ khó mở rộng, dễ xung đột.

-  Cách hiện đại: VXLAN

    - Mỗi công ty sử dụng **mã số riêng (VNI)**, ví dụ:
        - Công ty A: VNI 500001
        - Công ty B: VNI 500002

    - Thư được đặt trong phong bì trắng tiêu chuẩn, ghi:
        - **Người nhận**: Cô Lan, tầng 8 (IP của VTEP đích)
        - **Mã công ty**: VNI 500001

    - Nhân viên giao nhận (VTEP) chỉ cần:
        - Đọc địa chỉ tầng (IP)
        - Giao thư dựa trên mã công ty (VNI)

    - Thư gốc được giữ nguyên bên trong, không cần hệ thống chuyển phát hiểu chi tiết.

### Phép tương đương kỹ thuật

| Thành phần trong ví dụ | Trong VXLAN thực tế            |
|------------------------|-------------------------------|
| Công ty                | Mạng ảo (VXLAN Virtual Network) |
| Tòa nhà văn phòng      | Hạ tầng mạng vật lý (Underlay) |
| Mã công ty             | VXLAN Network Identifier (VNI) |
| Nhân viên giao thư     | VTEP (VXLAN Tunnel Endpoint)    |
| Phong bì ngoài         | Gói VXLAN bọc trong UDP/IP      |
| Thư bên trong          | Gói dữ liệu Ethernet gốc        |

### Kết luận

- Ví dụ gửi thư này giúp hình dung rõ cách VXLAN hoạt động: 
    - **Mỗi mạng ảo là một công ty**
    - **Hệ thống chuyển phát là mạng IP vật lý**
    - **Thông tin định tuyến nằm trong "phong bì ngoài" – không ảnh hưởng thư gốc**

- Với VXLAN, bạn có thể xây dựng mạng linh hoạt, mở rộng và dễ quản lý hơn bao giờ hết.

## Tóm tắt nhanh

- **VXLAN = mạng ảo (Layer 2) chạy trên mạng vật lý IP (Layer 3)**.

- Cho phép cô lập traffic giữa các tenant bằng VNI (giống VLAN nhưng lớn hơn nhiều).

- Giúp tăng tính **mở rộng, linh hoạt, di động** cho hệ thống mạng hiện đại.

