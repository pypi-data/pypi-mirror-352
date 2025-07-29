import contextlib
import json
from pathlib import Path
import secrets
import string
import time
from typing import Any

from jinja2 import Environment, FileSystemLoader


class APIGenerationError(Exception):
    """Custom exception for API generation errors."""

    pass


TEMPLATE_DIR = Path(__file__).parent / "templates"
if not TEMPLATE_DIR.is_dir():
    TEMPLATE_DIR = Path("src/mockloop_mcp/templates")
    if not TEMPLATE_DIR.is_dir():
        raise APIGenerationError("Template directory not found at expected locations.")

# Note: autoescape=False is intentional here as we're generating Python code, not HTML
# This is safe because we control all template inputs and don't render user-provided content
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)  # noqa: S701 # nosec B701

# Add base64 encode filter for admin UI template
import base64
def b64encode_filter(s):
    """Base64 encode filter for Jinja2 templates"""
    if isinstance(s, str):
        s = s.encode('utf-8')
    return base64.b64encode(s).decode('ascii')

jinja_env.filters['b64encode'] = b64encode_filter

# Add Python boolean conversion filter
def python_bool_filter(value):
    """Convert JavaScript-style boolean values to Python boolean values"""
    if isinstance(value, str):
        js_to_python = {'true': True, 'false': False, 'null': None}
        return js_to_python.get(value, value)
    return value

def convert_js_to_python(obj):
    """Recursively convert JavaScript-style boolean values to Python values"""
    if isinstance(obj, dict):
        return {k: convert_js_to_python(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_js_to_python(item) for item in obj]
    elif isinstance(obj, str):
        js_to_python = {'true': True, 'false': False, 'null': None}
        return js_to_python.get(obj, obj)
    return obj

jinja_env.filters['python_bool'] = python_bool_filter
jinja_env.filters['convert_js_to_python'] = convert_js_to_python


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "on")
    if isinstance(value, int):
        return value != 0
    return bool(value)


def _generate_mock_data_from_schema(schema: dict[str, Any]) -> Any:
    if not schema:
        return None
    schema_type = schema.get("type")
    if schema_type == "string":
        format_type = schema.get("format", "")
        if format_type == "date-time":
            return "2023-01-01T00:00:00Z"
        if format_type == "date":
            return "2023-01-01"
        if format_type == "email":
            return "user@example.com"
        if format_type == "uuid":
            return "00000000-0000-0000-0000-000000000000"
        length = schema.get("minLength", 5)
        if schema.get("maxLength") and schema.get("maxLength") < length:
            length = schema.get("maxLength")
        return "".join(secrets.choice(string.ascii_letters) for _ in range(length))
    if schema_type in {"number", "integer"}:
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 100)
        return (
            secrets.randbelow(maximum - minimum + 1) + minimum
            if schema_type == "integer"
            else round(
                secrets.randbelow(int((maximum - minimum) * 100)) / 100 + minimum, 2
            )
        )
    if schema_type == "boolean":
        return secrets.choice([True, False])
    if schema_type == "array":
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 1)
        max_items = schema.get("maxItems", 3)
        num_items = secrets.randbelow(max_items - min_items + 1) + min_items
        return [_generate_mock_data_from_schema(items_schema) for _ in range(num_items)]
    if schema_type == "object":
        result = {}
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for prop_name, prop_schema in properties.items():
            if prop_name in required or secrets.randbelow(10) > 2:
                result[prop_name] = _generate_mock_data_from_schema(prop_schema)
        return result
    if "$ref" in schema:
        return {"$ref_placeholder": schema["$ref"]}
    for key in ["oneOf", "anyOf"]:
        if key in schema and isinstance(schema[key], list) and len(schema[key]) > 0:
            return _generate_mock_data_from_schema(secrets.choice(schema[key]))
    if (
        "allOf" in schema
        and isinstance(schema["allOf"], list)
        and len(schema["allOf"]) > 0
    ):
        merged_schema = {}
        for sub_schema in schema["allOf"]:
            if isinstance(sub_schema, dict):
                merged_schema.update(sub_schema)
        return _generate_mock_data_from_schema(merged_schema)
    return "mock_data"


def generate_mock_api(
    spec_data: dict[str, Any],
    output_base_dir: str | Path | None = None,
    mock_server_name: str | None = None,
    auth_enabled: Any = True,
    webhooks_enabled: Any = True,
    admin_ui_enabled: Any = True,
    storage_enabled: Any = True,
    business_port: int = 8000,
    admin_port: int | None = None,
) -> Path:
    auth_enabled_bool = _to_bool(auth_enabled)
    webhooks_enabled_bool = _to_bool(webhooks_enabled)
    admin_ui_enabled_bool = _to_bool(admin_ui_enabled)
    storage_enabled_bool = _to_bool(storage_enabled)

    # Set admin port to business_port + 1 if not specified
    if admin_port is None:
        admin_port = business_port + 1

    try:
        api_title = (
            spec_data.get("info", {})
            .get("title", "mock_api")
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )
        api_version = (
            spec_data.get("info", {}).get("version", "v1").lower().replace(".", "_")
        )

        _mock_server_name = mock_server_name
        if not _mock_server_name:
            _mock_server_name = f"{api_title}_{api_version}_{int(time.time())}"

        _mock_server_name = "".join(
            c if c.isalnum() or c in ["_", "-"] else "_" for c in _mock_server_name
        )

        _output_base_dir = output_base_dir
        if _output_base_dir is None:
            project_root = Path(__file__).parent.parent.parent
            _output_base_dir = project_root / "generated_mocks"

        mock_server_dir = Path(_output_base_dir) / _mock_server_name
        mock_server_dir.mkdir(parents=True, exist_ok=True)

        requirements_content = "fastapi\nuvicorn[standard]\npsutil\n"

        with open(
            mock_server_dir / "requirements_mock.txt", "w", encoding="utf-8"
        ) as f:
            f.write(requirements_content)

        if auth_enabled_bool:
            auth_middleware_template = jinja_env.get_template(
                "auth_middleware_template.j2"
            )
            random_suffix = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(8)
            )
            auth_middleware_code = auth_middleware_template.render(
                random_suffix=random_suffix
            )
            with open(
                mock_server_dir / "auth_middleware.py", "w", encoding="utf-8"
            ) as f:
                f.write(auth_middleware_code)
            with open(
                mock_server_dir / "requirements_mock.txt", "a", encoding="utf-8"
            ) as f:
                f.write("pyjwt\n")
                f.write("python-multipart\n")  # Add python-multipart here

        if webhooks_enabled_bool:
            webhook_template = jinja_env.get_template("webhook_template.j2")
            webhook_code = webhook_template.render()
            with open(
                mock_server_dir / "webhook_handler.py", "w", encoding="utf-8"
            ) as f:
                f.write(webhook_code)
            with open(
                mock_server_dir / "requirements_mock.txt", "a", encoding="utf-8"
            ) as f:
                f.write("httpx\n")

        if storage_enabled_bool:
            storage_template = jinja_env.get_template("storage_template.j2")
            storage_code = storage_template.render()
            with open(mock_server_dir / "storage.py", "w", encoding="utf-8") as f:
                f.write(storage_code)
            (mock_server_dir / "mock_data").mkdir(exist_ok=True)

        if admin_ui_enabled_bool:
            # Load analytics charts and functions templates
            analytics_charts_template = jinja_env.get_template("analytics_charts_template.j2")
            analytics_charts_code = analytics_charts_template.render()

            analytics_functions_template = jinja_env.get_template("analytics_functions_template.j2")
            analytics_functions_code = analytics_functions_template.render()

            admin_ui_template = jinja_env.get_template("admin_ui_template.j2")
            admin_ui_code = admin_ui_template.render(
                api_title=spec_data.get("info", {}).get("title", "Mock API"),
                api_version=spec_data.get("info", {}).get("version", "1.0.0"),
                auth_enabled=auth_enabled_bool,
                webhooks_enabled=webhooks_enabled_bool,
                storage_enabled=storage_enabled_bool,
                analytics_charts_js=analytics_charts_code,
                analytics_functions_js=analytics_functions_code,
            )
            (mock_server_dir / "templates").mkdir(exist_ok=True)
            with open(
                mock_server_dir / "templates" / "admin.html", "w", encoding="utf-8"
            ) as f:
                f.write(admin_ui_code)
            with open(
                mock_server_dir / "requirements_mock.txt", "a", encoding="utf-8"
            ) as f:
                f.write("jinja2\n")

            # Generate log analyzer module for admin UI analytics
            log_analyzer_template = jinja_env.get_template("log_analyzer_template.j2")
            log_analyzer_code = log_analyzer_template.render()
            with open(
                mock_server_dir / "log_analyzer.py", "w", encoding="utf-8"
            ) as f:
                f.write(log_analyzer_code)

            # Copy favicon.ico to prevent 404s in admin UI
            import shutil
            favicon_source_paths = [
                Path(__file__).parent.parent.parent / "favicon.ico",  # Project root
                Path(__file__).parent / "favicon.ico",  # Template directory
                Path("favicon.ico"),  # Current directory
            ]

            for favicon_source in favicon_source_paths:
                if favicon_source.exists():
                    try:
                        shutil.copy2(favicon_source, mock_server_dir / "favicon.ico")
                        break
                    except Exception as e:
                        # Log the error and continue to next path if copy fails
                        print(f"Failed to copy favicon from {favicon_source}: {e}")
                        continue

        routes_code_parts: list[str] = []
        paths = spec_data.get("paths", {})
        for path_url, methods in paths.items():
            for method, details in methods.items():
                valid_methods = [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "options",
                    "head",
                    "trace",
                ]
                if method.lower() not in valid_methods:
                    continue
                path_params = ""
                parameters = details.get("parameters", [])
                path_param_list = []
                for param in parameters:
                    if param.get("in") == "path":
                        param_name = param.get("name")
                        param_type = param.get("schema", {}).get("type", "string")
                        python_type = "str"
                        if param_type == "integer":
                            python_type = "int"
                        elif param_type == "number":
                            python_type = "float"
                        elif param_type == "boolean":
                            python_type = "bool"
                        path_param_list.append(f"{param_name}: {python_type}")
                if path_param_list:
                    path_params = ", ".join(path_param_list)
                example_response = None
                responses = details.get("responses", {})
                for status_code, response_info in responses.items():
                    if status_code.startswith("2"):
                        content = response_info.get("content", {})
                        for content_type, content_schema in content.items():
                            if "application/json" in content_type:
                                if "example" in content_schema:
                                    converted_example = convert_js_to_python(content_schema["example"])
                                    example_response = repr(converted_example)
                                    break
                                schema = content_schema.get("schema", {})
                                if "example" in schema:
                                    converted_example = convert_js_to_python(schema["example"])
                                    example_response = repr(converted_example)
                                    break
                                examples = content_schema.get("examples", {})
                                if examples:
                                    first_example = next(iter(examples.values()), {})
                                    if "value" in first_example:
                                        converted_example = convert_js_to_python(first_example["value"])
                                        example_response = repr(converted_example)
                                        break
                        if example_response:
                            break
                if not example_response:
                    for status_code, response_info in responses.items():
                        if status_code.startswith("2"):
                            content = response_info.get("content", {})
                            for content_type, content_schema in content.items():
                                if "application/json" in content_type:
                                    schema = content_schema.get("schema", {})
                                    mock_data = _generate_mock_data_from_schema(schema)
                                    if mock_data:
                                        # Convert JavaScript-style values to Python values before repr()
                                        converted_data = convert_js_to_python(mock_data)
                                        # Use repr() to ensure Python boolean values are properly formatted
                                        example_response = repr(converted_data)
                                        break
                            if example_response:
                                break
                route_template = jinja_env.get_template("route_template.j2")
                route_code = route_template.render(
                    method=method.lower(),
                    path=path_url,
                    summary=details.get("summary", f"{method.upper()} {path_url}"),
                    path_params=path_params,
                    example_response=example_response,
                    webhooks_enabled=webhooks_enabled_bool,
                )
                routes_code_parts.append(route_code)

        # Add favicon route when admin UI is enabled to prevent 404s
        if admin_ui_enabled_bool:
            favicon_route = '''@app.get("/favicon.ico", summary="Favicon", tags=["_system"])
async def favicon():
    """Serve favicon to prevent 404 errors in admin UI"""
    from fastapi.responses import FileResponse
    import os

    # Try to find favicon.ico in common locations
    favicon_paths = [
        "favicon.ico",
        "../favicon.ico",
        "../../favicon.ico",
        os.path.join(os.path.dirname(__file__), "favicon.ico"),
        os.path.join(os.path.dirname(__file__), "..", "favicon.ico"),
        os.path.join(os.path.dirname(__file__), "..", "..", "favicon.ico")
    ]

    for favicon_path in favicon_paths:
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path, media_type="image/x-icon")

    # If no favicon found, return a simple 1x1 transparent PNG as fallback
    from fastapi.responses import Response
    # 1x1 transparent PNG in base64
    transparent_png = b'\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x01\\x08\\x06\\x00\\x00\\x00\\x1f\\x15\\xc4\\x89\\x00\\x00\\x00\\rIDATx\\x9cc\\xf8\\x0f\\x00\\x00\\x01\\x00\\x01\\x00\\x18\\xdd\\x8d\\xb4\\x00\\x00\\x00\\x00IEND\\xaeB`\\x82'
    return Response(content=transparent_png, media_type="image/png")'''
            routes_code_parts.append(favicon_route)

        all_routes_code = "\n\n".join(routes_code_parts)
        middleware_template = jinja_env.get_template("middleware_log_template.j2")
        logging_middleware_code = middleware_template.render()
        with open(
            mock_server_dir / "logging_middleware.py", "w", encoding="utf-8"
        ) as f:
            f.write(logging_middleware_code)

        # Generate separate admin logging middleware if admin UI is enabled
        if admin_ui_enabled_bool:
            admin_middleware_template = jinja_env.get_template("admin_middleware_log_template.j2")
            admin_logging_middleware_code = admin_middleware_template.render()
            with open(
                mock_server_dir / "admin_logging_middleware.py", "w", encoding="utf-8"
            ) as f:
                f.write(admin_logging_middleware_code)

        common_imports = "from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Body, Query, Path, BackgroundTasks\nfrom fastapi.responses import HTMLResponse, JSONResponse\nfrom fastapi.templating import Jinja2Templates\nfrom fastapi.staticfiles import StaticFiles\nfrom fastapi.middleware.cors import CORSMiddleware\nfrom typing import List, Dict, Any, Optional\nimport json\nimport os\nimport time\nimport sqlite3\nimport logging\nfrom datetime import datetime\nfrom pathlib import Path\nfrom logging_middleware import LoggingMiddleware\n"
        auth_imports = (
            "from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer\nfrom auth_middleware import verify_api_key, verify_jwt_token, generate_token_response\n"
            if auth_enabled_bool
            else ""
        )
        webhook_imports = (
            'from webhook_handler import register_webhook, get_webhooks, delete_webhook, get_webhook_history, trigger_webhooks, test_webhook\n\n# Configure logging for webhook functionality\nlogger = logging.getLogger("webhook_handler")\n'
            if webhooks_enabled_bool
            else ""
        )
        storage_imports = (
            "from storage import StorageManager, get_storage_stats, get_collections\n"
            if storage_enabled_bool
            else ""
        )
        imports_section = (
            common_imports + auth_imports + webhook_imports + storage_imports
        )
        app_setup = 'app = FastAPI(title="{{ api_title }}", version="{{ api_version }}")\ntemplates = Jinja2Templates(directory="templates")\napp.add_middleware(LoggingMiddleware)\napp.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])\n\n# Setup database path for logs (same as in middleware)\ndb_dir = Path("db")\ndb_dir.mkdir(exist_ok=True)\nDB_PATH = db_dir / "request_logs.db"\n\n# Global variable for active scenario\nactive_scenario = None\n\n# Initialize active scenario from database on startup\ndef load_active_scenario():\n    global active_scenario\n    try:\n        conn = sqlite3.connect(str(DB_PATH))\n        conn.row_factory = sqlite3.Row\n        cursor = conn.cursor()\n        cursor.execute("SELECT id, name, config FROM mock_scenarios WHERE is_active = 1")\n        row = cursor.fetchone()\n        if row:\n            active_scenario = {\n                "id": row[0],\n                "name": row[1],\n                "config": json.loads(row[2]) if row[2] else {}\n            }\n        conn.close()\n    except Exception as e:\n        print(f"Error loading active scenario: {e}")\n        active_scenario = None\n\n# Load active scenario on startup\nload_active_scenario()\n'
        auth_endpoints_str = (
            '@app.post("/token", summary="Get access token", tags=["authentication"])\nasync def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):\n    return generate_token_response(form_data.username, form_data.password)\n'
            if auth_enabled_bool
            else ""
        )

        admin_api_endpoints_str = ""
        if admin_ui_enabled_bool:
            _admin_api_endpoints_raw = """# --- Admin API Endpoints ---
@admin_app.get("/api/export", tags=["_admin"])
async def export_data():
            import io
            import zipfile
            from fastapi.responses import StreamingResponse

            # Create a BytesIO object to store the zip file
            zip_buffer = io.BytesIO()

            # Create a ZipFile object
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add request logs from SQLite to the zip
                try:
                    conn = sqlite3.connect(str(DB_PATH))
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    # Get all request logs
                    cursor.execute("SELECT * FROM request_logs")
                    rows = cursor.fetchall()

                    # Convert to list of dicts for JSON serialization
                    logs = []
                    for row in rows:
                        log_entry = dict(row)
                        if "headers" in log_entry and log_entry["headers"]:
                            try:
                                log_entry["headers"] = json.loads(log_entry["headers"])
                            except:
                                log_entry["headers"] = {}
                        logs.append(log_entry)

                    # Add logs to the zip file
                    zipf.writestr('request_logs.json', json.dumps(logs, indent=2))

                    # Add database schema information
                    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
                    schemas = cursor.fetchall()
                    schema_info = {row[0].split()[2]: row[0] for row in schemas if row[0] is not None}
                    zipf.writestr('database_schema.json', json.dumps(schema_info, indent=2))

                    conn.close()
                except Exception as e:
                    # If there's an error, add an error log to the zip
                    zipf.writestr('db_export_error.txt', f"Error exporting database: {str(e)}")

                # Add configuration information
                config_info = {
                    "api_title": app.title,
                    "api_version": app.version,
                    "server_time": datetime.now().isoformat(),
                    "database_path": str(DB_PATH),
                }
                zipf.writestr('config.json', json.dumps(config_info, indent=2))

                # Reset the buffer position to the beginning
                zip_buffer.seek(0)

            # Return the zip file as a streaming response
            return StreamingResponse(
                zip_buffer,
                media_type="application/zip",
                headers={
                    "Content-Disposition": "attachment; filename=mock-api-data.zip"
                }
            )

        @admin_app.get("/api/requests", tags=["_admin"])
        async def get_request_logs(limit: int = 100, offset: int = 0, method: str = None, path: str = None, include_admin: bool = False, id: int = None):
            try:
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Build query with filters
                query = "SELECT * FROM request_logs"
                params = []
                where_clauses = []

                # Filter by exact ID if provided
                if id is not None:
                    where_clauses.append("id = ?")
                    params.append(id)

                if method:
                    where_clauses.append("method = ?")
                    params.append(method)

                if path:
                    where_clauses.append("path LIKE ?")
                    params.append(f"%{path}%")

                # Filter out admin requests by default, but only if not querying by specific ID
                if not include_admin and id is None:
                    where_clauses.append("(is_admin = 0 OR is_admin IS NULL)")

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                # Skip limit/offset when querying by exact ID
                if id is not None:
                    query += " ORDER BY id DESC"
                else:
                    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
                    params.extend([limit, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

                logs = []
                for row in rows:
                    log_entry = dict(row)
                    if "headers" in log_entry and log_entry["headers"]:
                        try:
                            log_entry["headers"] = json.loads(log_entry["headers"])
                        except:
                            log_entry["headers"] = {}
                    logs.append(log_entry)

                conn.close()

                # If we're querying by ID and have a result, return just that single record instead of an array
                if id is not None and logs:
                    return logs[0]

                return logs
            except Exception as e:
                print(f"Error getting request logs: {e}")
                return []
        @admin_app.get("/api/debug", tags=["_admin"])
        async def get_debug_info():
            debug_info = {
                "db_path_exists": os.path.exists(str(DB_PATH)),
                "db_directory_exists": os.path.exists(str(db_dir)),
                "db_path": str(DB_PATH),
                "working_directory": os.getcwd(),
                "db_dir_listing": os.listdir(str(db_dir)) if os.path.exists(str(db_dir)) else None,
                "sqlite_version": sqlite3.version
            }

            # Try to check the database tables
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                debug_info["tables"] = [table[0] for table in tables]

                # Check if request_logs table exists and get count
                if tables and any("request_logs" in table[0] for table in tables):
                    cursor.execute("SELECT COUNT(*) FROM request_logs")
                    debug_info["request_logs_count"] = cursor.fetchone()[0]

                    # Get sample data if available
                    cursor.execute("SELECT * FROM request_logs LIMIT 1")
                    if cursor.description:
                        columns = [column[0] for column in cursor.description]
                        rows = cursor.fetchall()
                        if rows:
                            debug_info["sample_log"] = dict(zip(columns, rows[0]))
                        else:
                            debug_info["sample_log"] = None

                conn.close()
            except Exception as e:
                debug_info["db_error"] = str(e)

            return debug_info

        @admin_app.get("/api/requests/stats", tags=["_admin"])
        async def get_request_stats():
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()

                stats = {"total_requests": 0}

                # Total count
                cursor.execute("SELECT COUNT(*) FROM request_logs")
                result = cursor.fetchone()
                if result:
                    stats["total_requests"] = result[0]

                # Count by method
                cursor.execute("SELECT method, COUNT(*) FROM request_logs GROUP BY method")
                stats["methods"] = {row[0]: row[1] for row in cursor.fetchall()}

                # Count by status code
                cursor.execute("SELECT status_code, COUNT(*) FROM request_logs GROUP BY status_code")
                stats["status_codes"] = {str(row[0]): row[1] for row in cursor.fetchall()}

                # Average response time
                cursor.execute("SELECT AVG(process_time_ms) FROM request_logs")
                avg_time = cursor.fetchone()
                stats["avg_response_time"] = avg_time[0] if avg_time and avg_time[0] is not None else 0

                conn.close()
                return stats
            except Exception as e:
                print(f"Error getting request stats: {e}")
                return {"error": str(e), "total_requests": 0}
        @admin_app.get("/api/logs/search", tags=["_admin"])
        async def search_logs(
                q: str = None,
                method: str = None,
                status: int = None,
                path_regex: str = None,
                time_from: str = None,
                time_to: str = None,
                limit: int = 100,
                offset: int = 0,
                include_admin: bool = False
                ):
            \"\"\"Advanced log search with complex filtering\"\"\"
            import re
            import time as time_module

            search_start = time_module.time()

            try:
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Build dynamic query
                query = "SELECT * FROM request_logs"
                params = []
                where_clauses = []

                # Text search in path, headers, request_body, response_body
                if q:
                    search_clause = "(path LIKE ? OR headers LIKE ? OR request_body LIKE ? OR response_body LIKE ?)"
                    where_clauses.append(search_clause)
                    search_term = f"%{q}%"
                    params.extend([search_term, search_term, search_term, search_term])

                # Method filter
                if method:
                    where_clauses.append("method = ?")
                    params.append(method.upper())

                # Status code filter
                if status:
                    where_clauses.append("status_code = ?")
                    params.append(status)

                # Path regex filter
                if path_regex:
                    # SQLite doesn't have native regex, so we'll filter in Python after query
                    pass

                # Time range filters
                if time_from:
                    where_clauses.append("timestamp >= ?")
                    params.append(time_from)

                if time_to:
                    where_clauses.append("timestamp <= ?")
                    params.append(time_to)

                # Admin filter
                if not include_admin:
                    where_clauses.append("(is_admin = 0 OR is_admin IS NULL)")

                # Combine where clauses
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                # Add ordering and pagination
                query += " ORDER BY id DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

                # Convert to list of dicts and apply regex filter if needed
                logs = []
                for row in rows:
                    log_entry = dict(row)
                    if "headers" in log_entry and log_entry["headers"]:
                        try:
                            log_entry["headers"] = json.loads(log_entry["headers"])
                        except:
                            log_entry["headers"] = {}

                    # Apply regex filter if specified
                    if path_regex:
                        try:
                            if not re.search(path_regex, log_entry.get("path", "")):
                                continue
                        except re.error:
                            # Invalid regex, skip this filter
                            pass

                    logs.append(log_entry)

                # Get total count for pagination info
                count_query = "SELECT COUNT(*) FROM request_logs"
                if where_clauses:
                    count_query += " WHERE " + " AND ".join(where_clauses[:-2])  # Exclude limit/offset params
                    count_params = params[:-2]
                else:
                    count_params = []

                cursor.execute(count_query, count_params)
                total_count = cursor.fetchone()[0]

                conn.close()

                search_time = int((time_module.time() - search_start) * 1000)

                return {
                    "logs": logs,
                    "total_count": total_count,
                    "returned_count": len(logs),
                    "limit": limit,
                    "offset": offset,
                    "search_time": search_time,
                    "filters_applied": {
                        "query": q,
                        "method": method,
                        "status": status,
                        "path_regex": path_regex,
                        "time_from": time_from,
                        "time_to": time_to,
                        "include_admin": include_admin
                    }
                }
            except Exception as e:
                return {"error": str(e), "logs": []}
        @admin_app.get("/api/logs/analyze", tags=["_admin"])
        async def analyze_logs(
                method: str = None,
                status: int = None,
                path_regex: str = None,
                time_from: str = None,
                time_to: str = None,
                group_by: str = None,
                include_admin: bool = False
                ):
            \"\"\"Log analysis and insights generation\"\"\"
            try:
                # First get the logs using similar filtering logic
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Build query with filters
                query = "SELECT * FROM request_logs"
                params = []
                where_clauses = []

                if method:
                    where_clauses.append("method = ?")
                    params.append(method.upper())

                if status:
                    where_clauses.append("status_code = ?")
                    params.append(status)

                if time_from:
                    where_clauses.append("timestamp >= ?")
                    params.append(time_from)

                if time_to:
                    where_clauses.append("timestamp <= ?")
                    params.append(time_to)

                if not include_admin:
                    where_clauses.append("(is_admin = 0 OR is_admin IS NULL)")

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                query += " ORDER BY id DESC"

                cursor.execute(query, params)
                rows = cursor.fetchall()

                # Convert to list of dicts for analysis
                logs = []
                for row in rows:
                    log_entry = dict(row)
                    if "headers" in log_entry and log_entry["headers"]:
                        try:
                            log_entry["headers"] = json.loads(log_entry["headers"])
                        except:
                            log_entry["headers"] = {}
                    logs.append(log_entry)

                conn.close()

                # Apply regex filter if needed
                if path_regex:
                    import re
                    try:
                        logs = [log for log in logs if re.search(path_regex, log.get("path", ""))]
                    except re.error:
                        pass  # Invalid regex, skip filter

                # Use the existing LogAnalyzer
                from log_analyzer import LogAnalyzer
                analyzer = LogAnalyzer()
                analysis = analyzer.analyze_logs(logs)

                # Add filter information to the analysis
                analysis["filters_applied"] = {
                    "method": method,
                    "status": status,
                    "path_regex": path_regex,
                    "time_from": time_from,
                    "time_to": time_to,
                    "group_by": group_by,
                    "include_admin": include_admin
                }

                return analysis

            except Exception as e:
                return {"error": str(e), "total_requests": 0}
        @admin_app.get("/api/mock-data/scenarios", tags=["_admin"])
        async def get_scenarios():
            \"\"\"Get all mock scenarios\"\"\"
            try:
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(\"\"\"
                    SELECT id, name, description, config, is_active, created_at, updated_at
                    FROM mock_scenarios
                    ORDER BY created_at DESC
                \"\"\")
                rows = cursor.fetchall()

                scenarios = []
                for row in rows:
                    scenario = dict(row)
                    # Parse JSON config
                    try:
                        scenario['config'] = json.loads(scenario['config']) if scenario['config'] else {}
                    except:
                        scenario['config'] = {}
                    scenarios.append(scenario)

                conn.close()
                return scenarios
            except Exception as e:
                print(f"Error getting scenarios: {e}")
                return []
        @admin_app.post("/api/mock-data/scenarios", tags=["_admin"])
        async def create_scenario(scenario_data: dict = Body(...)):
            \"\"\"Create a new mock scenario\"\"\"
            try:
                name = scenario_data.get("name")
                description = scenario_data.get("description", "")
                config = scenario_data.get("config", {})

                if not name:
                    raise HTTPException(status_code=400, detail="Scenario name is required")

                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()

                # Check if name already exists
                cursor.execute("SELECT id FROM mock_scenarios WHERE name = ?", (name,))
                if cursor.fetchone():
                    conn.close()
                    raise HTTPException(status_code=400, detail="Scenario name already exists")

                # Insert new scenario
                cursor.execute(\"\"\"
                    INSERT INTO mock_scenarios (name, description, config, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                \"\"\", (name, description, json.dumps(config)))

                scenario_id = cursor.lastrowid
                conn.commit()
                conn.close()

                return {"id": scenario_id, "name": name, "description": description, "config": config, "is_active": False}
            except HTTPException:
                raise
            except Exception as e:
                print(f"Error creating scenario: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        @admin_app.put("/api/mock-data/scenarios/{scenario_id}", tags=["_admin"])
        async def update_scenario(scenario_id: int, scenario_data: dict = Body(...)):
            \"\"\"Update an existing mock scenario\"\"\"
            try:
                name = scenario_data.get("name")
                description = scenario_data.get("description", "")
                config = scenario_data.get("config", {})

                if not name:
                    raise HTTPException(status_code=400, detail="Scenario name is required")

                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()

                # Check if scenario exists
                cursor.execute("SELECT id FROM mock_scenarios WHERE id = ?", (scenario_id,))
                if not cursor.fetchone():
                    conn.close()
                    raise HTTPException(status_code=404, detail="Scenario not found")

                # Check if name conflicts with another scenario
                cursor.execute("SELECT id FROM mock_scenarios WHERE name = ? AND id != ?", (name, scenario_id))
                if cursor.fetchone():
                    conn.close()
                    raise HTTPException(status_code=400, detail="Scenario name already exists")

                # Update scenario
                cursor.execute(\"\"\"
                    UPDATE mock_scenarios
                    SET name = ?, description = ?, config = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                \"\"\", (name, description, json.dumps(config), scenario_id))

                conn.commit()
                conn.close()

                return {"id": scenario_id, "name": name, "description": description, "config": config}
            except HTTPException:
                raise
            except Exception as e:
                print(f"Error updating scenario: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        @admin_app.delete("/api/mock-data/scenarios/{scenario_id}", tags=["_admin"])
        async def delete_scenario(scenario_id: int):
            \"\"\"Delete a mock scenario\"\"\"
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()

                # Check if scenario exists
                cursor.execute("SELECT id, is_active FROM mock_scenarios WHERE id = ?", (scenario_id,))
                scenario = cursor.fetchone()
                if not scenario:
                    conn.close()
                    raise HTTPException(status_code=404, detail="Scenario not found")

                # Don't allow deletion of active scenario
                if scenario[1]:  # is_active
                    conn.close()
                    raise HTTPException(status_code=400, detail="Cannot delete active scenario. Deactivate it first.")

                # Delete scenario
                cursor.execute("DELETE FROM mock_scenarios WHERE id = ?", (scenario_id,))
                conn.commit()
                conn.close()

                return {"message": "Scenario deleted successfully"}
            except HTTPException:
                raise
            except Exception as e:
                print(f"Error deleting scenario: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        @admin_app.post("/api/mock-data/scenarios/{scenario_id}/activate", tags=["_admin"])
        async def activate_scenario(scenario_id: int):
            \"\"\"Activate a mock scenario (deactivates all others)\"\"\"
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()

                # Check if scenario exists
                cursor.execute("SELECT id, name, config FROM mock_scenarios WHERE id = ?", (scenario_id,))
                scenario = cursor.fetchone()
                if not scenario:
                    conn.close()
                    raise HTTPException(status_code=404, detail="Scenario not found")

                # Deactivate all scenarios first
                cursor.execute("UPDATE mock_scenarios SET is_active = 0")

                # Activate the selected scenario
                cursor.execute("UPDATE mock_scenarios SET is_active = 1 WHERE id = ?", (scenario_id,))

                conn.commit()
                conn.close()

                # Update in-memory active scenario
                global active_scenario
                active_scenario = {
                    "id": scenario[0],
                    "name": scenario[1],
                    "config": json.loads(scenario[2]) if scenario[2] else {}
                }

                return {"message": f"Scenario '{scenario[1]}' activated successfully", "active_scenario": active_scenario}
            except HTTPException:
                raise
            except Exception as e:
                print(f"Error activating scenario: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        @admin_app.post("/api/mock-data/scenarios/{scenario_id}/deactivate", tags=["_admin"])
        async def deactivate_scenario(scenario_id: int):
            \"\"\"Deactivate a mock scenario\"\"\"
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()

                # Check if scenario exists and is active
                cursor.execute("SELECT id, name, is_active FROM mock_scenarios WHERE id = ?", (scenario_id,))
                scenario = cursor.fetchone()
                if not scenario:
                    conn.close()
                    raise HTTPException(status_code=404, detail="Scenario not found")

                if not scenario[2]:  # is_active
                    conn.close()
                    raise HTTPException(status_code=400, detail="Scenario is not currently active")

                # Deactivate the scenario
                cursor.execute("UPDATE mock_scenarios SET is_active = 0 WHERE id = ?", (scenario_id,))

                conn.commit()
                conn.close()

                # Clear in-memory active scenario
                global active_scenario
                active_scenario = None

                return {"message": f"Scenario '{scenario[1]}' deactivated successfully"}
            except HTTPException:
                raise
            except Exception as e:
                print(f"Error deactivating scenario: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        @admin_app.get("/api/mock-data/scenarios/active", tags=["_admin"])
        async def get_active_scenario():
            \"\"\"Get the currently active scenario\"\"\"
            try:
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(\"\"\"
                    SELECT id, name, description, config, created_at, updated_at
                    FROM mock_scenarios
                    WHERE is_active = 1
                \"\"\")
                row = cursor.fetchone()

                if row:
                    scenario = dict(row)
                    try:
                        scenario['config'] = json.loads(scenario['config']) if scenario['config'] else {}
                    except:
                        scenario['config'] = {}
                    conn.close()
                    return scenario
                else:
                    conn.close()
                    return None
            except Exception as e:
                print(f"Error getting active scenario: {e}")
                return None
        @admin_app.get("/api/performance/metrics", tags=["_admin"])
        async def get_performance_metrics(
                limit: int = 100,
                offset: int = 0,
                time_from: str = None,
                time_to: str = None,
                request_id: int = None
                ):
            \"\"\"Get performance metrics data\"\"\"
            try:
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Build query with filters
                query = \"\"\"
                    SELECT pm.*, rl.method, rl.path, rl.status_code, rl.timestamp
                    FROM performance_metrics pm
                    LEFT JOIN request_logs rl ON pm.request_id = rl.id
                \"\"\"
                params = []
                where_clauses = []

                if request_id:
                    where_clauses.append("pm.request_id = ?")
                    params.append(request_id)

                if time_from:
                    where_clauses.append("pm.recorded_at >= ?")
                    params.append(time_from)

                if time_to:
                    where_clauses.append("pm.recorded_at <= ?")
                    params.append(time_to)

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                query += " ORDER BY pm.recorded_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

                metrics = [dict(row) for row in rows]
                conn.close()

                return {
                    "metrics": metrics,
                    "count": len(metrics),
                    "limit": limit,
                    "offset": offset
                }
            except Exception as e:
                print(f"Error getting performance metrics: {e}")
                return {"error": str(e), "metrics": []}
        @admin_app.get("/api/performance/sessions", tags=["_admin"])
        async def get_performance_sessions(
                limit: int = 100,
                offset: int = 0,
                status: str = None
                ):
                \"\"\"Get test session analytics\"\"\"
            try:
            conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Build query with filters
            query = "SELECT * FROM test_sessions"
            params = []
            where_clauses = []

            if status:
                where_clauses.append("status = ?")
                params.append(status)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

                query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

            sessions = []
            for row in rows:
                session = dict(row)
            # Parse metadata if it exists
            if session.get('metadata'):
            try:
                session['metadata'] = json.loads(session['metadata'])
            except:
                session['metadata'] = {}
                sessions.append(session)

            conn.close()

            return {
                "sessions": sessions,
                "count": len(sessions),
                "limit": limit,
                "offset": offset
                }
            except Exception as e:
            print(f"Error getting test sessions: {e}")
            return {"error": str(e), "sessions": []}
        @admin_app.get("/api/performance/summary", tags=["_admin"])
        async def get_performance_summary(
                time_from: str = None,
                time_to: str = None
                ):
                \"\"\"Get performance summary and analytics\"\"\"
            try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            # Build time filter
            time_filter = ""
            params = []
            if time_from or time_to:
                conditions = []
            if time_from:
                    conditions.append("pm.recorded_at >= ?")
                params.append(time_from)
            if time_to:
                    conditions.append("pm.recorded_at <= ?")
                params.append(time_to)
            time_filter = " WHERE " + " AND ".join(conditions)

            # Get overall performance metrics
                cursor.execute(f\"\"\"
                SELECT
                COUNT(*) as total_requests,
                AVG(response_time_ms) as avg_response_time,
                MIN(response_time_ms) as min_response_time,
                MAX(response_time_ms) as max_response_time,
                AVG(memory_usage_mb) as avg_memory_usage,
                AVG(cpu_usage_percent) as avg_cpu_usage,
                SUM(database_queries) as total_db_queries,
                SUM(cache_hits) as total_cache_hits,
                SUM(cache_misses) as total_cache_misses
                FROM performance_metrics pm{time_filter}
                \"\"\", params)

            summary = cursor.fetchone()

            # Get performance by endpoint
                cursor.execute(f\"\"\"
                SELECT
                rl.path,
                rl.method,
                COUNT(*) as request_count,
                AVG(pm.response_time_ms) as avg_response_time,
                AVG(pm.memory_usage_mb) as avg_memory_usage
                FROM performance_metrics pm
                LEFT JOIN request_logs rl ON pm.request_id = rl.id{time_filter}
                GROUP BY rl.path, rl.method
                ORDER BY avg_response_time DESC
                LIMIT 10
                \"\"\", params)

            endpoint_performance = cursor.fetchall()

            # Get session summary
                cursor.execute(\"\"\"
                SELECT
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_sessions,
                AVG(total_requests) as avg_requests_per_session,
                AVG(avg_response_time) as avg_session_response_time
                FROM test_sessions
                \"\"\")

            session_summary = cursor.fetchone()

            conn.close()

            return {
                "overall_performance": {
                "total_requests": summary[0] or 0,
                "avg_response_time_ms": round(summary[1] or 0, 2),
                "min_response_time_ms": summary[2] or 0,
                "max_response_time_ms": summary[3] or 0,
                "avg_memory_usage_mb": round(summary[4] or 0, 2),
                "avg_cpu_usage_percent": round(summary[5] or 0, 2),
                "total_db_queries": summary[6] or 0,
                "total_cache_hits": summary[7] or 0,
                "total_cache_misses": summary[8] or 0,
                "cache_hit_ratio": round((summary[7] or 0) / max((summary[7] or 0) + (summary[8] or 0), 1) * 100, 2)
                },
                "endpoint_performance": [
                {
                "path": row[0],
                "method": row[1],
                "request_count": row[2],
                "avg_response_time_ms": round(row[3] or 0, 2),
                "avg_memory_usage_mb": round(row[4] or 0, 2)
                }
            for row in endpoint_performance
                ],
                "session_summary": {
                "total_sessions": session_summary[0] or 0,
                "active_sessions": session_summary[1] or 0,
                "avg_requests_per_session": round(session_summary[2] or 0, 2),
                "avg_session_response_time_ms": round(session_summary[3] or 0, 2)
                }
                }
            except Exception as e:
            print(f"Error getting performance summary: {e}")
            return {"error": str(e)}
        @admin_app.get("/api/analytics/export", tags=["_admin"])
        async def export_analytics_data(
                format: str = "json",
                time_from: str = None,
                time_to: str = None,
                include_performance: bool = True,
                include_logs: bool = True
                ):
                \"\"\"Export analytics data in various formats\"\"\"
            try:
            from fastapi.responses import StreamingResponse
            import csv
            import io

            # Get analytics data
            analytics_data = {}

            if include_logs:
            # Get log analysis
            conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM request_logs"
            params = []
            where_clauses = []

            if time_from:
                where_clauses.append("timestamp >= ?")
                params.append(time_from)
            if time_to:
                where_clauses.append("timestamp <= ?")
                params.append(time_to)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                query += " ORDER BY id DESC"

                cursor.execute(query, params)
            logs = [dict(row) for row in cursor.fetchall()]

            # Use log analyzer for insights
            from log_analyzer import LogAnalyzer
                analyzer = LogAnalyzer()
                analytics_data["log_analysis"] = analyzer.analyze_logs(logs)
                analytics_data["raw_logs"] = logs
            conn.close()

            if include_performance:
            # Get performance data
            conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

                perf_query = "SELECT * FROM performance_metrics"
                perf_params = []
                perf_where = []

            if time_from:
                    perf_where.append("recorded_at >= ?")
                perf_params.append(time_from)
            if time_to:
                    perf_where.append("recorded_at <= ?")
                perf_params.append(time_to)

            if perf_where:
                perf_query += " WHERE " + " AND ".join(perf_where)
                perf_query += " ORDER BY recorded_at DESC"

                cursor.execute(perf_query, perf_params)
                analytics_data["performance_metrics"] = [dict(row) for row in cursor.fetchall()]
            conn.close()

            # Export in requested format
            if format.lower() == "csv":
            # Create CSV export
            output = io.StringIO()

            if include_logs and analytics_data.get("raw_logs"):
            writer = csv.DictWriter(output, fieldnames=analytics_data["raw_logs"][0].keys())
                writer.writeheader()
                writer.writerows(analytics_data["raw_logs"])

                output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=analytics_export.csv"}
                )
            else:
            # JSON export
            return StreamingResponse(
                io.BytesIO(json.dumps(analytics_data, indent=2, default=str).encode()),
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=analytics_export.json"}
                )

            except Exception as e:
            return {"error": str(e)}
        @admin_app.get("/api/analytics/realtime", tags=["_admin"])
        async def get_realtime_analytics():
                \"\"\"Get real-time analytics data for dashboard updates\"\"\"
            try:
            conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get recent activity (last 5 minutes)
                cursor.execute(\"\"\"
                SELECT COUNT(*) as recent_requests,
                AVG(process_time_ms) as avg_response_time,
                COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count
                FROM request_logs
                WHERE timestamp >= datetime('now', '-5 minutes')
                \"\"\")
            recent_stats = dict(cursor.fetchone())

            # Get current active scenarios
                cursor.execute("SELECT name FROM mock_scenarios WHERE is_active = 1")
            active_scenario = cursor.fetchone()

            # Get performance metrics from last hour
                cursor.execute(\"\"\"
                SELECT AVG(memory_usage_mb) as avg_memory,
                AVG(cpu_usage_percent) as avg_cpu
                FROM performance_metrics
                WHERE recorded_at >= datetime('now', '-1 hour')
                \"\"\")
            perf_stats = dict(cursor.fetchone())

            conn.close()

            return {
                "timestamp": datetime.now().isoformat(),
                "recent_activity": recent_stats,
                "active_scenario": active_scenario[0] if active_scenario else None,
                "system_performance": perf_stats,
                "status": "healthy"
                }
            except Exception as e:
            return {"error": str(e), "status": "error"}
        @admin_app.get("/api/analytics/charts", tags=["_admin"])
        async def get_chart_data(
                chart_type: str = "overview",
                time_range: str = "1h",
                limit: int = 50
                ):
                \"\"\"Get data formatted for chart rendering\"\"\"
            try:
            conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Calculate time filter based on range
            time_filters = {
                "1h": "datetime('now', '-1 hour')",
                "6h": "datetime('now', '-6 hours')",
                "24h": "datetime('now', '-24 hours')",
                "7d": "datetime('now', '-7 days')",
                "30d": "datetime('now', '-30 days')"
                }
            time_filter = time_filters.get(time_range, time_filters["1h"])

            chart_data = {}

            if chart_type == "overview" or chart_type == "requests":
            # Request volume over time
                cursor.execute(f\"\"\"
                SELECT strftime('%H:%M', timestamp) as time_bucket,
                COUNT(*) as request_count,
                AVG(process_time_ms) as avg_response_time
                FROM request_logs
                WHERE timestamp >= {time_filter}
                GROUP BY strftime('%H:%M', timestamp)
                ORDER BY time_bucket
                LIMIT ?
                \"\"\", (limit,))

                chart_data["request_volume"] = [dict(row) for row in cursor.fetchall()]

            if chart_type == "overview" or chart_type == "status":
            # Status code distribution
                cursor.execute(f\"\"\"
                SELECT status_code, COUNT(*) as count
                FROM request_logs
                WHERE timestamp >= {time_filter}
                GROUP BY status_code
                ORDER BY count DESC
                \"\"\")

                chart_data["status_distribution"] = [dict(row) for row in cursor.fetchall()]

            if chart_type == "overview" or chart_type == "endpoints":
            # Top endpoints
                cursor.execute(f\"\"\"
                SELECT path, COUNT(*) as request_count,
                AVG(process_time_ms) as avg_response_time
                FROM request_logs
                WHERE timestamp >= {time_filter}
                GROUP BY path
                ORDER BY request_count DESC
                LIMIT ?
                \"\"\", (limit,))

                chart_data["top_endpoints"] = [dict(row) for row in cursor.fetchall()]

            if chart_type == "overview" or chart_type == "performance":
            # Performance metrics
                cursor.execute(f\"\"\"
                SELECT strftime('%H:%M', recorded_at) as time_bucket,
                AVG(response_time_ms) as avg_response_time,
                AVG(memory_usage_mb) as avg_memory,
                AVG(cpu_usage_percent) as avg_cpu
                FROM performance_metrics
                WHERE recorded_at >= {time_filter}
                GROUP BY strftime('%H:%M', recorded_at)
                ORDER BY time_bucket
                LIMIT ?
                \"\"\", (limit,))

                chart_data["performance_trends"] = [dict(row) for row in cursor.fetchall()]

            conn.close()
            return chart_data

            except Exception as e:
            return {"error": str(e)}

"""
        webhook_api_endpoints_str = ""
        if webhooks_enabled_bool and admin_ui_enabled_bool:
            _webhook_api_endpoints_raw = """    @admin_app.get("/api/webhooks", tags=["_admin"])
    async def admin_get_webhooks():
        return get_webhooks()

    @admin_app.post("/api/webhooks", tags=["_admin"])
    async def admin_register_webhook(webhook_data: dict = Body(...)):
        event_type = webhook_data.get("event_type")
        url = webhook_data.get("url")
        description = webhook_data.get("description")
        if not event_type or not url:
            raise HTTPException(status_code=400, detail="event_type and url are required")
        return register_webhook(event_type, url, description)

    @admin_app.delete("/api/webhooks/{webhook_id}", tags=["_admin"])
    async def admin_delete_webhook(webhook_id: str):
        return delete_webhook(webhook_id)

    @admin_app.post("/api/webhooks/{webhook_id}/test", tags=["_admin"])
    async def admin_test_webhook(webhook_id: str):
        return await test_webhook(webhook_id)

    @admin_app.get("/api/webhooks/history", tags=["_admin"])
    async def admin_get_webhook_history():
        return get_webhook_history()
"""
            webhook_api_endpoints_str = _webhook_api_endpoints_raw.strip()
        storage_api_endpoints_str = ""
        if storage_enabled_bool and admin_ui_enabled_bool:
            _storage_api_endpoints_raw = """    @admin_app.get("/api/storage/stats", tags=["_admin"])
    async def admin_get_storage_stats():
        return get_storage_stats()

    @admin_app.get("/api/storage/collections", tags=["_admin"])
    async def admin_get_collections():
        return get_collections()
"""
            storage_api_endpoints_str = _storage_api_endpoints_raw.strip()

        if admin_ui_enabled_bool:
            admin_ui_endpoint_str = f'''    @admin_app.get("/", response_class=HTMLResponse, summary="Admin UI", tags=["_system"])
    async def read_admin_ui(request: Request):
        return templates.TemplateResponse("admin.html", {{
            "request": request,
            "api_title": "{api_title}",
            "api_version": "{api_version}",
            "auth_enabled": {auth_enabled_bool},
            "webhooks_enabled": {webhooks_enabled_bool},
            "storage_enabled": {storage_enabled_bool}
        }})'''
        else:
            admin_ui_endpoint_str = "    @app.get(\"/\")\n    async def no_admin(): return {'message': 'Admin UI not enabled'}"

        health_endpoint_str = '@app.get("/health", summary="Health check endpoint", tags=["_system"])\nasync def health_check(): return {"status": "healthy"}\n'

        # Create separate main sections for business and admin servers
        business_main_section_str = f'''if __name__ == "__main__":
    import uvicorn
    import threading
    import time

    def run_business_server():
        uvicorn.run(app, host="0.0.0.0", port={business_port})

    # Create admin app at module level
    admin_app = FastAPI(title="{api_title} Admin", version="{api_version}")
    admin_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    # Add admin-specific middleware for separate logging
    from admin_logging_middleware import AdminLoggingMiddleware
    admin_app.add_middleware(AdminLoggingMiddleware)

    def run_admin_server():
        # Run the admin server
        uvicorn.run(admin_app, host="0.0.0.0", port={admin_port})

    # Admin endpoints
    {admin_api_endpoints_str if admin_ui_enabled_bool else ""}
    {webhook_api_endpoints_str if webhooks_enabled_bool and admin_ui_enabled_bool else ""}
    {storage_api_endpoints_str if storage_enabled_bool and admin_ui_enabled_bool else ""}
    {admin_ui_endpoint_str if admin_ui_enabled_bool else ""}

    # Add health check for admin server
    @admin_app.get("/health", summary="Admin health check", tags=["_system"])
    async def admin_health_check():
        return {{"status": "healthy", "server": "admin"}}

    # Start both servers
    if {admin_ui_enabled_bool}:
        # Start admin server in separate thread
        admin_thread = threading.Thread(target=run_admin_server, daemon=True)
        admin_thread.start()
        time.sleep(1)  # Give admin server time to start

        print(f"Business API server starting on port {business_port}")
        print(f"Admin UI server running on port {admin_port}")
    else:
        print(f"Business API server starting on port {business_port}")

    # Start business server (main thread)
    run_business_server()
'''

        main_app_template_str = (
            imports_section
            + app_setup
            + auth_endpoints_str
            + "\n# --- Generated Routes ---\n{{ routes_code }}\n# --- End Generated Routes ---\n"
            + health_endpoint_str
            + business_main_section_str
        )
        main_app_jinja_template = jinja_env.from_string(main_app_template_str)
        main_py_content = main_app_jinja_template.render(
            api_title=api_title,
            api_version=api_version,
            routes_code=all_routes_code,
            default_port=business_port,
        )
        with open(mock_server_dir / "main.py", "w", encoding="utf-8") as f:
            f.write(main_py_content)

        dockerfile_template = jinja_env.get_template("dockerfile_template.j2")
        dockerfile_content = dockerfile_template.render(
            python_version="3.9-slim",
            port=business_port,
            auth_enabled=auth_enabled_bool,
            webhooks_enabled=webhooks_enabled_bool,
            storage_enabled=storage_enabled_bool,
            admin_ui_enabled=admin_ui_enabled_bool,
        )
        with open(mock_server_dir / "Dockerfile", "w", encoding="utf-8") as f:
            f.write(dockerfile_content)

        compose_template = jinja_env.get_template("docker_compose_template.j2")
        timestamp_for_id = str(int(time.time()))[-6:]
        raw_api_title = spec_data.get("info", {}).get("title", "mock_api")
        clean_service_name = "".join(
            c if c.isalnum() else "-" for c in raw_api_title.lower()
        )
        while "--" in clean_service_name:
            clean_service_name = clean_service_name.replace("--", "-")
        clean_service_name = clean_service_name.strip("-")
        if not clean_service_name:
            clean_service_name = "mock-api"
        final_service_name = f"{clean_service_name}-mock"
        compose_content = compose_template.render(
            service_name=final_service_name,
            business_port=business_port,
            admin_port=admin_port,
            admin_ui_enabled=admin_ui_enabled_bool,
            timestamp_id=timestamp_for_id,
        )
        with open(mock_server_dir / "docker-compose.yml", "w", encoding="utf-8") as f:
            f.write(compose_content)

        return mock_server_dir

    except Exception as e:
        raise APIGenerationError(f"Failed to generate mock API: {e}") from e


if __name__ == "__main__":
    dummy_spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.1"},
        "paths": {"/items": {"get": {"summary": "Get all items"}}},
    }
    with contextlib.suppress(APIGenerationError):
        generated_path = generate_mock_api(
            dummy_spec, mock_server_name="my_test_api_main"
        )
