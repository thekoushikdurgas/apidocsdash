import streamlit as st
import json
import pandas as pd
import uuid
from datetime import datetime
import time

# Import custom modules
from database import get_db_manager
from api_parser import APIParser
from api_runner import APIRunner

# Page configuration
st.set_page_config(
    page_title="API Documentation Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def get_api_runner():
    return APIRunner()

# Initialize database and API runner
db_manager = get_db_manager()
api_runner = get_api_runner()

# Session state initialization
if 'current_doc_id' not in st.session_state:
    st.session_state.current_doc_id = None
if 'current_endpoint' not in st.session_state:
    st.session_state.current_endpoint = None
if 'api_parser' not in st.session_state:
    st.session_state.api_parser = None
if 'selected_environment' not in st.session_state:
    st.session_state.selected_environment = None
if 'default_doc_loaded' not in st.session_state:
    st.session_state.default_doc_loaded = False

# Load default API documentation on first run
def load_default_documentation():
    """Load the default API documentation from file"""
    try:
        with open('default_api_docs.json', 'r') as f:
            file_content = json.load(f)
        
        # Save to database
        source_id = file_content.get('source_identifier', 'MyAPI_v1')
        doc_id = db_manager.save_api_documentation(
            name="MyAPI Documentation (Default)",
            source_identifier=source_id,
            file_content=file_content
        )
        
        # Load it immediately
        st.session_state.current_doc_id = doc_id
        st.session_state.api_parser = APIParser(file_content)
        if st.session_state.api_parser.parse_document():
            st.session_state.default_doc_loaded = True
            return True
    except Exception as e:
        st.error(f"Error loading default documentation: {str(e)}")
    return False

# Load default documentation if not already loaded
if not st.session_state.default_doc_loaded:
    load_default_documentation()

# Create default environment if none exists
def create_default_environment():
    """Create a default environment with variables from JSON file"""
    try:
        environments = db_manager.get_environments()
        if not environments:
            # Load from default environment JSON file
            try:
                with open('default_environment.json', 'r') as f:
                    env_data = json.load(f)
                
                # Convert Postman format to simple key-value pairs
                default_vars = {}
                if 'values' in env_data:
                    for item in env_data['values']:
                        if item.get('enabled', True):
                            default_vars[item['key']] = item['value']
                
                env_name = env_data.get('name', 'Prbal API Environment')
            except (FileNotFoundError, json.JSONDecodeError):
                # Fallback if file doesn't exist
                default_vars = {
                    "base_url": "http://localhost:8000",
                    "api_key": "your-api-key-here",
                    "token": "your-bearer-token-here",
                    "user_id": "test-user-id",
                    "admin_token": "admin-bearer-token"
                }
                env_name = "Default Environment"
            
            db_manager.save_environment(
                name=env_name,
                description="Auto-loaded environment variables for API testing",
                variables=default_vars,
                is_active=True
            )
    except Exception as e:
        st.error(f"Error creating default environment: {str(e)}")

# Create default environment
create_default_environment()

def main():
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #FF6C37 0%, #FF8C42 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: white !important;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .endpoint-button {
        margin: 0.2rem 0;
        width: 100%;
    }
    .stSelectbox > div > div {
        background-color: #F8F9FA;
    }
    .success-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
    }
    .method-get { color: #4CAF50; font-weight: bold; }
    .method-post { color: #FF6C37; font-weight: bold; }
    .method-put { color: #2196F3; font-weight: bold; }
    .method-delete { color: #F44336; font-weight: bold; }
    .method-patch { color: #FF9800; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header with gradient background
    st.markdown("""
    <div class="main-header">
        <h1>🚀 API Documentation Dashboard</h1>
        <p>Interactive Postman-like interface for testing APIs with environment management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create three-column layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        render_sidebar()
    
    with col2:
        render_main_content()
    
    with col3:
        render_environment_panel()

def render_sidebar():
    """Render left sidebar with navigation and API documentation management"""
    st.header("📚 API Documentation")
    
    # Export section at the top
    with st.expander("📤 Export Documentation", expanded=False):
        st.markdown("Export your API documentation in various formats")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 JSON", help="Export as JSON file", key="export_doc_json"):
                export_documentation_json()
            if st.button("🔗 Postman", help="Export as Postman collection", key="export_doc_postman"):
                export_documentation_postman()
        
        with col2:
            if st.button("📋 Markdown", help="Export as Markdown file", key="export_doc_md"):
                export_documentation_markdown()
            if st.button("📊 Report", help="Export comprehensive report", key="export_doc_report"):
                export_documentation_report()
    
    # Show default documentation status
    if st.session_state.default_doc_loaded:
        st.success("✅ MyAPI Documentation loaded and ready!")
        
    # Upload new API documentation
    with st.expander("📤 Upload Additional Documentation", expanded=False):
        st.markdown("Upload more API documentation files to expand your collection")
        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type=['json'],
            help="Upload your API documentation in JSON format"
        )
        
        if uploaded_file is not None:
            try:
                # Read and parse JSON
                file_content = json.load(uploaded_file)
                
                # Show JSON preview with confirmation
                st.subheader("JSON Preview")
                
                # Create scrollable container for JSON preview
                with st.container():
                    st.text_area(
                        "JSON Content Preview",
                        value=json.dumps(file_content, indent=2),
                        height=300,
                        disabled=True,
                        help="Preview of the uploaded JSON file"
                    )
                
                # Document name input
                doc_name = st.text_input(
                    "Document Name",
                    value=uploaded_file.name.replace('.json', ''),
                    key="doc_name_input"
                )
                
                # Confirmation buttons
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button("✅ Confirm & Save", type="primary", key="confirm_save"):
                        # Parse and save to database
                        source_id = file_content.get('source_identifier', 'Unknown')
                        doc_id = db_manager.save_api_documentation(
                            name=doc_name,
                            source_identifier=source_id,
                            file_content=file_content
                        )
                        
                        # Parse and update session state
                        st.session_state.api_parser = APIParser(file_content)
                        st.session_state.api_parser.parse_document()
                        
                        st.success(f"Documentation parsed and saved successfully! (ID: {doc_id})")
                        st.success("Data is now displayed in the navigation tree")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancel", key="cancel_save"):
                        st.info("Upload cancelled. Please select a different file.")
                        st.rerun()
                    
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please upload a valid JSON document.")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    # List existing documentation
    st.subheader("📋 Available Documentation")
    docs = db_manager.get_api_documentation()
    
    if not docs:
        st.info("Loading documentation...")
        return
    
    # Document selection
    doc_options = {f"{doc.name} (ID: {doc.id})": doc.id for doc in docs}
    selected_doc = st.selectbox(
        "Select Documentation",
        options=list(doc_options.keys()),
        key="doc_selector"
    )
    
    if selected_doc:
        selected_doc_id = doc_options[selected_doc]
        
        # Load selected documentation
        if st.session_state.current_doc_id != selected_doc_id:
            st.session_state.current_doc_id = selected_doc_id
            doc = db_manager.get_api_documentation(selected_doc_id)
            
            if doc and doc.file_content:
                st.session_state.api_parser = APIParser(doc.file_content)
                if st.session_state.api_parser.parse_document():
                    st.success("Documentation loaded successfully!")
                else:
                    st.error("Failed to parse documentation")
        
        # Display navigation tree
        if st.session_state.api_parser:
            st.subheader("API Endpoints")
            render_endpoint_navigation()
        
        # Delete documentation
        if st.button("🗑️ Delete Documentation", type="secondary"):
            if db_manager.delete_api_documentation(selected_doc_id):
                st.success("Documentation deleted successfully!")
                st.session_state.current_doc_id = None
                st.session_state.api_parser = None
                st.rerun()

def render_endpoint_navigation():
    """Render API endpoint navigation"""
    if not st.session_state.api_parser:
        return
    
    # Search functionality
    search_query = st.text_input("🔍 Search endpoints", placeholder="Search API endpoints...")
    
    # Get navigation tree and endpoints
    navigation_tree = st.session_state.api_parser.get_navigation_tree()
    
    if search_query:
        endpoints = st.session_state.api_parser.search_endpoints(search_query)
        # Display search results
        if endpoints:
            st.subheader("Search Results")
            for endpoint in endpoints:
                method = endpoint['method']
                url = endpoint['url']
                
                method_color = {
                    'GET': '🟢',
                    'POST': '🟡',
                    'PUT': '🔵',
                    'DELETE': '🔴',
                    'PATCH': '🟠'
                }.get(method, '⚪')
                
                button_text = f"{method_color} **{method}** `{url}`"
                
                if st.button(
                    button_text,
                    key=f"search_endpoint_{endpoint['endpoint']}",
                    help=f"{endpoint['description']}\n\nClick to test this endpoint",
                    use_container_width=True
                ):
                    st.session_state.current_endpoint = endpoint
                    st.rerun()
        else:
            st.info("No endpoints found for your search.")
    else:
        # Display complete navigation tree
        render_navigation_tree(navigation_tree)

def render_navigation_tree(tree, level=0):
    """Recursively render the navigation tree"""
    for section_name, section_data in tree.items():
        section_level = section_data.get('level', 1)
        has_endpoints = section_data.get('has_endpoints', False)
        has_children = section_data.get('has_children', False)
        section_content = section_data.get('section', {}).get('content_text', '')
        
        # Choose appropriate icon based on content
        if has_endpoints and has_children:
            icon = "📁"
        elif has_endpoints:
            icon = "🔗"
        elif has_children:
            icon = "📂"
        else:
            icon = "📄"
        
        # Only use expanders for top-level sections to avoid nesting
        if level == 0 and (has_children or has_endpoints):
            with st.expander(f"{icon} {section_name}", expanded=True):
                if section_content:
                    st.markdown(f"*{section_content}*")
                
                # Display endpoints in this section
                endpoints = section_data.get('api_endpoints', [])
                if endpoints:
                    render_endpoints_list(endpoints, section_data, level)
                
                # Render children as subsections without expanders
                children = section_data.get('children', {})
                if children:
                    render_subsections(children, level + 1)
        
        elif level > 0:
            # For nested sections, use headers instead of expanders
            header_level = min(level + 2, 6)  # Limit to h6
            st.markdown(f"{'#' * header_level} {icon} {section_name}")
            
            if section_content:
                st.markdown(f"*{section_content}*")
            
            # Display endpoints
            endpoints = section_data.get('api_endpoints', [])
            if endpoints:
                render_endpoints_list(endpoints, section_data, level)
            
            # Render children
            children = section_data.get('children', {})
            if children:
                render_subsections(children, level + 1)

def render_subsections(children_dict, level):
    """Render subsections without expanders"""
    for child_name, child_data in children_dict.items():
        has_endpoints = child_data.get('has_endpoints', False)
        has_children = child_data.get('has_children', False)
        section_content = child_data.get('section', {}).get('content_text', '')
        
        # Choose icon
        if has_endpoints and has_children:
            icon = "📁"
        elif has_endpoints:
            icon = "🔗"
        elif has_children:
            icon = "📂"
        else:
            icon = "📄"
        
        # Use markdown headers for nested sections
        header_level = min(level + 2, 6)
        st.markdown(f"{'#' * header_level} {icon} {child_name}")
        
        if section_content:
            st.markdown(f"*{section_content}*")
        
        # Display endpoints
        endpoints = child_data.get('api_endpoints', [])
        if endpoints:
            render_endpoints_list(endpoints, child_data, level)
        
        # Render grandchildren
        grandchildren = child_data.get('children', {})
        if grandchildren:
            render_subsections(grandchildren, level + 1)

def render_endpoints_list(endpoints, section_data, level):
    """Render a list of endpoints"""
    for endpoint in endpoints:
        method = endpoint.get('endpoint', '').split(' ')[0] if endpoint.get('endpoint') else 'GET'
        url = endpoint.get('endpoint', '').split(' ', 1)[1] if ' ' in endpoint.get('endpoint', '') else endpoint.get('endpoint', '')
        
        method_color = {
            'GET': '🟢',
            'POST': '🟡',
            'PUT': '🔵',
            'DELETE': '🔴',
            'PATCH': '🟠'
        }.get(method, '⚪')
        
        button_text = f"{method_color} **{method}** `{url}`"
        
        # Create endpoint data for session state
        endpoint_data = {
            'category': section_data['path'],
            'endpoint': endpoint.get('endpoint', ''),
            'method': method,
            'url': url,
            'description': section_data.get('section', {}).get('content_text', ''),
            'request_body': endpoint.get('request_body', {}),
            'curl_command': endpoint.get('curl_command', ''),
            'responses': endpoint.get('responses', {}),
            'raw_endpoint': endpoint
        }
        
        if st.button(
            button_text,
            key=f"nav_endpoint_{endpoint.get('endpoint', '')}_level_{level}_{hash(section_data['path'])}",
            help=f"{endpoint_data['description']}\n\nClick to test this endpoint",
            use_container_width=True
        ):
            st.session_state.current_endpoint = endpoint_data
            st.rerun()

def render_main_content():
    """Render main content area with API details and testing interface"""
    if not st.session_state.current_endpoint:
        st.info("Select an API endpoint from the sidebar to view details and test it.")
        return
    
    endpoint = st.session_state.current_endpoint
    
    # Endpoint header
    st.header(f"{endpoint['method']} {endpoint['url']}")
    st.markdown(f"**Category:** {endpoint['category']}")
    
    if endpoint['description']:
        st.markdown(f"**Description:** {endpoint['description']}")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Request", "🚀 Test", "📄 Response Examples", "📊 History"])
    
    with tab1:
        render_request_details(endpoint)
    
    with tab2:
        render_api_tester(endpoint)
    
    with tab3:
        render_response_examples(endpoint)
    
    with tab4:
        render_request_history()

def render_request_details(endpoint):
    """Render request details"""
    st.subheader("Request Details")
    
    # Method and URL
    col1, col2 = st.columns([1, 3])
    with col1:
        st.text_input("Method", value=endpoint['method'], disabled=True)
    with col2:
        st.text_input("URL", value=endpoint['url'], disabled=True)
    
    # Request body
    if endpoint.get('request_body'):
        st.subheader("Request Body Example")
        st.json(endpoint['request_body'])
    
    # cURL command
    if endpoint.get('curl_command'):
        st.subheader("cURL Command")
        st.code(endpoint['curl_command'], language='bash')

def render_api_tester(endpoint):
    """Render API testing interface"""
    st.subheader("API Tester")
    
    # Get current environment variables for preview
    active_env = db_manager.get_active_environment()
    env_vars = {}
    if active_env and active_env.variables:
        env_vars = active_env.variables
    
    # Show current environment info
    if active_env:
        st.info(f"Active Environment: **{active_env.name}** | Variables: {len(env_vars)} available")
    else:
        st.warning("No active environment set. Variables in {{brackets}} won't be replaced.")
    
    # Helper function to replace variables for preview
    def replace_variables_preview(text):
        if not text or not env_vars:
            return text
        
        preview_text = text
        for key, value in env_vars.items():
            pattern = f"{{{{{key}}}}}"
            preview_text = preview_text.replace(pattern, str(value))
        return preview_text
    
    # URL input with live preview
    st.subheader("URL")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        url = st.text_input(
            "URL Template",
            value=endpoint['url'],
            help="Use {{variable}} syntax for environment variables"
        )
    
    with col2:
        preview_url = replace_variables_preview(url)
        st.text_input(
            "Preview (with variables)",
            value=preview_url,
            disabled=True,
            help="This shows how the URL will look after variable replacement"
        )
    
    # Method selection
    method = st.selectbox(
        "HTTP Method",
        options=api_runner.get_supported_methods(),
        index=api_runner.get_supported_methods().index(endpoint['method'])
    )
    
    # Headers with preview
    st.subheader("Headers")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        headers_json = st.text_area(
            "Headers Template (JSON)",
            value=json.dumps(api_runner.get_common_headers(), indent=2),
            height=150,
            help="Use {{variable}} for environment variables"
        )
    
    with col2:
        try:
            headers_preview = replace_variables_preview(headers_json)
            st.text_area(
                "Headers Preview",
                value=headers_preview,
                height=150,
                disabled=True,
                help="Preview with variables replaced"
            )
        except:
            st.text_area(
                "Headers Preview",
                value="Invalid JSON format",
                height=150,
                disabled=True
            )
    
    # Request body with preview
    st.subheader("Request Body")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        body_json = st.text_area(
            "Body Template (JSON)",
            value=json.dumps(endpoint.get('request_body', {}), indent=2) if endpoint.get('request_body') else "",
            height=200,
            help="Use {{variable}} for environment variables"
        )
    
    with col2:
        try:
            body_preview = replace_variables_preview(body_json)
            st.text_area(
                "Body Preview",
                value=body_preview,
                height=200,
                disabled=True,
                help="Preview with variables replaced"
            )
        except:
            st.text_area(
                "Body Preview",
                value="Invalid JSON format or contains variables",
                height=200,
                disabled=True
            )
    
    # Parameters (query parameters) with preview
    st.subheader("Query Parameters")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        params_json = st.text_area(
            "Parameters Template (JSON)",
            value="{}",
            height=100,
            help="Use {{variable}} for environment variables"
        )
    
    with col2:
        try:
            params_preview = replace_variables_preview(params_json)
            st.text_area(
                "Parameters Preview",
                value=params_preview,
                height=100,
                disabled=True,
                help="Preview with variables replaced"
            )
        except:
            st.text_area(
                "Parameters Preview",
                value="Invalid JSON format",
                height=100,
                disabled=True
            )
    
    # Send request button
    if st.button("Send Request", type="primary"):
        try:
            # Parse JSON inputs
            headers = json.loads(headers_json) if headers_json.strip() else {}
            body = json.loads(body_json) if body_json.strip() else None
            params = json.loads(params_json) if params_json.strip() else {}
            
            # Get environment variables
            env_vars = {}
            active_env = db_manager.get_active_environment()
            if active_env and hasattr(active_env, 'variables') and active_env.variables:
                env_vars = active_env.variables
            
            # Show what variables will be replaced
            if env_vars:
                st.info(f"Using environment variables from: {active_env.name}")
                with st.expander("Variable replacements", expanded=False):
                    for key, value in env_vars.items():
                        st.text(f"{{{{ {key} }}}} → {value}")
            
            # Execute request
            with st.spinner("Sending request..."):
                response_data, execution_time = api_runner.execute_request(
                    method=method,
                    url=url or "",
                    headers=headers,
                    body=body,
                    params=params,
                    environment_vars=env_vars
                )
            
            # Save to history
            db_manager.save_api_history(
                endpoint=f"{method} {url}",
                method=method,
                request_headers=headers,
                request_body=json.dumps(body) if body else "",
                response_status=response_data.get('status_code', 0),
                response_headers=response_data.get('headers', {}),
                response_body=response_data.get('body', ''),
                execution_time=execution_time,
                environment_id=active_env.id if active_env else None
            )
            
            # Display response
            render_response(response_data)
            
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            st.error(f"Request failed: {str(e)}")

def render_response(response_data):
    """Render API response"""
    st.subheader("Response")
    
    # Status and timing info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_code = response_data.get('status_code', 0)
        color = api_runner.get_status_color(status_code)
        st.metric("Status Code", status_code)
    
    with col2:
        exec_time = response_data.get('execution_time', 0)
        st.metric("Time", f"{exec_time}ms")
    
    with col3:
        size = response_data.get('size', 0)
        st.metric("Size", f"{size} bytes")
    
    # Response headers
    if response_data.get('headers'):
        st.subheader("Response Headers")
        headers_df = pd.DataFrame(
            list(response_data['headers'].items()),
            columns=['Header', 'Value']
        )
        st.dataframe(headers_df, use_container_width=True)
    
    # Response body
    st.subheader("Response Body")
    if response_data.get('json'):
        st.json(response_data['json'])
    else:
        st.text_area(
            "Response Text",
            value=response_data.get('body', ''),
            height=300,
            disabled=True
        )

def render_response_examples(endpoint):
    """Render response examples from documentation"""
    st.subheader("Response Examples")
    
    responses = endpoint.get('responses', {})
    if not responses:
        st.info("No response examples available.")
        return
    
    for response_type, response_data in responses.items():
        st.subheader(f"{response_type.capitalize()} Response")
        
        # Status code
        status_code = response_data.get('status_code', 'N/A')
        description = response_data.get('description', 'N/A')
        st.text(f"Status: {status_code} - {description}")
        
        # Example response
        if 'example' in response_data:
            st.json(response_data['example'])

def render_request_history():
    """Render API request history"""
    st.subheader("Request History")
    
    history = db_manager.get_api_history(limit=20)
    if not history:
        st.info("No request history available.")
        return
    
    # Create DataFrame for history
    history_data = []
    for record in history:
        history_data.append({
            'Timestamp': record.executed_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Method': record.method,
            'Endpoint': record.endpoint,
            'Status': record.response_status,
            'Time (ms)': record.execution_time
        })
    
    history_df = pd.DataFrame(history_data)
    st.dataframe(history_df, use_container_width=True)

def render_environment_panel():
    """Render environment variables panel"""
    st.header("🌍 Environment Variables")
    
    # Export section at the top
    with st.expander("📤 Export Environment", expanded=False):
        st.markdown("Export your environment variables in various formats")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 JSON", help="Export as JSON file", key="export_env_json"):
                export_environment_json()
            if st.button("🔗 Postman", help="Export as Postman environment", key="export_env_postman"):
                export_environment_postman()
        
        with col2:
            if st.button("📋 Markdown", help="Export as Markdown file", key="export_env_md"):
                export_environment_markdown()
            if st.button("📊 Report", help="Export environment report", key="export_env_report"):
                export_environment_report()
    
    # Environment import section
    with st.expander("📥 Import Environment", expanded=False):
        st.markdown("Import environment variables from Postman or JSON files")
        env_file = st.file_uploader(
            "Choose environment file",
            type=['json'],
            help="Upload Postman environment or custom JSON file",
            key="env_uploader"
        )
        
        if env_file is not None:
            try:
                env_content = json.load(env_file)
                
                # Check if it's a Postman environment format
                if "_postman_variable_scope" in env_content and env_content["_postman_variable_scope"] == "environment":
                    # Postman format
                    env_name = env_content.get("name", "Imported Environment")
                    variables = {}
                    
                    for var in env_content.get("values", []):
                        if var.get("enabled", True):
                            variables[var["key"]] = var["value"]
                    
                    st.info(f"Postman environment detected: {env_name}")
                    st.json({"variables_count": len(variables), "sample_variables": list(variables.keys())[:5]})
                    
                elif "variables" in env_content:
                    # Custom JSON format
                    env_name = env_content.get("metadata", {}).get("environment_name", "Imported Environment")
                    variables = env_content["variables"]
                    
                    st.info(f"JSON environment detected: {env_name}")
                    st.json({"variables_count": len(variables), "sample_variables": list(variables.keys())[:5]})
                    
                else:
                    # Treat entire JSON as variables
                    env_name = "Imported Environment"
                    variables = env_content
                    
                    st.warning("Generic JSON detected - treating all key-value pairs as variables")
                    st.json({"variables_count": len(variables), "sample_variables": list(variables.keys())[:5]})
                
                # Environment name input
                final_env_name = st.text_input(
                    "Environment Name",
                    value=env_name,
                    key="import_env_name"
                )
                
                env_description = st.text_area(
                    "Description",
                    value="Imported from uploaded file",
                    key="import_env_desc"
                )
                
                if st.button("Import Environment", type="primary", key="import_env_btn"):
                    env_id = db_manager.save_environment(
                        name=final_env_name,
                        description=env_description,
                        variables=variables,
                        is_active=False
                    )
                    st.success(f"Environment imported successfully! (ID: {env_id})")
                    st.rerun()
                    
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please upload a valid JSON document.")
            except Exception as e:
                st.error(f"Error processing environment file: {str(e)}")
    
    # Get environments
    environments = db_manager.get_environments()
    active_env = db_manager.get_active_environment()
    
    # Environment selector
    if environments:
        env_options = {f"{env.name}": env.id for env in environments}
        env_options["None"] = None
        
        current_env = "None"
        if active_env:
            current_env = active_env.name
        
        selected_env = st.selectbox(
            "Active Environment",
            options=list(env_options.keys()),
            index=list(env_options.keys()).index(current_env)
        )
        
        if selected_env != "None":
            selected_env_id = env_options[selected_env]
            if st.button("Set Active"):
                db_manager.set_active_environment(selected_env_id)
                st.success(f"Environment '{selected_env}' is now active!")
                st.rerun()
    
    # Create/Edit Environment
    with st.expander("Create/Edit Environment", expanded=False):
        env_name = st.text_input("Environment Name")
        env_description = st.text_area("Description", height=100)
        
        # Variables input
        st.subheader("Variables")
        variables_json = st.text_area(
            "Variables (JSON format)",
            value='{\n  "api_key": "your-api-key",\n  "base_url": "https://api.example.com",\n  "token": "your-token"\n}',
            height=200,
            help="Enter environment variables in JSON format"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Environment", type="primary"):
                try:
                    variables = json.loads(variables_json)
                    env_id = db_manager.save_environment(
                        name=env_name,
                        description=env_description,
                        variables=variables,
                        is_active=False
                    )
                    st.success(f"Environment saved successfully! (ID: {env_id})")
                    st.rerun()
                except json.JSONDecodeError:
                    st.error("Invalid JSON format in variables")
                except Exception as e:
                    st.error(f"Error saving environment: {str(e)}")
    
    # Display active environment variables
    if active_env:
        st.subheader(f"Active: {active_env.name}")
        if active_env.description:
            st.text(active_env.description)
        
        if active_env.variables:
            st.json(active_env.variables)
        
        # Delete environment
        if st.button("🗑️ Delete Environment", type="secondary"):
            if db_manager.delete_environment(active_env.id):
                st.success("Environment deleted successfully!")
                st.rerun()
    else:
        st.info("No active environment. Create one to use variables in your requests.")
    
    # Environment list
    if environments:
        st.subheader("All Environments")
        for env in environments:
            status = "🟢 Active" if env.is_active else "⚪ Inactive"
            st.text(f"{status} {env.name}")

# Export functions for API Documentation
def export_documentation_json():
    """Export API documentation as JSON from database"""
    try:
        # Get current documentation from database
        docs = db_manager.get_api_documentation()
        if not docs:
            st.error("No API documentation found in database to export")
            return
            
        # Get the currently loaded documentation
        current_doc = None
        for doc in docs:
            if hasattr(doc, 'file_content') and doc.file_content:
                current_doc = doc
                break
                
        if not current_doc:
            st.error("No valid documentation found to export")
            return
            
        # Create parser from database content
        parser = APIParser(current_doc.file_content)
        parser.parse_document()
        
        doc_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "source": "API Documentation Dashboard",
                "format_version": "1.0",
                "document_name": current_doc.name,
                "source_identifier": getattr(current_doc, 'source_identifier', 'Unknown'),
                "last_modified": current_doc.last_modified.isoformat() if hasattr(current_doc, 'last_modified') else None
            },
            "navigation_tree": parser.get_navigation_tree(),
            "endpoints": parser.get_endpoints(),
            "categories": parser.get_categories(),
            "raw_content": current_doc.file_content
        }
        
        json_str = json.dumps(doc_data, indent=2)
        st.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"api_documentation_{current_doc.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    except Exception as e:
        st.error(f"Error exporting JSON: {str(e)}")

def export_documentation_postman():
    """Export API documentation as Postman collection with folders as categories"""
    try:
        # Get current documentation from database
        docs = db_manager.get_api_documentation()
        if not docs:
            st.error("No API documentation found in database to export")
            return
            
        # Get the currently loaded documentation
        current_doc = None
        for doc in docs:
            if hasattr(doc, 'file_content') and doc.file_content:
                current_doc = doc
                break
                
        if not current_doc:
            st.error("No valid documentation found to export")
            return
            
        # Create parser from database content
        parser = APIParser(current_doc.file_content)
        parser.parse_document()
        
        collection = {
            "info": {
                "name": f"{current_doc.name} API Collection",
                "description": f"Exported from API Documentation Dashboard\nSource: {getattr(current_doc, 'source_identifier', 'Unknown')}\nExported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "_postman_id": str(uuid.uuid4()),
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [],
            "variable": [
                {
                    "key": "base_url",
                    "value": "{{base_url}}",
                    "type": "string"
                }
            ]
        }
        
        # Group endpoints by category to create folders
        categories = parser.get_categories()
        navigation_tree = parser.get_navigation_tree()
        
        for category in categories:
            category_endpoints = parser.get_endpoints_by_category(category)
            
            if not category_endpoints:
                continue
                
            # Create folder for each category
            folder = {
                "name": category,
                "item": [],
                "description": f"All endpoints related to {category}"
            }
            
            # Add endpoints as requests within the folder
            for endpoint in category_endpoints:
                method = endpoint.get('method', 'GET')
                url = endpoint.get('url', '')
                description = endpoint.get('description', '')
                
                # Parse URL to extract path components
                url_parts = url.split('/')
                clean_path = [part for part in url_parts if part and not part.startswith('{{')]
                
                request_item = {
                    "name": f"{method} {url.split('/')[-1] or 'root'}",
                    "request": {
                        "method": method,
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json",
                                "type": "text"
                            },
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}",
                                "type": "text"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}" + url,
                            "host": ["{{base_url}}"],
                            "path": url_parts[1:] if url.startswith('/') else url_parts
                        },
                        "description": description
                    },
                    "response": []
                }
                
                # Add request body if available
                if endpoint.get('request_body'):
                    request_item["request"]["body"] = {
                        "mode": "raw",
                        "raw": json.dumps(endpoint['request_body'], indent=2),
                        "options": {
                            "raw": {
                                "language": "json"
                            }
                        }
                    }
                
                # Add query parameters if method is GET
                if method == 'GET':
                    request_item["request"]["url"]["query"] = [
                        {
                            "key": "limit",
                            "value": "{{limit}}",
                            "disabled": True
                        },
                        {
                            "key": "offset",
                            "value": "{{offset}}",
                            "disabled": True
                        }
                    ]
                
                folder["item"].append(request_item)
            
            collection["item"].append(folder)
        
        collection_str = json.dumps(collection, indent=2)
        st.download_button(
            label="🔗 Download Postman Collection",
            data=collection_str,
            file_name=f"postman_collection_{current_doc.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    except Exception as e:
        st.error(f"Error exporting Postman collection: {str(e)}")

def export_documentation_markdown():
    """Export API documentation as Markdown with table of contents and detailed sections"""
    try:
        # Get current documentation from database
        docs = db_manager.get_api_documentation()
        if not docs:
            st.error("No API documentation found in database to export")
            return
            
        # Get the currently loaded documentation
        current_doc = None
        for doc in docs:
            if hasattr(doc, 'file_content') and doc.file_content:
                current_doc = doc
                break
                
        if not current_doc:
            st.error("No valid documentation found to export")
            return
            
        # Create parser from database content
        parser = APIParser(current_doc.file_content)
        parser.parse_document()
        
        endpoints = parser.get_endpoints()
        categories = parser.get_categories()
        navigation_tree = parser.get_navigation_tree()
        
        # Build comprehensive markdown content
        markdown_content = f"""# {current_doc.name} API Documentation

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Source:** {getattr(current_doc, 'source_identifier', 'Unknown')}  
**Total Endpoints:** {len(endpoints)}  
**Categories:** {len(categories)}

---

## Table of Contents

### Quick Navigation
"""
        
        # Build detailed table of contents
        for category in categories:
            category_endpoints = parser.get_endpoints_by_category(category)
            category_anchor = category.lower().replace(' ', '-').replace('/', '-')
            markdown_content += f"\n#### [{category}](#{category_anchor}) ({len(category_endpoints)} endpoints)\n"
            
            # List endpoints under each category in TOC
            for endpoint in category_endpoints:
                method = endpoint.get('method', 'GET')
                url = endpoint.get('url', '')
                endpoint_name = f"{method} {url}"
                endpoint_anchor = endpoint_name.lower().replace(' ', '-').replace('/', '-').replace('{', '').replace('}', '')
                markdown_content += f"- [{endpoint_name}](#{endpoint_anchor})\n"
        
        markdown_content += "\n---\n"
        
        # Add detailed endpoint documentation by category
        for category in categories:
            category_endpoints = parser.get_endpoints_by_category(category)
            if not category_endpoints:
                continue
                
            category_anchor = category.lower().replace(' ', '-').replace('/', '-')
            markdown_content += f"\n## {category}\n\n"
            
            # Add category description if available from navigation tree
            category_info = navigation_tree.get(category, {})
            if category_info.get('section', {}).get('content_text'):
                markdown_content += f"*{category_info['section']['content_text']}*\n\n"
            
            for endpoint in category_endpoints:
                method = endpoint.get('method', 'GET')
                url = endpoint.get('url', '')
                description = endpoint.get('description', 'No description available')
                endpoint_name = f"{method} {url}"
                
                markdown_content += f"### {endpoint_name}\n\n"
                
                # Method badge
                method_color = {
                    'GET': '🟢',
                    'POST': '🟡', 
                    'PUT': '🔵',
                    'DELETE': '🔴',
                    'PATCH': '🟠'
                }.get(method, '⚪')
                
                markdown_content += f"{method_color} **{method}** `{url}`\n\n"
                markdown_content += f"**Description:** {description}\n\n"
                
                # Request details
                markdown_content += "#### Request Details\n\n"
                
                # Headers
                markdown_content += "**Headers:**\n"
                markdown_content += "```\nContent-Type: application/json\n"
                markdown_content += "Authorization: Bearer {{access_token}}\n```\n\n"
                
                # Request body
                if endpoint.get('request_body'):
                    markdown_content += "**Request Body:**\n```json\n"
                    markdown_content += json.dumps(endpoint['request_body'], indent=2)
                    markdown_content += "\n```\n\n"
                
                # cURL example
                if endpoint.get('curl_command'):
                    markdown_content += "**cURL Example:**\n```bash\n"
                    markdown_content += endpoint['curl_command']
                    markdown_content += "\n```\n\n"
                
                # Response examples
                if endpoint.get('responses'):
                    markdown_content += "#### Response Examples\n\n"
                    for response_type, response_data in endpoint['responses'].items():
                        status_code = response_data.get('status_code', 'N/A')
                        status_desc = response_data.get('description', 'N/A')
                        markdown_content += f"**{response_type.title()} Response ({status_code}):**\n"
                        markdown_content += f"*{status_desc}*\n\n"
                        
                        if 'example' in response_data:
                            markdown_content += "```json\n"
                            markdown_content += json.dumps(response_data['example'], indent=2)
                            markdown_content += "\n```\n\n"
                
                markdown_content += "---\n\n"
        
        # Add footer with metadata
        markdown_content += f"""
## Documentation Metadata

- **Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Source Document:** {current_doc.name}
- **Total Categories:** {len(categories)}
- **Total Endpoints:** {len(endpoints)}
- **Database ID:** {current_doc.id if hasattr(current_doc, 'id') else 'N/A'}

---

*Generated by API Documentation Dashboard*
"""
        
        st.download_button(
            label="📋 Download Markdown",
            data=markdown_content,
            file_name=f"api_documentation_{current_doc.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    except Exception as e:
        st.error(f"Error exporting Markdown: {str(e)}")

def export_documentation_report():
    """Export comprehensive documentation report"""
    try:
        if st.session_state.api_parser:
            endpoints = st.session_state.api_parser.get_endpoints()
            categories = st.session_state.api_parser.get_categories()
            
            report_data = {
                "summary": {
                    "total_endpoints": len(endpoints),
                    "total_categories": len(categories),
                    "export_date": datetime.now().isoformat(),
                    "methods_count": {}
                },
                "categories": categories,
                "endpoints_by_method": {},
                "detailed_endpoints": endpoints
            }
            
            # Count methods
            for endpoint in endpoints:
                method = endpoint.get('method', 'GET')
                report_data["summary"]["methods_count"][method] = report_data["summary"]["methods_count"].get(method, 0) + 1
                
                if method not in report_data["endpoints_by_method"]:
                    report_data["endpoints_by_method"][method] = []
                report_data["endpoints_by_method"][method].append(endpoint)
            
            report_str = json.dumps(report_data, indent=2)
            st.download_button(
                label="📊 Download Report",
                data=report_str,
                file_name=f"api_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.error("No API documentation loaded to export")
    except Exception as e:
        st.error(f"Error exporting report: {str(e)}")

# Export functions for Environment Management
def export_environment_json():
    """Export environment variables as JSON"""
    try:
        active_env = db_manager.get_active_environment()
        if active_env and hasattr(active_env, 'variables') and active_env.variables:
            env_data = {
                "metadata": {
                    "export_timestamp": datetime.now().isoformat(),
                    "environment_name": active_env.name,
                    "description": getattr(active_env, 'description', ''),
                    "source": "API Documentation Dashboard"
                },
                "variables": active_env.variables
            }
            
            json_str = json.dumps(env_data, indent=2)
            st.download_button(
                label="📄 Download Environment JSON",
                data=json_str,
                file_name=f"environment_{active_env.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.error("No active environment to export")
    except Exception as e:
        st.error(f"Error exporting environment JSON: {str(e)}")

def export_environment_postman():
    """Export environment variables as Postman environment"""
    try:
        active_env = db_manager.get_active_environment()
        if active_env and hasattr(active_env, 'variables') and active_env.variables:
            postman_env = {
                "id": str(uuid.uuid4()),
                "name": active_env.name,
                "values": [],
                "_postman_variable_scope": "environment",
                "_postman_exported_at": datetime.now().isoformat() + "Z",
                "_postman_exported_using": "API Documentation Dashboard"
            }
            
            # Convert variables to Postman format
            for key, value in active_env.variables.items():
                # Determine if variable should be secret
                is_secret = any(secret_word in key.lower() for secret_word in ['password', 'token', 'secret', 'key', 'auth'])
                
                postman_env["values"].append({
                    "key": key,
                    "value": str(value),
                    "type": "secret" if is_secret else "default",
                    "enabled": True
                })
            
            postman_str = json.dumps(postman_env, indent=2)
            st.download_button(
                label="🔗 Download Postman Environment",
                data=postman_str,
                file_name=f"postman_environment_{active_env.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.error("No active environment to export")
    except Exception as e:
        st.error(f"Error exporting Postman environment: {str(e)}")

def export_environment_markdown():
    """Export environment variables as Markdown"""
    try:
        active_env = db_manager.get_active_environment()
        if active_env and hasattr(active_env, 'variables') and active_env.variables:
            markdown_content = f"""# Environment Variables: {active_env.name}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Description
{getattr(active_env, 'description', 'No description available')}

## Variables

| Variable | Value | Type |
|----------|-------|------|
"""
            
            for key, value in active_env.variables.items():
                # Mask sensitive values
                is_secret = any(secret_word in key.lower() for secret_word in ['password', 'token', 'secret', 'key', 'auth'])
                display_value = "***HIDDEN***" if is_secret else str(value)
                var_type = "Secret" if is_secret else "Default"
                
                markdown_content += f"| {key} | {display_value} | {var_type} |\n"
            
            markdown_content += f"\n## Summary\n- Total Variables: {len(active_env.variables)}\n"
            
            st.download_button(
                label="📋 Download Environment Markdown",
                data=markdown_content,
                file_name=f"environment_{active_env.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        else:
            st.error("No active environment to export")
    except Exception as e:
        st.error(f"Error exporting environment Markdown: {str(e)}")

def export_environment_report():
    """Export comprehensive environment report"""
    try:
        environments = db_manager.get_environments()
        if environments:
            report_data = {
                "summary": {
                    "total_environments": len(environments),
                    "export_date": datetime.now().isoformat(),
                    "active_environment": None
                },
                "environments": []
            }
            
            active_env = db_manager.get_active_environment()
            if active_env:
                report_data["summary"]["active_environment"] = active_env.name
            
            for env in environments:
                env_data = {
                    "name": env.name,
                    "description": getattr(env, 'description', ''),
                    "is_active": bool(active_env and env.id == active_env.id),
                    "variable_count": len(getattr(env, 'variables', {})),
                    "created_at": env.created_at.isoformat() if hasattr(env, 'created_at') else None,
                    "variables": getattr(env, 'variables', {})
                }
                report_data["environments"].append(env_data)
            
            report_str = json.dumps(report_data, indent=2)
            st.download_button(
                label="📊 Download Environment Report",
                data=report_str,
                file_name=f"environment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.error("No environments available to export")
    except Exception as e:
        st.error(f"Error exporting environment report: {str(e)}")

if __name__ == "__main__":
    main()
