
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append('d:/MyProjects/MCP_coze')

from modules.financial_query import FinancialQuery

class TestMultiMetric(unittest.TestCase):
    def test_multi_metric_extraction(self):
        query_engine = FinancialQuery()
        
        # Test Case: Mock Text-to-SQL engine processing a multi-metric query
        # We simulate the SQL engine returning a row with multiple numeric columns
        
        mock_sql_results = [
            {'period_year': 2023, 'period_quarter': 1, '借方金额': 1000.0, '贷方金额': 500.0, '余额': 500.0},
            {'period_year': 2024, 'period_quarter': 1, '借方金额': 1200.0, '贷方金额': 600.0, '余额': 600.0}
        ]
        
        with patch('modules.text_to_sql.get_text_to_sql_engine') as mock_get_engine:
            mock_engine = MagicMock()
            mock_engine.query.return_value = (mock_sql_results, "success")
            mock_get_engine.return_value = mock_engine
            
            # Use a query that triggers Text-to-SQL (has "借方")
            results = query_engine.execute_query(1, {'year': 2023}, [], "22-24年应收账款借方金额、贷方金额、余额")
            
            # Expecting: 2 years * 3 metrics = 6 result items
            print(f"✅ Extracted {len(results)} items")
            
            # Verify specific items
            debit_2023 = next((r for r in results if r['year'] == 2023 and r['metric_name'] == '借方金额'), None)
            credit_2023 = next((r for r in results if r['year'] == 2023 and r['metric_name'] == '贷方金额'), None)
            balance_2023 = next((r for r in results if r['year'] == 2023 and r['metric_name'] == '余额'), None)
            
            self.assertIsNotNone(debit_2023)
            self.assertEqual(debit_2023['value'], 1000.0)
            
            self.assertIsNotNone(credit_2023)
            self.assertEqual(credit_2023['value'], 500.0)
            
            self.assertIsNotNone(balance_2023)
            self.assertEqual(balance_2023['value'], 500.0)
            
            print("✅ Verification Successful: All 3 metrics extracted correctly for 2023")

if __name__ == "__main__":
    unittest.main()
