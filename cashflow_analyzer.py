"""
Cong cu phan tich dong tien on-chain Ethereum (ETH) trong N ngay gan nhat.
Tuan thu dac ta tai SPEC.md va quy uoc tai AGENTS.md.
Chu thich trong ma nguon viet bang tieng Viet khong dau.
"""

import os
import sys
import re
import time
import argparse
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
import requests

try:
    # Ho tro doc bien moi truong tu tep .env
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Hang so quy doi: 1 ETH = 10^18 Wei
WEI_IN_ETH = Decimal("1000000000000000000")
# Mui gio Viet Nam GMT+7 phuc vu kiem toan doi soat
VN_TIMEZONE = timezone(timedelta(hours=7))

# Bang ma chainid chuan cua Etherscan API V2
CHAIN_IDS = {
    "mainnet": 1,
    "sepolia": 11155111,
}


def wei_to_eth(wei_value: int | Decimal | str) -> Decimal:
    """
    Quy tac R5: Chuyen doi tu don vi Wei sang ETH (chia cho 10^18).
    Dung kieu Decimal de dam bao do chinh xac so hoc tuyet doi.
    """
    return (Decimal(str(wei_value)) / WEI_IN_ETH).quantize(Decimal("0.000000000000000001"), rounding=ROUND_HALF_UP)


def format_eth(eth_value: Decimal) -> str:
    """
    Dinh dang hien thi so ETH gon gang cho nguoi dung.
    """
    formatted = f"{eth_value:.8f}".rstrip("0").rstrip(".")
    return formatted if formatted else "0"


def validate_address(address: str) -> bool:
    """
    Kiem tra dia chi vi Ethereum hop le (42 ky tu, bat dau bang 0x).
    """
    if not address or len(address) != 42:
        return False
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))


def fetch_all_transactions(address: str, api_key: str, days: int, network: str = "mainnet") -> list[dict]:
    """
    Lay toan bo danh sach giao dich cua vi tu Etherscan API V2.
    Xu ly phan trang neu vi co tren 10.000 giao dich.
    Kiem tra ma trang thai phan hoi va ma loi truoc khi xu ly du lieu.
    """
    chain_id = CHAIN_IDS.get(network.lower(), 1)
    base_url = "https://api.etherscan.io/v2/api"

    # Tinh moc thoi gian can loc (Unix timestamp)
    now_ts = int(time.time())
    cutoff_ts = now_ts - (days * 86400)

    all_txs = []
    page = 1
    offset = 10000  # Gioi han toi da moi trang cua Etherscan API

    print(f"Dang tai du lieu giao dich tu Etherscan V2 (network: {network}, chainid: {chain_id})...")

    while True:
        params = {
            "chainid": chain_id,
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "page": page,
            "offset": offset,
            "sort": "asc",
            "apikey": api_key,
        }

        try:
            response = requests.get(base_url, params=params, timeout=25)
        except requests.RequestException as e:
            print(f"[LOI KET NOI] Khong the ket noi den Etherscan API: {e}")
            sys.exit(1)

        # Kiem tra ma trang thai HTTP cua phan hoi
        if response.status_code != 200:
            print(f"[LOI HTTP] Etherscan tra ve ma trang thai HTTP: {response.status_code}")
            sys.exit(1)

        try:
            data = response.json()
        except Exception as e:
            print(f"[LOI PHAN HOI] Phan hoi khong phai dinh dang JSON hop le: {e}")
            sys.exit(1)

        status = str(data.get("status", ""))
        message = str(data.get("message", ""))
        result = data.get("result")

        # Xu ly truong hop API tra ve danh sach rong
        if status == "0":
            if "No transactions found" in message or result == [] or result is None:
                if page == 1:
                    print("Vi khong co giao dich trong ky")
                    sys.exit(0)
                # Da duyet het cac trang giao dich truoc do
                break
            else:
                # Etherscan thong bao ma loi cu the
                print(f"[LOI API] Ma loi Etherscan: {message}. Chi tiet: {result}")
                sys.exit(1)

        if not isinstance(result, list):
            print(f"[LOI DU LIEU] Du lieu ket qua khong hop le: {result}")
            sys.exit(1)

        all_txs.extend(result)

        # Neu so luong tra ve nho hon offset thi da lay het tat ca trang
        if len(result) < offset:
            break

        page += 1
        # Tranh rate limit khi goi nhieu trang
        time.sleep(0.25)

    # Loc cac giao dich nam trong khoang thoi gian xet (days ngay gan nhat)
    filtered_txs = [tx for tx in all_txs if int(tx.get("timeStamp", 0)) >= cutoff_ts]

    if not filtered_txs:
        print("Vi khong co giao dich trong ky")
        sys.exit(0)

    return filtered_txs


def analyze_cashflow(address: str, transactions: list[dict]) -> tuple[list[dict], dict]:
    """
    Phan tich dong tien on-chain theo cac quy tac R1 -> R6:
    - R1: to trung vi -> Dong tien vao (+ value).
    - R2: from trung vi -> Dong tien ra.
    - R3: Dong tien ra = value + phi giao dich (gasUsed * gasPrice).
    - R4: Giao dich that bai van bi tru phi neu vi la nguoi gui.
    - R5: Tinh toan va quy doi sang ETH.
    - R6: Sap xep thoi gian tang dan.
    """
    target = address.lower()

    # R6: Sap xep giao dich theo thoi gian tang dan
    sorted_txs = sorted(transactions, key=lambda x: int(x.get("timeStamp", 0)))

    processed_records = []
    total_inflow = Decimal("0")
    total_outflow = Decimal("0")
    cumulative_balance = Decimal("0")

    for tx in sorted_txs:
        ts = int(tx.get("timeStamp", 0))
        tx_hash = tx.get("hash", "")
        from_addr = (tx.get("from") or "").lower()
        to_addr = (tx.get("to") or "").lower()
        is_error = str(tx.get("isError", "0")) == "1"

        value_wei = int(tx.get("value", 0))
        gas_used = int(tx.get("gasUsed", 0))
        gas_price = int(tx.get("gasPrice", 0))
        fee_wei = gas_used * gas_price

        # Dinh dang thoi gian theo gio GMT+7
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(VN_TIMEZONE)
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

        fee_eth = wei_to_eth(fee_wei)
        value_eth = wei_to_eth(value_wei)

        direction = ""
        amount_eth = Decimal("0")
        actual_deduction_eth = Decimal("0")

        # R4: Xu ly giao dich that bai (reverted)
        if is_error:
            if from_addr == target:
                # Nguoi gui bi tru phi gas, so tien value khong bi tru
                direction = "RA (that bai)"
                amount_eth = Decimal("0")
                actual_deduction_eth = fee_eth
                total_outflow += actual_deduction_eth
                cumulative_balance -= actual_deduction_eth
            else:
                # Neu la nguoi nhan ma giao dich that bai thi khong nhan duoc gi va khong mat phi
                continue
        else:
            # Giao dich thanh cong
            is_outgoing = (from_addr == target)
            is_incoming = (to_addr == target)

            if is_outgoing and is_incoming:
                # Truong hop vi tu gui cho chinh minh: value vao ra can bang, chi mat phi gas
                direction = "TU GUI (phi)"
                amount_eth = value_eth
                actual_deduction_eth = fee_eth
                total_outflow += actual_deduction_eth
                cumulative_balance -= actual_deduction_eth

            elif is_outgoing:
                # R2 & R3: Dong tien ra = value + phi giao dich
                direction = "RA"
                amount_eth = value_eth
                actual_deduction_eth = value_eth + fee_eth
                total_outflow += actual_deduction_eth
                cumulative_balance -= actual_deduction_eth

            elif is_incoming:
                # R1: Dong tien vao = value (phi do ben gui chiu)
                direction = "VAO"
                amount_eth = value_eth
                fee_eth = Decimal("0")
                total_inflow += amount_eth
                cumulative_balance += amount_eth
            else:
                # Giao dich khong lien quan truc tiep den vi dang xet
                continue

        processed_records.append({
            "timestamp": ts,
            "datetime": time_str,
            "hash": tx_hash,
            "type": direction,
            "amount_eth": amount_eth,
            "fee_eth": fee_eth,
            "cumulative_balance": cumulative_balance,
        })

    summary = {
        "total_inflow": total_inflow,
        "total_outflow": total_outflow,
        "net_final_balance": cumulative_balance,
    }

    return processed_records, summary


def print_report(address: str, days: int, records: list[dict], summary: dict):
    """
    Xuat bang du lieu chi tiet va 3 con so tong hop ra man hinh console.
    """
    print("\n" + "=" * 102)
    print(f"BAO CAO PHAN TICH DONG TIEN ON-CHAIN (ETH)")
    print(f"Dia chi vi : {address}")
    print(f"Khoang tg  : {days} ngay gan nhat (Mui gio GMT+7)")
    print(f"So luong gd: {len(records)} giao dich hop le trong ky")
    print("=" * 102)

    headers = f"{'Thoi gian (GMT+7)':<20} | {'Ma Tx':<14} | {'Loai':<14} | {'So tien (ETH)':<16} | {'Phi (ETH)':<14} | {'So du luy ke':<16}"
    print(headers)
    print("-" * 102)

    for r in records:
        short_hash = f"{r['hash'][:6]}...{r['hash'][-4:]}" if len(r['hash']) > 10 else r['hash']
        row = (
            f"{r['datetime']:<20} | "
            f"{short_hash:<14} | "
            f"{r['type']:<14} | "
            f"{format_eth(r['amount_eth']):<16} | "
            f"{format_eth(r['fee_eth']):<14} | "
            f"{format_eth(r['cumulative_balance']):<16}"
        )
        print(row)

    print("-" * 102)
    print("BA CON SO TONG HOP TRONG KY:")
    print(f"1. Tong tien vao (Total Inflow)  : {format_eth(summary['total_inflow'])} ETH")
    print(f"2. Tong tien ra  (Total Outflow) : {format_eth(summary['total_outflow'])} ETH (bao gom ca phi mang luoi)")
    print(f"3. So du cuoi ky (Net Balance)   : {format_eth(summary['net_final_balance'])} ETH (bien dong dong tien rong)")
    print("=" * 102 + "\n")


def generate_chart(records: list[dict], output_file: str = "balance_chart.png"):
    """
    Xuat bieu do duong the hien su bien dong so du luy ke theo thoi gian.
    Truc ngang: Thoi gian, Truc doc: So du luy ke (ETH).
    """
    if not records:
        return

    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates

        dates = [datetime.fromtimestamp(r["timestamp"], tz=timezone.utc).astimezone(VN_TIMEZONE) for r in records]
        balances = [float(r["cumulative_balance"]) for r in records]

        plt.figure(figsize=(11, 5.5))
        plt.plot(dates, balances, marker="o", markersize=4, linestyle="-", color="#0284c7", linewidth=2, label="So du luy ke (ETH)")
        plt.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)

        # Dinh dang truc thoi gian
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%H:%M", tz=VN_TIMEZONE))
        plt.title("Bieu Do So Du Luy Ke On-Chain Theo Thoi Gian", fontsize=14, fontweight="bold", pad=15)
        plt.xlabel("Thoi gian (GMT+7)", fontsize=11)
        plt.ylabel("So du luy ke (ETH)", fontsize=11)
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend(loc="best")
        plt.tight_layout()

        plt.savefig(output_file, dpi=300)
        plt.close()
        print(f"[XUAT BIEU DO] Da luu bieu do so du vao tep: {output_file}")

    except ImportError:
        print("[THONG BAO] Chua cai dat thu vien 'matplotlib'. Bo qua buoc xuat anh bieu do.")
        print("Huong dan: Chay 'pip install matplotlib' de kich hoat tinh nang xuat bieu do.")


def main():
    """
    Ham khoi chay chinh cua chuong trinh.
    """
    parser = argparse.ArgumentParser(description="Cong cu phan tich dong tien on-chain Ethereum trong N ngay gan nhat.")
    parser.add_argument("address", help="Dia chi vi Ethereum (42 ky tu bat dau bang 0x)")
    parser.add_argument("--days", type=int, default=90, help="So ngay can phan tich (mac dinh 90 ngay)")
    parser.add_argument("--network", default="mainnet", choices=["mainnet", "sepolia"], help="Mang Ethereum (mainnet hoac sepolia)")
    parser.add_argument("--chart", default="balance_chart.png", help="Ten tep anh bieu do xuat ra (mac dinh: balance_chart.png)")

    args = parser.parse_args()

    # Kiem tra dinh dang dia chi vi
    if not validate_address(args.address):
        print(f"[LOI DAU VAO] Dia chi vi khong hop le: '{args.address}'. Dia chi phai co 42 ky tu va bat dau bang '0x'.")
        sys.exit(1)

    # Kiem tra so ngay phan tich
    if args.days <= 0:
        print(f"[LOI DAU VAO] So ngay can phan tich phai la so nguyen duong lon hon 0 (gia tri truyen vao: {args.days}).")
        sys.exit(1)

    # Doc khoa API tu bien moi truong
    api_key = os.environ.get("ETHERSCAN_API_KEY")
    if not api_key:
        print("[LOI CAU HINH] Khong tim thay bien moi truong 'ETHERSCAN_API_KEY'.")
        print("Vui long thiet lap bang cach: set ETHERSCAN_API_KEY=your_key (hoac luu vao tep .env).")
        sys.exit(1)

    # Lay danh sach giao dich tu Etherscan V2
    transactions = fetch_all_transactions(args.address, api_key, args.days, args.network)

    # Phan tich dong tien
    records, summary = analyze_cashflow(args.address, transactions)

    # Xuat bao cao bang va 3 chi so
    print_report(args.address, args.days, records, summary)

    # Xuat bieu do duong
    generate_chart(records, args.chart)


if __name__ == "__main__":
    main()
