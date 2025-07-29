<p align="center">
  <img src="logo.svg" alt="Google Search Console MCP Logo" width="120" />
</p>

# Google Search Console MCP Server

[![PyPI version](https://badge.fury.io/py/google-search-console-mcp.svg)](https://badge.fury.io/py/google-search-console-mcp)
[![GitHub stars](https://img.shields.io/github/stars/surendranb/google-search-console-mcp?style=social)](https://github.com/surendranb/google-search-console-mcp/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/surendranb/google-search-console-mcp?style=social)](https://github.com/surendranb/google-search-console-mcp/network/members)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/surendranb/google-search-console-mcp)

Connect Google Search Console data to Claude, Cursor and other MCP clients. Query your website's search performance data in natural language with access to all GSC dimensions and metrics.

**Compatible with:** Claude, Cursor and other MCP clients.

---

## Prerequisites

**Check your Python setup:**

```bash
# Check Python version (need 3.8+)
python --version
python3 --version

# Check pip
pip --version
pip3 --version
```

**Required:**
- Python 3.8 or higher
- Google Search Console property with data
- Service account with Search Console API access

---

## Step 1: Setup Google Search Console Credentials

### Create Service Account in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. **Create or select a project**:
   - New project: Click "New Project" → Enter project name → Create
   - Existing project: Select from dropdown
3. **Enable the Search Console API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Search Console API" → Click "Enable"
4. **Create Service Account**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Enter name (e.g., "gsc-mcp-server")
   - Click "Create and Continue"
   - Skip role assignment → Click "Done"
5. **Download JSON Key**:
   - Click your service account
   - Go to "Keys" tab → "Add Key" → "Create New Key"
   - Select "JSON" → Click "Create"
   - Save the JSON file - you'll need its path

### Add Service Account to Search Console

1. **Get service account email**:
   - Open the JSON file
   - Find the `client_email` field
   - Copy the email (format: `gsc-mcp-server@your-project.iam.gserviceaccount.com`)
2. **Add to Search Console**:
   - Go to [Google Search Console](https://search.google.com/search-console)
   - Select your property
   - Click "Settings" (gear icon)
   - Click "Users and permissions"
   - Click "Add User"
   - Paste the service account email
   - Select "Full" permission
   - Click "Add"

### Find Your Search Console Property

1. In [Google Search Console](https://search.google.com/search-console), select your property
2. The property URL will be in the format:
   - For domain properties: `sc-domain:example.com`
   - For URL-prefix properties: `https://example.com/`

### Test Your Setup (Optional)

Verify your credentials:

```bash
pip install google-api-python-client
```

Create a test script (`test_gsc.py`):

```python
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set credentials path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/your/service-account-key.json"

# Test connection
credentials = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
    scopes=['https://www.googleapis.com/auth/webmasters.readonly']
)

service = build('searchconsole', 'v1', credentials=credentials)
print("✅ GSC credentials working!")
```

Run the test:

```bash
python test_gsc.py
```

If you see "✅ GSC credentials working!" you're ready to proceed.

---

## Step 2: Install the MCP Server

Choose one method:

### Method A: pip install (Recommended)

```bash
pip install google-search-console-mcp
```

**MCP Configuration:**

First, check your Python command:

```bash
python3 --version
python --version
```

Then use the appropriate configuration:

If `python3 --version` worked:

```json
{
  "mcpServers": {
    "gsc-search": {
      "command": "python3",
      "args": ["-m", "gsc_mcp_server"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/your/service-account-key.json",
        "GSC_SITE_URL": "https://example.com/"
      }
    }
  }
}
```

If `python --version` worked:

```json
{
  "mcpServers": {
    "gsc-search": {
      "command": "python",
      "args": ["-m", "gsc_mcp_server"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/your/service-account-key.json",
        "GSC_SITE_URL": "https://example.com/"
      }
    }
  }
}
```

### Method B: GitHub download

```bash
git clone https://github.com/surendranb/google-search-console-mcp.git
cd google-search-console-mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**MCP Configuration:**

```json
{
  "mcpServers": {
    "gsc-search": {
      "command": "/full/path/to/google-search-console-mcp/venv/bin/python",
      "args": ["/full/path/to/google-search-console-mcp/gsc_mcp_server.py"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/your/service-account-key.json",
        "GSC_SITE_URL": "https://example.com/"
      }
    }
  }
}
```

---

## Step 3: Update Configuration

**Replace these placeholders in your MCP configuration:**
- `/path/to/your/service-account-key.json` with your JSON file path
- `https://example.com/` with your Search Console property URL
- `/full/path/to/google-search-console-mcp/` with your download path (Method B only)

**Important Notes:**
- For URL-prefix properties: Use `https://example.com/` format
- For domain properties: Use `sc-domain:example.com` format
- Make sure the URL format exactly matches your Search Console property

---

## Usage

Once configured, ask your MCP client questions like:

### Search Performance Analysis
- What's my website's search performance for the past week?
- Show me clicks and impressions by country for last month
- Compare CTR between different date ranges

### Keyword Analysis
- What are my top-performing keywords by clicks?
- Show me average position by query and device
- Analyze search appearance by query type

### Page Performance
- What are my top pages by impressions?
- Show me CTR by page and device type
- Analyze search performance by content type

### Multi-Dimensional Analysis
- Show me clicks and impressions by country and device
- Analyze search performance by query and page
- Compare performance across different search appearances

---

## Quick Start Examples

Try these example queries to see the MCP's analytical capabilities:

### 1. Geographic Distribution
```
Show me a map of search impressions by country for the last 30 days, with a breakdown of clicks vs impressions
```
This demonstrates:
- Geographic analysis
- Performance metrics
- Time-based filtering
- Data visualization

### 2. Keyword Performance
```
Compare average position and CTR by query and device type over the last 90 days
```
This demonstrates:
- Multi-dimensional analysis
- Time series comparison
- Search metrics
- Device segmentation

### 3. Page Performance
```
Show me clicks and impressions by page, comparing last 30 days vs previous 30 days
```
This demonstrates:
- Content analysis
- Period-over-period comparison
- Performance tracking
- Page attribution

### 4. Search Appearance
```
What are my top 10 search appearances by CTR, and how has their performance changed over the last 3 months?
```
This demonstrates:
- Feature analysis
- Trend analysis
- Performance metrics
- Ranking and sorting

---

## Available Tools

The server provides 7 main tools:

1. **`list_gsc_sites`** - List all verified sites in your Search Console
2. **`list_available_dimensions`** - Show all available GSC dimensions
3. **`list_available_metrics`** - Show all available GSC metrics
4. **`get_search_analytics`** - Retrieve search performance data with custom filters
5. **`get_sitemaps`** - List all submitted sitemaps for your site
6. **`submit_sitemap`** - Submit a new sitemap to Search Console
7. **`delete_sitemap`** - Remove a sitemap from Search Console

---

## Dimensions & Metrics

Access to all GSC dimensions and metrics:

### Available Dimensions
- **country**: Three-letter ISO 3166-1 alpha-3 country code
- **device**: DESKTOP, MOBILE, or TABLET
- **page**: Canonical URL of the page
- **query**: Search query string
- **searchAppearance**: Type like AMP_BLUE_LINK, RICHCARD, FEATURED_SNIPPET
- **date**: Date in YYYY-MM-DD format

### Available Metrics (Always Returned)
- **clicks**: Total number of clicks
- **impressions**: Total number of impressions
- **ctr**: Click-through rate as percentage
- **position**: Average search position

---

## Troubleshooting

**If you get "No module named gsc_mcp_server" (Method A):**
```bash
pip3 install --user google-search-console-mcp
```

**If you get "executable file not found":**
- Try the other Python command (`python` vs `python3`)
- Use `pip3` instead of `pip` if needed

**Permission errors:**
```bash
# Try user install instead of system-wide
pip install --user google-search-console-mcp
```

**Credentials not working:**
1. **Verify the JSON file path** is correct and accessible
2. **Check service account permissions**:
   - Go to Google Cloud Console → IAM & Admin → IAM
   - Find your service account → Check permissions
3. **Verify Search Console access**:
   - Search Console → Settings → Users and permissions
   - Check for your service account email
4. **Verify property format**:
   - Domain property: `sc-domain:example.com` ✅
   - URL-prefix property: `https://example.com/` ✅

**API quota/rate limit errors:**
- Search Console has daily quotas and rate limits
- Try reducing the date range in your queries
- Wait a few minutes between large requests

---

## Project Structure

```
google-search-console-mcp/
├── gsc_mcp_server.py       # Main MCP server
├── gsc_dimensions.json     # GSC dimensions configuration
├── gsc_metrics.json        # GSC metrics configuration
├── gsc_filters.json        # GSC filters configuration
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Package configuration
├── README.md              # Documentation
├── claude-config-template.json  # MCP configuration template
└── logo.svg               # Project logo
```

---

## License

MIT License