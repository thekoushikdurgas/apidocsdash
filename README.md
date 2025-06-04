
# API Documentation Dashboard

A powerful, interactive web application built with Streamlit that provides a Postman-like interface for testing APIs with comprehensive environment management and documentation parsing capabilities.

![API Documentation Dashboard](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)

## 🚀 Overview

The API Documentation Dashboard is a comprehensive tool that allows developers to:
- Parse and visualize API documentation from JSON files
- Test API endpoints with an intuitive interface
- Manage environment variables across different configurations
- Track API request history and responses
- Export documentation and environments in multiple formats

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │  Backend Logic  │    │    Database     │
│   (Streamlit)   │◄──►│   (Python)      │◄──►│  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│  External APIs  │              │
                        │   (HTTP Calls)  │              │
                        └─────────────────┘              │
                                                         │
                        ┌─────────────────┐              │
                        │   File System   │◄─────────────┘
                        │ (JSON Exports)  │
                        └─────────────────┘
```

### Component Architecture

```
app.py (Main Application)
├── Frontend Components
│   ├── Sidebar Navigation
│   ├── Main Content Area
│   └── Environment Panel
│
├── Backend Modules
│   ├── api_parser.py (Documentation Parser)
│   ├── api_runner.py (HTTP Client)
│   ├── database.py (Database Manager)
│   └── models.py (Data Models)
│
└── Data Layer
    ├── PostgreSQL Database
    ├── JSON Configuration Files
    └── Export Files
```

## 📁 Project Structure

### Core Files

| File | Purpose | Description |
|------|---------|-------------|
| **app.py** | Main Application | Streamlit web application entry point with UI components and user interactions |
| **api_parser.py** | Documentation Parser | Parses JSON API documentation and extracts endpoints, navigation tree, and metadata |
| **api_runner.py** | HTTP Client | Handles API requests, response parsing, and cURL command generation |
| **database.py** | Database Manager | Manages PostgreSQL operations for documentation, environments, and history |
| **models.py** | Data Models | SQLAlchemy ORM models for database schema definition |

### Configuration Files

| File | Purpose | Description |
|------|---------|-------------|
| **requirements.txt** | Dependencies | Python package dependencies for the project |
| **pyproject.toml** | Project Config | Python project metadata and build configuration |
| **.streamlit/config.toml** | Streamlit Config | Streamlit-specific configuration settings |
| **default_api_docs.json** | Sample Documentation | Default API documentation loaded on startup |
| **default_environment.json** | Sample Environment | Default environment variables configuration |

### Support Files

| File | Purpose | Description |
|------|---------|-------------|
| **.replit** | Replit Config | Replit environment configuration |
| **uv.lock** | Dependency Lock | Locked dependency versions for reproducible builds |
| **generated-icon.png** | App Icon | Application icon for branding |

## 🛠️ Technology Stack

### Frontend
- **Streamlit 1.45.1** - Web application framework for rapid prototyping
- **CSS/HTML** - Custom styling and layout components
- **JavaScript** - Client-side interactions (WebSocket connections)

### Backend
- **Python 3.11+** - Core programming language
- **SQLAlchemy 2.0.41** - Object-Relational Mapping (ORM) framework
- **Requests 2.32.3** - HTTP library for API calls
- **Pandas 2.2.3** - Data manipulation and analysis

### Database
- **PostgreSQL** - Primary database for persistent storage
- **psycopg2-binary 2.9.10** - PostgreSQL adapter for Python

### Development & Deployment
- **Replit** - Cloud-based development and deployment platform
- **UV** - Modern Python package manager
- **Git** - Version control system

## 🎯 Application Flow

### 1. Application Startup
```
1. Load Streamlit configuration
2. Initialize database connection
3. Create database tables if not exists
4. Load default API documentation
5. Create default environment variables
6. Initialize session state
```

### 2. Documentation Management Flow
```
User uploads JSON file
        ↓
APIParser validates and parses structure
        ↓
Extract endpoints and navigation tree
        ↓
Save to PostgreSQL database
        ↓
Update UI with new documentation
        ↓
Display in sidebar navigation
```

### 3. API Testing Flow
```
User selects endpoint from navigation
        ↓
Load endpoint details and templates
        ↓
User configures request parameters
        ↓
APIRunner processes environment variables
        ↓
Execute HTTP request to target API
        ↓
Parse and display response
        ↓
Save request/response to history
```

### 4. Environment Management Flow
```
User creates/imports environment
        ↓
Variables stored in database
        ↓
Set environment as active
        ↓
Variables available for API requests
        ↓
Template replacement during execution
```

### 5. Export Flow
```
User initiates export
        ↓
Gather data from database/parser
        ↓
Format according to export type
        ↓
Generate downloadable file
        ↓
Provide download link to user
```

## 🗄️ Database Schema

### APIDocumentation Table
```sql
CREATE TABLE api_documentation (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    source_identifier VARCHAR(255),
    file_content JSON,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    last_modified TIMESTAMP DEFAULT NOW()
);
```

### Environment Table
```sql
CREATE TABLE environments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    variables JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT FALSE
);
```

### APIHistory Table
```sql
CREATE TABLE api_history (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_headers JSON,
    request_body TEXT,
    response_status INTEGER,
    response_headers JSON,
    response_body TEXT,
    execution_time INTEGER,
    executed_at TIMESTAMP DEFAULT NOW(),
    environment_id INTEGER
);
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Replit account (for deployment)

### Installation
1. Clone or fork this repository in Replit
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables for database connection
4. Run the application:
   ```bash
   streamlit run app.py --server.port 5000
   ```

### Configuration
- Database: Configure PostgreSQL connection in environment variables
- Streamlit: Modify `.streamlit/config.toml` for custom settings
- Default data: Update `default_api_docs.json` and `default_environment.json`

## 📊 Features

### Core Features
- ✅ **Documentation Parsing** - Parse JSON API documentation files
- ✅ **Interactive Navigation** - Tree-style endpoint navigation
- ✅ **API Testing** - Postman-like request interface
- ✅ **Environment Management** - Multiple environment configurations
- ✅ **Request History** - Track all API calls and responses
- ✅ **Export Capabilities** - Multiple export formats (JSON, Postman, Markdown)

### Advanced Features
- ✅ **Variable Templating** - Environment variable substitution
- ✅ **Search Functionality** - Search across endpoints
- ✅ **Response Analysis** - Detailed response inspection
- ✅ **cURL Generation** - Generate cURL commands
- ✅ **Import/Export** - Backup and restore configurations

## 🔧 Customization

### Adding New Export Formats
1. Create export function in `app.py`
2. Add UI button in appropriate expander
3. Implement format-specific logic

### Extending Parser Support
1. Modify `APIParser` class in `api_parser.py`
2. Add new parsing methods for different formats
3. Update validation logic

### Database Modifications
1. Update models in `models.py`
2. Create migration scripts if needed
3. Update database manager methods

## 🚀 Deployment on Replit

This application is designed to run seamlessly on Replit:

1. **Auto-dependency Installation** - Requirements are automatically installed
2. **Database Integration** - PostgreSQL databases can be easily attached
3. **Environment Variables** - Secure variable management through Replit
4. **Instant Deployment** - One-click deployment to production
5. **Custom Domain** - Optional custom domain configuration

### Deployment Steps
1. Ensure all environment variables are set in Replit
2. Click the "Run" button to start the application
3. Access via the provided Replit URL
4. Deploy to production using Replit Deployments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙋‍♂️ Support

For support and questions:
- Create an issue in the repository
- Check the documentation for common solutions
- Review the code comments for implementation details

---

**Built with ❤️ using Streamlit and deployed on Replit**
