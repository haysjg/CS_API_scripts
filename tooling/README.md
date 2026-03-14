# Tooling Scripts

This directory contains utility scripts for development, testing, and maintenance of the CrowdStrike API automation scripts.

## 🛠️ Available Tools

### generate_firewall_test_data.py

**Purpose:** Generate test configurations for Firewall Management to facilitate testing of the replication script.

**Creates:**
- Network Locations (Contexts) - IP ranges, DNS, DHCP configs ✅
- Firewall Rules - Individual firewall rules (TCP/UDP/ICMP with ports) ✅
- Rule Groups - Collections of firewall rules (3 rules per group by default) ✅
- Firewall Policies - Policy containers with assigned rule groups ✅

**Usage:**

```bash
# Generate 100 of each resource type
python generate_firewall_test_data.py --config ../config/credentials.json --count 100

# Generate specific quantities
python generate_firewall_test_data.py --config ../config/credentials.json \
  --locations 50 --rule-groups 30

# Dry run (preview without creating)
python generate_firewall_test_data.py --config ../config/credentials.json --count 50 --dry-run

# Auto-confirm (skip confirmation prompt)
python generate_firewall_test_data.py --config ../config/credentials.json --count 10 --yes
```

**Example Output:**

```
Test Data Generation Plan:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Network Locations (Contexts):    100
  - Randomly generated IP ranges
  - Various connection types (wired/wireless)
  - DNS and DHCP configurations

Rule Groups:                      100
  - Each group contains 1-10 rules
  - Categorized by purpose (Security, Compliance, etc.)

Policy Containers:                100
  - Linked to rule groups
  - Various platforms (Windows, Linux, macOS)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Resources to Create:        300
Estimated Time:                   ~0.8 minutes
```

**✅ Current Status:**
- Network Location creation: **Fully functional**
- Rule creation: **Fully functional** (embedded in rule groups)
- Rule Group creation: **Fully functional** (creates 3 rules per group by default)
- Policy creation: **Fully functional** (automatically assigns rule groups)

**⚠️ NOTES:**
- Each rule group contains 3 firewall rules by default
- Rules include random TCP/UDP ports, directions (IN/OUT/BOTH), and actions (ALLOW/DENY)
- Policies are automatically created with assigned rule groups
- Requires API credentials with Firewall Management: Write scope

## 📋 API Scopes Required

### generate_firewall_test_data.py
- **Firewall Management: Read**
- **Firewall Management: Write**

## 🚀 Adding New Tools

When adding new utility scripts to this directory:

1. **Follow naming convention:** `action_resource.py` (e.g., `cleanup_test_ioas.py`)
2. **Include docstring** at the top explaining purpose
3. **Add help text** with examples via argparse
4. **Update this README** with usage instructions
5. **Use existing utilities** from `utils/` directory

**Template:**

```python
#!/usr/bin/env python3
"""
Brief description of what this tool does.

Author: Your Name
Date: YYYY-MM-DD
"""

import sys
import os
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from falconpy import SomeAPI
from utils.auth import get_credentials_smart
from utils.formatting import print_header, print_success, print_error

def main():
    parser = argparse.ArgumentParser(description="Tool description")
    # Add arguments
    args = parser.parse_args()

    # Your logic here

if __name__ == "__main__":
    main()
```

## 🔒 Security Notes

- Never commit credentials or sensitive data in tooling scripts
- Use `get_credentials_smart()` for credential management
- Add confirmation prompts for destructive operations
- Test in isolated environments first

## 📚 Related Documentation

- [../README.md](../README.md) - Main project documentation
- [../CREDENTIALS_GUIDE.md](../CREDENTIALS_GUIDE.md) - Credential setup
- [../script_replicate_firewall/README.md](../script_replicate_firewall/README.md) - Firewall replication script

---

**Note:** Tools in this directory are for development and testing purposes.
They should not be used in production environments without careful review.
