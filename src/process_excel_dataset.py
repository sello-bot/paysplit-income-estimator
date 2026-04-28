"""
Excel Dataset Processor for PaySplit
=====================================
Processes dataset_2.xlsx with 10 tabs of synthetic bank data.

Usage:
    cd to project root, then run:
    python -m src.process_excel_dataset
"""

import pandas as pd
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now we can import our modules
from src.models import Transaction
from src.income_estimator import IncomeEstimator


# Categories to EXCLUDE (from your requirements)
EXCLUDED_CATEGORY_IDS = {
    3,    # charitable giving
    43,   # electronics/general merchandise
    7,    # entertainment/recreation
    114,  # expense reimbursement
    9,    # gifts
    13,   # home improvement
    104,  # postage/shipping
    227,  # refunds/adjustments
    22,   # restaurants
    40,   # savings
    36,   # securities trades
    23    # travel
}


class ExperianProcessor:
    """Process Experian-style data."""
    
    def __init__(self):
        self.estimator = IncomeEstimator()
    
    def parse_transactions(self, json_data: dict) -> list:
        """Parse Experian JSON to Transaction objects."""
        transactions = []
        
        try:
            accounts = json_data.get('return_data', {}).get('fetched_data', {}).get('fetch_accounts', [])
            
            for account in accounts:
                for txn_data in account.get('transactions', []):
                    try:
                        date_str = txn_data.get('transaction_date', '')
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        amount = float(txn_data.get('amount', 0))
                        
                        category = txn_data.get('category', {})
                        category_id = category.get('id', 0)
                        category_title = category.get('title', 'Unknown')
                        
                        # Skip excluded categories
                        if category_id in EXCLUDED_CATEGORY_IDS:
                            continue
                        
                        full_title = txn_data.get('full_title', '')
                        title = txn_data.get('title', '')
                        
                        transaction = Transaction(
                            date=date,
                            amount=amount,
                            category=category_title,
                            description=full_title or title
                        )
                        
                        transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"  Warning: Skipping transaction: {e}")
                        continue
            
            print(f"  Parsed {len(transactions)} valid transactions")
            
        except Exception as e:
            print(f"  Error parsing JSON: {e}")
        
        return transactions
    
    def process_customer(self, experian_json: dict) -> dict:
        """Process customer data."""
        transactions = self.parse_transactions(experian_json)
        
        if not transactions:
            return {
                'income': {'monthly_amount': 0.0, 'clusters': 0, 'confidence': 'none', 'details': []},
                'expenses': {'monthly_amount': 0.0, 'clusters': 0, 'confidence': 'none', 'details': []},
                'net_monthly_income': 0.0,
                'recommendation': 'MANUAL_REVIEW',
                'error': 'No valid transactions found'
            }
        
        result = self.estimator.estimate_income_and_expenses(transactions)
        
        formatted_result = {
            'income': {
                'monthly_amount': result['income']['monthly_amount'],
                'clusters': result['income']['clusters'],
                'confidence': result['income']['confidence'],
                'details': [
                    {
                        'day_of_month': int(s.center_day),
                        'median_amount': s.median_amount,
                        'occurrences': s.transaction_count,
                        'variance': s.amount_variance
                    }
                    for s in result['income']['streams']
                ]
            },
            'expenses': {
                'monthly_amount': result['expenses']['monthly_amount'],
                'clusters': result['expenses']['clusters'],
                'confidence': result['expenses']['confidence'],
                'details': [
                    {
                        'day_of_month': int(s.center_day),
                        'median_amount': s.median_amount,
                        'occurrences': s.transaction_count,
                        'variance': s.amount_variance
                    }
                    for s in result['expenses']['streams']
                ]
            },
            'net_monthly_income': result['net_monthly_income'],
            'recommendation': result['recommendation'],
            'total_transactions_analyzed': len(transactions)
        }
        
        return formatted_result


def check_excel_structure(file_path: str):
    """Check the structure of the Excel file."""
    print("\n" + "="*70)
    print("CHECKING EXCEL FILE STRUCTURE")
    print("="*70)
    
    try:
        excel_file = pd.ExcelFile(file_path)
        print(f"\nFile: {file_path}")
        print(f"Sheets found: {len(excel_file.sheet_names)}")
        print(f"Sheet names: {', '.join(excel_file.sheet_names)}")
        
        first_sheet = excel_file.sheet_names[0]
        df = pd.read_excel(file_path, sheet_name=first_sheet, nrows=5)
        
        print(f"\nFirst sheet: {first_sheet}")
        print(f"Columns: {list(df.columns)}")
        print(f"\nFirst 5 rows:")
        print(df.to_string())
        
        print(f"\nColumn D (index 3) - Amount column:")
        print(df.iloc[:, 3])
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def convert_excel_to_json(df: pd.DataFrame, sheet_name: str) -> dict:
    """Convert Excel DataFrame to Experian JSON format."""
    transactions = []
    
    for idx, row in df.iterrows():
        try:
            if pd.isna(row.iloc[0]) or pd.isna(row.iloc[3]):
                continue
            
            date = pd.to_datetime(row.iloc[0])
            amount = float(row.iloc[3])
            description = str(row.iloc[1]) if not pd.isna(row.iloc[1]) else "Transaction"
            category_value = row.iloc[2] if not pd.isna(row.iloc[2]) else 0
            
            if isinstance(category_value, (int, float)):
                category_id = int(category_value)
                category_title = f"Category_{category_id}"
            else:
                category_id = 0
                category_title = str(category_value)
            
            transaction = {
                'transaction_date': date.strftime('%Y-%m-%d'),
                'amount': amount,
                'category': {'id': category_id, 'title': category_title},
                'full_title': description,
                'title': description
            }
            
            transactions.append(transaction)
            
        except Exception as e:
            continue
    
    experian_json = {
        'response_status': 'Success',
        'return_data': {
            'fetched_data': {
                'fetch_accounts': [{
                    'account_id': sheet_name,
                    'title': f'Account {sheet_name}',
                    'currency': 'ZAR',
                    'transactions': transactions
                }]
            }
        }
    }
    
    return experian_json


def process_all_sheets(file_path: str, output_dir: str = 'output'):
    """Process all sheets in the Excel file."""
    print("\n" + "="*70)
    print("PROCESSING ALL SHEETS")
    print("="*70)
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    processor = ExperianProcessor()
    excel_file = pd.ExcelFile(file_path)
    all_results = []
    
    for sheet_name in excel_file.sheet_names:
        print(f"\n{'='*70}")
        print(f"Processing: {sheet_name}")
        print(f"{'='*70}")
        
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"  Rows: {len(df)}")
            
            experian_json = convert_excel_to_json(df, sheet_name)
            result = processor.process_customer(experian_json)
            result['sheet_name'] = sheet_name
            all_results.append(result)
            
            print(f"\n✓ {sheet_name} Results:")
            print(f"  Income: R{result['income']['monthly_amount']:,.2f}")
            print(f"  Expenses: R{result['expenses']['monthly_amount']:,.2f}")
            print(f"  Net: R{result['net_monthly_income']:,.2f}")
            print(f"  Recommendation: {result['recommendation']}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Save results
    json_file = output_path / 'results.json'
    with open(json_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n✓ Saved: {json_file}")
    
    csv_data = []
    for r in all_results:
        csv_data.append({
            'Sheet': r['sheet_name'],
            'Income': r['income']['monthly_amount'],
            'Expenses': r['expenses']['monthly_amount'],
            'Net': r['net_monthly_income'],
            'Recommendation': r['recommendation']
        })
    
    df_results = pd.DataFrame(csv_data)
    csv_file = output_path / 'results.csv'
    df_results.to_csv(csv_file, index=False)
    print(f"✓ Saved: {csv_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Processed: {len(all_results)} sheets")
    print(f"Average Income: R{sum(r['income']['monthly_amount'] for r in all_results) / len(all_results):,.2f}")
    print(f"Average Expenses: R{sum(r['expenses']['monthly_amount'] for r in all_results) / len(all_results):,.2f}")
    
    return all_results


def main():
    """Main execution."""
    print("="*70)
    print("PAYSPLIT EXCEL DATASET PROCESSOR")
    print("="*70)
    
    excel_path = Path("src/dataset_2.xlsx")
    
    if not excel_path.exists():
        print(f"\n❌ File not found: {excel_path}")
        print("\nSearching in other locations...")
        
        for path in ["data/dataset_2.xlsx", "dataset_2.xlsx"]:
            if Path(path).exists():
                excel_path = Path(path)
                print(f"✓ Found at: {path}")
                break
        else:
            print("\n❌ Could not find dataset_2.xlsx")
            return
    
    if not check_excel_structure(str(excel_path)):
        return
    
    print("\n" + "="*70)
    print("Continue with processing? (yes/no):")
    response = input().strip().lower()
    
    if response != 'yes':
        print("\nCancelled.")
        return
    
    process_all_sheets(str(excel_path))
    
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()