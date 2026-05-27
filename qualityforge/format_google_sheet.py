#!/usr/bin/env python3
"""
Format Google Sheet with styling copied from a reference spreadsheet.
Uses Google Sheets API via OAuth for desktop applications.
"""

import os
import json
import pickle
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Source spreadsheet (formatting guide)
SOURCE_SPREADSHEET_ID = "1M-hX9tNlGmXi-Efis05T35uftDkfR9w6QHg-kPM9h4g"
SOURCE_SHEET_ID = 1131357631

# Destination spreadsheet (to be formatted)
DEST_SPREADSHEET_ID = "1OwdsZEMWRS2hsweWGv546V14l4QhxV-KnIxjnBrsYSM"
DEST_SHEET_ID = 834261524


def get_credentials():
    """Get or refresh OAuth credentials."""
    creds = None
    token_path = Path.home() / '.cursor' / 'google_sheets_token.pickle'
    credentials_path = Path.home() / '.cursor' / 'google_credentials.json'
    
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                print(f"Error: OAuth credentials file not found at {credentials_path}")
                print("\nTo set up OAuth credentials:")
                print("1. Go to https://console.cloud.google.com/apis/credentials")
                print("2. Create OAuth 2.0 Client ID (Desktop application)")
                print("3. Download the JSON and save as ~/.cursor/google_credentials.json")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


def get_sheet_formatting(service, spreadsheet_id, sheet_id):
    """Get formatting data from a spreadsheet."""
    result = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        includeGridData=True,
        ranges=[f"Test Cases"]
    ).execute()
    
    return result


def create_formatting_requests(source_data, dest_sheet_id):
    """Create batchUpdate requests based on source formatting."""
    requests = []
    
    sheets = source_data.get('sheets', [])
    if not sheets:
        return requests
    
    sheet = sheets[0]
    grid_data = sheet.get('data', [{}])[0]
    row_data = grid_data.get('rowData', [])
    
    # Get column metadata for widths
    column_metadata = grid_data.get('columnMetadata', [])
    
    # Apply column widths
    for col_idx, col_meta in enumerate(column_metadata):
        pixel_size = col_meta.get('pixelSize', 100)
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": dest_sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": col_idx,
                    "endIndex": col_idx + 1
                },
                "properties": {"pixelSize": pixel_size},
                "fields": "pixelSize"
            }
        })
    
    # Apply row formatting
    for row_idx, row in enumerate(row_data):
        cells = row.get('values', [])
        for col_idx, cell in enumerate(cells):
            user_format = cell.get('userEnteredFormat', {})
            if not user_format:
                continue
            
            # Build the cell format
            cell_format = {}
            fields = []
            
            if 'backgroundColor' in user_format:
                cell_format['backgroundColor'] = user_format['backgroundColor']
                fields.append('userEnteredFormat.backgroundColor')
            
            if 'textFormat' in user_format:
                cell_format['textFormat'] = user_format['textFormat']
                fields.append('userEnteredFormat.textFormat')
            
            if 'horizontalAlignment' in user_format:
                cell_format['horizontalAlignment'] = user_format['horizontalAlignment']
                fields.append('userEnteredFormat.horizontalAlignment')
            
            if 'verticalAlignment' in user_format:
                cell_format['verticalAlignment'] = user_format['verticalAlignment']
                fields.append('userEnteredFormat.verticalAlignment')
            
            if 'wrapStrategy' in user_format:
                cell_format['wrapStrategy'] = user_format['wrapStrategy']
                fields.append('userEnteredFormat.wrapStrategy')
            
            if 'borders' in user_format:
                cell_format['borders'] = user_format['borders']
                fields.append('userEnteredFormat.borders')
            
            if cell_format and fields:
                requests.append({
                    "repeatCell": {
                        "range": {
                            "sheetId": dest_sheet_id,
                            "startRowIndex": row_idx,
                            "endRowIndex": row_idx + 1,
                            "startColumnIndex": col_idx,
                            "endColumnIndex": col_idx + 1
                        },
                        "cell": {"userEnteredFormat": cell_format},
                        "fields": ",".join(fields)
                    }
                })
    
    # Get sheet properties for frozen rows/columns
    sheet_props = sheet.get('properties', {})
    grid_props = sheet_props.get('gridProperties', {})
    
    frozen_row_count = grid_props.get('frozenRowCount', 0)
    frozen_col_count = grid_props.get('frozenColumnCount', 0)
    
    if frozen_row_count > 0 or frozen_col_count > 0:
        frozen_props = {}
        if frozen_row_count > 0:
            frozen_props['frozenRowCount'] = frozen_row_count
        if frozen_col_count > 0:
            frozen_props['frozenColumnCount'] = frozen_col_count
        
        requests.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": dest_sheet_id,
                    "gridProperties": frozen_props
                },
                "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"
            }
        })
    
    return requests


def apply_header_formatting(dest_sheet_id, num_columns):
    """Create requests to apply header formatting (dark gray bg, white bold text)."""
    return [
        {
            "repeatCell": {
                "range": {
                    "sheetId": dest_sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": num_columns
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.204, "green": 0.204, "blue": 0.204},
                        "textFormat": {
                            "bold": True,
                            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                            "fontSize": 10
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
            }
        }
    ]


def apply_data_formatting(dest_sheet_id, num_columns, num_rows):
    """Create requests to apply data row formatting (top alignment, wrap text)."""
    return [
        {
            "repeatCell": {
                "range": {
                    "sheetId": dest_sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 0,
                    "endColumnIndex": num_columns
                },
                "cell": {
                    "userEnteredFormat": {
                        "verticalAlignment": "TOP",
                        "wrapStrategy": "WRAP"
                    }
                },
                "fields": "userEnteredFormat(verticalAlignment,wrapStrategy)"
            }
        }
    ]


def main():
    print("Google Sheets Formatting Copier")
    print("=" * 50)
    print(f"Source: {SOURCE_SPREADSHEET_ID}")
    print(f"Destination: {DEST_SPREADSHEET_ID}")
    print()
    
    # Get credentials
    creds = get_credentials()
    if not creds:
        return 1
    
    # Build service
    service = build('sheets', 'v4', credentials=creds)
    
    # Get source spreadsheet formatting
    print("Fetching formatting from source spreadsheet...")
    source_data = get_sheet_formatting(service, SOURCE_SPREADSHEET_ID, SOURCE_SHEET_ID)
    
    # Get destination metadata to know dimensions
    dest_meta = service.spreadsheets().get(
        spreadsheetId=DEST_SPREADSHEET_ID
    ).execute()
    
    dest_sheet = dest_meta['sheets'][0]
    dest_grid_props = dest_sheet['properties'].get('gridProperties', {})
    num_rows = dest_grid_props.get('rowCount', 1000)
    num_columns = dest_grid_props.get('columnCount', 13)
    
    print(f"Destination sheet has {num_rows} rows and {num_columns} columns")
    
    # Create formatting requests
    print("Creating formatting requests...")
    requests = create_formatting_requests(source_data, DEST_SHEET_ID)
    
    # Add header and data formatting
    requests.extend(apply_header_formatting(DEST_SHEET_ID, num_columns))
    requests.extend(apply_data_formatting(DEST_SHEET_ID, num_columns, num_rows))
    
    # Freeze header row
    requests.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": DEST_SHEET_ID,
                "gridProperties": {"frozenRowCount": 1}
            },
            "fields": "gridProperties.frozenRowCount"
        }
    })
    
    print(f"Generated {len(requests)} formatting requests")
    
    # Apply formatting
    print("Applying formatting to destination spreadsheet...")
    result = service.spreadsheets().batchUpdate(
        spreadsheetId=DEST_SPREADSHEET_ID,
        body={"requests": requests}
    ).execute()
    
    print(f"Successfully applied {len(result.get('replies', []))} formatting changes!")
    print(f"\nView the formatted spreadsheet at:")
    print(f"https://docs.google.com/spreadsheets/d/{DEST_SPREADSHEET_ID}/edit")
    
    return 0


if __name__ == "__main__":
    exit(main())
