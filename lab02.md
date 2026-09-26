# Báo cáo Thực hành Lab 02: Giao dịch trên Blockchain Sepolia

## Bước 3 — Ghi nhận kết quả giao dịch

| Trường | Giao dịch thành công | Giao dịch thất bại |
| :--- | :--- | :--- |
| **Mã băm giao dịch** | `0xc279f4bdb082e5691af8465530c01fb1b8ffea4cde7ea08decde18c32c5a5eb3` | Không có (Giao dịch chưa được tạo mã băm do bị chặn tại ví) |
| **Số tiền chuyển** | 0.01 ETH | 0.35 SepoliaETH |
| **Phí giao dịch thực trả** | 0.000052041932397 ETH | 0 ETH (Chưa phát sóng lên mạng lưới) |
| **Trạng thái** | Thành công (Success) | Thất bại (Không thể gửi / Bị chặn ở bước xác nhận ví) |
| **Nguyên nhân (nếu thất bại)** | Không có | Không đủ số dư (Insufficient funds): Số tiền muốn gửi (0.35 SepoliaETH) cùng phí gas vượt quá số dư hiện có trong ví, MetaMask hiển thị cảnh báo đỏ tại phí mạng và khóa nút xác nhận. |

---

## Trả lời câu hỏi

**Câu hỏi:** *Nếu bạn chuyển nhầm cho người lạ, có lấy lại được không? Vì sao?*

**Trả lời:**
Nếu bạn chuyển nhầm tiền cho người lạ trên blockchain, bạn không thể tự ý lấy lại số tiền đó. Nguyên nhân là do các giao dịch trên blockchain có tính bất biến (immutability) và không thể đảo ngược một khi đã được thợ đào/validator xác thực đưa vào khối. Do bản chất phi tập trung không có ngân hàng hay bên trung gian nào có quyền can thiệp thu hồi tiền, cách duy nhất để lấy lại là liên hệ và trông đợi vào sự tự nguyện chuyển trả của người nhận.
