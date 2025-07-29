import gspread
import csv
import os
import tempfile
import json
from typing import List, Dict
from .get_secrets import get_secrets


def export_worksheet_to_csv(
    worksheet_key: str,
    worksheet_name: str,
    output_path: str,
    credentials_secret_name: str = 'google_sheets_api_key'
) -> None:
    """
    Export a Google Sheets worksheet to a CSV file.
    """
    try:
        creds_json = get_secrets(credentials_secret_name)
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as tmp:
            if isinstance(creds_json, (dict, list)):
                tmp.write(json.dumps(creds_json))
            elif isinstance(creds_json, bytes):
                tmp.write(creds_json.decode())
            else:
                tmp.write(creds_json)
            tmp_path = tmp.name
        gc = gspread.service_account(filename=tmp_path)
        worksheet = gc.open_by_key(worksheet_key).worksheet(worksheet_name)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(worksheet.get_all_values())
    except gspread.exceptions.WorksheetNotFound:
        raise ValueError(f"Worksheet '{worksheet_name}' not found in sheet '{worksheet_key}'")
    except gspread.exceptions.SpreadsheetNotFound:
        raise ValueError(f"Spreadsheet with key '{worksheet_key}' not found or permission denied.")
    except Exception as e:
        raise RuntimeError(f"Failed to export worksheet: {e}")
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)

def export_worksheets_to_csv(
    worksheet_key: str,
    worksheet_configs: List[Dict],
    credentials_secret_name: str = 'google_sheets_api_key'
) -> None:
    """
    Export multiple worksheets from a Google Sheet to CSV files.
    worksheet_configs: List of dicts with keys:
        - name: worksheet name
        - output_path: where to save the CSV
    """
    for config in worksheet_configs:
        if 'name' not in config or 'output_path' not in config:
            raise ValueError("Each worksheet config must have 'name' and 'output_path' keys.")
        export_worksheet_to_csv(
            worksheet_key=worksheet_key,
            worksheet_name=config['name'],
            output_path=config['output_path'],
            credentials_secret_name=credentials_secret_name
        )

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Export Google Sheets worksheet(s) to CSV')
    parser.add_argument('--worksheet-key', required=True, help='Google Sheet key/ID')
    parser.add_argument('--worksheet-name', help='Worksheet name to export (for single export)')
    parser.add_argument('--output-path', help='CSV output path (for single export)')
    parser.add_argument('--credentials-secret-name', default='google_sheets_api_key', help='Secret name for Google credentials')
    parser.add_argument('--multi', action='store_true', help='Export multiple worksheets (expects a JSON list of configs)')
    parser.add_argument('--worksheet-configs', help='JSON string: list of {"name": ..., "output_path": ...}')

    args = parser.parse_args()

    if args.multi:
        import json
        if not args.worksheet_configs:
            parser.error('--worksheet-configs is required when using --multi')
        worksheet_configs = json.loads(args.worksheet_configs)
        export_worksheets_to_csv(
            worksheet_key=args.worksheet_key,
            worksheet_configs=worksheet_configs,
            credentials_secret_name=args.credentials_secret_name
        )
    else:
        if not args.worksheet_name or not args.output_path:
            parser.error('--worksheet-name and --output-path are required for single export')
        export_worksheet_to_csv(
            worksheet_key=args.worksheet_key,
            worksheet_name=args.worksheet_name,
            output_path=args.output_path,
            credentials_secret_name=args.credentials_secret_name
        )

if __name__ == "__main__":
    main() 