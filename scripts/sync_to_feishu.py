#!/usr/bin/env python3
"""
Sync trending repositories to Feishu Bitable (多维表格).
Supports automatic creation of bitable and fields.
Official API documentation: https://open.feishu.cn/document/server-docs/docs/bitable-v1/bitable-overview
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

FIELD_DEFINITIONS = [
    {"field_name": "项目名称", "type": 1},
    {"field_name": "描述", "type": 3},
    {"field_name": "Stars", "type": 2},
    {"field_name": "Forks", "type": 2},
    {"field_name": "语言", "type": 3},
    {"field_name": "链接", "type": 15},
    {"field_name": "作者", "type": 1},
    {"field_name": "标签", "type": 1},
    {"field_name": "更新时间", "type": 5},
    {"field_name": "是否已读", "type": 7},
    {"field_name": "是否关注", "type": 7},
    {"field_name": "备注", "type": 3},
]

def get_env_vars():
    """Get required environment variables."""
    return {
        "app_id": os.environ.get("FEISHU_APP_ID"),
        "app_secret": os.environ.get("FEISHU_APP_SECRET"),
        "base_id": os.environ.get("FEISHU_BASE_ID"),
        "table_id": os.environ.get("FEISHU_TABLE_ID"),
    }

def validate_config(config: dict, require_table: bool = True) -> bool:
    """Validate that all required config is present."""
    required = ["app_id", "app_secret"]
    if require_table:
        required.extend(["base_id", "table_id"])
    
    missing = [k for k in required if not config.get(k)]
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        return False
    return True

def make_feishu_request(url: str, token: str = None, data: dict = None, method: str = "POST") -> dict:
    """Make a request to Feishu API."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = json.dumps(data).encode("utf-8") if data else None
    request = Request(url, data=body, headers=headers, method=method)
    
    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("code") != 0:
                print(f"Feishu API error: {result}", file=sys.stderr)
            return result
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"HTTP error: {e.code} - {e.reason}", file=sys.stderr)
        print(f"Response: {error_body}", file=sys.stderr)
        raise
    except URLError as e:
        print(f"Network error: {e}", file=sys.stderr)
        raise

def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    """Get tenant access token for API authentication."""
    url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    data = {"app_id": app_id, "app_secret": app_secret}
    
    result = make_feishu_request(url, data=data)
    
    if result.get("code") != 0:
        raise Exception(f"Failed to get token: {result.get('msg')}")
    
    return result["tenant_access_token"]

def create_bitable(token: str, name: str = "GitHub AI Skill 热门项目") -> dict:
    """Create a new bitable (多维表格)."""
    url = f"{FEISHU_API_BASE}/bitable/v1/apps"
    
    data = {"app": {"name": name}}
    
    result = make_feishu_request(url, token=token, data=data)
    
    if result.get("code") == 0:
        app = result.get("data", {}).get("app", {})
        print(f"Created bitable: {name}", file=sys.stderr)
        print(f"  App Token (Base ID): {app.get('app_token')}", file=sys.stderr)
        return app
    else:
        raise Exception(f"Failed to create bitable: {result.get('msg')}")

def get_default_table(token: str, base_id: str) -> dict | None:
    """Get the default table in a bitable."""
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{base_id}/tables"
    
    result = make_feishu_request(url, token=token, method="GET")
    
    if result.get("code") == 0:
        tables = result.get("data", {}).get("items", [])
        if tables:
            return tables[0]
    return None

def create_table(token: str, base_id: str, name: str = "热门项目") -> dict:
    """Create a new table in the bitable."""
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{base_id}/tables"
    
    default_fields = [
        {"field_name": "项目名称", "type": 1}
    ]
    
    data = {
        "table": {
            "name": name,
            "default_field_names": ["项目名称"]
        }
    }
    
    result = make_feishu_request(url, token=token, data=data)
    
    if result.get("code") == 0:
        table = result.get("data", {}).get("table", {})
        print(f"Created table: {name}", file=sys.stderr)
        return table
    else:
        raise Exception(f"Failed to create table: {result.get('msg')}")

def get_table_fields(token: str, base_id: str, table_id: str) -> dict:
    """Get existing fields in the table."""
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{base_id}/tables/{table_id}/fields"
    result = make_feishu_request(url, token=token, method="GET")
    
    if result.get("code") != 0:
        return {}
    
    return {field["field_name"]: field for field in result.get("data", {}).get("items", [])}

def create_field(token: str, base_id: str, table_id: str, field_def: dict) -> bool:
    """Create a new field in the table."""
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{base_id}/tables/{table_id}/fields"
    
    data = {"field": field_def}
    
    result = make_feishu_request(url, token=token, data=data)
    
    if result.get("code") == 0:
        print(f"  Created field: {field_def['field_name']}", file=sys.stderr)
        return True
    else:
        print(f"  Failed to create field {field_def['field_name']}: {result.get('msg')}", file=sys.stderr)
        return False

def ensure_fields_exist(token: str, base_id: str, table_id: str) -> bool:
    """Ensure all required fields exist in the table."""
    print("Checking table fields...", file=sys.stderr)
    
    existing_fields = get_table_fields(token, base_id, table_id)
    
    missing_fields = []
    for field_def in FIELD_DEFINITIONS:
        if field_def["field_name"] not in existing_fields:
            missing_fields.append(field_def)
    
    if not missing_fields:
        print("All fields exist.", file=sys.stderr)
        return True
    
    print(f"Creating {len(missing_fields)} missing fields...", file=sys.stderr)
    
    success = True
    for field_def in missing_fields:
        if not create_field(token, base_id, table_id, field_def):
            success = False
        time.sleep(0.3)
    
    return success

def search_existing_record(token: str, base_id: str, table_id: str, repo_full_name: str) -> str | None:
    """Search for existing record by repository full name."""
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{base_id}/tables/{table_id}/records/search"
    
    data = {
        "view_id": "",
        "field_names": ["项目名称"],
        "sort": [],
        "filter": {
            "conjunction": "and",
            "conditions": [
                {
                    "field_name": "项目名称",
                    "operator": "is",
                    "value": [repo_full_name]
                }
            ]
        },
        "automatic_fields": False
    }
    
    result = make_feishu_request(url, token=token, data=data)
    
    if result.get("code") == 0:
        items = result.get("data", {}).get("items", [])
        if items:
            return items[0].get("record_id")
    return None

def create_record(token: str, base_id: str, table_id: str, repo: dict, existing_fields: dict) -> bool:
    """Create a new record in the bitable."""
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{base_id}/tables/{table_id}/records"
    
    fields = {}
    
    if "项目名称" in existing_fields:
        fields["项目名称"] = repo["full_name"]
    if "描述" in existing_fields:
        fields["描述"] = repo.get("description", "")[:2000] if repo.get("description") else ""
    if "Stars" in existing_fields:
        fields["Stars"] = repo.get("stargazers_count", 0)
    if "Forks" in existing_fields:
        fields["Forks"] = repo.get("forks_count", 0)
    if "语言" in existing_fields:
        fields["语言"] = repo.get("language", "Unknown")
    if "链接" in existing_fields:
        fields["链接"] = {
            "link": repo["html_url"],
            "text": repo["name"]
        }
    if "作者" in existing_fields:
        fields["作者"] = repo.get("owner", {}).get("login", "")
    if "标签" in existing_fields and repo.get("topics"):
        fields["标签"] = ", ".join(repo["topics"][:10])
    if "更新时间" in existing_fields:
        fields["更新时间"] = int(datetime.now(timezone.utc).timestamp() * 1000)
    
    data = {"fields": fields}
    
    result = make_feishu_request(url, token=token, data=data)
    
    if result.get("code") == 0:
        print(f"  Created: {repo['full_name']}", file=sys.stderr)
        return True
    else:
        print(f"  Failed to create {repo['full_name']}: {result.get('msg')}", file=sys.stderr)
        return False

def update_record(token: str, base_id: str, table_id: str, record_id: str, repo: dict, existing_fields: dict) -> bool:
    """Update an existing record."""
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{base_id}/tables/{table_id}/records/{record_id}"
    
    fields = {}
    
    if "Stars" in existing_fields:
        fields["Stars"] = repo.get("stargazers_count", 0)
    if "Forks" in existing_fields:
        fields["Forks"] = repo.get("forks_count", 0)
    if "更新时间" in existing_fields:
        fields["更新时间"] = int(datetime.now(timezone.utc).timestamp() * 1000)
    
    data = {"fields": fields}
    
    result = make_feishu_request(url, token=token, data=data, method="PUT")
    
    if result.get("code") == 0:
        print(f"  Updated: {repo['full_name']}", file=sys.stderr)
        return True
    else:
        print(f"  Failed to update {repo['full_name']}: {result.get('msg')}", file=sys.stderr)
        return False

def setup_bitable(token: str) -> dict:
    """Create a new bitable with default table and fields."""
    print("\n" + "="*50, file=sys.stderr)
    print("Creating new bitable...", file=sys.stderr)
    print("="*50, file=sys.stderr)
    
    app = create_bitable(token, "GitHub AI Skill 热门项目")
    base_id = app.get("app_token")
    
    if not base_id:
        raise Exception("Failed to get app_token from created bitable")
    
    time.sleep(1)
    
    table = get_default_table(token, base_id)
    if not table:
        table = create_table(token, base_id, "热门项目")
    
    table_id = table.get("table_id")
    
    if not table_id:
        raise Exception("Failed to get table_id")
    
    time.sleep(0.5)
    
    ensure_fields_exist(token, base_id, table_id)
    
    print("\n" + "="*50, file=sys.stderr)
    print("Bitable created successfully!", file=sys.stderr)
    print("="*50, file=sys.stderr)
    print(f"\nPlease add these to your GitHub Secrets:", file=sys.stderr)
    print(f"  FEISHU_BASE_ID = {base_id}", file=sys.stderr)
    print(f"  FEISHU_TABLE_ID = {table_id}", file=sys.stderr)
    print(f"\nBitable URL: https://feishu.cn/base/{base_id}", file=sys.stderr)
    print("="*50 + "\n", file=sys.stderr)
    
    return {
        "base_id": base_id,
        "table_id": table_id
    }

def sync_to_feishu(repos: list, config: dict) -> dict:
    """Sync repositories to Feishu Bitable."""
    if not config.get("app_id") or not config.get("app_secret"):
        return {"success": False, "error": "Missing app_id or app_secret"}
    
    print("Getting Feishu access token...", file=sys.stderr)
    token = get_tenant_access_token(config["app_id"], config["app_secret"])
    
    base_id = config.get("base_id")
    table_id = config.get("table_id")
    
    if not base_id or not table_id:
        print("\nNo base_id or table_id provided. Creating new bitable...", file=sys.stderr)
        result = setup_bitable(token)
        base_id = result["base_id"]
        table_id = result["table_id"]
    else:
        ensure_fields_exist(token, base_id, table_id)
    
    existing_fields = get_table_fields(token, base_id, table_id)
    
    print(f"\nSyncing {len(repos)} repositories to Feishu Bitable...", file=sys.stderr)
    
    created = 0
    updated = 0
    failed = 0
    
    for i, repo in enumerate(repos):
        try:
            existing_id = search_existing_record(token, base_id, table_id, repo["full_name"])
            
            if existing_id:
                if update_record(token, base_id, table_id, existing_id, repo, existing_fields):
                    updated += 1
                else:
                    failed += 1
            else:
                if create_record(token, base_id, table_id, repo, existing_fields):
                    created += 1
                else:
                    failed += 1
            
            if (i + 1) % 5 == 0:
                time.sleep(0.5)
                
        except Exception as e:
            print(f"  Error processing {repo['full_name']}: {e}", file=sys.stderr)
            failed += 1
    
    print(f"\nSync complete: {created} created, {updated} updated, {failed} failed", file=sys.stderr)
    
    return {
        "success": True,
        "created": created,
        "updated": updated,
        "failed": failed,
        "base_id": base_id,
        "table_id": table_id
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync trending repos to Feishu Bitable")
    parser.add_argument("-i", "--input", default="trending.json", help="Input JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Test without syncing")
    parser.add_argument("--create-table", action="store_true", help="Create new bitable (no base_id/table_id needed)")
    args = parser.parse_args()
    
    config = get_env_vars()
    
    if args.create_table:
        if not config.get("app_id") or not config.get("app_secret"):
            print("Error: FEISHU_APP_ID and FEISHU_APP_SECRET are required", file=sys.stderr)
            return 1
        
        print("Getting Feishu access token...", file=sys.stderr)
        token = get_tenant_access_token(config["app_id"], config["app_secret"])
        setup_bitable(token)
        return 0
    
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1
    
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    repos = data.get("repositories", [])
    
    if args.dry_run:
        print(f"Dry run: would sync {len(repos)} repositories", file=sys.stderr)
        print(f"Config: {list(config.keys())}", file=sys.stderr)
        return 0
    
    result = sync_to_feishu(repos, config)
    
    if result["success"]:
        return 0
    else:
        print(f"Sync failed: {result.get('error')}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
