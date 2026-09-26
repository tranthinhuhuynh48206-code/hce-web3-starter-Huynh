# Báo Cáo Thẩm Định Rủi Ro Hợp Đồng Token — Lab 04

**Mã nguồn thẩm định:** [contracts/lab04/ClubTokens.sol](file:///d:/crypto-smart-contract-2026/hce-web3-starter-/hce-web3-starter-Huynh/contracts/lab04/ClubTokens.sol)  
**Tiêu chuẩn cơ sở:** OpenZeppelin Contracts v5.x (ERC-20, Ownable)  
**Chuyên viên thẩm định:** Sinh viên thực hiện

---

## 1. Bảng Kết Luận Thẩm Định Quyền Hạn Hợp Đồng

| Hợp đồng | Kết luận | Tên hàm | Số dòng | Rủi ro cho người nắm giữ |
| :---: | :--- | :--- | :--- | :--- |
| **A** | **An toàn**<br>*(Không có đặc quyền)* | Không có *(Chỉ có constructor)* | Dòng 8 – 10<br>*(File: `ClubTokens.sol`)* | **Không có rủi ro từ quyền đặc biệt của chủ sở hữu.** Hợp đồng không kế thừa `Ownable`, không có cơ chế `mint` thêm token hay đóng băng tài khoản. Tổng cung cố định 1.000.000 CTA được đúc một lần duy nhất lúc khởi tạo (dòng 9). |
| **B** | **Rủi ro cao**<br>*(Nguy cơ lạm phát & xả hàng)* | `mint(address to, uint256 amount)` | Dòng 18 – 20<br>*(File: `ClubTokens.sol`)* | **Rủi ro lạm phát vô hạn và pha loãng giá trị (Dilution Risk).** Chủ sở hữu (`onlyOwner`) có toàn quyền in thêm token tùy thích mà không bị giới hạn trần tổng cung (`cap`). Chủ sở hữu có thể tự mint lượng lớn token để xả bán (dump) làm sập giá trị tài sản của người nắm giữ. |
| **C** | **Rủi ro rất cao**<br>*(Đóng băng tài sản & Honeypot)* | `setRestricted(address user, bool status)`<br>*(kết hợp `_update`)* | Dòng 30 – 32<br>*(Hàm `setRestricted`)*;<br>Dòng 34 – 37<br>*(Kiểm tra tại dòng 35)* | **Rủi ro đóng băng tài sản & bẫy không thể bán (Honeypot Risk).** Chủ sở hữu (`onlyOwner`) có thể đơn phương đưa bất kỳ ví nào vào danh sách hạn chế (`restricted = true`). Tại dòng 35, hàm `_update` chặn toàn bộ chiều chuyển đi (`from`), khiến người dùng bị tịch thu thanh khoản, không thể bán hay chuyển token đi. |

---

## 2. Phân Tích Kỹ Thuật Chi Tiết Từng Hợp Đồng

### 2.1. Hợp đồng `ClubTokenA`
```solidity
contract ClubTokenA is ERC20 {
    constructor() ERC20("Club Token A", "CTA") {
        _mint(msg.sender, 1_000_000 * 10 ** decimals());
    }
}
```
* **Phân tích quyền hạn:** Hợp đồng chỉ kế thừa duy nhất `ERC20` tiêu chuẩn của OpenZeppelin. Sau khi hoàn tất hàm `constructor` (dòng 8 – 10), mã nguồn không có bất kỳ hàm ngoại vi nào khác.
* **Đánh giá rủi ro:** 
  - Hoàn toàn tự trị, không có biến lưu địa chỉ chủ sở hữu (`owner`), không có modifier `onlyOwner`.
  - Không thể can thiệp số dư, không thể tạm dừng hay thu hồi token của bất kỳ ví nào.
  - Người nắm giữ chỉ cần lưu ý cơ chế phân bổ ban đầu của 1.000.000 CTA đúc cho ví triển khai (`msg.sender`).

---

### 2.2. Hợp đồng `ClubTokenB`
```solidity
contract ClubTokenB is ERC20, Ownable {
    constructor() ERC20("Club Token B", "CTB") Ownable(msg.sender) {
        _mint(msg.sender, 1_000_000 * 10 ** decimals());
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
```
* **Phân tích quyền hạn:** Kế thừa `Ownable` (dòng 13) và thiết lập chủ sở hữu ban đầu tại dòng 14. Định nghĩa hàm `mint` công khai cho phép chủ sở hữu gọi với modifier `onlyOwner` (dòng 18).
* **Đánh giá rủi ro:**
  - Hàm `mint` không có điều kiện ràng buộc giới hạn tổng cung tối đa (Max Supply / Cap).
  - Không có thời gian giãn cách giữa các lần mint (Timelock) hay cơ chế biểu quyết phi tập trung (Multi-sig/Governance).
  - Chủ sở hữu có thể tùy tiện in thêm hàng tỷ token bất cứ lúc nào, làm xói mòn giá trị kinh tế của token CTB trên thị trường.

---

### 2.3. Hợp đồng `ClubTokenC`
```solidity
contract ClubTokenC is ERC20, Ownable {
    mapping(address => bool) public restricted;

    constructor() ERC20("Club Token C", "CTC") Ownable(msg.sender) {
        _mint(msg.sender, 1_000_000 * 10 ** decimals());
    }

    function setRestricted(address user, bool status) external onlyOwner {
        restricted[user] = status;
    }

    function _update(address from, address to, uint256 value) internal override {
        require(!restricted[from], "Dia chi bi han che");
        super._update(from, to, value);
    }
}
```
* **Phân tích quyền hạn:**
  - Khai báo bảng ánh xạ `restricted` lưu trạng thái cấm giao dịch của các ví (dòng 24).
  - Hàm `setRestricted` (dòng 30 – 32) chỉ cho phép `onlyOwner` thay đổi cờ trạng thái này của bất kỳ địa chỉ ví nào.
  - Hàm `_update` (hook chuẩn của OpenZeppelin v5.x xử lý mọi lệnh chuyển token) bị ghi đè tại dòng 34 – 37 với điều kiện bắt buộc: `require(!restricted[from], "Dia chi bi han che")` (dòng 35).
* **Đánh giá rủi ro:**
  - **Kiểm duyệt tập trung (Censorship):** Chủ sở hữu có quyền lực tuyệt đối để vô hiệu hóa quyền sở hữu tài sản của bất kỳ thành viên nào.
  - **Mô hình Honeypot một chiều:** Điều kiện kiểm tra chỉ nhắm vào `from` (người gửi) mà không kiểm tra `to` (người nhận). Nghĩa là ví bị hạn chế vẫn có thể nạp/mua thêm token vào nhưng vĩnh viễn không thể chuyển hoặc bán ra ngoài được.
