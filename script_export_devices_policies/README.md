# Devices & Policies Exporter

Exports comprehensive device, host group, and policy information to CSV format for CrowdStrike Falcon Flight Control environments.

## Overview

This script retrieves all devices from selected CIDs (Parent and/or Children) and exports detailed information including host groups and policy assignments to a CSV file. It clearly differentiates between policies that are **applied** (active) versus merely **assigned** (pending).

## Features

- ✨ **CSV Export** - Clean, structured data export
- ✨ **Interactive CID selection** - Choose which CIDs to export
- ✨ **Policy differentiation** - Distinguishes Applied vs Assigned vs None
- ✨ **Flight Control support** - Handles parent and child CIDs
- ✨ **Comprehensive data** - Devices, groups, 3 types of policies
- ✨ **Colored output** - Visual feedback during export
- ✨ **Progress indicators** - Track export progress in real-time
- ✨ **Multiple credential methods** - Config file, CLI args, or environment variables

## Prerequisites

- Python 3.9 or higher
- FalconPy SDK 1.6.0 or higher
- CrowdStrike Falcon API credentials with the following scopes:
  - **Hosts: Read**
  - **Host Groups: Read**
  - **Prevention Policies: Read**
  - **Response Policies: Read**
  - **Sensor Update Policies: Read**
- Flight Control environment (optional - works with single CID too)

## Usage

### Interactive Mode (Default)

You'll be prompted to select which CIDs to export:

```bash
python export_devices_policies.py --config ../config/credentials.json
```

**Selection Options:**
- Enter CID numbers separated by commas: `1,3,4`
- Enter `all` to export all CIDs (Parent + Children)
- Enter `children` to export only Child CIDs
- Enter `q` to quit

### Non-Interactive Mode

Export all CIDs without prompting:

```bash
python export_devices_policies.py --config ../config/credentials.json --non-interactive
```

### Custom Output File

Specify a custom output filename:

```bash
python export_devices_policies.py --config ../config/credentials.json --output my_export.csv
```

Default filename: `devices_export_TIMESTAMP.csv`

### Credential Methods

**Method 1: Config File (Recommended for testing)**
```bash
python export_devices_policies.py --config ../config/credentials.json
```

**Method 2: Environment Variables (Recommended for production)**
```powershell
# PowerShell
$env:FALCON_CLIENT_ID = "your_client_id"
$env:FALCON_CLIENT_SECRET = "your_client_secret"
python export_devices_policies.py
```

**Method 3: CLI Arguments**
```bash
python export_devices_policies.py --client-id "YOUR_ID" --client-secret "YOUR_SECRET"
```

See [../CREDENTIALS_GUIDE.md](../CREDENTIALS_GUIDE.md) for detailed credential setup instructions.

## CSV Output Format

The exported CSV contains **19 columns** with comprehensive device and policy information:

### CID Information
| Column | Description |
|--------|-------------|
| `CID Name` | Friendly name of the CID |
| `CID` | Unique CID identifier |
| `CID Type` | PARENT or CHILD |

### Device Information
| Column | Description |
|--------|-------------|
| `Device ID` | Unique device identifier |
| `Hostname` | Device hostname |
| `OS Version` | Operating system version |
| `Platform` | Platform name (Windows, Linux, macOS) |
| `Last Seen` | Last check-in timestamp (ISO 8601) |
| `Status` | Device status (normal, offline, etc.) |
| `Agent Version` | Falcon sensor version |

### Host Groups
| Column | Description |
|--------|-------------|
| `Host Groups` | Comma-separated list of group names (or "None") |

### Prevention Policy
| Column | Description |
|--------|-------------|
| `Prevention Policy` | Policy name |
| `Prevention Status` | **Applied** / **Assigned** / **None** |

### Response Policy
| Column | Description |
|--------|-------------|
| `Response Policy` | Policy name |
| `Response Status` | **Applied** / **Assigned** / **None** |

### Sensor Update Policy
| Column | Description |
|--------|-------------|
| `Sensor Update Policy` | Policy name |
| `Sensor Update Status` | **Applied** / **Assigned** / **None** |

### Cloud Provider Information
| Column | Description |
|--------|-------------|
| `Service Provider` | Cloud provider (AWS_EC2_V2, AZURE_VM, GCP, etc.) |
| `Service Provider Account ID` | Cloud account ID |

## Understanding Policy Status

### Applied
✅ The policy is **actively applied** to the device. The device is using this policy's settings.

**Example:** A device shows `Prevention Policy: "Corporate Standard"` with `Prevention Status: "Applied"`
- The device is protected using the "Corporate Standard" prevention policy
- Settings are active and enforced

### Assigned
⚠️ The policy is **assigned but not yet applied**. The device will use this policy after next check-in or reboot.

**Example:** A device shows `Response Policy: "New RTR Policy"` with `Response Status: "Assigned"`
- The policy has been assigned to the device
- It will become active after the device checks in with the cloud
- Until then, the previous policy settings remain in effect

### None
❌ No policy is assigned to this device.

**Example:** A device shows `Sensor Update Policy: "None"` with `Sensor Update Status: "None"`
- No sensor update policy is assigned
- Device may be using default settings or awaiting policy assignment

## Example Output

### Sample CSV Row

```csv
CID Name,CID,CID Type,Device ID,Hostname,OS Version,Platform,Last Seen,Status,Host Groups,Prevention Policy,Prevention Status,Response Policy,Response Status,Sensor Update Policy,Sensor Update Status,Agent Version,Service Provider,Service Provider Account ID
SE FR FCTL - Servers,6946f672680e49448ef343eddf5dd9d7,CHILD,93cf90e6c30545ffbe3ebce3a7548e71,SE-VMA-W2019-DT,Windows Server 2019,Windows,2026-03-01T01:02:38Z,normal,Windows Servers,platform_default,Applied,platform_default,Applied,platform_default,Applied,7.33.20505.0,AWS_EC2_V2,517716713836
```

### Readable Format

```
CID Name                 : SE FR FCTL - Servers
CID                      : 6946f672680e49448ef343eddf5dd9d7
CID Type                 : CHILD
Device ID                : 93cf90e6c30545ffbe3ebce3a7548e71
Hostname                 : SE-VMA-W2019-DT
OS Version               : Windows Server 2019
Platform                 : Windows
Last Seen                : 2026-03-01T01:02:38Z
Status                   : normal
Host Groups              : Windows Servers
Prevention Policy        : platform_default
Prevention Status        : Applied ✅
Response Policy          : platform_default
Response Status          : Applied ✅
Sensor Update Policy     : platform_default
Sensor Update Status     : Applied ✅
Agent Version            : 7.33.20505.0
Service Provider         : AWS_EC2_V2
Service Provider Account ID: 517716713836
```

## Visual Output

The script provides real-time visual feedback:

```
════════════════════════════════════════════════════════════════════════════════
                  FLIGHT CONTROL - DEVICES & POLICIES EXPORT
════════════════════════════════════════════════════════════════════════════════

ℹ️ Authenticating to Falcon API...
✓ Authentication successful!

▶ Processing: SE FR FCTL - Servers (CHILD)
ℹ️   Querying devices...
✓   Found 147 device(s)
ℹ️   Retrieving device details...
✓   Retrieved details for 147 device(s)
ℹ️   Loading host groups...
✓   Loaded 12 host group(s)
ℹ️   Loading policies...
✓   Loaded 42 policie(s)
ℹ️   Converting to CSV format...
✓   Processed 147 device(s)

Overall progress [██████████████████████████████] 100% (SE FR FCTL - Servers)

╔══════════════════════════════════════════════════════════════════════════════╗
║                               EXPORT COMPLETE                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ CIDs processed:          3                                                   ║
║ Total devices exported:  412                                                 ║
║ Output file:             devices_export_20260312_143052.csv                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Use Cases

### 1. Inventory Management
Export all devices to create a complete inventory:
```bash
python export_devices_policies.py --config ../config/credentials.json --non-interactive
```

### 2. Policy Audit
Review which policies are applied vs assigned across your environment:
- Open CSV in Excel/Google Sheets
- Filter by `Prevention Status` = "Assigned" to find pending changes
- Sort by `CID Name` to analyze per-CID policy distribution

### 3. Compliance Reporting
Generate regular reports for compliance:
```bash
# Weekly export
python export_devices_policies.py --config ../config/credentials.json --non-interactive --output weekly_report_$(date +%Y%m%d).csv
```

### 4. Migration Planning
Before migrating devices between CIDs:
1. Export current CID devices
2. Review host groups and policies
3. Plan group/policy mapping for target CID

### 5. Troubleshooting
Identify devices with policy issues:
- Devices with no host groups
- Devices with unassigned policies
- Devices offline for extended periods

## API Scopes Required

| Scope | Permission | Required For |
|-------|------------|--------------|
| Hosts | Read | Querying and retrieving device information |
| Host Groups | Read | Retrieving host group memberships |
| Prevention Policies | Read | Retrieving prevention policy information |
| Response Policies | Read | Retrieving response policy information |
| Sensor Update Policies | Read | Retrieving sensor update policy information |

To create API credentials with proper scopes:
1. Go to Falcon Console → Support → API Clients and Keys
2. Click "Add new API client"
3. Enable all 5 required Read scopes
4. Save Client ID and Secret

## Performance Considerations

### Large Environments

For environments with thousands of devices:
- **Export time:** ~30-60 seconds per 1,000 devices
- **Memory usage:** Minimal (streaming processing)
- **Network:** Batched API calls (1,000 devices per batch)

### Optimization Tips

1. **Export specific CIDs** instead of all if you only need subset
2. **Use non-interactive mode** for scheduled/automated exports
3. **API rate limits:** Script handles automatically with pagination

## Troubleshooting

### Authentication Errors

**Error:** `Authentication failed: 401`
- Verify Client ID and Client Secret are correct
- Check that credentials have all 5 required Read scopes
- Ensure base URL matches your Falcon cloud

### No Devices Found

**Message:** `Found 0 device(s)`
- Normal if CID has no devices
- Verify you're authenticated to correct CID
- Check that API credentials have Hosts Read scope

### Policy Names Show as IDs

**Issue:** Policy column shows UUID instead of name
- This occurs if the policy was deleted
- Device is assigned to a non-existent policy
- The script will show the policy ID as fallback

### Unicode/Emoji Display Issues (Windows)

**Error:** `UnicodeEncodeError: 'charmap' codec can't encode character`
- The script automatically handles this
- If issues persist, use Windows Terminal or PowerShell 7+

### Large CSV Files

**Issue:** CSV file is very large (>50MB)
- This is normal for large environments (10,000+ devices)
- Consider exporting specific CIDs separately
- Use Excel Online or Google Sheets for viewing large files
- Use tools like `pandas` or `csvkit` for programmatic analysis

## Advanced Options

### Custom Base URL

For different Falcon clouds:

```bash
python export_devices_policies.py \
  --config ../config/credentials.json \
  --base-url "https://api.eu-1.crowdstrike.com"
```

**Common Base URLs:**
- US-1: `https://api.crowdstrike.com` (default)
- US-2: `https://api.us-2.crowdstrike.com`
- EU-1: `https://api.eu-1.crowdstrike.com`
- US-GOV-1: `https://api.laggar.gcw.crowdstrike.com`

## Analyzing the CSV

### Using Excel

1. Open CSV in Excel
2. Use "Format as Table" for easy filtering
3. Apply filters to find:
   - Devices with "Assigned" policies (pending changes)
   - Devices with no host groups
   - Offline devices (check Last Seen column)

### Using Python pandas

```python
import pandas as pd

# Load CSV
df = pd.read_csv('devices_export_20260312_143052.csv')

# Find devices with assigned but not applied policies
pending = df[
    (df['Prevention Status'] == 'Assigned') |
    (df['Response Status'] == 'Assigned') |
    (df['Sensor Update Status'] == 'Assigned')
]

# Group by CID
by_cid = df.groupby('CID Name').size()
print(f"Devices per CID:\n{by_cid}")
```

### Using csvkit

```bash
# View summary statistics
csvstat devices_export_20260312_143052.csv

# Filter specific CID
csvgrep -c "CID Name" -m "SE FR FCTL - Servers" devices_export_20260312_143052.csv

# Count by platform
csvcut -c Platform devices_export_20260312_143052.csv | tail -n +2 | sort | uniq -c
```

## Related Documentation

- [../CREDENTIALS_GUIDE.md](../CREDENTIALS_GUIDE.md) - Credential configuration guide
- [../INSTALLATION.md](../INSTALLATION.md) - Installation instructions
- [../README.md](../README.md) - Main project documentation

## Example Workflows

### Weekly Inventory Export

```bash
#!/bin/bash
# weekly_export.sh

TIMESTAMP=$(date +%Y%m%d)
OUTPUT="reports/inventory_${TIMESTAMP}.csv"

python export_devices_policies.py \
  --config ../config/credentials.json \
  --non-interactive \
  --output "$OUTPUT"

echo "Export complete: $OUTPUT"
```

### Policy Compliance Check

1. Export devices to CSV
2. Open in Excel
3. Create pivot table with:
   - Rows: CID Name
   - Columns: Prevention Status
   - Values: Count of Device ID
4. Identify CIDs with high "Assigned" counts (pending policy applications)

### Audit Trail

Keep historical exports for audit:
```bash
mkdir -p exports/$(date +%Y%m)
python export_devices_policies.py \
  --config ../config/credentials.json \
  --non-interactive \
  --output "exports/$(date +%Y%m)/export_$(date +%Y%m%d).csv"
```

## Support

For issues or questions:
- FalconPy SDK: https://github.com/CrowdStrike/falconpy
- CrowdStrike API Docs: https://falcon.crowdstrike.com/documentation
- Hosts API: https://falcon.crowdstrike.com/documentation/84/hosts-api
