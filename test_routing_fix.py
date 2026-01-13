
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append('d:/MyProjects/MCP_coze')

from modules.financial_query import FinancialQuery

class TestRouting(unittest.TestCase):
    def test_routing_triggers(self):
        query_engine = FinancialQuery()
        
        # Test Case 1: Debit Amount (Should trigger Text-to-SQL)
        # We can't easily mock the internal method without partial mocking, 
        # but we can observe the side effects or check logic if we refactor.
        # Alternatively, we can inspect private attributes if any, but `complex_condition_patterns` is local.
        # Let's mock the `text_to_sql` module import inside the method or just mock `execute_query`'s internal logic?
        # Actually, `execute_query` prints "Detect complex condition...". We can capture stdout? 
        # Or easier: we can subclass and override `execute_query` to just check the complex detection part if we extracted it.
        # But since I didn't extract it, let's just create a dummy "Text-to-SQL" engine mock and see if it gets called.

        with patch('modules.text_to_sql.get_text_to_sql_engine') as mock_get_engine:
            mock_engine = MagicMock()
            mock_engine.query.return_value = ([], "success")
            mock_get_engine.return_value = mock_engine
            
            # 1. Test "借方"
            query_engine.execute_query(1, {'year': 2023}, [], "2023年应收账款借方金额")
            mock_engine.query.assert_called()
            print("✅ '借方' triggered Text-to-SQL")
            mock_engine.reset_mock()
            
            # 2. Test "销售部"
            query_engine.execute_query(1, {'year': 2023}, [], "2023年销售部工资")
            mock_engine.query.assert_called()
            print("✅ '销售部' triggered Text-to-SQL")
            mock_engine.reset_mock()
            
            # 3. Test Normal Query (Should NOT trigger Strategy 0)
            # We assume it bypasses Strategy 0. To prevent falling through to Strategy 3 (Fallback),
            # we manually populate metrics_map.
            query_engine._metrics_map = {'total_revenue': ('income_statements', 'total_revenue')}
            
            with patch.object(query_engine, '_get_connection') as mock_conn:
                mock_cursor = MagicMock()
                mock_conn.return_value.cursor.return_value = mock_cursor
                mock_cursor.fetchall.return_value = []
                
                query_engine.execute_query(1, {'year': 2023}, ['total_revenue'], "2023年收入")
                
                # Verify calling via Strategy 0 (Complex Condition) happened 0 times
                # If it fell through to Strategy 1 (Direct Query), it wouldn't call mock_engine.query
                mock_engine.query.assert_not_called()
                print("✅ Normal query matched by keyword bypassed Text-to-SQL")

if __name__ == "__main__":
    unittest.main()
