
import sys
import unittest
from unittest.mock import MagicMock, patch
import json

# Add project root to path
sys.path.append('d:/MyProjects/MCP_coze')

from modules.financial_query import FinancialQuery
from modules.text_to_sql import TextToSQLEngine

class TestAllInSql(unittest.TestCase):
    
    def setUp(self):
        self.query_engine = FinancialQuery()
    
    @patch('modules.text_to_sql.get_text_to_sql_engine')
    def test_basic_financial_query(self, mock_get_engine):
        """Test Case 1: Standard Metric (Was Strategy 1) -> Must now use SQL"""
        mock_engine = MagicMock()
        mock_engine.query.return_value = (
            [{'period_year': 2023, 'total_revenue': 100000.0}], 
            "success"
        )
        mock_get_engine.return_value = mock_engine
        
        results = self.query_engine.execute_query(1, {'year': 2023}, ['total_revenue'], "2023年收入")
        
        # Verify result structure
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['metric_name'], 'total_revenue')
        self.assertEqual(results[0]['value'], 100000.0)
        
        # Verify SQL engine was called (Crucial for "all-in" Strategy)
        mock_engine.query.assert_called_once()
        print("✅ Basic Query '2023年收入' correctly routed to Text-to-SQL")

    @patch('modules.text_to_sql.get_text_to_sql_engine')
    def test_routing_query_debit(self, mock_get_engine):
        """Test Case 2: Routing Query (Was Strategy 0) -> Continues to use SQL"""
        mock_engine = MagicMock()
        mock_engine.query.return_value = (
            [{'period_year': 2023, '借方金额': 5000.0}], 
            "success"
        )
        mock_get_engine.return_value = mock_engine
        
        results = self.query_engine.execute_query(1, {'year': 2023}, [], "2023年借方金额")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['metric_name'], '借方金额')
        
        mock_engine.query.assert_called_once()
        print("✅ Routing Query '2023年借方金额' correctly routed to Text-to-SQL")

    @patch('modules.text_to_sql.get_text_to_sql_engine')
    def test_ambiguous_invoice_query(self, mock_get_engine):
        """Test Case 3: Ambiguous Query (Input Invoice) -> Uses SQL with Input Filter"""
        mock_engine = MagicMock()
        # Mock result assuming SQL correctly filtered for INPUT
        mock_engine.query.return_value = (
            [{'period_year': 2023, '进项税额': 200.0}], 
            "success"
        )
        mock_get_engine.return_value = mock_engine
        
        # Simulating the prompt generation check is hard here without integration test,
        # but we verify that the Python layer handles the result correctly.
        results = self.query_engine.execute_query(1, {'year': 2023}, [], "2023年进项发票税额")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['metric_name'], '进项税额')
        print("✅ Ambiguous Query '2023年进项发票税额' correctly handled via SQL path")

    def test_prompt_injection(self):
        """Test Case 4: Verify Prompt contains Schema Mappings"""
        # Instantiate actual engine to check prompt building logic logic (no mock)
        engine = TextToSQLEngine()
        # Force load schema provider mock if needed, or rely on lazy load
        # We just want to check _build_prompt output
        
        # Provide dummy data
        prompt = engine._build_prompt("测试问题", 1, [2023])
        
        # Check for key phrases from schema_mappings.json
        self.assertIn("Business Rules", prompt)
        self.assertIn("invoice_type", prompt)
        self.assertIn("value_mappings", prompt)
        
        # Check specifically for generated synonyms
        # We assume '进项' is in the generated mapping for Input Invoice
        self.assertIn("进项", prompt) 
        
        print("✅ Prompt correctly matches 'schema_mappings.json' content")

if __name__ == "__main__":
    unittest.main()
