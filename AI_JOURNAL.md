# NHẬT KÝ LÀM VIỆC VỚI AI — Lab 04: Thẩm Định Rủi Ro Hợp Đồng Token

---

## Lần 1 — Thẩm định hợp đồng `ClubTokenA`

**Prompt:**  
> Bạn là chuyên viên thẩm định rủi ro tài sản số. Dưới đây là mã nguồn một hợp đồng token. Hãy liệt kê mọi quyền đặc biệt mà chủ sở hữu hợp đồng có thể thực hiện, và với mỗi quyền, nêu rõ: Tên hàm và số dòng; Người nắm giữ token chịu rủi ro gì. Chỉ trả lời dựa trên mã nguồn tôi cung cấp. Nếu không tìm thấy, nói là không tìm thấy.  
> [// SPDX-License-Identifier: MIT  
> pragma solidity ^0.8.20;  
> import "@openzeppelin/contracts/token/ERC20/ERC20.sol";  
> /// @title Token cau lac bo - khong co quyen dac biet nao  
> contract ClubTokenA is ERC20 {  
>     constructor() ERC20("Club Token A", "CTA") {  
>         _mint(msg.sender, 1_000_000 * 10 ** decimals());  
>     }  
> }]

**AI trả về:**  
- Kết luận: Không tìm thấy bất kỳ quyền đặc biệt nào của chủ sở hữu hợp đồng.
- Tên hàm và số dòng: Không tìm thấy (chỉ có `constructor()` tại dòng 8 – 10).
- Phân tích rủi ro: Không có rủi ro can thiệp từ chủ sở hữu vì hợp đồng không kế thừa `Ownable` hay `AccessControl`. Tổng cung cố định 1.000.000 CTA đúc một lần ban đầu cho người triển khai.

**So sánh Đối chiếu:**
- **Đọc thủ công tìm ra gì:** Mã nguồn rất ngắn, chỉ có hàm khởi tạo `constructor()` đúc 1.000.000 CTA cho `msg.sender`, không có bất kỳ hàm `function` nào khác.
- **AI tìm thêm được gì:** AI phân tích chi tiết tính chất kỹ thuật: không có biến lưu địa chỉ admin/owner, không có cơ chế nâng cấp (Proxy), không thể tạm dừng (Pausable) hay can thiệp số dư, khẳng định tính tự trị của mã nguồn.
- **AI có nói sai chỗ nào không:** **Không sai**. AI trả lời đúng định dạng yêu cầu "không tìm thấy" khi không có quyền đặc biệt.

**Đánh giá:** Dùng được.  
**Ai phát hiện:** Không có lỗi sai cần chỉnh sửa.

---

## Lần 2 — Thẩm định hợp đồng `ClubTokenB`

**Prompt:**  
> Bạn là chuyên viên thẩm định rủi ro tài sản số. Dưới đây là mã nguồn một hợp đồng token. Hãy liệt kê mọi quyền đặc biệt mà chủ sở hữu hợp đồng có thể thực hiện, và với mỗi quyền, nêu rõ: Tên hàm và số dòng; Người nắm giữ token chịu rủi ro gì. Chỉ trả lời dựa trên mã nguồn tôi cung cấp. Nếu không tìm thấy, nói là không tìm thấy.  
> [// SPDX-License-Identifier: MIT  
> pragma solidity ^0.8.20;  
> import "@openzeppelin/contracts/token/ERC20/ERC20.sol";  
> import "@openzeppelin/contracts/access/Ownable.sol";  
> /// @title Token cau lac bo - ban B  
> contract ClubTokenB is ERC20, Ownable {  
>     constructor() ERC20("Club Token B", "CTB") Ownable(msg.sender) {  
>         _mint(msg.sender, 1_000_000 * 10 ** decimals());  
>     }  
>     /// @notice Phat hanh them token de phuc vu chuong trinh khuyen mai  
>     function mint(address to, uint256 amount) external onlyOwner {  
>         _mint(to, amount);  
>     }  
> }]

**AI trả về:**  
- Tên hàm: `mint(address to, uint256 amount)`.
- Số dòng: Dòng 14 – 16 (trong đoạn mã gửi; tương ứng dòng 18 – 20 trong `ClubTokens.sol`).
- Đối tượng được gọi: `onlyOwner` (chủ sở hữu).
- Rủi ro người nắm giữ: Rủi ro lạm phát không giới hạn (không có `cap`), rủi ro pha loãng giá trị và nguy cơ chủ sở hữu tự in thêm token rồi bán tháo (dump) làm sập giá. Ngoài ra có nhắc tới các hàm quản trị từ `Ownable` (`transferOwnership`, `renounceOwnership`).

**So sánh Đối chiếu:**
- **Đọc thủ công tìm ra gì:** Phát hiện hàm `mint` có modifier `onlyOwner` cho phép chủ sở hữu in thêm token tự do.
- **AI tìm thêm được gì:** AI phân tích sâu hơn góc độ kinh tế tài chính: việc thiếu trần tổng cung tối đa (`MAX_SUPPLY`) kết hợp với việc không có cơ chế khóa thời gian (Timelock) sẽ dẫn đến rủi ro "Rug Pull" / rút cạn thanh khoản bể DEX.
- **AI có nói sai chỗ nào không:** **Không sai**. AI bám sát mã nguồn và chỉ ra chính xác quyền của `onlyOwner`.

**Đánh giá:** Dùng được.  
**Ai phát hiện:** Sinh viên đối chiếu và chuẩn hóa số dòng theo tệp nguồn gốc [contracts/lab04/ClubTokens.sol](file:///d:/crypto-smart-contract-2026/hce-web3-starter-/hce-web3-starter-Huynh/contracts/lab04/ClubTokens.sol#L18-L20) (dòng 18 – 20).

---

## Lần 3 — Thẩm định hợp đồng `ClubTokenC`

**Prompt:**  
> Bạn là chuyên viên thẩm định rủi ro tài sản số. Dưới đây là mã nguồn một hợp đồng token. Hãy liệt kê mọi quyền đặc biệt mà chủ sở hữu hợp đồng có thể thực hiện, và với mỗi quyền, nêu rõ: Tên hàm và số dòng; Người nắm giữ token chịu rủi ro gì. Chỉ trả lời dựa trên mã nguồn tôi cung cấp. Nếu không tìm thấy, nói là không tìm thấy.  
> [// SPDX-License-Identifier: MIT  
> pragma solidity ^0.8.20;  
> import "@openzeppelin/contracts/token/ERC20/ERC20.sol";  
> import "@openzeppelin/contracts/access/Ownable.sol";  
> /// @title Token cau lac bo - ban C  
> contract ClubTokenC is ERC20, Ownable {  
>     mapping(address => bool) public restricted;  
>     constructor() ERC20("Club Token C", "CTC") Ownable(msg.sender) {  
>         _mint(msg.sender, 1_000_000 * 10 ** decimals());  
>     }  
>     function setRestricted(address user, bool status) external onlyOwner {  
>         restricted[user] = status;  
>     }  
>     function _update(address from, address to, uint256 value) internal override {  
>         require(!restricted[from], "Dia chi bi han che");  
>         super._update(from, to, value);  
>     }  
> }]

**AI trả về:**  
- Tên hàm: `setRestricted(address user, bool status)`.
- Số dòng: Dòng 16 – 18 (trong trích đoạn; tương ứng dòng 30 – 32 trong `ClubTokens.sol`), kết hợp hàm nội bộ `_update` tại dòng 20 – 23 (dòng 34 – 37 trong `ClubTokens.sol`).
- Rủi ro người nắm giữ: Bị đóng băng tài sản đơn phương, tước quyền chuyển nhượng và thanh khoản, rủi ro mô hình lừa đảo bẫy không thể bán (Honeypot).

**So sánh Đối chiếu:**
- **Đọc thủ công tìm ra gì:** Hàm `setRestricted` cho phép `owner` đưa địa chỉ vào danh sách `restricted` để chặn chuyển tiền.
- **AI tìm thêm được gì:** AI phát hiện một chi tiết nghiệp vụ rất tinh vi: điều kiện `require(!restricted[from])` tại hàm `_update` **chỉ kiểm tra chiều gửi đi (`from`) mà không kiểm tra chiều nhận (`to`)**. Điều này tạo ra rủi ro bất cân xứng một chiều kinh điển của các mã độc Web3 (nạn nhân vẫn mua/nhận được token vào ví bình thường, nhưng khi muốn bán/chuyển đi thì bị chặn đứng).
- **AI có nói sai chỗ nào không:** **Không sai**. AI giải thích logic chuẩn xác theo hook `_update` của OpenZeppelin v5.x.

**Đánh giá:** Dùng được.  
**Ai phát hiện:** Sinh viên bổ sung số dòng chính xác theo file tổng thể [contracts/lab04/ClubTokens.sol](file:///d:/crypto-smart-contract-2026/hce-web3-starter-/hce-web3-starter-Huynh/contracts/lab04/ClubTokens.sol#L30-L37) (dòng 30 – 37) để phục vụ chấm bài.

---

# NHẬT KÝ LÀM VIỆC VỚI AI — Lab: Công Cụ Phân Tích Dòng Tiền On-Chain (SPEC.md)

## Phần B.1 — Bảng Kết Quả Rà Soát 6 Điểm Kiểm Tra

| # | Điểm kiểm tra | Cách kiểm | Kết quả kiểm tra | Đánh giá |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **Đơn vị tiền** | Số dư hiển thị có hợp lý không? | Mã nguồn sử dụng `Decimal` và chia cho $10^{18}$ (`wei_to_eth`) trước khi hiển thị, không bị tràn số hay hiển thị số thô 19 chữ số. | **Đạt** |
| **2** | **Khóa API** | Tìm chuỗi khóa trong mã nguồn | Không có chuỗi API key nào bị hardcode trong mã; đọc an toàn từ biến môi trường `ETHERSCAN_API_KEY` (kết hợp `dotenv`). | **Đạt** |
| **3** | **Phân trang** | Ví có nhiều giao dịch, có lấy đủ không? | Đã thiết lập vòng lặp `while True` với `page += 1` và `offset = 10000`, lấy đầy đủ dữ liệu cho đến khi số lượng trả về `< offset`. | **Đạt** |
| **4** | **Giao dịch thất bại** | Có tính phí của giao dịch thất bại không? | **Có lỗi logic ban đầu:** AI có xu hướng bỏ qua toàn bộ tx lỗi hoặc tính sai phí của người nhận. Cần xử lý riêng: nếu `isError == "1"` và ví là người gửi (`from`), vẫn trừ phí gas vào dòng tiền ra. | **Phát hiện lỗi & Đã sửa** |
| **5** | **Xử lý lỗi** | Thử dùng khóa API sai | Nếu API key sai hoặc bị lỗi, Etherscan trả về `result` dạng chuỗi thay vì danh sách. Nếu không kiểm tra `status == "0"` và `isinstance(result, list)`, chương trình sẽ bị crash đột ngột với `TypeError`. | **Phát hiện lỗi & Đã sửa** |
| **6** | **Phiên bản API** | Đối chiếu với tài liệu Etherscan hiện hành | **Lỗi nghiêm trọng điển hình:** AI sinh mã dùng endpoint Etherscan V1 cũ (`https://api.etherscan.io/api` và `https://api-sepolia.etherscan.io/api`), bị Etherscan chặn với lỗi `NOTOK: You are using a deprecated V1 endpoint`. | **Phát hiện lỗi & Đã sửa** |

---

## Phần B.3 — Sửa Mã Nguồn Và Ghi Nhật Ký 

### B.3.1 — Lỗi 1: Sử dụng Endpoint API V1 đã lỗi thời

**Prompt ban đầu:**  
> Đọc tệp SPEC.md trong dự án và viết chương trình Python thực hiện đúng đặc tả đó. Tuân thủ các quy ước trong AGENTS.md.

**Hành vi ban đầu của AI:**  
- AI sinh mã sử dụng các endpoint Etherscan V1 riêng biệt:
  - Mainnet: `https://api.etherscan.io/api`
  - Sepolia: `https://api-sepolia.etherscan.io/api`

**So sánh Đối chiếu:**
- **Kiểm tra thực tế tìm ra gì:** Khi chạy thử nghiệm chương trình trên terminal, Etherscan từ chối xử lý và trả về mã lỗi:
  ```text
  [LOI API] Ma loi Etherscan: NOTOK. Chi tiet: You are using a deprecated V1 endpoint, switch to Etherscan API V2 using https://docs.etherscan.io/v2-migration
  ```
- **Nguyên nhân cốt lõi:** Dữ liệu huấn luyện của mô hình AI chứa các tài liệu Etherscan V1 cũ. Etherscan đã nâng cấp toàn diện sang API V2 hợp nhất nhiều chuỗi khối (Multi-chain API) và ngừng hỗ trợ (deprecated) endpoint V1. Đây là minh chứng rõ ràng: *AI chỉ biết những gì đã có trong quá khứ, không cập nhật ngay những thay đổi vừa diễn ra*.
- **AI có làm sai chỗ nào không:** **Có sai**. Mã nguồn sinh ra không chạy được trong thực tế nếu không cập nhật endpoint theo chuẩn V2.

**Đánh giá:** Cần sửa.  
**Ai phát hiện:** **Sinh viên phát hiện** khi chạy thử mã thực tế trên terminal và đối chiếu tài liệu chính thức [Etherscan API V2 Migration Guide](https://docs.etherscan.io/v2-migration).  
**Cách sửa:**
- Chuyển toàn bộ yêu cầu về một endpoint V2 duy nhất: `https://api.etherscan.io/v2/api`.
- Bổ sung tham số bắt buộc `chainid` tương ứng với từng mạng lưới: `chainid=1` cho Ethereum Mainnet và `chainid=11155111` cho Ethereum Sepolia Testnet.

---

### B.3.2 — Lỗi 2: Xử lý giao dịch thất bại và phân định người chịu phí gas (Điểm kiểm tra #4)

**Prompt ban đầu:**  
> Đọc quy tắc R4 trong SPEC.md: "Giao dịch có trạng thái thất bại vẫn bị trừ phí, phải tính vào dòng tiền ra." Hãy đảm bảo tính đúng số dư.

**Hành vi ban đầu của AI:**  
- Trong phiên bản sinh mã thô, AI thường có hai lỗi logic kinh điển:
  1. Chỉ lọc `if tx.get("isError") == "0"` và dùng `continue` bỏ qua toàn bộ giao dịch có `isError == "1"`, làm sai lệch hoàn toàn số dư ví (bỏ quên khoản phí gas đã mất).
  2. Hoặc khi nhận biết `isError == "1"`, AI tự động trừ phí của giao dịch đó vào ví đang xét mà **quên không kiểm tra xem ví đang xét là bên gửi (`from`) hay bên nhận (`to`)**.

**So sánh Đối chiếu:**
- **Đọc thủ công & Kiến trúc EVM tìm ra gì:** Trên blockchain Ethereum, khi một giao dịch chuyển ETH hoặc tương tác Smart Contract bị Revert/Fail:
  - Nếu ví là người gửi (`from == target`): Tiền chuyển `value` được hoàn trả lại, nhưng máy ảo EVM **vẫn thu phí gas thực thi** (`gasUsed * gasPrice`). Khoản này bắt buộc phải tính vào dòng tiền ra (Outflow).
  - Nếu ví là người nhận (`to == target`): Giao dịch thất bại đồng nghĩa tiền không tới ví, và người nhận **hoàn toàn không phải trả bất kỳ khoản phí gas nào**. Nếu trừ phí của người nhận thì số dư của ví sẽ bị hao hụt sai thực tế.
- **AI có làm sai chỗ nào không:** **Có sai logic nghiệp vụ EVM**. AI không phân biệt vai trò `from` vs `to` khi xử lý sự cố giao dịch thất bại.

**Đánh giá:** Cần sửa.  
**Ai phát hiện (Trường được chấm):** **Sinh viên phát hiện** thông qua việc xây dựng ca kiểm thử biên (Edge Case Test) tại `test_case_2_failed_transactions` trong file [test_cashflow.py](file:///d:/crypto-smart-contract-2026/hce-web3-starter-/hce-web3-starter-Huynh/test_cashflow.py).  
**Cách sửa:**
- Tách bạch rõ ràng logic xử lý `if is_error`:
  - Chỉ khi `from_addr == target` mới ghi nhận loại `"RA (that bai)"` với `amount_eth = 0` và trừ `fee_eth` vào dòng tiền ra.
  - Nếu `to_addr == target` thì lập tức `continue` bỏ qua, không tính tiền vào và không trừ phí.

---

### B.3.3 — Lỗi 3 (Bổ sung): Chương trình crash khi API trả về thông báo lỗi hoặc sai khóa API (Điểm kiểm tra #5)

**Prompt ban đầu:**  
> Kiểm tra các trường hợp ngoại lệ theo Mục 5 của SPEC.md khi API trả về mã lỗi.

**Hành vi ban đầu của AI:**  
- AI thường gọi `data = response.json()` rồi trực tiếp duyệt `for tx in data["result"]:`.

**So sánh Đối chiếu:**
- **Kiểm tra thực tế tìm ra gì:** Khi khóa API sai hoặc API bị vượt ngưỡng giới hạn tần suất (Rate limit exceeded), Etherscan trả về cấu trúc:
  ```json
  {"status": "0", "message": "NOTOK", "result": "Invalid API Key"}
  ```
  Lúc này trường `result` là một chuỗi ký tự (`str`) chứ không phải một danh sách (`list`). Việc lặp qua chuỗi hoặc truy cập index không đúng sẽ làm chương trình văng ngoại lệ `TypeError: string indices must be integers` và sập đột ngột (crash) kèm thông báo Traceback khó hiểu cho người dùng cuối.
- **AI có làm sai chỗ nào không:** **Có sai sót**. Thiếu cơ chế phòng vệ dữ liệu (Defensive Programming) trước phản hồi lỗi của API bên thứ ba.

**Đánh giá:** Cần sửa.  
**Ai phát hiện (Trường được chấm):** **Sinh viên phát hiện** khi chạy thử nghiệm kịch bản với API key giả lập không hợp lệ.  
**Cách sửa:**
- Kiểm tra điều kiện `status == "0"`. Nếu `message` chứa `"No transactions found"` hoặc `result` rỗng thì thông báo êm dịu `"Vi khong co giao dich trong ky"` và thoát (exit 0).
- Nếu `status == "0"` với các mã lỗi khác, in rõ thông báo `[LOI API] Ma loi Etherscan: {message}. Chi tiet: {result}` và dừng chương trình có kiểm soát (exit 1).
- Bổ sung kiểm tra `isinstance(result, list)` trước khi xử lý mảng giao dịch.


