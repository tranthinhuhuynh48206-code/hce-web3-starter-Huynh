# Báo Cáo Phân Tích Cấu Trúc Phí Gas và Tính Khả Thi Kinh Tế — Lab 07

**Đề tài đồ án nhóm:** Nền tảng TrustScholar cho nhà tài trợ và sinh viên để đảm bảo giải ngân học bổng tự động, minh bạch và chống sai đối tượng.  
**Môn học:** ECO2432 — Công Nghệ Web3 & Smart Contract  
**Thành viên thực hiện:** Sinh viên nhóm thực hiện  

---

## Bước 1: Hiểu Cấu Trúc Phí Giao Dịch Trên Blockchain

### 1.1. Công thức tính phí giao dịch (Transaction Fee)
$$\text{Chi phí giao dịch (ETH)} = \text{Lượng gas tiêu thụ (Gas Used)} \times \text{Đơn giá gas (Gas Price in Gwei)} \times 10^{-9}$$
$$\text{Chi phí giao dịch (USD)} = \text{Chi phí giao dịch (ETH)} \times \text{Giá ETH (USD)}$$

### 1.2. Bảng tham khảo mức tiêu thụ Gas theo EVM
| Loại thao tác | Lượng gas tham khảo | Bản chất kỹ thuật EVM |
| :--- | :---: | :--- |
| **Chuyển ETH thông thường** | **21.000** | Phí cơ sở (Base transaction fee) cho giao dịch ví cá nhân (EOA to EOA). |
| **Chuyển token chuẩn ERC-20** | **~50.000 – 65.000** | Thực thi hàm `transfer`, đọc và ghi cập nhật số dư vào mapping `balanceOf`. |
| **Ghi biến mới vào bộ nhớ dài hạn** | **~20.000** | Lệnh `SSTORE` khởi tạo một slot bộ nhớ mới từ giá trị 0 sang khác 0. |
| **Sửa một biến đã có trong bộ nhớ** | **~5.000** | Lệnh `SSTORE` ghi đè giá trị lên slot bộ nhớ đã có sẵn (khác 0 sang khác 0). |
| **Triển khai hợp đồng cỡ nhỏ** | **~500.000 – 1.500.000** | Tạo hợp đồng, biên dịch bytecode đưa vào trạng thái chuỗi (State storage). |

*Ghi chú: Lượng gas thực tế sẽ được đo đạc chính xác bằng Remix IDE trong các bài thực hành tiếp theo.*

---

## Bước 2: Giải Bài Toán Chi Phí — Câu Lạc Bộ Sinh Viên Phát Hành Thẻ Tích Điểm

### 2.1. Đặt bài toán
- **Số lượng giao dịch:** 1.000 lượt cộng điểm / tháng (mỗi lượt là một giao dịch ghi/sửa dữ liệu trên Smart Contract).
- **Lượng gas tham khảo:** $\sim 20.000\text{ gas}$ cho thao tác ghi dữ liệu (cộng dồn điểm thưởng cho thành viên).
- **Đơn giá gas:** $20\text{ Gwei} = 20 \times 10^{-9}\text{ ETH}$.
- **Giá ETH quy đổi:** $3.000\text{ USD / ETH}$.

---

### 2.2. Tính toán chi tiết các câu hỏi

#### a. Chi phí một tháng trên mạng Ethereum Layer 1 (USD)
- Phí gas cho 1 giao dịch:
  $$\text{Fee}_{\text{1 tx}} = 20.000 \times 20 \times 10^{-9} = 0,0004\text{ ETH}$$
  $$\text{Fee}_{\text{1 tx (USD)}} = 0,0004 \times 3.000\text{ USD} = 1,20\text{ USD / giao dịch}$$
- Chi phí cho 1.000 lượt giao dịch trong 1 tháng:
  $$\text{Tổng chi phí tháng (L1)} = 1.000 \times 1,20\text{ USD} = 1.200\text{ USD / tháng}$$
  *(Quy đổi tương đương $\approx 30.600.000\text{ VNĐ / tháng}$ với tỷ giá 25.500 VNĐ/USD).*
  
*(Lưu ý: Nếu tính đầy đủ cả phí cơ sở 21.000 gas + 20.000 gas ghi bộ nhớ = 41.000 gas thì chi phí thực tế lên tới $2.460\text{ USD / tháng}$, tương đương $\approx 62.700.000\text{ VNĐ / tháng}$).*

#### b. Chi phí một tháng khi chuyển sang Layer 2 (rẻ hơn 100 lần)
- Mức phí trên Layer 2 (như Arbitrum, Optimism, Base):
  $$\text{Tổng chi phí tháng (L2)} = \frac{1.200\text{ USD}}{100} = 12\text{ USD / tháng}$$
  $$\text{Phí mỗi lượt giao dịch (L2)} = \frac{1,20\text{ USD}}{100} = 0,012\text{ USD / giao dịch} \approx 300\text{ VNĐ / lượt}$$
  *(Quy đổi tương đương $\approx 306.000\text{ VNĐ / tháng}$).*

#### c. Ai trả khoản này — Câu lạc bộ hay Sinh viên?
- **Nếu Sinh viên tự trả:** 
  - Mỗi lần uống một ly nước hoặc tham gia một hoạt động tích điểm nhỏ, sinh viên phải trả **$1,20\text{ USD}$ ($\approx 30.000\text{ VNĐ}$)** tiền phí mạng trên Layer 1. 
  - Khoản phí này thậm chí cao hơn hoặc ngang bằng giá trị món đồ mua. **Sinh viên chắc chắn sẽ tẩy chay và không bao giờ chấp nhận sử dụng.**
- **Nếu Câu lạc bộ trả thay (Sponsor):**
  - Quỹ hoạt động của một câu lạc bộ sinh viên thông thường chỉ dao động từ vài triệu đến vài chục triệu đồng mỗi kỳ. CLB không thể gánh nổi khoản ngân sách **$1.200\text{ USD / tháng}$ ($\approx 30,6\text{ triệu VNĐ}$)** chỉ để duy trì hệ thống điểm thưởng trên Layer 1.

#### d. Kết luận về tính khả thi
- **Trên Ethereum Layer 1:** **HOÀN TOÀN BẤT KHẢ THI** về mặt kinh tế. Mô hình điểm thưởng micro-transaction không thể hoạt động trên Mainnet do phí nghẽn mạng quá cao so với giá trị kinh tế của mỗi lượt tương tác.
- **Trên Layer 2 (Arbitrum / Optimism / Base):** **HOÀN TOÀN KHẢ THI**. Tổng chi phí chỉ **$12\text{ USD / tháng}$ ($\approx 306.000\text{ VNĐ}$)**, hoàn toàn nằm trong khả năng chi trả của quỹ CLB. CLB có thể ứng dụng cơ chế Paymaster (ERC-4337) để tài trợ 100% phí gas cho sinh viên một cách dễ dàng và mượt mà.

---

## Bước 3: Mở Rộng Cho Đồ Án Nhóm — Nền Tảng "TrustScholar"

### 3.1. Giới thiệu bài toán kinh tế của TrustScholar
- **Tên đề tài:** Nền tảng TrustScholar cho nhà tài trợ và sinh viên để đảm bảo giải ngân học bổng tự động, minh bạch và chống sai đối tượng.
- **Mục tiêu:**
  - Nhà tài trợ (Doanh nghiệp, Quỹ cựu sinh viên) nạp tiền quỹ học bổng minh bạch vào Smart Contract.
  - Nhà trường thẩm định và phê duyệt danh sách sinh viên đủ tiêu chuẩn (học lực, hoàn cảnh khó khăn).
  - Hợp đồng thông minh tự động giải ngân học bổng trực tiếp về ví sinh viên, loại bỏ hoàn toàn khâu trung gian, chống thất thoát hoặc giải ngân sai đối tượng.

### 3.2. Quy mô bài toán ước tính cho một học kỳ (1 đợt giải ngân)
- **Số suất học bổng giải ngân:** 100 sinh viên / học kỳ.
- **Giá trị mỗi suất học bổng:** $500\text{ USD}$ (tổng quỹ giải ngân: $50.000\text{ USD} \approx 1,275\text{ tỷ VNĐ}$).
- **Quy trình tương tác Smart Contract:**
  1. *Triển khai hợp đồng quản lý quỹ (`ScholarshipPool`):* 1 lần duy nhất ban đầu ($\approx 800.000\text{ gas}$).
  2. *Nhà tài trợ nạp tiền vào quỹ:* 5 giao dịch nạp tiền lớn ($\approx 60.000\text{ gas / tx}$).
  3. *Hội đồng xét duyệt cập nhật danh sách 100 sinh viên:* 100 giao dịch ghi dữ liệu sinh viên đủ điều kiện ($\approx 30.000\text{ gas / tx}$).
  4. *Giải ngân học bổng về ví sinh viên (`disburse` / `claim`):* 100 giao dịch chuyển tiền kèm xác thực điều kiện ($\approx 50.000\text{ gas / tx}$).

---

### 3.3. Bảng Tính Toán So Sánh Chi Phí Gas Giữa Layer 1 và Layer 2

> **Giả định tính toán:**
> - Giá ETH = $3.000\text{ USD}$.
> - Đơn giá gas Layer 1 (Ethereum Mainnet): $20\text{ Gwei}$.
> - Đơn giá gas Layer 2 (Arbitrum / Optimism / Base): Rẻ hơn Layer 1 trung bình $80\text{ lần}$ (tương đương $\approx 0,25\text{ Gwei}$).

| Hạng mục thao tác | Số lượt (tx) | Lượng Gas / tx | Tổng Gas tiêu thụ | Chi phí Layer 1 (ETH) | Chi phí Layer 1 (USD) | Chi phí Layer 2 (USD) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Triển khai hợp đồng** *(1 lần đầu)* | 1 | 800.000 | 800.000 | 0,01600 ETH | $48,00 | $0,60 |
| **Nhà tài trợ nạp quỹ học bổng** | 5 | 60.000 | 300.000 | 0,00600 ETH | $18,00 | $0,23 |
| **Cập nhật hồ sơ & cấp quyền 100 SV** | 100 | 30.000 | 3.000.000 | 0,06000 ETH | $180,00 | $2,25 |
| **Giải ngân học bổng cho 100 SV** | 100 | 50.000 | 5.000.000 | 0,10000 ETH | $300,00 | $3,75 |
| **TỔNG CỘNG MỖI KỲ GIẢI NGÂN** | **206** | — | **9.100.000** | **0,18200 ETH** | **$546,00** | **$6,83** |

*(Ghi chú: Nếu trừ chi phí triển khai hợp đồng chỉ làm một lần duy nhất thì chi phí vận hành mỗi kỳ là **$498\text{ USD}$** trên L1 và **$6,23\text{ USD}$** trên L2).*

---

### 3.4. Phân Tích Cơ Chế Chi Trả & Trải Nghiệm Sinh Viên (UX)

| Tiêu chí so sánh | Triển khai trên Ethereum Layer 1 | Triển khai trên Layer 2 (Arbitrum / Base) |
| :--- | :--- | :--- |
| **Phí nhận học bổng / sinh viên** | **$3,00\text{ USD} \approx 76.500\text{ VNĐ / lần}$** | **$0,0375\text{ USD} \approx 950\text{ VNĐ / lần}$** |
| **Tỷ lệ phí trên giá trị học bổng ($500)** | **$0,6\%$** (60 basis points) | **$0,0075\%$** (~0,75 basis point) |
| **Rào cản tiếp cận của sinh viên** | **Rất cao:** Sinh viên phải tự mua ETH trên sàn, rút về ví để có tiền trả gas trước khi nhận học bổng. | **Rất thấp:** Sinh viên chỉ cần tạo ví, hệ thống hoặc nhà tài trợ dễ dàng tài trợ gas (Gasless Transaction). |
| **Khả năng Quỹ tài trợ chi trả thay** | Khó khăn: Quỹ phải trích ra gần **14 triệu VNĐ** mỗi kỳ chỉ để trả phí giao dịch. | Dễ dàng: Quỹ chỉ tốn khoảng **$6,83\text{ USD} \approx 175.000\text{ VNĐ / kỳ}$** để đài thọ 100% phí vận hành cho cả đợt. |

---

## 4. Kết Luận Về Tính Khả Thi Của Đồ Án TrustScholar

1. **Khả thi về mặt kinh tế:**
   - Đồ án **TrustScholar** có tính khả thi vượt trội khi được triển khai trên các mạng **Layer 2 (Arbitrum One, Optimism hoặc Base)**. Với tổng chi phí vận hành giải ngân cho 100 sinh viên chỉ vỏn vẹn **$6,83\text{ USD}$ (chưa tới 180.000 VNĐ)**, chi phí mạng chỉ chiếm **$0,013\%$** tổng giá trị quỹ học bổng ($50.000 USD), hoàn toàn nằm trong biên độ chi phí quản lý cho phép của các tổ chức từ thiện và giáo dục.
   - Ngược lại, nếu triển khai trực tiếp trên Layer 1, mức chi phí **$546\text{ USD}$** sẽ gây lãng phí nguồn lực tài trợ và tạo ra rào cản tài chính phi lý đối với sinh viên có hoàn cảnh khó khăn.

2. **Khuyến nghị kiến trúc kỹ thuật cho nhóm:**
   - **Mạng lưới triển khai:** Lựa chọn **Arbitrum Sepolia** (cho môi trường thử nghiệm) và **Arbitrum One / Base** (cho môi trường thực tế) để đảm bảo tốc độ giao dịch dưới 2 giây và phí gas cực thấp.
   - **Tối ưu hóa dữ liệu:** Sử dụng cấu trúc cây **Merkle Tree** để xác thực danh sách sinh viên đủ điều kiện (chỉ cần lưu 1 Merkle Root trên Smart Contract), giúp giảm thiểu thêm $80\%$ lượng gas ở khâu cập nhật danh sách hồ sơ.
   - **Cơ chế tài trợ phí (Gasless / Paymaster):** Ứng dụng tiêu chuẩn **ERC-4337 (Account Abstraction)** để hợp đồng Quỹ học bổng tự động trả phí gas thay cho sinh viên. Khi đó, sinh viên chỉ cần bấm ký xác nhận nhận học bổng mà không cần sở hữu bất kỳ đồng ETH nào trong ví, giúp nền tảng TrustScholar đạt được sự minh bạch, thân thiện và ứng dụng thực tiễn cao nhất.
