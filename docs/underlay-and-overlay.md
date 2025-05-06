# Tổng quan về Underlay và Overlay trong Network Virtualization

Đây là lý thuyết được tìm hiểu và nghiên cứu nhằm phục vụ cho đồ án môn học.

## I. Giới thiệu chung

Trong **ảo hóa mạng (Network Virtualization)**, chúng ta thường gặp hai khái niệm cơ bản là **underlay** và **overlay**. Việc hiểu rõ sự khác biệt giữa chúng giúp triển khai hệ thống mạng linh hoạt, dễ mở rộng và dễ quản lý hơn trong các môi trường như **cloud**, **data center**, và **SDN**.

## II. Underlay Network

### Khái niệm:

- Là **mạng vật lý** thật sự, gồm các thiết bị như **router, switch, cáp mạng, IP thật**.

- Là nền tảng để các mạng overlay có thể hoạt động.

- Giao tiếp sử dụng các **giao thức định tuyến truyền thống** như:

  - OSPF (Open Shortest Path First)

  - BGP (Border Gateway Protocol)
  
  - IS-IS (Intermediate System to Intermediate System)

### Vai trò:

- Đảm bảo **định tuyến và truyền dẫn dữ liệu vật lý** giữa các thiết bị trong hệ thống.

- Chịu trách nhiệm vận chuyển gói tin giữa các điểm **mạng thực tế**.

### Ví dụ:

- Hệ thống các router và switch kết nối trung tâm dữ liệu A và B thông qua mạng WAN là underlay network.

## III. Overlay Network

### Khái niệm:

- Là **mạng logic (ảo)** được xây dựng **trên nền underlay**.

- Cho phép các thiết bị ở xa nhau **giao tiếp như thể nằm trong cùng một mạng LAN**.

- Dùng các kỹ thuật như:

  - **VXLAN (Virtual Extensible LAN)**

  - **GRE (Generic Routing Encapsulation)**

  - **NVGRE (Network Virtualization using Generic Routing Encapsulation)**
  
  - **GENEVE (Generic Network Virtualization Encapsulation)**

### Vai trò:

- Tạo ra các mạng logic linh hoạt, dễ quản lý.

- Giúp **trừu tượng hóa cấu trúc vật lý**, tách biệt mạng ứng dụng với hạ tầng vật lý bên dưới.

- Hỗ trợ **multi-tenancy** (nhiều người dùng dùng chung hạ tầng mà không ảnh hưởng lẫn nhau).

### Cơ chế hoạt động:

- Gói tin của mạng ảo được **đóng gói (encapsulate)** vào trong gói tin của underlay để truyền đi.

- Ví dụ: Một gói tin VXLAN sẽ được bọc trong UDP/IP trước khi truyền qua Internet.

## IV. Minh Họa Thực Tế

### Tình huống:

- **VM1 ở Hà Nội**, **VM2 ở TP.HCM**
- Muốn hai máy nằm trong cùng một subnet: `192.168.10.0/24`
- Dùng **VXLAN** để tạo overlay

### Mô tả:

| Thành phần     | Vai trò                       |
|----------------|-------------------------------|
| Underlay       | Mạng vật lý kết nối 2 DC      |
| Overlay        | VXLAN tunnel giữa VM1 và VM2  |
| IP VM1         | 192.168.10.10                 |
| IP VM2         | 192.168.10.20                 |

>[!NOTE] 
> VM1 gửi gói đến VM2, gói đó được **bọc trong gói VXLAN** và truyền qua mạng vật lý.

## V. So Sánh Underlay và Overlay

| Tiêu chí         | Underlay                          | Overlay                           |
|------------------|------------------------------------|------------------------------------|
| Loại mạng        | Vật lý                             | Logic (ảo)                         |
| Thành phần       | Router, Switch, cáp mạng           | VXLAN, Tunnel, vSwitch             |
| Giao thức        | IP, OSPF, BGP, IS-IS               | VXLAN, GRE, GENEVE                 |
| Mục tiêu         | Truyền dữ liệu vật lý              | Kết nối logic giữa các máy ảo     |
| Tính linh hoạt   | Thấp (phụ thuộc thiết bị vật lý)   | Cao (triển khai nhanh, mở rộng)   |
| Tính mở rộng     | Bị giới hạn bởi thiết bị vật lý     | Mở rộng dễ dàng, theo nhu cầu     |

---

## VI. Một số lưu ý khi triển khai

- Underlay cần **ổn định, băng thông đủ mạnh** để đảm bảo hiệu năng cho overlay.

- Overlay giúp **đơn giản hóa quản trị mạng**, nhất là trong mô hình Data Center lớn hoặc Cloud.

- Overlay có thể **kết hợp với SDN** để tăng khả năng lập trình và tự động hóa mạng.

## VII. Kết luận

- **Underlay và Overlay** không thay thế nhau mà **bổ sung cho nhau** trong việc xây dựng mạng hiện đại.

- Sử dụng overlay giúp giải quyết bài toán **tách biệt logic mạng và vật lý**, hỗ trợ **multi-tenant**, mở rộng linh hoạt và triển khai nhanh chóng.
