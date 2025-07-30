# NSKBot - Selenium Automation Bot

**NSK** là một bộ công cụ tự động hóa (RPA) được phát triển để hỗ trợ các quy trình làm việc của **NSK**. Dự án này sử dụng Python và Selenium để thao tác với các nền tảng nội bộ như SharePoint, Web Access và Mail Dealer.

## 🛠 Yêu cầu Hệ thống

- Python **3.12+** 
- Chrome browser
- ChromeDriver
- Các thư viện dependencies trong `pyproject.toml`

## 📦 Cài đặt

```bash
pip install nsk
```

Hoặc sử dụng uv (khuyến nghị):
```bash
uv pip install nsk
```

## 🚀 Các chức năng hỗ trợ

### WebAccess Bot
- Lấy danh sách đơn hàng với các bộ lọc:
  - Tên công trình
  - Thời gian giao hàng
  - Nhà máy sản xuất 
  - Loại bản vẽ
- Cập nhật thông tin đơn hàng

### SharePoint Bot 
- Xác thực Microsoft 365
- Tải file từ SharePoint
- Lấy thông tin file/folder
- Quản lý document library

### Mail Dealer Bot
- Gửi email với file đính kèm
- Quản lý email template

### Dandoli Bot
- Tự động xác thực
- Lấy thông tin công trình
- Quản lý mã công trình

## 📄 License

MIT License