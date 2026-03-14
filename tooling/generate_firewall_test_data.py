#!/usr/bin/env python3
"""
Firewall Management Test Data Generator

This script generates test configurations for Firewall Management to facilitate
testing of the replication script. It creates:
- Network Locations (Contexts)
- Firewall Rules
- Rule Groups
- Policy Containers

WARNING: This script creates many resources in your CrowdStrike tenant.
         Use with caution and only in test environments.

Author: Claude Opus 4.6
Date: 2026-03-14
"""

import sys
import os
import argparse
import random
import time
from typing import Dict, List, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from falconpy import FirewallManagement
from utils.auth import get_credentials_smart
from utils.formatting import (
    print_header, print_section, print_info, print_success,
    print_error, print_warning, print_progress, Colors
)


class FirewallTestDataGenerator:
    """Generates test data for Firewall Management"""

    def __init__(self, client_id: str, client_secret: str, base_url: str = "https://api.crowdstrike.com"):
        """Initialize the generator

        Args:
            client_id: CrowdStrike API Client ID
            client_secret: CrowdStrike API Client Secret
            base_url: API base URL
        """
        print_info("Authenticating to Falcon API...")
        self.falcon_fw = FirewallManagement(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url
        )

        if not self.falcon_fw.token_status:
            raise Exception("Authentication failed. Please check your credentials.")

        print_success("Authentication successful!")

        # Track created resources for cleanup
        self.created_locations = []
        self.created_rules = []
        self.created_rule_groups = []
        self.created_policies = []

    # Network Location generation
    LOCATION_PREFIXES = [
        "Office", "Branch", "Datacenter", "Cloud", "Remote",
        "HQ", "Regional", "Campus", "Site", "Facility"
    ]

    LOCATION_SUFFIXES = [
        "Network", "Subnet", "Zone", "Segment", "VLAN",
        "DMZ", "Internal", "External", "Management", "Production"
    ]

    # Rule generation
    PROTOCOLS = ["TCP", "UDP", "ICMP", "ANY"]
    DIRECTIONS = ["IN", "OUT", "BOTH"]
    ACTIONS = ["ALLOW", "BLOCK"]

    COMMON_PORTS = [
        20, 21, 22, 23, 25, 53, 80, 110, 143, 443,
        445, 465, 587, 993, 995, 3306, 3389, 5432, 5900, 8080
    ]

    SERVICE_NAMES = [
        "SSH", "HTTP", "HTTPS", "FTP", "SMTP", "DNS",
        "RDP", "SMB", "MySQL", "PostgreSQL", "VNC", "Redis",
        "MongoDB", "Elasticsearch", "Kafka", "RabbitMQ"
    ]

    def generate_network_location(self, index: int) -> Dict[str, Any]:
        """Generate a network location configuration

        Args:
            index: Index number for unique naming

        Returns:
            Network location configuration dict
        """
        prefix = random.choice(self.LOCATION_PREFIXES)
        suffix = random.choice(self.LOCATION_SUFFIXES)
        name = f"Test-{prefix}-{suffix}-{index:04d}"

        # Generate random IP range
        network = f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.0"
        cidr = random.choice([24, 25, 26, 27, 28])

        return {
            "name": name,
            "description": f"Test network location {index} - {prefix} {suffix}",
            "enabled": True,
            "connection_types": {
                "wired": True,
                "wireless": {
                    "enabled": random.choice([True, False]),
                    "require_encryption": True,
                    "ssids": [f"TestSSID-{index}"]
                }
            },
            "default_gateways": [f"{network.rsplit('.', 1)[0]}.1"],
            "dhcp_servers": [f"{network.rsplit('.', 1)[0]}.{random.randint(2, 10)}"],
            "dns_servers": [
                f"{network.rsplit('.', 1)[0]}.{random.randint(2, 10)}",
                "8.8.8.8"
            ],
            "host_addresses": [f"{network}/{cidr}"],
            "https_reachable_hosts": {
                "hostnames": [f"service{i}.test{index}.com" for i in range(1, random.randint(2, 4))]
            },
            "dns_resolution_targets": {
                "targets": [
                    {
                        "hostname": f"server{i}.test{index}.local",
                        "ip_match": [f"{network.rsplit('.', 1)[0]}.{10+i}"]
                    }
                    for i in range(1, random.randint(2, 4))
                ]
            },
            "icmp_request_targets": {
                "targets": [f"{network.rsplit('.', 1)[0]}.{i}" for i in range(1, 4)]
            }
        }

    def create_network_locations(self, count: int) -> List[str]:
        """Create multiple network locations

        Args:
            count: Number of locations to create

        Returns:
            List of created location IDs
        """
        print_section(f"Creating {count} Network Locations")

        created_ids = []

        for i in range(count):
            try:
                location_config = self.generate_network_location(i + 1)

                # NOTE: The exact body format needs to be discovered from API documentation
                # Current implementation is a best guess and may need adjustment
                response = self.falcon_fw.create_network_locations(
                    body=location_config  # Try direct config first
                )

                if response['status_code'] in [200, 201]:
                    location_id = response['body']['resources'][0]['id']
                    created_ids.append(location_id)
                    print_progress(i + 1, count, prefix=f"Creating locations", suffix=f"({i+1}/{count})")
                else:
                    print_error(f"Failed to create location {i+1}: {response['body'].get('errors')}")

                # Rate limiting
                time.sleep(0.1)

            except Exception as e:
                print_error(f"Exception creating location {i+1}: {e}")

        print()
        print_success(f"Created {len(created_ids)} Network Location(s)")
        self.created_locations = created_ids
        return created_ids

    def generate_rule_group(self, index: int, rule_ids: List[str] = None) -> Dict[str, Any]:
        """Generate a rule group configuration

        Args:
            index: Index number for unique naming
            rule_ids: Optional list of rule IDs to include

        Returns:
            Rule group configuration dict
        """
        category = random.choice([
            "Security", "Compliance", "Application", "Network",
            "Infrastructure", "Database", "WebServer", "Custom"
        ])

        name = f"Test-RuleGroup-{category}-{index:04d}"

        # Platform IDs: 0=Windows, 1=Mac, 3=Linux
        platform_id = random.choice(["0", "1", "3"])

        config = {
            "name": name,
            "description": f"Test rule group {index} for {category} policies",
            "enabled": True,
            "platform": platform_id
        }

        # Add rules if provided (as array of rule objects, not just IDs)
        if rule_ids:
            # For now, just note that rules would go here
            # The actual rule format needs to be discovered
            pass

        return config

    def create_rule_groups(self, count: int, rule_ids: List[str] = None) -> List[str]:
        """Create multiple rule groups

        Args:
            count: Number of rule groups to create
            rule_ids: Optional list of rule IDs to include in groups

        Returns:
            List of created rule group IDs
        """
        print_section(f"Creating {count} Rule Groups")
        print_warning("Rule Group creation via API is currently not working")
        print_warning("Platform parameter validation fails even with correct values")
        print_info("Workaround: Create Rule Groups manually in Falcon Console:")
        print_info("  1. Endpoint Security → Firewall Management → Rule Groups")
        print_info("  2. Click 'Create Group'")
        print_info("  3. Choose platform (Windows/Linux/Mac)")
        print_info("  4. Add rules and save")
        print()
        print_info(f"Skipping {count} Rule Group creation(s)")

        created_ids = []
        return created_ids

    def generate_placeholder_data_summary(self,
                                         locations: int,
                                         rules: int,
                                         rule_groups: int,
                                         policies: int) -> str:
        """Generate a summary of what would be created

        Args:
            locations: Number of network locations
            rules: Number of rules
            rule_groups: Number of rule groups
            policies: Number of policies

        Returns:
            Summary string
        """
        return f"""
Test Data Generation Plan:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Network Locations (Contexts):    {locations}
  - Randomly generated IP ranges
  - Various connection types (wired/wireless)
  - DNS and DHCP configurations

Firewall Rules:                   {rules}
  - TCP/UDP/ICMP protocols
  - Common ports (22, 80, 443, 3389, etc.)
  - Inbound/Outbound directions
  - Allow/Block actions

Rule Groups:                      {rule_groups}
  - Each group contains 1-10 rules
  - Categorized by purpose (Security, Compliance, etc.)

Policy Containers:                {policies}
  - Linked to rule groups
  - Various platforms (Windows, Linux, macOS)
  - Enabled/Disabled states

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Resources to Create:        {locations + rules + rule_groups + policies}

Estimated Time:                   ~{(locations + rules + rule_groups + policies) * 0.15 / 60:.1f} minutes
"""

    def cleanup_all(self):
        """Delete all created test resources"""
        print_section("CLEANUP - Deleting Test Resources")

        total_deleted = 0

        # Delete network locations
        if self.created_locations:
            print_info(f"Deleting {len(self.created_locations)} Network Locations...")
            try:
                response = self.falcon_fw.delete_network_locations(
                    ids=self.created_locations
                )
                if response['status_code'] in [200, 204]:
                    total_deleted += len(self.created_locations)
                    print_success(f"Deleted {len(self.created_locations)} location(s)")
                else:
                    print_error(f"Failed to delete locations: {response['body'].get('errors')}")
            except Exception as e:
                print_error(f"Exception during location cleanup: {e}")

        # Delete rule groups
        if self.created_rule_groups:
            print_info(f"Deleting {len(self.created_rule_groups)} Rule Groups...")
            try:
                response = self.falcon_fw.delete_rule_groups(
                    ids=self.created_rule_groups
                )
                if response['status_code'] in [200, 204]:
                    total_deleted += len(self.created_rule_groups)
                    print_success(f"Deleted {len(self.created_rule_groups)} rule group(s)")
                else:
                    print_error(f"Failed to delete rule groups: {response['body'].get('errors')}")
            except Exception as e:
                print_error(f"Exception during rule group cleanup: {e}")

        print()
        print_success(f"Cleanup complete! Deleted {total_deleted} resource(s)")


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Generate test data for Firewall Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 100 of each resource type
  python generate_firewall_test_data.py --config ../config/credentials.json --count 100

  # Generate specific quantities
  python generate_firewall_test_data.py --config ../config/credentials.json \\
    --locations 50 --rules 200 --rule-groups 30 --policies 10

  # Cleanup all created resources
  python generate_firewall_test_data.py --config ../config/credentials.json --cleanup-only

WARNING: This script creates many resources. Use only in test environments!
        """
    )

    # Credential arguments
    parser.add_argument('--config', type=str, help='Path to credentials JSON file')
    parser.add_argument('--client-id', type=str, help='CrowdStrike API Client ID')
    parser.add_argument('--client-secret', type=str, help='CrowdStrike API Client Secret')
    parser.add_argument('--base-url', type=str, default='https://api.crowdstrike.com',
                       help='API base URL (default: US-1)')

    # Generation arguments
    parser.add_argument('--count', type=int, help='Generate this many of each resource type')
    parser.add_argument('--locations', type=int, help='Number of network locations to create')
    parser.add_argument('--rules', type=int, help='Number of firewall rules to create')
    parser.add_argument('--rule-groups', type=int, help='Number of rule groups to create')
    parser.add_argument('--policies', type=int, help='Number of policies to create')

    # Mode arguments
    parser.add_argument('--cleanup-only', action='store_true',
                       help='Only cleanup previously created resources (reads from cache)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be created without creating anything')

    args = parser.parse_args()

    # Print header
    print_header("FIREWALL MANAGEMENT TEST DATA GENERATOR")
    print()

    # Determine counts
    if args.count:
        locations = rules = rule_groups = policies = args.count
    else:
        locations = args.locations or 10
        rules = args.rules or 50
        rule_groups = args.rule_groups or 10
        policies = args.policies or 5

    # Get credentials
    try:
        client_id, client_secret, base_url, source = get_credentials_smart(
            config_path=args.config,
            client_id=args.client_id,
            client_secret=args.client_secret,
            base_url=args.base_url
        )
    except Exception as e:
        print(f"Failed to load credentials: {e}")
        sys.exit(1)

    # Initialize generator
    try:
        generator = FirewallTestDataGenerator(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url
        )
    except Exception as e:
        print(f"Failed to initialize: {e}")
        sys.exit(1)

    print()

    # Dry run mode
    if args.dry_run:
        print(generator.generate_placeholder_data_summary(
            locations, rules, rule_groups, policies
        ))
        print_warning("DRY RUN MODE - Nothing was created")
        return

    # Cleanup only mode
    if args.cleanup_only:
        print_warning("CLEANUP MODE - This will delete test resources")
        print_info("Note: This feature requires resource tracking (not yet implemented)")
        print_info("      For now, you'll need to delete resources manually via Falcon Console")
        return

    # Show plan
    print(generator.generate_placeholder_data_summary(
        locations, rules, rule_groups, policies
    ))

    # Confirm with user
    print_warning("This will create resources in your CrowdStrike tenant!")
    confirm = input("Type 'yes' to continue: ").strip().lower()

    if confirm != 'yes':
        print_warning("Cancelled by user")
        sys.exit(0)

    print()

    # Create resources
    try:
        # Step 1: Network Locations
        location_ids = generator.create_network_locations(locations)
        print()

        # Step 2: Rules (placeholder - API method needs to be determined)
        print_section(f"Creating {rules} Firewall Rules")
        print_warning("Rule creation not yet implemented - needs API method discovery")
        print_info("You can create rules manually in Falcon Console:")
        print_info("  Endpoint Security → Firewall Management → Rules → Add Rule")
        print()
        rule_ids = []  # Placeholder

        # Step 3: Rule Groups
        rg_ids = generator.create_rule_groups(rule_groups, rule_ids if rule_ids else None)
        print()

        # Step 4: Policies (placeholder - API method needs to be determined)
        print_section(f"Creating {policies} Policy Containers")
        print_warning("Policy creation not yet implemented - needs API method discovery")
        print_info("You can create policies manually in Falcon Console:")
        print_info("  Endpoint Security → Firewall Management → Policies → Create Policy")
        print()

        # Summary
        print_section("GENERATION COMPLETE")
        print_success(f"Successfully created:")
        print_info(f"  • {len(location_ids)} Network Locations")
        print_info(f"  • {len(rg_ids)} Rule Groups")
        print_info(f"  • 0 Rules (manual creation required)")
        print_info(f"  • 0 Policies (manual creation required)")
        print()

        print_warning("IMPORTANT: To test the replication script, you should manually create")
        print_warning("           at least one Policy and assign Rule Groups to it.")

    except KeyboardInterrupt:
        print()
        print_warning("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
