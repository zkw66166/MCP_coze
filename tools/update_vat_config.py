import json
import os

CONFIG_DIR = 'config'
METRICS_CONFIG = os.path.join(CONFIG_DIR, 'metrics_config.json')
GLOSSARY_CONFIG = os.path.join(CONFIG_DIR, 'business_glossary.json')
SCHEMA_MAPPINGS = os.path.join(CONFIG_DIR, 'schema_mappings.json')

# Full list of 100 columns for tax_returns_vat
VAT_COLUMNS = [
    'period_year', 'period_month', 'period_quarter', 'tax_period', 'filing_date',
    'gen_sales_taxable_current', 'gen_sales_taxable_ytd', 
    'gen_sales_goods_current', 'gen_sales_goods_ytd', 
    'gen_sales_service_current', 'gen_sales_service_ytd', 
    'gen_sales_adjustment_current', 'gen_sales_adjustment_ytd', 
    'gen_sales_simple_current', 'gen_sales_simple_ytd', 
    'gen_sales_simple_adjustment_current', 'gen_sales_simple_adjustment_ytd', 
    'gen_sales_export_current', 'gen_sales_export_ytd', 
    'gen_sales_exempt_current', 'gen_sales_exempt_ytd', 
    'gen_sales_exempt_goods_current', 'gen_sales_exempt_goods_ytd', 
    'gen_sales_exempt_service_current', 'gen_sales_exempt_service_ytd', 
    'gen_output_tax_current', 'gen_output_tax_ytd', 
    'gen_input_tax_current', 'gen_input_tax_ytd', 
    'gen_previous_credit_current', 'gen_previous_credit_ytd', 
    'gen_input_tax_transfer_current', 'gen_input_tax_transfer_ytd', 
    'gen_export_refund_current', 'gen_tax_inspection_current', 
    'gen_deductible_total_current', 'gen_actual_deduction_current', 
    'gen_actual_deduction_ytd', 'gen_tax_payable_current', 
    'gen_tax_payable_ytd', 'gen_ending_credit_current', 
    'gen_simple_tax_current', 'gen_simple_tax_ytd', 
    'gen_simple_inspection_current', 'gen_tax_reduction_current', 
    'gen_tax_reduction_ytd', 'gen_tax_total_current', 
    'gen_tax_total_ytd', 'gen_opening_unpaid_tax_current', 
    'gen_opening_unpaid_tax_ytd', 'gen_export_refund_received_current', 
    'gen_paid_tax_total_current', 'gen_paid_tax_total_ytd', 
    'gen_prepaid_tax_current', 'gen_export_prepaid_current', 
    'gen_paid_previous_tax_current', 'gen_paid_previous_tax_ytd', 
    'gen_paid_overdue_tax_current', 'gen_paid_overdue_tax_ytd', 
    'gen_ending_unpaid_tax_current', 'gen_ending_unpaid_tax_ytd', 
    'gen_overdue_tax_current', 'gen_tax_payable_refund_current', 
    'gen_opening_inspection_unpaid_current', 'gen_opening_inspection_unpaid_ytd', 
    'gen_inspection_paid_current', 'gen_inspection_paid_ytd', 
    'gen_ending_inspection_unpaid_current', 'gen_ending_inspection_unpaid_ytd', 
    'ref_sales_taxable_current', 'ref_sales_taxable_ytd', 
    'ref_output_tax_current', 'ref_output_tax_ytd', 
    'ref_input_tax_current', 'ref_input_tax_ytd', 
    'ref_tax_payable_current', 'ref_tax_payable_ytd', 
    'ref_tax_total_current', 'ref_tax_total_ytd', 
    'ref_actual_refund_current', 'ref_actual_refund_ytd', 
    'urban_construction_tax_current', 'urban_construction_tax_ytd', 
    'education_surcharge_current', 'education_surcharge_ytd', 
    'local_education_surcharge_current', 'local_education_surcharge_ytd', 
    'preparer', 'preparer_id_card', 'taxpayer_signature', 'signature_date', 
    'receiver', 'agent_org', 'agent_org_code', 'tax_authority', 'acceptance_date'
]

# Chinese mapping helpers
def generate_vat_field_config(col_name):
    aliases = []
    unit = "元"
    category = "一般项目"
    
    name_map = {
        'sales_taxable': '按适用税率计税销售额',
        'sales_goods': '其中：应税货物销售额',
        'sales_service': '其中：应税劳务销售额',
        'sales_adjustment': '纳税检查调整的销售额',
        'sales_simple': '按简易办法计税销售额',
        'sales_simple_adjustment': '纳税检查调整的销售额（简易）',
        'sales_export': '免、抵、退办法出口销售额',
        'sales_exempt': '免税销售额',
        'sales_exempt_goods': '其中：免税货物销售额',
        'sales_exempt_service': '其中：免税劳务销售额',
        'output_tax': '销项税额',
        'input_tax': '进项税额',
        'previous_credit': '上期留抵税额',
        'input_tax_transfer': '进项税额转出',
        'export_refund': '免、抵、退应退税额',
        'tax_inspection': '按适用税率计算的纳税检查应补缴税额',
        'deductible_total': '应抵扣税额合计',
        'actual_deduction': '实际抵扣税额',
        'tax_payable': '应纳税额',
        'ending_credit': '期末留抵税额',
        'simple_tax': '简易计税办法计算的应纳税额',
        'simple_inspection': '按简易计税办法计算的纳税检查应补缴税额',
        'tax_reduction': '应纳税额减征额',
        'tax_total': '应纳税额合计',
        'opening_unpaid_tax': '期初未缴税额',
        'export_refund_received': '实收出口退税额',
        'paid_tax_total': '本期已缴税额',
        'prepaid_tax': '①分次预缴税额',
        'export_prepaid': '②出口开具专用缴款书预缴税额',
        'paid_previous_tax': '③本期缴纳上期应纳税额',
        'paid_overdue_tax': '④本期缴纳欠缴税额',
        'ending_unpaid_tax': '期末未缴税额',
        'overdue_tax': '其中：欠缴税额',
        'tax_payable_refund': '本期应补（退）税额',
        'opening_inspection_unpaid': '即征即退期初未缴税额', # Adjust for logic
        'inspection_paid': '即征即退本期已缴税额', # Adjust
        'ending_inspection_unpaid': '即征即退期末未缴税额', # Adjust
        'actual_refund': '实际退税额',
        'urban_construction_tax': '城建税',
        'education_surcharge': '教育费附加',
        'local_education_surcharge': '地方教育附加'
    }

    # Handle gen_ vs ref_
    prefix = ""
    suffix = ""
    is_ytd = col_name.endswith('_ytd')
    
    base_name = col_name
    if col_name.startswith('gen_'):
        category = "一般项目"
        base_name = col_name[4:]
        prefix = "一般项目"
    elif col_name.startswith('ref_'):
        category = "即征即退项目"
        base_name = col_name[4:]
        prefix = "即征即退"
    else:
        category = "附加税及信息"
    
    if is_ytd:
        base_name = base_name[:-4]
        suffix = "（本年累计）"
    else:
        base_name = base_name[:-8] if base_name.endswith('_current') else base_name
        suffix = "（本期）"

    # Special handling for basic fields
    if col_name in ['period_year', 'period_month', 'period_quarter', 'tax_period', 'filing_date', 
                    'preparer', 'preparer_id_card', 'taxpayer_signature', 'signature_date', 
                    'receiver', 'agent_org', 'agent_org_code', 'tax_authority', 'acceptance_date']:
        category = "基础信息"
        unit = ""
        base_map = {
            'period_year': '年份', 'period_month': '月份', 'period_quarter': '季度', 
            'tax_period': '税款所属期', 'filing_date': '申报日期', 'preparer': '办税人',
            'preparer_id_card': '办税人身份证号', 'taxpayer_signature': '纳税人签字',
            'signature_date': '签字日期', 'receiver': '受理人', 'agent_org': '代理机构',
            'agent_org_code': '代理机构代码', 'tax_authority': '受理税务机关', 'acceptance_date': '受理日期'
        }
        if col_name in base_map:
            aliases.append(base_map[col_name])
    else:
        # Standard tax fields
        if base_name in name_map:
            cn_name = name_map[base_name]
            aliases.append(prefix + cn_name + suffix)
            aliases.append(cn_name + suffix)
            if not is_ytd:
                aliases.append(prefix + cn_name) # Short for current
                aliases.append(cn_name) # Shortest

    return {
        "aliases": list(set(aliases)), # Remove duplicates
        "unit": unit,
        "category": category
    }

def update_metrics_config():
    with open(METRICS_CONFIG, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. Prepare tax_returns_vat definition
    fields = {}
    for col in VAT_COLUMNS:
        if col in ['id', 'company_id', 'created_at', 'updated_at']:
            continue
        fields[col] = generate_vat_field_config(col)
        
    vat_config = {
        "description": "增值税申报表（一般纳税人适用）",
        "fields": fields
    }
    
    # 2. Update tables
    if 'vat_returns' in data['tables']:
        del data['tables']['vat_returns']
    if 'vat_return_items' in data['tables']:
        del data['tables']['vat_return_items']
        
    data['tables']['tax_returns_vat'] = vat_config
    
    # 3. Add tax_returns_vat to aggregation_tables if not present
    if "tax_returns_vat" not in data['query_settings']['aggregation_tables']:
        data['query_settings']['aggregation_tables'].append("tax_returns_vat")
        
    # Remove old tables from aggregation if present
    if "vat_returns" in data['query_settings']['aggregation_tables']:
        data['query_settings']['aggregation_tables'].remove("vat_returns")
        
    with open(METRICS_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Updated {METRICS_CONFIG}")

def update_business_glossary():
    with open(GLOSSARY_CONFIG, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Update table descriptions
    if "vat_returns" in data['table_descriptions']:
        del data['table_descriptions']['vat_returns']
    if "vat_return_items" in data['table_descriptions']:
        del data['table_descriptions']['vat_return_items']
        
    data['table_descriptions']['tax_returns_vat'] = "增值税申报表数据,包含一般计税方法、简易计税方法及即征即退项目的销售额、税额等全量信息"
    
    with open(GLOSSARY_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Updated {GLOSSARY_CONFIG}")

def update_schema_mappings():
    with open(SCHEMA_MAPPINGS, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Update tables list
    # Remove old
    if "vat_returns" in data['tables']:
        del data['tables']['vat_returns']
    if "vat_return_items" in data['tables']:
        del data['tables']['vat_return_items']
        
    # Add new
    data['tables']['tax_returns_vat'] = [
        "增值税申报表",
        "增值税表",
        "增值税主表"
    ]
    
    with open(SCHEMA_MAPPINGS, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Updated {SCHEMA_MAPPINGS}")

if __name__ == "__main__":
    update_metrics_config()
    update_business_glossary()
    update_schema_mappings()
    print("All config updates completed.")
