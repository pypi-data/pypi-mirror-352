![MockLoop](logo.png "MockLoop")

# MockLoop MCP - AI-Native Testing Platform

[![PyPI version](https://img.shields.io/pypi/v/mockloop-mcp.svg)](https://pypi.org/project/mockloop-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/mockloop-mcp.svg)](https://pypi.org/project/mockloop-mcp/)
[![Downloads](https://img.shields.io/pypi/dm/mockloop-mcp.svg)](https://pypi.org/project/mockloop-mcp/)
[![License](https://img.shields.io/pypi/l/mockloop-mcp.svg)](https://github.com/mockloop/mockloop-mcp/blob/main/LICENSE)
[![Tests](https://github.com/mockloop/mockloop-mcp/workflows/Tests/badge.svg)](https://github.com/mockloop/mockloop-mcp/actions)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://docs.mockloop.com)
[![AI-Native](https://img.shields.io/badge/AI--Native-Testing-blue.svg)](https://docs.mockloop.com/ai-integration/overview/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

**The world's first AI-native API testing platform** powered by the Model Context Protocol (MCP). MockLoop MCP revolutionizes API testing with comprehensive AI-driven scenario generation, automated test execution, and intelligent analysis capabilities.

**🚀 Revolutionary Capabilities:** 5 AI Prompts • 15 Scenario Resources • 16 Testing Tools • 10 Context Tools • 4 Core Tools • Complete MCP Integration

**📚 Documentation:** https://docs.mockloop.com  
**📦 PyPI Package:** https://pypi.org/project/mockloop-mcp/  
**🐙 GitHub Repository:** https://github.com/mockloop/mockloop-mcp

## 🌟 What Makes MockLoop MCP Revolutionary?

MockLoop MCP represents a paradigm shift in API testing, introducing the world's first **AI-native testing architecture** that combines:

- **🤖 AI-Driven Test Generation**: 5 specialized MCP prompts for intelligent scenario creation  
- **📦 Community Scenario Packs**: 15 curated testing resources with community architecture  
- **⚡ Automated Test Execution**: 30 comprehensive MCP tools for complete testing workflows (16 testing + 10 context + 4 core)  
- **🔄 Stateful Testing**: Advanced context management with GlobalContext and AgentContext  
- **📊 Enterprise Compliance**: Complete audit logging and regulatory compliance tracking  
- **🏗️ Dual-Port Architecture**: Eliminates /admin path conflicts with separate business and admin ports  

## 🎯 Core AI-Native Architecture

### MCP Audit Logging
**Enterprise-grade compliance and regulatory tracking**  
- Complete request/response audit trails  
- Regulatory compliance monitoring  
- Performance metrics and analytics  
- Security event logging  

### MCP Prompts (5 AI-Driven Capabilities)  
**Intelligent scenario generation powered by AI**  
- [`analyze_openapi_for_testing`](src/mockloop_mcp/mcp_prompts.py:1) - Comprehensive API analysis for testing strategies  
- [`generate_scenario_config`](src/mockloop_mcp/mcp_prompts.py:1) - Dynamic test scenario configuration  
- [`optimize_scenario_for_load`](src/mockloop_mcp/mcp_prompts.py:1) - Load testing optimization  
- [`generate_error_scenarios`](src/mockloop_mcp/mcp_prompts.py:1) - Error condition simulation  
- [`generate_security_test_scenarios`](src/mockloop_mcp/mcp_prompts.py:1) - Security vulnerability testing  

### MCP Resources (15 Scenario Packs)  
**Community-driven testing scenarios with advanced architecture**  
- **Load Testing Scenarios**: High-volume traffic simulation  
- **Error Simulation Packs**: Comprehensive error condition testing  
- **Security Testing Suites**: Vulnerability assessment scenarios   
- **Performance Benchmarks**: Standardized performance testing  
- **Integration Test Packs**: Cross-service testing scenarios  
- **Community Architecture**: Collaborative scenario sharing and validation  

### MCP Tools (16 Automated Testing Tools)  
**Complete automated test execution capabilities**  

#### Scenario Management (4 tools)  
- [`validate_scenario_config`](src/mockloop_mcp/mcp_tools.py:1) - Scenario validation and verification  
- [`deploy_scenario`](src/mockloop_mcp/mcp_tools.py:1) - Automated scenario deployment  
- [`switch_scenario`](src/mockloop_mcp/mcp_tools.py:1) - Dynamic scenario switching  
- [`list_active_scenarios`](src/mockloop_mcp/mcp_tools.py:1) - Active scenario monitoring  

#### Test Execution (4 tools)  
- [`execute_test_plan`](src/mockloop_mcp/mcp_tools.py:1) - Comprehensive test plan execution
- [`run_test_iteration`](src/mockloop_mcp/mcp_tools.py:1) - Individual test iteration management
- [`run_load_test`](src/mockloop_mcp/mcp_tools.py:1) - Load testing execution
- [`run_security_test`](src/mockloop_mcp/mcp_tools.py:1) - Security testing automation

#### Analysis & Reporting (4 tools)
- [`analyze_test_results`](src/mockloop_mcp/mcp_tools.py:1) - Intelligent test result analysis
- [`generate_test_report`](src/mockloop_mcp/mcp_tools.py:1) - Comprehensive reporting
- [`compare_test_runs`](src/mockloop_mcp/mcp_tools.py:1) - Test run comparison and trends
- [`get_performance_metrics`](src/mockloop_mcp/mcp_tools.py:1) - Performance metrics collection

#### Workflow Management (4 tools)
- [`create_test_session`](src/mockloop_mcp/mcp_tools.py:1) - Test session initialization
- [`end_test_session`](src/mockloop_mcp/mcp_tools.py:1) - Session cleanup and finalization
- [`schedule_test_suite`](src/mockloop_mcp/mcp_tools.py:1) - Automated test scheduling
- [`monitor_test_progress`](src/mockloop_mcp/mcp_tools.py:1) - Real-time progress monitoring

### MCP Context Management (10 Stateful Workflow Tools)
**Advanced state management for complex testing workflows**

#### Context Creation & Management
- [`create_test_session_context`](src/mockloop_mcp/mcp_context.py:1) - Test session state management
- [`create_workflow_context`](src/mockloop_mcp/mcp_context.py:1) - Complex workflow orchestration
- [`create_agent_context`](src/mockloop_mcp/mcp_context.py:1) - AI agent state management

#### Data Management
- [`get_context_data`](src/mockloop_mcp/mcp_context.py:1) - Context data retrieval
- [`update_context_data`](src/mockloop_mcp/mcp_context.py:1) - Dynamic context updates
- [`list_contexts_by_type`](src/mockloop_mcp/mcp_context.py:1) - Context discovery and listing

#### Snapshot & Recovery
- [`create_context_snapshot`](src/mockloop_mcp/mcp_context.py:1) - State snapshot creation
- [`restore_context_snapshot`](src/mockloop_mcp/mcp_context.py:1) - State rollback capabilities

#### Global Context
- [`get_global_context_data`](src/mockloop_mcp/mcp_context.py:1) - Cross-session data sharing
- [`update_global_context_data`](src/mockloop_mcp/mcp_context.py:1) - Global state management

## 🚀 Quick Start

Get started with the world's most advanced AI-native testing platform:

```bash
# 1. Install MockLoop MCP
pip install mockloop-mcp

# 2. Verify installation
mockloop-mcp --version

# 3. Configure with your MCP client (Cline, Claude Desktop, etc.)
# See configuration examples below
```

## 📋 Prerequisites

- Python 3.10+
- Pip package manager
- Docker and Docker Compose (for containerized mock servers)
- An MCP-compatible client (Cline, Claude Desktop, etc.)

## 🔧 Installation

### Option 1: Install from PyPI (Recommended)

```bash
# Install the latest stable version
pip install mockloop-mcp

# Or install with optional dependencies
pip install mockloop-mcp[dev]   # Development tools
pip install mockloop-mcp[docs]  # Documentation tools
pip install mockloop-mcp[all]   # All optional dependencies

# Verify installation
mockloop-mcp --version
```

### Option 2: Development Installation

```bash
# Clone the repository
git clone https://github.com/mockloop/mockloop-mcp.git
cd mockloop-mcp

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## ⚙️ Configuration

### MCP Client Configuration

#### Cline (VS Code Extension)

Add to your Cline MCP settings file:

```json
{
  "mcpServers": {
    "MockLoopLocal": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "command": "mockloop-mcp",
      "args": [],
      "transportType": "stdio"
    }
  }
}
```

#### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mockloop": {
      "command": "mockloop-mcp",
      "args": []
    }
  }
}
```

#### Virtual Environment Installations

For virtual environment installations, use the full Python path:

```json
{
  "mcpServers": {
    "MockLoopLocal": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["-m", "mockloop_mcp"],
      "transportType": "stdio"
    }
  }
}
```

## 🛠️ Available MCP Tools

### Core Mock Generation

#### `generate_mock_api`
Generate sophisticated FastAPI mock servers with dual-port architecture.

**Parameters:**
- `spec_url_or_path` (string, required): API specification URL or local file path
- `output_dir_name` (string, optional): Output directory name
- `auth_enabled` (boolean, optional): Enable authentication middleware (default: true)
- `webhooks_enabled` (boolean, optional): Enable webhook support (default: true)
- `admin_ui_enabled` (boolean, optional): Enable admin UI (default: true)
- `storage_enabled` (boolean, optional): Enable storage functionality (default: true)

**Revolutionary Dual-Port Architecture:**
- **Business API Port**: Serves your API endpoints (default: 8000)
- **Admin UI Port**: Separate admin interface (default: 8001)
- **Conflict Resolution**: Eliminates /admin path conflicts in OpenAPI specs
- **Enhanced Security**: Port-based access control and isolation

### Advanced Analytics

#### `query_mock_logs`
Query and analyze request logs with AI-powered insights.

**Parameters:**
- `server_url` (string, required): Mock server URL
- `limit` (integer, optional): Maximum logs to return (default: 100)
- `offset` (integer, optional): Pagination offset (default: 0)
- `method` (string, optional): Filter by HTTP method
- `path_pattern` (string, optional): Regex pattern for path filtering
- `time_from` (string, optional): Start time filter (ISO format)
- `time_to` (string, optional): End time filter (ISO format)
- `include_admin` (boolean, optional): Include admin requests (default: false)
- `analyze` (boolean, optional): Perform AI analysis (default: true)

**AI-Powered Analysis:**
- Performance metrics (P95/P99 response times)
- Error rate analysis and categorization
- Traffic pattern detection
- Automated debugging recommendations
- Session correlation and tracking

#### `discover_mock_servers`
Intelligent server discovery with dual-port architecture support.

**Parameters:**
- `ports` (array, optional): Ports to scan (default: common ports)
- `check_health` (boolean, optional): Perform health checks (default: true)
- `include_generated` (boolean, optional): Include generated mocks (default: true)

**Advanced Discovery:**
- Automatic architecture detection (single-port vs dual-port)
- Health status monitoring
- Server correlation and matching
- Port usage analysis

#### `manage_mock_data`
Dynamic response management without server restart.

**Parameters:**
- `server_url` (string, required): Mock server URL
- `operation` (string, required): Operation type ("update_response", "create_scenario", "switch_scenario", "list_scenarios")
- `endpoint_path` (string, optional): API endpoint path
- `response_data` (object, optional): New response data
- `scenario_name` (string, optional): Scenario name
- `scenario_config` (object, optional): Scenario configuration

**Dynamic Capabilities:**
- Real-time response updates
- Scenario-based testing
- Runtime configuration management
- Zero-downtime modifications

## 🤖 AI Framework Integration

MockLoop MCP provides native integration with popular AI frameworks:

### LangGraph Integration

```python
from langgraph.graph import StateGraph, END
from mockloop_mcp import MockLoopClient

# Initialize MockLoop client
mockloop = MockLoopClient()

def setup_ai_testing(state):
    """AI-driven test setup"""
    # Generate mock API with AI analysis
    result = mockloop.generate_mock_api(
        spec_url_or_path="https://api.example.com/openapi.json",
        output_dir_name="ai_test_environment"
    )
    
    # Use AI prompts for scenario generation
    scenarios = mockloop.analyze_openapi_for_testing(
        api_spec=state["api_spec"],
        analysis_depth="comprehensive",
        include_security_tests=True
    )
    
    state["mock_server_url"] = "http://localhost:8000"
    state["test_scenarios"] = scenarios
    return state

def execute_ai_tests(state):
    """Execute AI-generated test scenarios"""
    # Deploy AI-generated scenarios
    for scenario in state["test_scenarios"]:
        mockloop.deploy_scenario(
            server_url=state["mock_server_url"],
            scenario_config=scenario
        )
        
        # Execute load tests with AI optimization
        results = mockloop.run_load_test(
            server_url=state["mock_server_url"],
            scenario_name=scenario["name"],
            duration=300,
            concurrent_users=100
        )
        
        # AI-powered result analysis
        analysis = mockloop.analyze_test_results(
            test_results=results,
            include_recommendations=True
        )
        
        state["test_results"].append(analysis)
    
    return state

# Build AI-native testing workflow
workflow = StateGraph(dict)
workflow.add_node("setup_ai_testing", setup_ai_testing)
workflow.add_node("execute_ai_tests", execute_ai_tests)
workflow.set_entry_point("setup_ai_testing")
workflow.add_edge("setup_ai_testing", "execute_ai_tests")
workflow.add_edge("execute_ai_tests", END)

app = workflow.compile()
```

### CrewAI Multi-Agent Testing

```python
from crewai import Agent, Task, Crew
from mockloop_mcp import MockLoopClient

# Initialize MockLoop client
mockloop = MockLoopClient()

# AI Testing Specialist Agent
api_testing_agent = Agent(
    role='AI API Testing Specialist',
    goal='Generate and execute comprehensive AI-driven API tests',
    backstory='Expert in AI-native testing with MockLoop MCP integration',
    tools=[
        mockloop.generate_mock_api,
        mockloop.analyze_openapi_for_testing,
        mockloop.generate_scenario_config
    ]
)

# Performance Analysis Agent
performance_agent = Agent(
    role='AI Performance Analyst',
    goal='Analyze API performance with AI-powered insights',
    backstory='Specialist in AI-driven performance analysis and optimization',
    tools=[
        mockloop.run_load_test,
        mockloop.get_performance_metrics,
        mockloop.analyze_test_results
    ]
)

# Security Testing Agent
security_agent = Agent(
    role='AI Security Testing Expert',
    goal='Conduct AI-driven security testing and vulnerability assessment',
    backstory='Expert in AI-powered security testing methodologies',
    tools=[
        mockloop.generate_security_test_scenarios,
        mockloop.run_security_test,
        mockloop.compare_test_runs
    ]
)

# Define AI-driven tasks
ai_setup_task = Task(
    description='Generate AI-native mock API with comprehensive testing scenarios',
    agent=api_testing_agent,
    expected_output='Mock server with AI-generated test scenarios deployed'
)

performance_task = Task(
    description='Execute AI-optimized performance testing and analysis',
    agent=performance_agent,
    expected_output='Comprehensive performance analysis with AI recommendations'
)

security_task = Task(
    description='Conduct AI-driven security testing and vulnerability assessment',
    agent=security_agent,
    expected_output='Security test results with AI-powered threat analysis'
)

# Create AI testing crew
ai_testing_crew = Crew(
    agents=[api_testing_agent, performance_agent, security_agent],
    tasks=[ai_setup_task, performance_task, security_task],
    verbose=True
)

# Execute AI-native testing workflow
results = ai_testing_crew.kickoff()
```

### LangChain AI Testing Tools

```python
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from mockloop_mcp import MockLoopClient

# Initialize MockLoop client
mockloop = MockLoopClient()

# AI-Native Testing Tools
def ai_generate_mock_api(spec_path: str) -> str:
    """Generate AI-enhanced mock API with intelligent scenarios"""
    # Generate mock API
    result = mockloop.generate_mock_api(spec_url_or_path=spec_path)
    
    # Use AI to analyze and enhance
    analysis = mockloop.analyze_openapi_for_testing(
        api_spec=spec_path,
        analysis_depth="comprehensive",
        include_security_tests=True
    )
    
    return f"AI-enhanced mock API generated: {result}\nAI Analysis: {analysis['summary']}"

def ai_execute_testing_workflow(server_url: str) -> str:
    """Execute comprehensive AI-driven testing workflow"""
    # Create test session context
    session = mockloop.create_test_session_context(
        session_name="ai_testing_session",
        configuration={"ai_enhanced": True}
    )
    
    # Generate and deploy AI scenarios
    scenarios = mockloop.generate_scenario_config(
        api_spec=server_url,
        scenario_types=["load", "error", "security"],
        ai_optimization=True
    )
    
    results = []
    for scenario in scenarios:
        # Deploy scenario
        mockloop.deploy_scenario(
            server_url=server_url,
            scenario_config=scenario
        )
        
        # Execute tests with AI monitoring
        test_result = mockloop.execute_test_plan(
            server_url=server_url,
            test_plan=scenario["test_plan"],
            ai_monitoring=True
        )
        
        results.append(test_result)
    
    # AI-powered analysis
    analysis = mockloop.analyze_test_results(
        test_results=results,
        include_recommendations=True,
        ai_insights=True
    )
    
    return f"AI testing workflow completed: {analysis['summary']}"

# Create LangChain tools
ai_testing_tools = [
    Tool(
        name="AIGenerateMockAPI",
        func=ai_generate_mock_api,
        description="Generate AI-enhanced mock API with intelligent testing scenarios"
    ),
    Tool(
        name="AIExecuteTestingWorkflow",
        func=ai_execute_testing_workflow,
        description="Execute comprehensive AI-driven testing workflow with intelligent analysis"
    )
]

# Create AI testing agent
llm = ChatOpenAI(temperature=0)
ai_testing_prompt = PromptTemplate.from_template("""
You are an AI-native testing assistant powered by MockLoop MCP.
You have access to revolutionary AI-driven testing capabilities including:
- AI-powered scenario generation
- Intelligent test execution
- Advanced performance analysis
- Security vulnerability assessment
- Stateful workflow management

Tools available: {tools}
Tool names: {tool_names}

Question: {input}
{agent_scratchpad}
""")

agent = create_react_agent(llm, ai_testing_tools, ai_testing_prompt)
agent_executor = AgentExecutor(agent=agent, tools=ai_testing_tools, verbose=True)

# Execute AI-native testing
response = agent_executor.invoke({
    "input": "Generate a comprehensive AI-driven testing environment for a REST API and execute full testing workflow"
})
```

## 🏗️ Dual-Port Architecture

MockLoop MCP introduces a revolutionary **dual-port architecture** that eliminates common conflicts and enhances security:

### Architecture Benefits

- **🔒 Enhanced Security**: Complete separation of business and admin functionality
- **⚡ Zero Conflicts**: Eliminates /admin path conflicts in OpenAPI specifications
- **📊 Clean Analytics**: Admin calls don't appear in business API metrics
- **🔄 Independent Scaling**: Scale business and admin services separately
- **🛡️ Port-Based Access Control**: Enhanced security through network isolation

### Port Configuration

```python
# Generate mock with dual-port architecture
result = mockloop.generate_mock_api(
    spec_url_or_path="https://api.example.com/openapi.json",
    business_port=8000,  # Business API port
    admin_port=8001,     # Admin UI port
    admin_ui_enabled=True
)
```

### Access Points

- **Business API**: `http://localhost:8000` - Your API endpoints
- **Admin UI**: `http://localhost:8001` - Management interface
- **API Documentation**: `http://localhost:8000/docs` - Interactive Swagger UI
- **Health Check**: `http://localhost:8000/health` - Server status

## 📊 Enterprise Features

### Compliance & Audit Logging

MockLoop MCP provides enterprise-grade compliance features:

- **Complete Audit Trails**: Every request/response logged with metadata
- **Regulatory Compliance**: GDPR, SOX, HIPAA compliance support
- **Performance Metrics**: P95/P99 response times, error rates
- **Security Monitoring**: Threat detection and analysis
- **Session Tracking**: Cross-request correlation and analysis

### Advanced Analytics

- **AI-Powered Insights**: Intelligent analysis and recommendations
- **Traffic Pattern Detection**: Automated anomaly detection
- **Performance Optimization**: AI-driven performance recommendations
- **Error Analysis**: Intelligent error categorization and resolution
- **Trend Analysis**: Historical performance and usage trends

## 🔄 Stateful Testing Workflows

MockLoop MCP supports complex, stateful testing workflows through advanced context management:

### Context Types

- **Test Session Context**: Maintain state across test executions
- **Workflow Context**: Complex multi-step testing orchestration
- **Agent Context**: AI agent state management and coordination
- **Global Context**: Cross-session data sharing and persistence

### Example: Stateful E-commerce Testing

```python
# Create test session context
session = mockloop.create_test_session_context(
    session_name="ecommerce_integration_test",
    configuration={
        "test_type": "integration",
        "environment": "staging",
        "ai_enhanced": True
    }
)

# Create workflow context for multi-step testing
workflow = mockloop.create_workflow_context(
    workflow_name="user_journey_test",
    parent_context=session["context_id"],
    steps=[
        "user_registration",
        "product_browsing",
        "cart_management",
        "checkout_process",
        "order_fulfillment"
    ]
)

# Execute stateful test workflow
for step in workflow["steps"]:
    # Update context with step data
    mockloop.update_context_data(
        context_id=workflow["context_id"],
        data={"current_step": step, "timestamp": datetime.now()}
    )
    
    # Execute step-specific tests
    test_result = mockloop.execute_test_plan(
        server_url="http://localhost:8000",
        test_plan=f"{step}_test_plan",
        context_id=workflow["context_id"]
    )
    
    # Create snapshot for rollback capability
    snapshot = mockloop.create_context_snapshot(
        context_id=workflow["context_id"],
        snapshot_name=f"{step}_completion"
    )

# Analyze complete workflow results
final_analysis = mockloop.analyze_test_results(
    test_results=workflow["results"],
    context_id=workflow["context_id"],
    include_recommendations=True
)
```

## 🚀 Running Generated Mock Servers

### Using Docker Compose (Recommended)

```bash
# Navigate to generated mock directory
cd generated_mocks/your_api_mock

# Start with dual-port architecture
docker-compose up --build

# Access points:
# Business API: http://localhost:8000
# Admin UI: http://localhost:8001
```

### Using Uvicorn Directly

```bash
# Install dependencies
pip install -r requirements_mock.txt

# Start the mock server
uvicorn main:app --reload --port 8000
```

### Enhanced Features Access

- **Admin UI**: `http://localhost:8001` - Enhanced management interface
- **API Documentation**: `http://localhost:8000/docs` - Interactive Swagger UI
- **Health Check**: `http://localhost:8000/health` - Server status and metrics
- **Log Analytics**: `http://localhost:8001/api/logs/search` - Advanced log querying
- **Performance Metrics**: `http://localhost:8001/api/logs/analyze` - AI-powered insights
- **Scenario Management**: `http://localhost:8001/api/mock-data/scenarios` - Dynamic testing

## 📈 Performance & Scalability

MockLoop MCP is designed for enterprise-scale performance:

### Performance Metrics

- **Response Times**: P50, P95, P99 percentile tracking
- **Throughput**: Requests per second monitoring
- **Error Rates**: Comprehensive error analysis
- **Resource Usage**: Memory, CPU, and network monitoring
- **Concurrency**: Multi-user load testing support

### Scalability Features

- **Horizontal Scaling**: Multi-instance deployment support
- **Load Balancing**: Built-in load balancing capabilities
- **Caching**: Intelligent response caching
- **Database Optimization**: Efficient SQLite and PostgreSQL support
- **Container Orchestration**: Kubernetes and Docker Swarm ready

## 🔒 Security Features

### Built-in Security

- **Authentication Middleware**: Configurable auth mechanisms
- **Rate Limiting**: Prevent abuse and DoS attacks
- **Input Validation**: Comprehensive request validation
- **Security Headers**: CORS, CSP, and security headers
- **Audit Logging**: Complete security event logging

### Security Testing

- **Vulnerability Assessment**: AI-powered security testing
- **Penetration Testing**: Automated security scenario generation
- **Compliance Checking**: Security standard compliance verification
- **Threat Modeling**: AI-driven threat analysis
- **Security Reporting**: Comprehensive security analytics

## 🛣️ Roadmap & Future Development

### Completed Phases ✅

- **Phase 1**: MCP Audit Logging - Enterprise compliance tracking
- **Phase 2**: MCP Prompts - AI-driven scenario generation
- **Phase 3**: MCP Resources - Community scenario packs
- **Phase 4**: MCP Tools - Automated test execution
- **Phase 5**: MCP Context Management - Stateful workflows

### Upcoming Features 🚧

#### Enhanced AI Capabilities
- **Advanced ML Models**: Custom model training for API testing
- **Predictive Analytics**: AI-powered failure prediction
- **Intelligent Test Generation**: Self-improving test scenarios
- **Natural Language Testing**: Plain English test descriptions

#### Extended Protocol Support
- **GraphQL Support**: Native GraphQL API testing
- **gRPC Integration**: Protocol buffer testing support
- **WebSocket Testing**: Real-time communication testing
- **Event-Driven Testing**: Async and event-based API testing

#### Enterprise Integration
- **CI/CD Integration**: Native pipeline integration
- **Monitoring Platforms**: Datadog, New Relic, Prometheus integration
- **Identity Providers**: SSO and enterprise auth integration
- **Compliance Frameworks**: Extended regulatory compliance support

## 🤝 Contributing

We welcome contributions to MockLoop MCP! Please see our [Contributing Guidelines](docs/contributing/guidelines.md) for details.

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/mockloop-mcp.git
cd mockloop-mcp

# Create development environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run quality checks
ruff check src/
bandit -r src/
```

### Community

- **GitHub Repository**: [mockloop/mockloop-mcp](https://github.com/mockloop/mockloop-mcp)
- **Issues & Bug Reports**: [GitHub Issues](https://github.com/mockloop/mockloop-mcp/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/mockloop/mockloop-mcp/issues)
- **Documentation**: [docs.mockloop.com](https://docs.mockloop.com)

## 📄 License

MockLoop MCP is licensed under the [MIT License](LICENSE).

---

## 🎉 Get Started Today!

Ready to revolutionize your API testing with the world's first AI-native testing platform?

```bash
pip install mockloop-mcp
```

**Join the AI-native testing revolution** and experience the future of API testing with MockLoop MCP!

**🚀 [Get Started Now](https://docs.mockloop.com/getting-started/installation/) →**
