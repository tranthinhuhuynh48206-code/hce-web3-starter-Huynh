# Báo Cáo Phân Tích Pháp Y Dữ Liệu Giao Dịch (Blockchain Transaction Forensics)

**Mã băm giao dịch (Transaction Hash):**  
`0xc279f4bdb082e5691af8465530c01fb1b8ffea4cde7ea08decde18c32c5a5eb3`  
**Mạng thử nghiệm:** Ethereum Sepolia Testnet  
**Liên kết Etherscan:** [Xem trên Sepolia Etherscan](https://sepolia.etherscan.io/tx/0xc279f4bdb082e5691af8465530c01fb1b8ffea4cde7ea08decde18c32c5a5eb3)

---

## Bảng Chi Tiết Các Trường Giao Dịch

| Trường (Field) | Giá trị thực tế trên Sepolia | Ý nghĩa kỹ thuật | Vì sao người làm nghiệp vụ cần |
| :--- | :--- | :--- | :--- |
| **Status** | **Success** (Thành công - `0x1`) | Trạng thái thực thi của giao dịch: thành công (`Success / 1`) hoặc thất bại (`Failed / Reverted / 0`). | **Giao dịch thất bại vẫn bị trừ phí gas.** Kế toán/kiểm toán cần đối soát để không nhầm lẫn giữa việc "tiền đã tới tay đối tác" với "giao dịch bị lỗi". Tránh thanh toán trùng lặp (double payment) hoặc ghi nhận sai lệch công nợ. |
| **Block** | **11779465** | Số thứ tự của khối (Block Number) chứa giao dịch này trên blockchain Sepolia. | **Xác định thời điểm ghi nhận bất biến.** Dùng để tính toán số lượt xác nhận (block confirmations), đánh giá rủi ro đảo ngược giao dịch (reorganization risk) trước khi quyết định giải ngân hay bàn giao hàng hóa/dịch vụ. |
| **Timestamp** | **25/09/2026 20:17:48 (GMT+7)**<br>*(13:17:48 UTC - Unix: 1790342268)* | Dấu thời gian khối được thợ đào/validator đóng dấu và chấp thuận vào chuỗi. | **Mốc ghi nhận doanh thu / chi phí.** Phục vụ chốt sổ kế toán theo kỳ (cut-off period), quy đổi tỷ giá hối đoái tiền điện tử sang VNĐ/USD tại đúng thời điểm phát sinh nghĩa vụ tài chính. |
| **From** | `0xafb64eef8093cf3dc4e2c51bb1d18e16afddb6f5` | Địa chỉ ví bên gửi (khởi tạo và ký số cho giao dịch). | **Định danh nguồn tiền (KYC/AML).** Xác minh danh tính người thanh toán, kiểm tra xem nguồn ví có thuộc danh sách đen/cấm vận (sanction list) hoặc tài khoản gian lận hay không. |
| **To** | `0xee917bc552f81fe4db72025e05f146919b3b4032` | Địa chỉ ví bên nhận (hoặc hợp đồng đích được tương tác). | **Đối tượng nhận thanh toán.** Đảm bảo tiền được chuyển đúng ví nhà cung cấp/khách hàng theo thỏa thuận hợp đồng; phân loại luồng tiền chuyển nội bộ hay chuyển ra bên ngoài. |
| **Value** | **0.01 ETH**<br>*(10,000,000,000,000,000 Wei)* | Số lượng đồng tiền cơ sở (Native Token ETH) được chuyển đi trong giao dịch. | **Giá trị giao dịch gốc.** Là căn cứ cốt lõi để đối soát công nợ, xuất hóa đơn thương mại và ghi tăng/giảm tài sản trên bảng cân đối kế toán. |
| **Transaction Fee** | **0.000052041932397 ETH**<br>*(52,041,932,397,000 Wei)* | Tổng chi phí mạng thực tế người gửi phải trả cho mạng lưới để xử lý giao dịch. | **Chi phí vận hành giao dịch (OPEX).** Phải hạch toán riêng vào chi phí tài chính/phí dịch vụ, không được cộng gộp vào giá vốn hàng hóa để đảm bảo báo cáo thuế và tài chính chính xác. |
| **Gas Price** | **2.478187257 Gwei**<br>*(2,478,187,257 Wei)* | Đơn giá gas thị trường tại thời điểm giao dịch được đưa vào khối (Base fee + Priority fee). | **Giải thích sự biến động chi phí.** Giúp phân tích nguyên nhân vì sao cùng chuyển 0.01 ETH nhưng ở các thời điểm mạng nghẽn thì phí cao, lúc mạng rảnh thì phí thấp; từ đó lên kế hoạch tối ưu giờ gửi giao dịch. |
| **Gas Limit** | **31,500** | Lượng gas tối đa mà ví người gửi cho phép giao dịch này tiêu thụ. | **Quản trị rủi ro thất thoát vốn.** Đặt giới hạn trần chi phí. Nếu đặt quá thấp (< 21,000 với chuyển ETH), giao dịch sẽ bị lỗi *Out of Gas* — vừa không chuyển được tiền vừa mất trắng phí. Nếu đặt quá cao mà tương tác hợp đồng lỗi lặp vô tận, ví sẽ bị trừ cạn sạch gas. |
| **Gas Used** | **21,000** (66.67% của Gas Limit) | Lượng gas thực tế mà máy ảo Ethereum (EVM) đã tiêu tốn để thực thi giao dịch. | **Phân tích bản chất kỹ thuật & tính phí:**<br>• Công thức: $\text{Transaction Fee} = \text{Gas Used} \times \text{Gas Price}$.<br>• Lượng tiêu thụ đúng 21,000 gas xác nhận đây là giao dịch chuyển ETH tiêu chuẩn giữa hai ví người dùng (EOA to EOA), không gọi hàm logic hay hợp đồng phức tạp.<br>• Nếu *Gas Used = Gas Limit* kèm lỗi thì đó là dấu hiệu cạn kiệt gas. |
| **Nonce** | **1** | Số thứ tự giao dịch xuất phát từ ví gửi (đếm tuần tự từ 0, 1, 2,...). | **Phát hiện giao dịch bị sót, treo hoặc thay thế.** Giúp đối soát tính liên tục của sổ nhật ký giao dịch, xử lý tình trạng giao dịch bị kẹt mạng (pending) bằng tính năng ghi đè tăng phí (*Speed Up / Cancel*), đồng thời ngăn ngừa tấn công phát lại (Replay Attack). |

---

## Công thức và Kiểm Chứng Số Liệu

$$\text{Transaction Fee} = \text{Gas Used} \times \text{Effective Gas Price}$$
$$= 21,000 \times 2,478,187,257 \text{ Wei} = 52,041,932,397,000 \text{ Wei} = 0.000052041932397 \text{ ETH}$$

- **Tỷ lệ Gas tiêu thụ:** $\frac{21,000}{31,500} \approx 66.67\%$ (Phần dư 10,500 gas được hoàn lại vào số dư của ví gửi ngay sau khi kết thúc giao dịch).

---

## Trả Lời Các Câu Hỏi Về Smart Contract

### Câu 1: Hợp đồng bạn xem có công bố mã nguồn đã xác thực không?
- **Trả lời:** **Có (Yes)**.
- **Chi tiết:** Trên giao diện Etherscan (Sepolia / Ethereum Mainnet), tại tab **Contract** của hợp đồng token có dấu tích xanh xác nhận: **`Contract Source Code Verified (Exact Match)`**. 
- **Ý nghĩa:** Điều này chứng minh mã nguồn Solidity do đơn vị phát hành tải lên đã được Etherscan biên dịch lại độc lập và khớp chính xác 100% với mã máy (Bytecode) đang chạy trên blockchain. Nhờ đó, người dùng và kiểm toán viên có thể đọc trực tiếp mã nguồn, kiểm tra tính minh bạch của các hàm và tương tác an toàn qua giao diện *Read/Write Contract*.

---

### Câu 2: Tổng cung của đồng đó là bao nhiêu? Đọc ra từ hàm nào?
- **Trả lời:**
  - **Hàm đọc ra:** Hàm **`totalSupply`** (hoặc `totalSupply() public view returns (uint256)` theo chuẩn ERC-20). Đọc tại tab **Read Contract** (hoặc tab **Read as Proxy** đối với hợp đồng có mô hình nâng cấp Proxy).
  - **Giá trị tổng cung (Total Supply):**
    - *Với hợp đồng USDC (Circle - FiatTokenProxy):* Đọc giá trị tại hàm `totalSupply` trong tab **Read as Proxy**, sau đó chia cho $10^6$ (vì USDC quy ước `decimals = 6`).
    - *Với hợp đồng USDT (TetherToken - `0xdAC17F958D2ee523a2206206994597C13D831ec7`):* Đọc tại hàm `totalSupply` trong tab **Read Contract**, giá trị hiển thị dạng số nguyên thô (ví dụ: `88305985017331899`, tương ứng $\sim 88.3$ tỷ USDT lưu hành với `decimals = 6`).

---

### Câu 3: Trong tab Write Contract (với USDC: Write as Proxy), có hàm nào cho phép một địa chỉ đặc biệt đóng băng tài khoản người khác không? Nếu có, tên hàm là gì?
- **Trả lời:** **CÓ**.
- **Tên hàm:**
  - **Đối với USDC (Circle):** Tên hàm là **`blacklist(address _account)`** (nằm trong tab **Write as Proxy**).
    - **Địa chỉ có quyền thực thi:** Chỉ địa chỉ ví được phân quyền giữ vai trò **`blacklister`** (được chỉ định bởi Circle) mới có quyền gọi hàm này (`onlyBlacklister`).
    - **Các hàm liên quan:**
      - `unBlacklist(address _account)`: Mở đóng băng cho tài khoản đã bị khóa.
      - `isBlacklisted(address _account)`: Đọc và kiểm tra trạng thái đóng băng (trong tab *Read as Proxy*).
      - `destroyBlackFunds(address _blackListedUser)`: Tiêu hủy/tịch thu toàn bộ số dư USDC của tài khoản nằm trong danh sách đen.
  - **Đối với USDT (Tether):** Tên hàm là **`addBlackList(address _evilUser)`** (nằm trong tab **Write Contract**).
    - **Địa chỉ có quyền thực thi:** Chỉ duy nhất chủ sở hữu hợp đồng (**`owner`**) mới có quyền gọi hàm này (`onlyOwner`).
    - **Hàm liên quan:** `removeBlackList(address _clearedUser)` (gỡ danh sách đen) và `destroyBlackFunds(address _blackListedUser)` (hủy số dư ví đen).
- **Ý nghĩa nghiệp vụ:** Đây là cơ chế kiểm soát tập trung (Centralized Control & Compliance) bắt buộc của các đơn vị phát hành Stablecoin pháp định (Fiat-backed Stablecoins). Cơ chế này phục vụ việc thực thi lệnh đóng băng khẩn cấp từ các cơ quan hành pháp (cảnh sát, tòa án, lệnh trừng phạt OFAC) để phong tỏa dòng tiền liên quan đến mã độc, tấn công sàn (hack) hoặc rửa tiền.
