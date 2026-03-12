# Custom Roles Analyzer

Analyzes custom roles in a CrowdStrike Falcon Flight Control environment and generates comprehensive reports.

## Overview

This script helps Flight Control administrators identify which custom roles exist in the Parent CID and checks their presence across all Child CIDs. It generates detailed reports to help replicate roles manually where needed.

## Features

- ✨ **Colored output** - Easy-to-read terminal output with colors and formatting
- ✨ **Interactive mode** - Select specific roles and children to analyze
- ✨ **Progress bars** - Visual feedback during analysis
- ✨ **Summary tables** - Clear coverage matrix view
- ✨ **Multiple credential methods** - Config file, CLI args, or environment variables
- Lists all custom roles in Parent CID
- Checks which Child CIDs already have these roles
- Generates detailed JSON, text, and markdown reports
- Creates a step-by-step manual replication guide

## Prerequisites

- Python 3.9 or higher
- FalconPy SDK 1.6.0 or higher
- CrowdStrike Falcon API credentials with **User Management Read** scope
- Flight Control environment (Parent CID with Child CIDs)

## Usage

### Interactive Mode (Default)

You'll be prompted to select which roles and child CIDs to analyze:

```bash
python analyze_roles.py --config ../config/credentials.json
```

**Selection Process:**
1. Script displays all custom roles found in Parent CID
2. Select roles by numbers (e.g., `1,3,5`), `all`, or `q` to quit
3. Script displays all Child CIDs
4. Select children by numbers, `all`, `children`, or `q` to quit
5. Analysis begins with visual progress indicators

### Non-Interactive Mode

Analyzes all roles across all children without prompting:

```bash
python analyze_roles.py --config ../config/credentials.json --non-interactive
```

### Credential Methods

**Method 1: Config File (Recommended for testing)**
```bash
python analyze_roles.py --config ../config/credentials.json
```

**Method 2: Environment Variables (Recommended for production)**
```powershell
# PowerShell
$env:FALCON_CLIENT_ID = "your_client_id"
$env:FALCON_CLIENT_SECRET = "your_client_secret"
python analyze_roles.py
```

**Method 3: CLI Arguments**
```bash
python analyze_roles.py --client-id "YOUR_ID" --client-secret "YOUR_SECRET"
```

See [../CREDENTIALS_GUIDE.md](../CREDENTIALS_GUIDE.md) for detailed credential setup instructions.

## Visual Output

The script uses color-coded output for easy reading:

- ✅ **Green** - Success messages, roles that exist
- ❌ **Red** - Errors, missing roles
- ⚠️ **Yellow** - Warnings
- ℹ️ **Cyan** - Information
- 🔷 **Magenta** - Highlights and selections

### Example Output

```
════════════════════════════════════════════════════════════════════════════════
               FLIGHT CONTROL - CUSTOM ROLES ANALYZER
════════════════════════════════════════════════════════════════════════════════

ℹ️ Authenticating to Falcon API...
✓ Authentication successful!

▶ mytest1
  Coverage [██████████░░░░░░░░░░░░░░░░░░░░] 25%

    SE FR FCTL - Servers              [✗ MISSING]
    SE FR FCTL - Workstations A       [✓ EXISTS]
    SE FR FCTL - Workstations B       [✗ MISSING]
```

See [VISUAL_OUTPUT_FEATURE.md](VISUAL_OUTPUT_FEATURE.md) for complete visual feature documentation.

## Output Files

The script generates three types of reports in the `../reports/` directory:

### 1. JSON Report
**Filename:** `role_analysis_TIMESTAMP.json`

Machine-readable format containing:
- Complete role definitions (permissions, descriptions)
- Child CID status for each role
- Timestamps and metadata

**Use case:** Automation, data processing, integration with other tools

### 2. Text Report
**Filename:** `role_analysis_TIMESTAMP.txt`

Human-readable summary with:
- List of all custom roles analyzed
- Coverage summary per role
- Missing roles by Child CID

**Use case:** Quick review, sharing with team

### 3. Manual Replication Guide
**Filename:** `manual_replication_guide_TIMESTAMP.md`

Step-by-step instructions for manually creating missing roles:
- Complete permission lists for each role
- Checkboxes to track progress
- Organized by Child CID
- Copy-paste ready role names and descriptions

**Use case:** Actual role replication work

## Understanding Custom Roles

### How the Script Identifies Custom Roles

The script distinguishes custom roles from built-in roles by examining the role ID format:

- **Custom roles:** ID is a 32-character hexadecimal UUID (e.g., `71078f5c73a44ae09be31c9116c81c20`)
- **Built-in roles:** ID is a text string (e.g., `falcon_administrator`, `sensor_manager`)

### Why Manual Replication?

CrowdStrike Falcon API does **not** support creating or modifying custom roles programmatically. Custom roles must be created through the Falcon web console. This script helps by:

1. Identifying which roles need to be replicated
2. Extracting complete role definitions
3. Generating step-by-step guides for manual creation

## Interactive Mode Guide

For detailed interactive mode usage, see [INTERACTIVE_GUIDE.md](INTERACTIVE_GUIDE.md).

**Quick Tips:**
- You can select multiple items with comma-separated numbers: `1,2,5,7`
- Use `all` to select everything
- Use `children` to select only child CIDs (exclude parent)
- Press `q` to quit at any selection prompt

## Troubleshooting

### Authentication Errors

**Error:** `Authentication failed: 401`
- Verify your Client ID and Client Secret are correct
- Check that credentials have **User Management Read** scope
- Ensure your base URL matches your Falcon cloud (US-1, US-2, EU-1, etc.)

### No Custom Roles Found

**Message:** `No custom roles found in Parent CID`
- This is normal if your Parent CID only uses built-in roles
- Custom roles must be created in the Falcon console first
- Verify you're authenticated to the correct Parent CID

### Unicode/Emoji Display Issues (Windows)

**Error:** `UnicodeEncodeError: 'charmap' codec can't encode character`
- The script automatically handles this
- If issues persist, use Windows Terminal or PowerShell 7+
- Set console to UTF-8: `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`

### Cannot Find Child CIDs

**Error:** `Failed to retrieve CID information`
- Verify your account has Flight Control enabled
- Check API credentials have proper permissions
- Ensure you're authenticating to the Parent CID

## API Scopes Required

| Scope | Permission | Required For |
|-------|------------|--------------|
| User Management | Read | Querying roles, retrieving role details |

To create API credentials with proper scopes:
1. Go to Falcon Console → Support → API Clients and Keys
2. Click "Add new API client"
3. Enable **User Management: Read**
4. Save Client ID and Secret

## Advanced Options

### Custom Base URL

For different Falcon clouds:

```bash
python analyze_roles.py \
  --config ../config/credentials.json \
  --base-url "https://api.eu-1.crowdstrike.com"
```

**Common Base URLs:**
- US-1: `https://api.crowdstrike.com` (default)
- US-2: `https://api.us-2.crowdstrike.com`
- EU-1: `https://api.eu-1.crowdstrike.com`
- US-GOV-1: `https://api.laggar.gcw.crowdstrike.com`

## Performance Considerations

- **Large environments:** Analysis time increases with number of roles and children
- **API rate limits:** The script handles pagination automatically
- **Network latency:** Flight Control API calls may take longer for distant clouds

## Related Documentation

- [INTERACTIVE_GUIDE.md](INTERACTIVE_GUIDE.md) - Detailed interactive mode guide
- [VISUAL_OUTPUT_FEATURE.md](VISUAL_OUTPUT_FEATURE.md) - Visual features documentation
- [../CREDENTIALS_GUIDE.md](../CREDENTIALS_GUIDE.md) - Credential configuration guide
- [../INSTALLATION.md](../INSTALLATION.md) - Installation instructions

## Example Workflow

1. **Run Analysis:**
   ```bash
   python analyze_roles.py --config ../config/credentials.json
   ```

2. **Select Roles:** Choose roles you want to check (e.g., `1,3,5`)

3. **Select Children:** Choose target Child CIDs (e.g., `all`)

4. **Review Results:** Check the coverage summary table

5. **Use Replication Guide:** Open `manual_replication_guide_TIMESTAMP.md`

6. **Create Roles:** Follow the step-by-step guide in Falcon console

7. **Re-run Analysis:** Verify roles are now present

## Support

For issues or questions:
- FalconPy SDK: https://github.com/CrowdStrike/falconpy
- CrowdStrike API Docs: https://falcon.crowdstrike.com/documentation
- Flight Control Docs: Check your Falcon console documentation
