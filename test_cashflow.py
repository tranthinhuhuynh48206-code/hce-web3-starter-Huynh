"""
Kiem thu tu dong cho cong cu phan tich dong tien on-chain.
Tuan thu quy uoc tai AGENTS.md: toi thieu ba truong hop kiem thu, gom mot truong hop gian lan.
Chu thich viet bang tieng Viet khong dau.
"""

import unittest
from decimal import Decimal
from cashflow_analyzer import validate_address, wei_to_eth, analyze_cashflow


class TestCashflowAnalyzer(unittest.TestCase):
    def setUp(self):
        # Dia chi vi khao sat
        self.target_address = "0xafb64eef8093cf3dc4e2c51bb1d18e16afddb6f5"
        self.other_address = "0xee917bc552f81fe4db72025e05f146919b3b4032"

    def test_case_1_happy_path(self):
        """
        Truong hop kiem thu 1: Dong tien binh thuong (Happy Path).
        Vi nhan 1.0 ETH, sau do chuyen di 0.4 ETH voi phi gas 0.001 ETH.
        Sau do vi tu gui cho chinh minh 0.1 ETH voi phi gas 0.0005 ETH.
        """
        # Gia lap du lieu tu Etherscan
        mock_txs = [
            # Giao dich 1: Nhan 1.0 ETH tu ben ngoai (Thanh cong)
            {
                "hash": "0xtx1",
                "timeStamp": "1700000000",
                "from": self.other_address,
                "to": self.target_address,
                "value": "1000000000000000000",  # 1.0 ETH
                "gasUsed": "21000",
                "gasPrice": "20000000000",
                "isError": "0",
            },
            # Giao dich 2: Gui 0.4 ETH ra ngoai, phi = 21000 * 50 Gwei = 0.00105 ETH
            {
                "hash": "0xtx2",
                "timeStamp": "1700001000",
                "from": self.target_address,
                "to": self.other_address,
                "value": "400000000000000000",   # 0.4 ETH
                "gasUsed": "21000",
                "gasPrice": "50000000000",       # 50 Gwei (0.00105 ETH phi)
                "isError": "0",
            },
            # Giao dich 3: Tu gui cho chinh minh 0.1 ETH, phi = 21000 * 20 Gwei = 0.00042 ETH
            {
                "hash": "0xtx3",
                "timeStamp": "1700002000",
                "from": self.target_address,
                "to": self.target_address,
                "value": "100000000000000000",   # 0.1 ETH
                "gasUsed": "21000",
                "gasPrice": "20000000000",       # 20 Gwei (0.00042 ETH phi)
                "isError": "0",
            }
        ]

        records, summary = analyze_cashflow(self.target_address, mock_txs)

        # Kiem tra so luong ban ghi
        self.assertEqual(len(records), 3)

        # Giao dich 1: Tien vao = 1.0 ETH
        self.assertEqual(records[0]["type"], "VAO")
        self.assertEqual(records[0]["amount_eth"], Decimal("1"))
        self.assertEqual(records[0]["fee_eth"], Decimal("0"))
        self.assertEqual(records[0]["cumulative_balance"], Decimal("1"))

        # Giao dich 2: Tien ra = 0.4 ETH + 0.00105 ETH = 0.40105 ETH
        expected_fee_tx2 = Decimal("0.00105")
        self.assertEqual(records[1]["type"], "RA")
        self.assertEqual(records[1]["amount_eth"], Decimal("0.4"))
        self.assertEqual(records[1]["fee_eth"], expected_fee_tx2)
        expected_balance_tx2 = Decimal("1") - Decimal("0.40105")
        self.assertEqual(records[1]["cumulative_balance"], expected_balance_tx2)

        # Giao dich 3: Tu gui, chi ton phi = 0.00042 ETH
        expected_fee_tx3 = Decimal("0.00042")
        self.assertEqual(records[2]["type"], "TU GUI (phi)")
        expected_balance_tx3 = expected_balance_tx2 - expected_fee_tx3
        self.assertEqual(records[2]["cumulative_balance"], expected_balance_tx3)

        # Kiem tra tong hop
        self.assertEqual(summary["total_inflow"], Decimal("1"))
        expected_outflow = Decimal("0.40105") + Decimal("0.00042")
        self.assertEqual(summary["total_outflow"], expected_outflow)
        self.assertEqual(summary["net_final_balance"], summary["total_inflow"] - summary["total_outflow"])

    def test_case_2_failed_transactions(self):
        """
        Truong hop kiem thu 2: Giao dich that bai (Failed Revert Transaction - R4).
        - Giao dich 1 (Nguoi gui): Vi co gui 2.0 ETH nhung bi revert. Vi van mat phi gas.
        - Giao dich 2 (Nguoi nhan): Nguoi khac gui cho vi nhung bi fail. Vi khong duoc cong va khong mat phi.
        """
        mock_txs = [
            # Giao dich 1: Vi gui that bai (isError = 1)
            {
                "hash": "0xfail1",
                "timeStamp": "1700005000",
                "from": self.target_address,
                "to": self.other_address,
                "value": "2000000000000000000",  # 2.0 ETH
                "gasUsed": "50000",
                "gasPrice": "30000000000",       # 30 Gwei -> phi = 0.0015 ETH
                "isError": "1",
            },
            # Giao dich 2: Ben ngoai gui vao vi nhung bi that bai
            {
                "hash": "0xfail2",
                "timeStamp": "1700006000",
                "from": self.other_address,
                "to": self.target_address,
                "value": "5000000000000000000",  # 5.0 ETH
                "gasUsed": "21000",
                "gasPrice": "20000000000",
                "isError": "1",
            }
        ]

        records, summary = analyze_cashflow(self.target_address, mock_txs)

        # Chi co giao dich nguoi gui bi tru phi moi duoc ghi nhan vao dong tien ra
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["type"], "RA (that bai)")
        self.assertEqual(records[0]["amount_eth"], Decimal("0"))  # Khong bi tru 2.0 ETH

        expected_fee = Decimal("0.0015")
        self.assertEqual(records[0]["fee_eth"], expected_fee)
        self.assertEqual(records[0]["cumulative_balance"], -expected_fee)

        self.assertEqual(summary["total_inflow"], Decimal("0"))
        self.assertEqual(summary["total_outflow"], expected_fee)
        self.assertEqual(summary["net_final_balance"], -expected_fee)

    def test_case_3_fraud_dusting_address_poisoning(self):
        """
        Truong hop kiem thu 3: Kich ban gian lan (Address Poisoning / Dusting Attack).
        Ke gian gui 0 ETH tu mot dia chi ma mao nham dau doc lich su giao dich
        cua nan nhan de lua ho copy nham dia chi vi trong tuong lai.
        He thong phai xu ly an toan khong crash, ghi nhan 0 ETH va khong tru phi nguoi nhan.
        """
        scam_address = "0xafb64eef8093cf3dc4e2c51bb1d18e16afddb6aa"  # Dia chi ma mao tuong tu
        mock_txs = [
            {
                "hash": "0xscam_tx_dusting",
                "timeStamp": "1700010000",
                "from": scam_address,
                "to": self.target_address,
                "value": "0",                    # 0 ETH dusting
                "gasUsed": "21000",
                "gasPrice": "10000000000",
                "isError": "0",
            },
            {
                "hash": "0xscam_tx_micro_dust",
                "timeStamp": "1700010100",
                "from": scam_address,
                "to": self.target_address,
                "value": "1",                    # 1 Wei dusting
                "gasUsed": "21000",
                "gasPrice": "10000000000",
                "isError": "0",
            }
        ]

        records, summary = analyze_cashflow(self.target_address, mock_txs)

        self.assertEqual(len(records), 2)
        # Tx 1: 0 ETH
        self.assertEqual(records[0]["type"], "VAO")
        self.assertEqual(records[0]["amount_eth"], Decimal("0"))
        self.assertEqual(records[0]["fee_eth"], Decimal("0"))
        self.assertEqual(records[0]["cumulative_balance"], Decimal("0"))

        # Tx 2: 1 Wei
        self.assertEqual(records[1]["type"], "VAO")
        self.assertEqual(records[1]["amount_eth"], Decimal("0.000000000000000001"))
        self.assertEqual(records[1]["cumulative_balance"], Decimal("0.000000000000000001"))

        self.assertEqual(summary["total_inflow"], Decimal("0.000000000000000001"))
        self.assertEqual(summary["total_outflow"], Decimal("0"))

    def test_address_validation(self):
        """
        Kiem thu xac thuc dia chi vi.
        """
        self.assertTrue(validate_address("0xafb64eef8093cf3dc4e2c51bb1d18e16afddb6f5"))
        self.assertTrue(validate_address("0xAFB64EEF8093CF3DC4E2C51BB1D18E16AFDDB6F5"))
        # Thieu 0x
        self.assertFalse(validate_address("afb64eef8093cf3dc4e2c51bb1d18e16afddb6f5"))
        # Thieu ky tu
        self.assertFalse(validate_address("0xafb64eef8093cf3dc4e2c51bb1d18e16afddb6f"))
        # Chua ky tu khong phai hex
        self.assertFalse(validate_address("0xafb64eef8093cf3dc4e2c51bb1d18e16afddb6fz"))


if __name__ == "__main__":
    unittest.main()
