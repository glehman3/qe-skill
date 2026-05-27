#!/usr/bin/env python3
"""
Setup Test Jam Google Sheet with tabs, formatting, and test cases.
Creates individual tester tabs and populates them with assigned test cases.
Uses Google Sheets API via OAuth - reuses credentials from google-drive-mcp.
"""

import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# OAuth scopes - use full access for tab creation
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# OAuth client credentials — set via environment variables or credentials file
CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
CREDENTIALS_FILE = os.environ.get(
    "GOOGLE_OAUTH_CREDENTIALS_FILE",
    str(Path.home() / ".config" / "google-drive-mcp" / "credentials.json"),
)

# Token file path (reuse from google-drive-mcp)
TOKEN_FILE = Path.home() / '.google-drive-mcp' / 'oauth_token.json'

# Reference spreadsheet (formatting guide)
REFERENCE_SPREADSHEET_ID = "1ExampleReferenceSpreadsheetId000000000"

# Source spreadsheet (test cases)
SOURCE_SPREADSHEET_ID = "1ExampleSourceSpreadsheetId00000000000"

# Destination spreadsheet (Test Jam to be created)
DEST_SPREADSHEET_ID = "1ExampleDestSpreadsheetId000000000000"

# Tester assignments
TESTERS = [
    {"name": "Jordan Blake", "tab": "jordan_blake", "tests": ["TC-001", "TC-004", "TC-007", "TC-008", "TC-009", "TC-010", "TC-011", "TC-012"]},
    {"name": "Casey Reed", "tab": "casey_reed", "tests": ["TC-013", "TC-014", "TC-015", "TC-016", "TC-017", "TC-018", "TC-019", "TC-020"]},
    {"name": "Alex Morgan", "tab": "alex_morgan", "tests": ["TC-021", "TC-022", "TC-023", "TC-024", "TC-025", "TC-026", "TC-027", "TC-028"]},
    {"name": "Riley Chen", "tab": "riley_chen", "tests": ["TC-029", "TC-031", "TC-033", "TC-034", "TC-035", "TC-036", "TC-037", "TC-038"]},
    {"name": "Sam Foster", "tab": "sam_foster", "tests": ["TC-039", "TC-040", "TC-041", "TC-042", "TC-043", "TC-044", "TC-045", "TC-046", "TC-047"]},
    {"name": "Taylor Brooks", "tab": "taylor_brooks", "tests": ["TC-048", "TC-049", "TC-051", "TC-052", "TC-053", "TC-057", "TC-058", "TC-059"]},
    {"name": "Morgan Ellis", "tab": "morgan_ellis", "tests": ["TC-060", "TC-061", "TC-062", "TC-063", "TC-064", "TC-065", "TC-066", "TC-071", "TC-072"]},
    {"name": "Jamie Patel", "tab": "jamie_patel", "tests": ["TC-076", "TC-078", "TC-080", "TC-083", "TC-085", "TC-086", "TC-087", "TC-088"]},
]

# Tab column structure for tester sheets
TESTER_COLUMNS = ["ID", "Component", "Objective", "Conditions", "Steps to Test", "Expected Results", "Tester", "Testing Evidence", "Results"]

# Column widths for tester sheets (in pixels)
TESTER_COLUMN_WIDTHS = [80, 150, 250, 250, 300, 350, 120, 200, 100]


def get_credentials():
    """Get or refresh OAuth credentials from google-drive-mcp token."""
    creds = None
    
    # Try to load existing token from google-drive-mcp
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
            
            creds = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                scopes=token_data.get('scopes', SCOPES)
            )
        except Exception as e:
            print(f"Warning: Could not load token: {e}")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
            # Save refreshed token
            _save_token(creds)
        else:
            # Need to authenticate
            print("No valid token found. Running OAuth flow...")
            client_config = {
                "installed": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
            _save_token(creds)
    
    return creds


def _save_token(creds):
    """Save credentials to token file."""
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'scopes': creds.scopes,
        'expiry': creds.expiry.isoformat() if creds.expiry else None
    }
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)


def get_sheet_id_by_name(service, spreadsheet_id, sheet_name):
    """Get sheet ID by name."""
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in spreadsheet.get('sheets', []):
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    return None


def read_test_cases(service):
    """Read all test cases from source spreadsheet."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SOURCE_SPREADSHEET_ID,
        range="Test Cases!A:L"
    ).execute()
    
    rows = result.get('values', [])
    if not rows:
        return {}
    
    header = rows[0]
    test_cases = {}
    
    for row in rows[1:]:
        if not row:
            continue
        test_id = row[0] if row else ""
        if not test_id.startswith("TC-"):
            continue
        
        # Skip consolidated test cases
        status = row[7] if len(row) > 7 else ""
        if "CONSOLIDATED INTO" in status:
            continue
        
        # Map to tester tab format
        test_cases[test_id] = {
            "id": test_id,
            "component": row[2] if len(row) > 2 else "",
            "objective": row[3] if len(row) > 3 else "",
            "conditions": row[4] if len(row) > 4 else "",
            "steps": row[5] if len(row) > 5 else "",
            "expected": row[6] if len(row) > 6 else "",
        }
    
    return test_cases


def create_tabs(service):
    """Create all required tabs in destination spreadsheet."""
    print("Creating tabs...")
    
    # Get existing sheets
    spreadsheet = service.spreadsheets().get(spreadsheetId=DEST_SPREADSHEET_ID).execute()
    existing_sheets = {s['properties']['title']: s['properties']['sheetId'] for s in spreadsheet.get('sheets', [])}
    
    requests = []
    
    # Rename Sheet1 to Overview if it exists
    if "Sheet1" in existing_sheets:
        requests.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": existing_sheets["Sheet1"],
                    "title": "Overview"
                },
                "fields": "title"
            }
        })
        existing_sheets["Overview"] = existing_sheets.pop("Sheet1")
    
    # Tabs to create
    tabs_to_create = ["Test Accounts", "Bug Tracking"] + [t["tab"] for t in TESTERS]
    
    for tab_name in tabs_to_create:
        if tab_name not in existing_sheets:
            requests.append({
                "addSheet": {
                    "properties": {
                        "title": tab_name
                    }
                }
            })
    
    if requests:
        result = service.spreadsheets().batchUpdate(
            spreadsheetId=DEST_SPREADSHEET_ID,
            body={"requests": requests}
        ).execute()
        print(f"  Created/updated {len(requests)} tabs")
        
        # Update sheet IDs from response
        for reply in result.get('replies', []):
            if 'addSheet' in reply:
                props = reply['addSheet']['properties']
                existing_sheets[props['title']] = props['sheetId']
    
    return existing_sheets


def populate_overview(service, sheet_id):
    """Populate the Overview tab with Test Jam info."""
    print("Populating Overview tab...")
    
    overview_data = [
        ["", "Domain Authentication Test Jam 🥳"],
        [],
        ["", "Desired Outcomes:"],
        ["", "Collaborative hands-on event where teams come together to focus on testing the Domain Authentication experience. The goal is to uncover issues, generate insights, and strengthen overall quality."],
        [],
        ["", "Key Links:"],
        ["", "Feature Flags: \nfeature.streamlined_template_management"],
        ["", "Jira Project: https://jira.example.com/browse/HELIX"],
        ["", "Test Jam Bug Environments: Production"],
        ["", "Test Jam Bug Labels: tx_fy26_domain-authentication"],
        ["", "Figma Designs: https://www.figma.com/file/EXAMPLE/design-mockups"],
        [],
        ["", "Testers:"],
        ["", "Jordan Blake, Casey Reed, Alex Morgan, Riley Chen"],
        ["", "Sam Foster, Taylor Brooks, Morgan Ellis, Jamie Patel"],
        [],
        ["", "Instructions:"],
        ["", "1. Create test account with the test tool, ensuring feature flags are enabled"],
        ["", "2. Navigate to Transactional section and complete the onboarding flow"],
        ["", "3. Document results in your assigned tester tab"],
    ]
    
    service.spreadsheets().values().update(
        spreadsheetId=DEST_SPREADSHEET_ID,
        range="Overview!A1",
        valueInputOption="RAW",
        body={"values": overview_data}
    ).execute()


def populate_test_accounts(service, sheet_id):
    """Populate the Test Accounts tab."""
    print("Populating Test Accounts tab...")
    
    test_accounts_data = [
        ["Account ID", "Plan", "Username", "Password", "Status", "Assignee", "Account Test Tool", "Instructions:"],
        ["", "", "", "", "", "", "", "1. Create test account with the test tool"],
        ["", "", "", "", "", "", "", "2. Enable feature flags"],
        ["", "", "", "", "", "", "", "3. Log in and navigate to Transactional"],
    ]
    
    service.spreadsheets().values().update(
        spreadsheetId=DEST_SPREADSHEET_ID,
        range="Test Accounts!A1",
        valueInputOption="RAW",
        body={"values": test_accounts_data}
    ).execute()


def populate_bug_tracking(service, sheet_id):
    """Populate the Bug Tracking tab."""
    print("Populating Bug Tracking tab...")
    
    bug_tracking_data = [
        ["Bug Description", "Jira Link", "Priority", "Status", "Notes", "", "Key"],
        ["", "", "", "", "", "", "Severity"],
        ["", "", "", "", "", "", "P0 - Critical blocker"],
        ["", "", "", "", "", "", "P1 - Major issue"],
        ["", "", "", "", "", "", "P2 - Moderate issue"],
        ["", "", "", "", "", "", "P3 - Minor issue"],
    ]
    
    service.spreadsheets().values().update(
        spreadsheetId=DEST_SPREADSHEET_ID,
        range="Bug Tracking!A1",
        valueInputOption="RAW",
        body={"values": bug_tracking_data}
    ).execute()


def populate_tester_tab(service, tester, test_cases, sheet_id):
    """Populate a tester's tab with their assigned test cases."""
    print(f"  Populating {tester['tab']}...")
    
    rows = [TESTER_COLUMNS]
    
    for test_id in tester["tests"]:
        tc = test_cases.get(test_id)
        if tc:
            rows.append([
                tc["id"],
                tc["component"],
                tc["objective"],
                tc["conditions"],
                tc["steps"],
                tc["expected"],
                tester["name"],
                "",  # Testing Evidence
                "NOT STARTED"  # Results
            ])
    
    if rows:
        service.spreadsheets().values().update(
            spreadsheetId=DEST_SPREADSHEET_ID,
            range=f"{tester['tab']}!A1",
            valueInputOption="RAW",
            body={"values": rows}
        ).execute()


def apply_header_formatting(sheet_id, num_columns):
    """Create formatting request for header row."""
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
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


def apply_data_formatting(sheet_id, num_columns, num_rows):
    """Create formatting request for data rows."""
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
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


def apply_column_widths(sheet_id, widths):
    """Create formatting requests for column widths."""
    requests = []
    for col_idx, width in enumerate(widths):
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": col_idx,
                    "endIndex": col_idx + 1
                },
                "properties": {"pixelSize": width},
                "fields": "pixelSize"
            }
        })
    return requests


def freeze_header_row(sheet_id):
    """Create formatting request to freeze header row."""
    return {
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {"frozenRowCount": 1}
            },
            "fields": "gridProperties.frozenRowCount"
        }
    }


def apply_formatting(service, sheet_ids):
    """Apply formatting to all tabs."""
    print("Applying formatting...")
    
    requests = []
    
    # Format tester tabs
    for tester in TESTERS:
        sheet_id = sheet_ids.get(tester["tab"])
        if sheet_id is not None:
            num_cols = len(TESTER_COLUMNS)
            num_rows = len(tester["tests"]) + 1
            
            requests.append(apply_header_formatting(sheet_id, num_cols))
            requests.append(apply_data_formatting(sheet_id, num_cols, num_rows + 10))
            requests.extend(apply_column_widths(sheet_id, TESTER_COLUMN_WIDTHS))
            requests.append(freeze_header_row(sheet_id))
    
    # Format Test Accounts tab
    test_accounts_id = sheet_ids.get("Test Accounts")
    if test_accounts_id is not None:
        requests.append(apply_header_formatting(test_accounts_id, 8))
        requests.append(freeze_header_row(test_accounts_id))
    
    # Format Bug Tracking tab
    bug_tracking_id = sheet_ids.get("Bug Tracking")
    if bug_tracking_id is not None:
        requests.append(apply_header_formatting(bug_tracking_id, 5))
        requests.append(freeze_header_row(bug_tracking_id))
    
    if requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=DEST_SPREADSHEET_ID,
            body={"requests": requests}
        ).execute()
        print(f"  Applied {len(requests)} formatting changes")


def main():
    print("=" * 60)
    print("Test Jam Sheet Setup")
    print("=" * 60)
    print(f"Source (test cases): {SOURCE_SPREADSHEET_ID}")
    print(f"Reference (formatting): {REFERENCE_SPREADSHEET_ID}")
    print(f"Destination: {DEST_SPREADSHEET_ID}")
    print()
    
    # Get credentials
    creds = get_credentials()
    if not creds:
        return 1
    
    # Build service
    service = build('sheets', 'v4', credentials=creds)
    
    # Read test cases from source
    print("Reading test cases from source spreadsheet...")
    test_cases = read_test_cases(service)
    print(f"  Found {len(test_cases)} active test cases")
    
    # Create tabs
    sheet_ids = create_tabs(service)
    
    # Populate Overview
    populate_overview(service, sheet_ids.get("Overview"))
    
    # Populate Test Accounts
    populate_test_accounts(service, sheet_ids.get("Test Accounts"))
    
    # Populate Bug Tracking
    populate_bug_tracking(service, sheet_ids.get("Bug Tracking"))
    
    # Populate tester tabs
    print("Populating tester tabs...")
    for tester in TESTERS:
        populate_tester_tab(service, tester, test_cases, sheet_ids.get(tester["tab"]))
    
    # Apply formatting
    apply_formatting(service, sheet_ids)
    
    print()
    print("=" * 60)
    print("Setup complete!")
    print(f"View the Test Jam spreadsheet at:")
    print(f"https://docs.google.com/spreadsheets/d/{DEST_SPREADSHEET_ID}/edit")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
