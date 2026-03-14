# Firewall Management Replication Script

Automates the replication of Firewall Management configurations (Policies, Rule Groups, Rules, and Network Locations) from a Parent CID to Child CIDs in a CrowdStrike Flight Control environment.

## 🎯 Purpose

In Flight Control environments, Firewall Management configurations must be manually replicated across Child CIDs. This script automates that process while preserving all relationships between:
- **Policy Containers** (Firewall Policies)
- **Rule Groups** (collections of rules)
- **Rules** (individual firewall rules)
- **Network Locations** (contexts where rules apply)

## ✨ Features

- 🔍 **Interactive Selection** - Choose which policies to replicate
- 🔗 **Dependency Management** - Automatically includes all related elements
- ⚠️ **Conflict Detection** - Identifies existing configurations in target CIDs
- 📊 **Progress Tracking** - Visual feedback during replication
- 🎨 **Color-Coded Output** - Easy-to-read terminal output
- 🔒 **Safe Operation** - Prompts for confirmation on conflicts

## 📋 Prerequisites

- Python 3.9 or higher
- FalconPy SDK 1.6.0 or higher
- colorama 0.4.6 or higher
- CrowdStrike Falcon API credentials with the following scopes:
  - **Firewall Management: Read** (query configurations)
  - **Firewall Management: Write** (create/update configurations)
  - **Flight Control: Read** (query Child CIDs)

Install dependencies:
```bash
pip install -r ../../requirements.txt
```

## 🚀 Usage

### Interactive Mode (Recommended)

Select specific policies and target Child CIDs:

```bash
python replicate_firewall.py --config ../../config/credentials.json
```

**Interactive Selection Process:**
1. Script retrieves all Firewall Policies from Parent CID
2. You select which policies to replicate (e.g., `1,3,5` or `all`)
3. You select target Child CIDs (e.g., `1,2` or `all`)
4. Script automatically includes all dependencies (Rule Groups, Rules, Contexts)
5. Confirmation prompts for any conflicts

### Non-Interactive Mode

Replicate ALL policies to ALL Child CIDs without prompts:

```bash
python replicate_firewall.py --config ../../config/credentials.json --non-interactive
```

⚠️ **Warning:** This mode replicates everything. Use with caution.

### Credential Methods

**Method 1: Config File (Recommended for testing)**
```bash
python replicate_firewall.py --config ../../config/credentials.json
```

**Method 2: Environment Variables (Recommended for production)**
```powershell
# PowerShell
$env:FALCON_CLIENT_ID = "your_client_id"
$env:FALCON_CLIENT_SECRET = "your_client_secret"
python replicate_firewall.py
```

**Method 3: CLI Arguments**
```bash
python replicate_firewall.py --client-id "YOUR_ID" --client-secret "YOUR_SECRET"
```

See [../../CREDENTIALS_GUIDE.md](../../CREDENTIALS_GUIDE.md) for detailed credential setup instructions.

## 📊 How It Works

### Replication Flow

```
1. EXTRACTION (from Parent CID)
   ├─ Network Locations (Contexts)
   ├─ Rules (firewall rules)
   ├─ Rule Groups (rule collections)
   └─ Policy Containers (policies)

2. SELECTION (interactive or all)
   ├─ Choose Firewall Policies
   └─ Choose Target Child CIDs

3. REPLICATION (to each Child CID)
   ├─ Create Network Locations
   ├─ Create Rules (with context references)
   ├─ Create Rule Groups (with rule references)
   └─ Create/Update Policy Containers
```

### Dependency Handling

The script automatically resolves dependencies in the correct order:

```
Network Locations  →  Rules  →  Rule Groups  →  Policy Containers
  (no dependencies)    (use contexts)  (use rules)  (use rule groups)
```

**Example:**
- You select: "Production Firewall Policy"
- Script automatically includes:
  - All Rule Groups assigned to that policy
  - All Rules contained in those Rule Groups
  - All Network Locations (contexts) used by those Rules

This ensures nothing is missing and all relationships are maintained.

## 📖 Visual Output Example

```
════════════════════════════════════════════════════════════════════════════════
              FIREWALL MANAGEMENT REPLICATION
════════════════════════════════════════════════════════════════════════════════

ℹ Authenticating to Falcon API...
✓ Authentication successful!

ℹ Retrieving CIDs from Flight Control...
✓ Found 1 Parent CID and 4 Child CID(s)

────────────────────────────────────────────────────────────────────────────────
Extracting Firewall Configurations from Parent CID
────────────────────────────────────────────────────────────────────────────────
ℹ Parent CID: a1b2c3d4e5f6...

ℹ   Extracting Network Locations (Contexts)...
✓   Found 5 Network Location(s)

ℹ   Extracting Firewall Rules...
✓   Found 23 Rule(s)

ℹ   Extracting Rule Groups...
✓   Found 3 Rule Group(s)

ℹ   Extracting Policy Containers (Firewall Policies)...
✓   Found 2 Policy Container(s)

✓ Extraction complete!
ℹ Summary:
  - Network Locations: 5
  - Rules: 23
  - Rule Groups: 3
  - Policy Containers: 2

────────────────────────────────────────────────────────────────────────────────
SELECT FIREWALL POLICIES TO REPLICATE
────────────────────────────────────────────────────────────────────────────────
ℹ Available Firewall Policies:

  [1] Production Firewall Policy
      Platform: Windows | ✓ Enabled
      ID: 71078f5c73a44ae09be31c9116c81c20

  [2] Development Firewall Policy
      Platform: Linux | ○ Disabled
      ID: 89cf004ef6f64a29956c0e64b11a1972

ℹ Enter your selection:
  - Policy numbers (comma-separated): 1,3,5
  - 'all' to select all policies
  - 'q' to quit

Select Policies: 1

✓ Selected 1 Policy/Policies:
ℹ   • Production Firewall Policy
```

## 🔧 Configuration Elements

### Policy Containers
Firewall policies that define overall firewall behavior. Each policy:
- Targets a specific platform (Windows, Linux, macOS)
- Contains Rule Groups
- Can be enabled/disabled
- Has priority settings

### Rule Groups
Collections of related firewall rules. Each rule group:
- Contains multiple Rules
- Has a name and description
- Is assigned to one or more Policies

### Rules
Individual firewall rules that define:
- Direction (inbound/outbound)
- Protocol (TCP, UDP, ICMP, etc.)
- Ports and IP ranges
- Action (allow/block)
- Network Locations (contexts) where they apply

### Network Locations
Contexts that define WHERE rules apply:
- Default (all locations)
- Specific networks (IP ranges, subnets)
- Named locations (Office, VPN, etc.)

## ⚠️ Conflict Handling

When the script detects existing configurations in target Child CIDs, it will prompt:

```
⚠ Rule Group "Corporate Rules" already exists in Development Workstations A

Options:
  [1] Skip (leave existing)
  [2] Update (overwrite with Parent version)
  [3] Skip All (for this Child CID)
  [4] Update All (for this Child CID)

Your choice:
```

This ensures you have full control over how conflicts are resolved.

## 🎯 Use Cases

### 1. Initial Deployment
Deploy Firewall Management to new Child CIDs:
```bash
python replicate_firewall.py --config ../../config/credentials.json
# Select: all policies
# Select: new Child CIDs only
```

### 2. Policy Updates
Propagate policy changes from Parent to Children:
```bash
python replicate_firewall.py --config ../../config/credentials.json
# Select: updated policies only
# Select: all Child CIDs
# Choose: Update on conflicts
```

### 3. Selective Rollout
Deploy specific policies to specific CIDs:
```bash
python replicate_firewall.py --config ../../config/credentials.json
# Select: Production Firewall Policy
# Select: Production Child CIDs only
```

## 🔍 Troubleshooting

### Authentication Errors

**Error:** `Authentication failed`
- Verify Client ID and Client Secret are correct
- Check that credentials have both **Read** and **Write** scopes for Firewall Management
- Ensure base URL matches your Falcon cloud

### No Policies Found

**Message:** `No Firewall Policies found in Parent CID`
- Verify Firewall Management is configured in Parent CID
- Check API credentials have Firewall Management: Read scope
- Confirm you're authenticated to the correct Parent CID

### Replication Failures

**Error:** `Failed to create rule group`
- Check that all dependencies (Rules, Network Locations) were created first
- Verify API credentials have Firewall Management: Write scope
- Review error messages for specific API errors (rate limits, validation errors)

### Permission Errors

**Error:** `403 Forbidden`
- Your API credentials lack required scopes
- Request updated credentials with:
  - Firewall Management: Read
  - Firewall Management: Write
  - Flight Control: Read

## 📚 API Scopes Required

| Scope | Permission | Required For |
|-------|------------|--------------|
| Firewall Management | Read | Querying policies, rule groups, rules, network locations |
| Firewall Management | Write | Creating/updating configurations in Child CIDs |
| Flight Control | Read | Retrieving Parent and Child CID information |

To create API credentials with proper scopes:
1. Go to Falcon Console → Support → API Clients and Keys
2. Click "Add new API client"
3. Enable the 3 required scopes above
4. Save Client ID and Secret

## 🔗 Related Documentation

- [../../CREDENTIALS_GUIDE.md](../../CREDENTIALS_GUIDE.md) - Credential configuration
- [../../INSTALLATION.md](../../INSTALLATION.md) - Installation instructions
- [../../README.md](../../README.md) - Main project documentation
- [CrowdStrike Firewall Management API Docs](https://falcon.crowdstrike.com/documentation)

## 🚧 Current Status

**Version:** 1.0.0 (Initial Development)

**Implemented:**
- ✅ Authentication and CID retrieval
- ✅ Extraction of all Firewall configurations from Parent
- ✅ Interactive policy and Child CID selection
- ✅ Non-interactive mode
- ✅ Structured framework for replication logic

**In Progress:**
- 🚧 Actual replication implementation (Network Locations, Rules, Rule Groups, Policies)
- 🚧 Conflict detection and resolution
- 🚧 Validation and error handling

**Planned:**
- 📋 Dry-run mode (preview without making changes)
- 📋 Rollback capability
- 📋 Export/import of configurations (JSON backup)
- 📋 Detailed logging and audit trail

## 💡 Tips

1. **Start Small:** Test with one policy and one Child CID first
2. **Use Dry-Run:** (When implemented) Preview changes before applying
3. **Backup First:** Export Parent CID configurations before replicating
4. **Test in Dev:** Test replication in development environment first
5. **Monitor Logs:** Check for warnings or errors during replication

## 🤝 Support

For issues or questions:
- FalconPy SDK: https://github.com/CrowdStrike/falconpy
- CrowdStrike API Docs: https://falcon.crowdstrike.com/documentation
- Firewall Management API: https://falcon.crowdstrike.com/documentation/firewall-management

---

**Author:** Claude Opus 4.6
**Date:** 2026-03-14
**Status:** Active Development
