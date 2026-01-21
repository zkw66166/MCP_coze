import json
import os

CONFIG_PATH = 'config/metrics_config.json'

# Definition of new metrics to add
# Format: "Metric Name": ["Field Name", "Unit", ["Alias1", "Alias2"...]]
NEW_METRICS = {
    # Sales Breakdown
    "增值税货物销售额": ["gen_sales_goods_current", "元", ["货物销售额", "一般货物销售额"]],
    "增值税劳务销售额": ["gen_sales_service_current", "元", ["劳务销售额", "应税劳务销售额"]],
    "增值税简易计税销售额": ["gen_sales_simple_current", "元", ["简易计税销售额", "简易办法销售额"]],
    "增值税出口销售额": ["gen_sales_export_current", "元", ["出口销售额", "免抵退销售额"]],
    "增值税免税销售额": ["gen_sales_exempt_current", "元", ["免税销售额", "增值税免税额"]],
    
    # Tax Details - Input/Output adjustment
    "增值税进项转出额": ["gen_input_tax_transfer_current", "元", ["进项税额转出", "进项转出"]],
    "增值税上期留抵税额": ["gen_previous_credit_current", "元", ["上期留抵税额", "期初留抵"]],
    "增值税期末留抵税额": ["gen_ending_credit_current", "元", ["期末留抵税额", "留抵税额"]],
    "增值税应抵扣税额合计": ["gen_deductible_total_current", "元", ["应抵扣税额合计", "可抵扣税额"]],
    "增值税实际抵扣税额": ["gen_actual_deduction_current", "元", ["实际抵扣税额"]],
    
    # Tax Details - Payable/Paid
    "增值税简易计税应纳税额": ["gen_simple_tax_current", "元", ["简易计税应纳税额", "简易办法应纳税额"]],
    "增值税减免税额": ["gen_tax_reduction_current", "元", ["增值税减免额", "应纳税额减征额"]],
    "增值税本期已缴税额": ["gen_paid_tax_total_current", "元", ["增值税已缴税额", "本期已缴税额"]],
    "增值税期末未缴税额": ["gen_ending_unpaid_tax_current", "元", ["期末未缴税额", "增值税欠税"]],
    "增值税查补税额": ["gen_tax_inspection_current", "元", ["查补税额", "纳税检查应补缴税额"]],
    
    # Refunds
    "增值税实收出口退税": ["gen_export_refund_received_current", "元", ["实收出口退税", "出口退税额"]],
    "增值税免抵退应退税额": ["gen_export_refund_current", "元", ["免抵退应退税额"]],
    
    # Immediate Refund (即征即退)
    "即征即退销售额": ["ref_sales_taxable_current", "元", ["即征即退销售额"]],
    "即征即退应纳税额": ["ref_tax_payable_current", "元", ["即征即退应纳税额"]],
    "即征即退实际退税额": ["ref_actual_refund_current", "元", ["即征即退实际退税额", "软件退税额"]],
    
    # Surcharges
    "城建税": ["urban_construction_tax_current", "元", ["城市维护建设税", "城建税额"]],
    "教育费附加": ["education_surcharge_current", "元", ["教育费附加额"]],
    "地方教育附加": ["local_education_surcharge_current", "元", ["地方教育附加额"]]
}

def generate_vat_metrics():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    metrics = config.get('financial_metrics', {})
    
    for metric_name, details in NEW_METRICS.items():
        field_name, unit, aliases = details
        
        # Construct the metric definition
        metric_def = {
            "table": "tax_returns_vat",
            "value_field": field_name,
            "company_field": "company_id",
            "year_field": "period_year",
            "month_field": "period_month",
            "unit": unit,
            "aliases": aliases
        }
        
        # Add to metrics
        metrics[metric_name] = metric_def
        print(f"Added metric: {metric_name}")
        
    config['financial_metrics'] = metrics
    
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    print(f"Successfully added {len(NEW_METRICS)} VAT metrics to {CONFIG_PATH}")

if __name__ == "__main__":
    generate_vat_metrics()
