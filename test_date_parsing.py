
import sys
import unittest

# Add project root to path
sys.path.append('d:/MyProjects/MCP_coze')

from modules.financial_query import FinancialQuery

class TestDateParsing(unittest.TestCase):
    def setUp(self):
        self.query_engine = FinancialQuery()

    def test_two_digit_list(self):
        """Test '22、23年' -> [2022, 2023]"""
        res = self.query_engine.extract_time_range("查询22、23年收入")
        self.assertEqual(res['years'], [2022, 2023])
        print("✅ '22、23年' parsed as:", res['years'])

    def test_two_digit_range_short(self):
        """Test '22-25' -> [2022, 2023, 2024, 2025]"""
        res = self.query_engine.extract_time_range("22-25利润")
        self.assertEqual(res['years'], [2022, 2023, 2024, 2025])
        print("✅ '22-25' parsed as:", res['years'])
        
    def test_two_digit_range_chinese(self):
        """Test '22-25年' -> [2022, 2023, 2024, 2025]"""
        res = self.query_engine.extract_time_range("22-25年税负")
        self.assertEqual(res['years'], [2022, 2023, 2024, 2025])
        print("✅ '22-25年' parsed as:", res['years'])
        
    def test_mixed_list(self):
        """Test '22,23年' -> [2022, 2023]"""
        res = self.query_engine.extract_time_range("22,23年税负")
        self.assertEqual(res['years'], [2022, 2023])
        print("✅ '22,23年' parsed as:", res['years'])

if __name__ == "__main__":
    unittest.main()
