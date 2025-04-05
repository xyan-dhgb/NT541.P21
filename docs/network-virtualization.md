# Ảo Hóa Mạng (Network Virtualization)

## Vấn Đề

- **Sự phát triển của ảo hóa mạng**:
  - Xuất hiện sau ảo hóa máy tính (compute virtualization) và được thúc đẩy bởi nó.
  - Ảo hóa máy tính loại bỏ cấu hình máy chủ thủ công, làm lộ rõ hạn chế của cấu hình mạng thủ công.

- **Hạn chế của cấu hình mạng thủ công**:
  - Tốn thời gian, trở thành "rào cản" trong việc cung cấp dịch vụ đám mây.
  - Ví dụ: Di chuyển máy ảo (virtual machine migration) làm nổi bật hạn chế khi địa chỉ IP cần giữ nguyên.

- **Nhu cầu tự động hóa**:
  - Ban đầu được nhận ra bởi các nhà cung cấp dịch vụ đám mây lớn.
  - Trở thành xu hướng phổ biến trong các trung tâm dữ liệu doanh nghiệp.

- **Lợi ích của ảo hóa mạng**:
  - Đơn giản hóa và tự động hóa việc cấp phát tài nguyên mạng.
  - Tích hợp các dịch vụ bảo mật (tường lửa, kiểm tra gói tin sâu) ngay từ đầu.
  - Cô lập tài nguyên mạng, giảm nguy cơ tấn công và hạn chế lan rộng.

- **Ví dụ thực tế**:
  - Doanh nghiệp tạo mạng ảo riêng cho từng bộ phận (tài chính, nhân sự, kỹ thuật) để cô lập tài nguyên và tăng cường bảo mật.

---

## Microsegmentation (Phân Đoạn Vi Mô)

- **Khái niệm**:
  - Tạo các mạng con biệt lập (microsegment) với độ chi tiết cao.
  - Thiết kế riêng theo nhu cầu của từng nhóm tiến trình trong ứng dụng phân tán.

- **Lợi ích**:
  - Giảm bề mặt tấn công.
  - Hạn chế sự lan rộng của các cuộc tấn công trong doanh nghiệp hoặc trung tâm dữ liệu.

- **Ví dụ thực tế**:
  - Ứng dụng thương mại điện tử:
    - Microsegment cho xử lý thanh toán, quản lý đơn hàng, giao diện người dùng.
    - Nếu một microsegment bị tấn công, các microsegment khác vẫn an toàn.

---

## Định Nghĩa

- **Ảo hóa mạng (Network Virtualization)**:
  - Tạo nhiều mạng ảo trên cùng một hạ tầng mạng vật lý.
  - Trừu tượng hóa và cô lập tài nguyên mạng (switch, router, liên kết mạng).
  - Các mạng ảo hoạt động như trên phần cứng vật lý riêng biệt.

- **Ví dụ thực tế**:
  - Trung tâm dữ liệu tạo mạng ảo riêng cho từng khách hàng, đảm bảo dữ liệu không bị can thiệp.

---

## Kiến Trúc

- **Thành phần cơ bản**:
  - **Virtual switch (switch ảo)**: Nằm trên máy chủ đầu cuối, nơi các máy ảo (VMs) kết nối.
  - **Network virtualization controller**:
    - Cung cấp **northbound API** để nhận yêu cầu cấu hình mạng ảo.
    - Ví dụ: "VM1 và VM2 nằm trên cùng một subnet ảo lớp 2, mạng X".

- **Đặc điểm**:
  - Địa chỉ IP của máy ảo độc lập với mạng vật lý (underlay network).
  - Sử dụng encapsulation (VXLAN, NVGRE) để tách biệt không gian địa chỉ mạng ảo khỏi mạng vật lý.

- **Ví dụ thực tế**:
  - Khi một máy ảo giao tiếp với máy ảo khác trong cùng mạng ảo, bộ điều khiển cung cấp thông tin ánh xạ (mapping) để định tuyến chính xác.

---

## Mạng Ảo (Virtual Networks)

- **Khái niệm**:
  - Trừu tượng logic của hạ tầng mạng vật lý.
  - Tạo môi trường mạng độc lập, cô lập trong một mạng vật lý chia sẻ.

- **Đặc điểm**:
  - Mỗi mạng ảo có địa chỉ, chính sách, và cấu hình riêng.
  - Sử dụng chung tài nguyên mạng vật lý.

- **Ví dụ thực tế**:
  - Công ty cung cấp dịch vụ đám mây tạo mạng ảo riêng cho từng khách hàng, đảm bảo dữ liệu và lưu lượng mạng không bị can thiệp.

---

## Các Thành Phần: Management, Control, và Data Plane

1. **Management Plane (Mặt phẳng quản lý)**:
   - Cấu hình và quản lý cấp cao của mạng ảo.
   - Cung cấp API và giao diện người dùng để định nghĩa topology, chính sách, và dịch vụ mạng ảo.
   - Xử lý cấp phát mạng ảo, giám sát, và quản lý vòng đời.

2. **Control Plane (Mặt phẳng điều khiển)**:
   - Kiểm soát logic và ra quyết định cho mạng ảo.
   - Xác định hành vi chuyển tiếp và chính sách mạng.
   - Giao tiếp với data plane để cài đặt quy tắc và cấu hình chuyển tiếp.
   - Duy trì trạng thái mạng logic (topology, ánh xạ địa chỉ, định nghĩa dịch vụ).

3. **Data Plane (Mặt phẳng dữ liệu)**:
   - Chuyển tiếp và xử lý lưu lượng mạng trong môi trường mạng ảo.
   - Thực hiện logic chuyển tiếp và chính sách do control plane định nghĩa.
   - Xử lý encapsulation/decapsulation, chuyển mạch ảo (virtual switching), và định tuyến ảo (virtual routing).
   - Được triển khai trên hypervisor hoặc thiết bị mạng chuyên dụng.

- **Ví dụ thực tế**:
  - Trong trung tâm dữ liệu lớn:
    - Management plane định nghĩa chính sách bảo mật.
    - Control plane thực thi chính sách.
    - Data plane xử lý lưu lượng mạng theo chính sách.