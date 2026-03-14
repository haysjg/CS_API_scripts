# Test Data Generator - Quick Start Guide

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure dependencies are installed
pip install -r ../requirements.txt

# Ensure credentials are configured
# File: ../config/credentials.json
```

### Basic Usage

#### Generate 10 of Everything (Interactive)
```bash
python generate_firewall_test_data.py --config ../config/credentials.json --count 10
# Will prompt for confirmation
```

#### Generate 10 of Everything (Auto-confirm)
```bash
python generate_firewall_test_data.py --config ../config/credentials.json --count 10 --yes
```

#### Generate Custom Quantities
```bash
python generate_firewall_test_data.py --config ../config/credentials.json \
  --locations 50 \
  --rule-groups 30 \
  --policies 10 \
  --yes
```

#### Preview Without Creating (Dry Run)
```bash
python generate_firewall_test_data.py --config ../config/credentials.json --count 100 --dry-run
```

---

## 📊 What Gets Created

### Network Locations (Contexts)
- Random IP ranges (10.x.x.0/24-28)
- Wired and wireless connection types
- Random SSIDs for wireless
- Default gateways, DHCP servers, DNS servers
- HTTPS reachable hosts
- DNS resolution targets
- ICMP request targets

**Naming:** `Test-{Prefix}-{Suffix}-{Number}`
- Prefixes: Office, Branch, Datacenter, Cloud, Remote, HQ, etc.
- Suffixes: Network, Subnet, Zone, Segment, VLAN, DMZ, etc.

### Rule Groups
- Empty rule groups (rules can be added via console)
- Random platform assignment (windows/mac/linux)
- Categorized names (Security, Compliance, Application, etc.)

**Naming:** `Test-RuleGroup-{Category}-{Number}`

### Firewall Policies
- Automatically created with assigned rule groups
- Platform-specific (Windows, Mac, Linux)
- Each policy gets 1-3 random rule groups assigned

**Naming:** `Test-Policy-{Platform}-{Number}`

---

## 🎯 Common Scenarios

### Scenario 1: Initial Test Environment Setup
**Goal:** Create complete test environment from scratch

```bash
python generate_firewall_test_data.py \
  --config ../config/credentials.json \
  --count 20 \
  --yes
```

**Result:**
- 20 Network Locations
- 20 Rule Groups
- 20 Policies (with assigned rule groups)

---

### Scenario 2: Add More Policies Only
**Goal:** Add policies without creating more locations/groups

```bash
python generate_firewall_test_data.py \
  --config ../config/credentials.json \
  --locations 0 \
  --rule-groups 0 \
  --policies 10 \
  --yes
```

**Note:** This will create policies but won't have rule groups to assign (since none are being created and the script doesn't fetch existing ones).

**Better approach:**
1. Create rule groups first
2. Then create policies that can reference them

---

### Scenario 3: Large Scale Testing
**Goal:** Generate hundreds of configurations for scale testing

```bash
python generate_firewall_test_data.py \
  --config ../config/credentials.json \
  --locations 200 \
  --rule-groups 100 \
  --policies 50 \
  --yes
```

**Warning:** This creates 350 resources. Ensure:
- You're in a test environment
- You have API rate limits accounted for
- Cleanup plan is in place

---

### Scenario 4: Preview Before Creating
**Goal:** See what would be created without actually creating it

```bash
python generate_firewall_test_data.py \
  --config ../config/credentials.json \
  --count 50 \
  --dry-run
```

**Output:** Shows counts and estimated time, but creates nothing.

---

## ⚙️ Command-Line Options

### Credential Options
```bash
--config PATH              # Path to credentials.json file (recommended)
--client-id ID             # API Client ID (alternative)
--client-secret SECRET     # API Client Secret (alternative)
--base-url URL             # API base URL (default: https://api.crowdstrike.com)
```

### Generation Options
```bash
--count N                  # Generate N of each resource type
--locations N              # Generate N network locations
--rule-groups N            # Generate N rule groups
--policies N               # Generate N policies
```

### Mode Options
```bash
--dry-run                  # Preview without creating
--yes, -y                  # Skip confirmation prompt
--cleanup-only             # Cleanup mode (not yet implemented)
```

---

## 🔒 Required API Scopes

Your API credentials must have:
- **Firewall Management: Read** - Query existing resources
- **Firewall Management: Write** - Create resources

---

## 📋 Output Example

```
================================================================================
                    FIREWALL MANAGEMENT TEST DATA GENERATOR
================================================================================

ℹ Authenticating to Falcon API...
✓ Authentication successful!

Test Data Generation Plan:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Network Locations (Contexts):    10
  - Randomly generated IP ranges
  - Various connection types (wired/wireless)
  - DNS and DHCP configurations

Firewall Rules:                   50
  - TCP/UDP/ICMP protocols
  - Common ports (22, 80, 443, 3389, etc.)
  - Inbound/Outbound directions
  - Allow/Block actions

Rule Groups:                      10
  - Each group contains 1-10 rules
  - Categorized by purpose (Security, Compliance, etc.)

Policy Containers:                10
  - Linked to rule groups
  - Various platforms (Windows, Linux, macOS)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Resources to Create:        80
Estimated Time:                   ~0.2 minutes

⚠ This will create resources in your CrowdStrike tenant!

--------------------------------------------------------------------------------
Creating 10 Network Locations
--------------------------------------------------------------------------------
Creating locations: 100% |████████████████████| (10/10)

✓ Created 10 Network Location(s)

--------------------------------------------------------------------------------
Creating 10 Rule Groups (empty - rules TBD)
--------------------------------------------------------------------------------
ℹ Note: Creating empty rule groups. Rules can be added later via console.
Creating rule groups: 100% |████████████████████| (10/10)

✓ Created 10 Rule Group(s)

--------------------------------------------------------------------------------
Creating 10 Firewall Policies
--------------------------------------------------------------------------------
Creating policies: 100% |████████████████████| (10/10)

✓ Created 10 Policy Container(s)

--------------------------------------------------------------------------------
GENERATION COMPLETE
--------------------------------------------------------------------------------
✓ Successfully created:
ℹ   • 10 Network Locations
ℹ   • 10 Rule Groups (empty - ready for rules)
ℹ   • 10 Policies (with assigned rule groups)

⚠ NEXT STEPS:
ℹ   1. (Optional) Add rules to Rule Groups via Falcon Console
ℹ   2. Test replication script
ℹ   3. (Optional) Modify policy settings in Falcon Console
```

---

## 🧹 Cleanup

### Manual Cleanup (Current)
Delete resources via Falcon Console:
1. Navigate to Endpoint Security → Firewall Management
2. Delete Policies (delete or disable)
3. Delete Rule Groups
4. Delete Network Locations

### Automated Cleanup (Planned)
```bash
python generate_firewall_test_data.py --config ../config/credentials.json --cleanup-only
```

**Note:** Cleanup feature not yet implemented. Track created resource IDs if you need to delete programmatically.

---

## ⚠️ Important Notes

### Test Environment Only
This script creates many resources. **ONLY use in test/dev environments.**

### Rate Limiting
The script includes 0.1s delays between requests. For large batches (100+), expect:
- ~0.15 seconds per resource
- Example: 100 of each = 300 resources = ~45 seconds

### Rule Groups Are Empty
Rule groups are created without rules. You can:
1. Add rules manually via Falcon Console
2. Wait for future script enhancement to generate rules

### Credentials
If you see 401 Unauthorized errors:
1. Check credentials file exists: `../config/credentials.json`
2. Verify credentials have Firewall Management: Write scope
3. Check credentials haven't expired

---

## 📚 Related Documentation

- **Full README:** `README.md`
- **API Discoveries:** `TEST_DATA_STATUS.md`
- **Implementation Details:** `POLICY_IMPLEMENTATION.md`
- **Replication Script:** `../script_replicate_firewall/README.md`

---

## 🐛 Troubleshooting

### "Authentication failed"
- Verify `credentials.json` exists and is valid
- Check Client ID and Client Secret are correct
- Ensure base_url matches your Falcon cloud

### "401 Unauthorized"
- Credentials lack Firewall Management: Write scope
- Request new API credentials with proper scopes

### "Failed to create {resource}"
- Check error message for details
- Verify API is accessible
- Check for rate limiting (429 errors)

### Script hangs at "Type 'yes' to continue"
- Use `--yes` flag for non-interactive mode
- Or type `yes` and press Enter

---

**Last Updated:** 2026-03-14
**Version:** 1.0.0 - Complete implementation
