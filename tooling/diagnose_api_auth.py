#!/usr/bin/env python3
"""
Diagnostic script to test API authentication and permissions
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from falconpy import OAuth2, FirewallManagement, FirewallPolicies
from utils.auth import get_credentials_smart
from utils.formatting import print_info, print_success, print_error, print_section, print_warning

print_section("API AUTHENTICATION & PERMISSIONS DIAGNOSTIC")
print()

# Get credentials
try:
    client_id, client_secret, base_url, source = get_credentials_smart(
        config_path='../../config/credentials.json'
    )
    print_success(f"✓ Credentials loaded from: {source}")
    print_info(f"  Base URL: {base_url}")
    print_info(f"  Client ID: {client_id[:20]}...")
    print()
except Exception as e:
    print_error(f"Failed to load credentials: {e}")
    sys.exit(1)

# Test OAuth2 authentication
print_info("Testing OAuth2 authentication...")
try:
    auth = OAuth2(client_id=client_id, client_secret=client_secret, base_url=base_url)

    # Force token generation
    token_result = auth.token()

    print_info(f"  Token request status: {token_result.get('status_code')}")

    if token_result.get('status_code') == 201:
        print_success("✓ OAuth2 token generated successfully")
        print_info(f"  Token valid: {auth.token_valid}")
        print_info(f"  Token status: {auth.token_status}")
    else:
        print_error(f"✗ Token generation failed")
        print_error(f"  Response: {token_result.get('body')}")
        sys.exit(1)
except Exception as e:
    print_error(f"✗ OAuth2 authentication failed: {e}")
    sys.exit(1)

print()

# Test FirewallManagement API - READ operations
print_section("Testing FirewallManagement API (READ operations)")
print()

falcon_fw = FirewallManagement(auth_object=auth)

# Test 1: Query Network Locations
print_info("1. Query Network Locations...")
response = falcon_fw.query_network_locations(limit=5)
print_info(f"   Status: {response['status_code']}")
if response['status_code'] == 200:
    print_success(f"   ✓ Found {len(response['body'].get('resources', []))} locations")
elif response['status_code'] == 403:
    print_error(f"   ✗ Forbidden - Missing 'Firewall Management: Read' scope")
elif response['status_code'] == 401:
    print_error(f"   ✗ Unauthorized - Check API credentials")
else:
    print_warning(f"   Response: {response['body'].get('errors')}")
print()

# Test 2: Query Rule Groups
print_info("2. Query Rule Groups...")
response = falcon_fw.query_rule_groups(limit=5)
print_info(f"   Status: {response['status_code']}")
if response['status_code'] == 200:
    print_success(f"   ✓ Found {len(response['body'].get('resources', []))} rule groups")
elif response['status_code'] == 403:
    print_error(f"   ✗ Forbidden - Missing 'Firewall Management: Read' scope")
elif response['status_code'] == 401:
    print_error(f"   ✗ Unauthorized - Check API credentials")
else:
    print_warning(f"   Response: {response['body'].get('errors')}")
print()

# Test 3: Query Rules
print_info("3. Query Rules...")
response = falcon_fw.query_rules(limit=5)
print_info(f"   Status: {response['status_code']}")
if response['status_code'] == 200:
    print_success(f"   ✓ Found {len(response['body'].get('resources', []))} rules")
elif response['status_code'] == 403:
    print_error(f"   ✗ Forbidden - Missing 'Firewall Management: Read' scope")
elif response['status_code'] == 401:
    print_error(f"   ✗ Unauthorized - Check API credentials")
else:
    print_warning(f"   Response: {response['body'].get('errors')}")
print()

# Test FirewallManagement API - WRITE operations
print_section("Testing FirewallManagement API (WRITE operations)")
print()

# Test 4: Try to create a test location
print_info("4. Create Network Location (test)...")
test_location = {
    "name": "DiagnosticTestLocation_DELETE_ME",
    "description": "Diagnostic test - can be deleted",
    "connection_types": {"wired": True},
    "enabled": False
}
response = falcon_fw.create_network_locations(body=test_location)
print_info(f"   Status: {response['status_code']}")
if response['status_code'] in [200, 201]:
    print_success(f"   ✓ Successfully created test location")
    created_id = response['body']['resources'][0]['id']
    print_info(f"   Location ID: {created_id}")

    # Clean up
    print_info("   Cleaning up test location...")
    delete_response = falcon_fw.delete_network_locations(ids=[created_id])
    if delete_response['status_code'] in [200, 204]:
        print_success(f"   ✓ Test location deleted")
    else:
        print_warning(f"   Could not delete test location: {delete_response['body'].get('errors')}")
elif response['status_code'] == 403:
    print_error(f"   ✗ Forbidden - Missing 'Firewall Management: Write' scope")
elif response['status_code'] == 401:
    print_error(f"   ✗ Unauthorized - Check API credentials or token expiration")
else:
    print_warning(f"   Response: {response['body'].get('errors')}")
print()

# Test FirewallPolicies API
print_section("Testing FirewallPolicies API")
print()

falcon_fp = FirewallPolicies(auth_object=auth)

# Test 5: Query Policies
print_info("5. Query Firewall Policies...")
response = falcon_fp.query_policies(limit=5)
print_info(f"   Status: {response['status_code']}")
if response['status_code'] == 200:
    print_success(f"   ✓ Found {len(response['body'].get('resources', []))} policies")
elif response['status_code'] == 403:
    print_error(f"   ✗ Forbidden - Missing 'Firewall Management: Read' scope")
elif response['status_code'] == 401:
    print_error(f"   ✗ Unauthorized - Check API credentials")
else:
    print_warning(f"   Response: {response['body'].get('errors')}")
print()

# Summary
print_section("DIAGNOSTIC SUMMARY")
print()
print_info("Required API Scopes for Firewall Management:")
print_info("  • Firewall Management: Read")
print_info("  • Firewall Management: Write")
print()
print_info("If you see 401 or 403 errors above:")
print_info("  1. Check that your API credentials have the required scopes")
print_info("  2. Regenerate your API keys if necessary")
print_info("  3. Verify the keys are not expired")
print_info("  4. Make sure you're using the correct base URL for your cloud region")
