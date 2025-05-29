# API Logger Pro

**API Logger Pro** là extension cho Burp Suite giúp ghi lại, quản lý và xuất báo cáo các request API trong quá trình pentest.

## Tính năng

- **Tự động ghi lại các request API** gửi từ Burp Repeater (theo phương thức và đường dẫn).
- **Hiển thị danh sách API** đã log với các trường thông tin: STT, ngày, method, URL, trạng thái kiểm thử bảo mật (checkbox).
- **Chỉnh sửa trạng thái kiểm thử** trực tiếp trên bảng giao diện.
- **Xuất báo cáo** ra file CSV (có thể mở bằng Excel) với đầy đủ thông tin và trạng thái kiểm thử.
- **Nạp lại dữ liệu từ file CSV** để tiếp tục làm việc.
- **Xóa toàn bộ dữ liệu** chỉ với một nút bấm ("Clear All").
- **Xóa từng dòng** đã chọn trong bảng ("Clear Selected").

## Hướng dẫn sử dụng

1. **Cài đặt extension** vào Burp Suite (Jython).
2. Thực hiện kiểm thử API với Burp Repeater, các request sẽ tự động được log vào bảng.
3. Đánh dấu trạng thái kiểm thử cho từng API bằng checkbox.
4. Sử dụng các nút:
   - **Export Report**: Xuất báo cáo ra file CSV.
   - **Load CSV**: Nạp lại dữ liệu từ file CSV đã lưu.
   - **Clear All**: Xóa toàn bộ dữ liệu khỏi bảng.
   - **Clear Selected**: Xóa dòng đang chọn khỏi bảng.
5. Mở file CSV bằng Excel để xem hoặc chỉnh sửa thêm.

## Lưu ý

- Extension này chỉ hoạt động với Burp Suite sử dụng Jython.
- File xuất ra là CSV, có thể đổi đuôi thành `.xlsx` để mở bằng Excel nhưng dữ liệu vẫn là dạng bảng CSV.
- Không hỗ trợ xuất file Excel chuẩn do hạn chế môi trường Jython.

---

Tác giả: Lê Đức Anh
Email: leducanh1503.works@gmail.com
