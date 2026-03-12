#!/usr/bin/env python3
"""
Export devices, groups, and policies to CSV for Flight Control CIDs.

This script exports detailed device information including:
- Device details (hostname, OS, etc.)
- Host groups
- Prevention policies (applied vs assigned)
- Response policies (applied vs assigned)
- Sensor update policies (applied vs assigned)

Supports interactive CID selection in Flight Control environments.
"""

import sys
import os
import csv
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from falconpy import Hosts, HostGroup, PreventionPolicy, ResponsePolicies, SensorUpdatePolicies, FlightControl
from utils.auth import get_credentials_smart
from utils.formatting import (
    print_header, print_success, print_error, print_info, print_warning,
    print_progress, print_summary_box, Colors, print_child_item
)

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def get_all_cids(flight_control: FlightControl) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Get parent CID and all child CIDs in Flight Control.

    Args:
        flight_control: FlightControl API instance

    Returns:
        Tuple of (parent_info, children_list)
    """
    print_info("Retrieving Flight Control CID information...")

    # Get parent CID info
    parent_response = flight_control.query_children()

    if parent_response['status_code'] != 200:
        print_error("Failed to retrieve parent CID information")
        return None, []

    # Get parent CID from a sensor update policy (reliable source)
    from falconpy import SensorUpdatePolicies
    sensor_policies = SensorUpdatePolicies(auth_object=flight_control.auth_object)
    policies_response = sensor_policies.queryCombinedSensorUpdatePoliciesV2(limit=1)

    if policies_response['status_code'] == 200 and policies_response['body'].get('resources'):
        parent_cid = policies_response['body']['resources'][0].get('cid', 'Unknown')
    else:
        parent_cid = 'Unknown'

    parent_name = "Parent CID"

    parent_info = {
        'cid': parent_cid,
        'name': parent_name,
        'type': 'parent'
    }

    # Get children
    child_cids = parent_response['body'].get('resources', [])

    if not child_cids:
        print_warning("No child CIDs found")
        return parent_info, []

    # Get details for each child
    children = []
    if child_cids:
        details_response = flight_control.get_children(ids=child_cids)

        if details_response['status_code'] == 200:
            for child in details_response['body'].get('resources', []):
                children.append({
                    'cid': child.get('child_cid', 'Unknown'),
                    'name': child.get('name', 'Unknown'),
                    'type': 'child'
                })
        else:
            # Fallback: use CIDs without names
            for cid in child_cids:
                children.append({
                    'cid': cid,
                    'name': cid,
                    'type': 'child'
                })

    print_success(f"Found parent CID and {len(children)} child CID(s)")
    return parent_info, children


def select_cids_to_export(parent: Dict[str, Any], children: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Interactive selection of CIDs to export.

    Args:
        parent: Parent CID info
        children: List of child CIDs

    Returns:
        List of selected CIDs
    """
    print_header("SELECT CIDs TO EXPORT", width=80)

    all_cids = [parent] + children

    print()
    print(f"{Colors.INFO}Available CIDs:{Colors.RESET}\n")

    for i, cid in enumerate(all_cids, 1):
        cid_type = "PARENT" if cid['type'] == 'parent' else "CHILD"
        print(f"  {Colors.HIGHLIGHT}[{i}]{Colors.RESET} {Colors.BRIGHT}{cid['name']}{Colors.RESET} ({cid_type})")
        print(f"      {Colors.DIM}CID: {cid['cid']}{Colors.RESET}")
        print()

    print(f"{Colors.INFO}Selection options:{Colors.RESET}")
    print("  • Enter CID numbers separated by commas (e.g., 1,3,4)")
    print("  • Enter 'all' to select all CIDs")
    print("  • Enter 'children' to select all children only")
    print("  • Enter 'q' to quit")
    print()

    while True:
        selection = input(f"{Colors.HIGHLIGHT}Select CIDs to export: {Colors.RESET}").strip().lower()

        if selection == 'q':
            print_warning("Export cancelled")
            sys.exit(0)

        if selection == 'all':
            print_success(f"Selected all {len(all_cids)} CID(s)")
            return all_cids

        if selection == 'children':
            if not children:
                print_error("No child CIDs available")
                continue
            print_success(f"Selected {len(children)} child CID(s)")
            return children

        # Parse comma-separated numbers
        try:
            numbers = [int(n.strip()) for n in selection.split(',')]
            if not all(1 <= n <= len(all_cids) for n in numbers):
                print_error(f"Invalid selection. Enter numbers between 1 and {len(all_cids)}")
                continue

            selected = [all_cids[n-1] for n in numbers]
            print_success(f"Selected {len(selected)} CID(s):")
            for cid in selected:
                print(f"  • {cid['name']}")
            print()
            return selected

        except (ValueError, IndexError):
            print_error("Invalid input. Please enter numbers separated by commas, 'all', 'children', or 'q'")


def get_devices_for_cid(hosts: Hosts, cid_info: Dict[str, Any]) -> List[str]:
    """
    Get all device IDs for a specific CID.

    Args:
        hosts: Hosts API instance
        cid_info: CID information dict

    Returns:
        List of device IDs
    """
    import time
    import threading

    device_ids = []
    offset = None
    limit = 5000

    # Spinner animation
    spinner_running = True
    spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    def spinner():
        idx = 0
        while spinner_running:
            sys.stdout.write(f'\r  {Colors.INFO}{spinner_chars[idx % len(spinner_chars)]}{Colors.RESET} Querying devices (this may take several minutes for large environments)...')
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)

    # Start spinner
    spinner_thread = threading.Thread(target=spinner, daemon=True)
    spinner_thread.start()

    try:
        while True:
            response = hosts.query_devices_by_filter(
                offset=offset,
                limit=limit
            )

            if response['status_code'] != 200:
                spinner_running = False
                time.sleep(0.2)  # Let spinner finish
                sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear line
                sys.stdout.flush()
                print_error(f"Failed to query devices for {cid_info['name']}")
                break

            batch_ids = response['body'].get('resources', [])

            # If no results in this batch, we're done
            if not batch_ids:
                break

            device_ids.extend(batch_ids)

            # Check pagination
            meta = response['body'].get('meta', {})
            pagination = meta.get('pagination', {})
            new_offset = pagination.get('offset')

            # If offset hasn't changed or is the same, we're done
            if not new_offset or new_offset == offset:
                break

            offset = new_offset
    finally:
        spinner_running = False
        time.sleep(0.2)  # Let spinner finish
        sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear line
        sys.stdout.flush()

    return device_ids


def get_device_details(hosts: Hosts, device_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Get detailed information for devices.

    Args:
        hosts: Hosts API instance
        device_ids: List of device IDs

    Returns:
        List of device details
    """
    if not device_ids:
        return []

    import time
    import threading

    devices = []
    batch_size = 1000
    total_batches = (len(device_ids) + batch_size - 1) // batch_size

    # Progress indicator
    progress_running = True

    def progress_indicator():
        dots = 0
        while progress_running:
            sys.stdout.write(f'\r  {Colors.INFO}⏳{Colors.RESET} Retrieving device details (batch processing){"." * (dots % 4)}{" " * (3 - (dots % 4))}')
            sys.stdout.flush()
            dots += 1
            time.sleep(0.3)

    # Start progress indicator
    progress_thread = threading.Thread(target=progress_indicator, daemon=True)
    progress_thread.start()

    try:
        for i in range(0, len(device_ids), batch_size):
            batch = device_ids[i:i + batch_size]

            response = hosts.get_device_details(ids=batch)

            if response['status_code'] == 200:
                devices.extend(response['body'].get('resources', []))
            else:
                # Don't stop progress for warnings
                pass
    finally:
        progress_running = False
        time.sleep(0.4)  # Let progress finish
        sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear line
        sys.stdout.flush()

    return devices


def get_host_groups(host_group: HostGroup, devices: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Get all host groups and create ID to name mapping.

    Args:
        host_group: HostGroup API instance
        devices: List of devices (to collect all group IDs)

    Returns:
        Dictionary mapping group ID to group name
    """
    groups = {}

    # Collect all unique group IDs from devices
    all_group_ids = set()
    for device in devices:
        device_groups = device.get('groups', [])
        all_group_ids.update(device_groups)

    if not all_group_ids:
        return {}

    # Try to get details for all group IDs in batches
    group_ids_list = list(all_group_ids)
    batch_size = 100

    for i in range(0, len(group_ids_list), batch_size):
        batch = group_ids_list[i:i + batch_size]

        try:
            details_response = host_group.get_host_groups(ids=batch)

            if details_response['status_code'] == 200:
                for group in details_response['body'].get('resources', []):
                    groups[group['id']] = group.get('name', group['id'])
        except:
            # If batch fails, try individually
            for group_id in batch:
                try:
                    details_response = host_group.get_host_groups(ids=[group_id])
                    if details_response['status_code'] == 200:
                        for group in details_response['body'].get('resources', []):
                            groups[group['id']] = group.get('name', group['id'])
                except:
                    pass

    # For any group IDs we couldn't resolve, use the ID itself
    for group_id in all_group_ids:
        if group_id not in groups:
            groups[group_id] = group_id  # Use ID as fallback

    return groups


def get_policies(prevention: PreventionPolicy, response_policy: ResponsePolicies,
                 sensor_update: SensorUpdatePolicies) -> Dict[str, Dict[str, str]]:
    """
    Get all policies and create ID to name mappings.

    Args:
        prevention: PreventionPolicy API instance
        response_policy: ResponsePolicies API instance
        sensor_update: SensorUpdatePolicies API instance

    Returns:
        Dictionary with policy type as key and ID->name mappings as values
    """
    policies = {
        'prevention': {},
        'response': {},
        'sensor_update': {}
    }

    # Prevention policies
    prev_response = prevention.queryCombinedPreventionPolicies()
    if prev_response['status_code'] == 200:
        for policy in prev_response['body'].get('resources', []):
            policies['prevention'][policy['id']] = policy.get('name', 'Unknown')

    # Response policies
    resp_response = response_policy.queryCombinedRTResponsePolicies()
    if resp_response['status_code'] == 200:
        for policy in resp_response['body'].get('resources', []):
            policies['response'][policy['id']] = policy.get('name', 'Unknown')

    # Sensor update policies
    sensor_response = sensor_update.queryCombinedSensorUpdatePoliciesV2()
    if sensor_response['status_code'] == 200:
        for policy in sensor_response['body'].get('resources', []):
            policies['sensor_update'][policy['id']] = policy.get('name', 'Unknown')

    return policies


def export_cid_to_csv(cid_info: Dict[str, Any], devices: List[Dict[str, Any]],
                      host_groups: Dict[str, str], policies: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Convert device data to CSV rows.

    Args:
        cid_info: CID information
        devices: List of device details
        host_groups: Host group ID to name mapping
        policies: Policy mappings

    Returns:
        List of CSV row dictionaries
    """
    rows = []

    for device in devices:
        # Get host groups
        device_groups = device.get('groups', [])
        group_names = [host_groups.get(gid, gid) for gid in device_groups]

        # Get prevention policy
        prevention_policy_id = device.get('device_policies', {}).get('prevention', {}).get('policy_id')
        prevention_applied = device.get('device_policies', {}).get('prevention', {}).get('applied', False)
        prevention_policy_name = policies['prevention'].get(prevention_policy_id, 'None') if prevention_policy_id else 'None'
        prevention_status = 'Applied' if prevention_applied else 'Assigned'

        # Get response policy
        response_policy_id = device.get('device_policies', {}).get('remote_response', {}).get('policy_id')
        response_applied = device.get('device_policies', {}).get('remote_response', {}).get('applied', False)
        response_policy_name = policies['response'].get(response_policy_id, 'None') if response_policy_id else 'None'
        response_status = 'Applied' if response_applied else 'Assigned'

        # Get sensor update policy
        sensor_policy_id = device.get('device_policies', {}).get('sensor_update', {}).get('policy_id')
        sensor_applied = device.get('device_policies', {}).get('sensor_update', {}).get('applied', False)
        sensor_policy_name = policies['sensor_update'].get(sensor_policy_id, 'None') if sensor_policy_id else 'None'
        sensor_status = 'Applied' if sensor_applied else 'Assigned'

        row = {
            'CID Name': cid_info['name'],
            'CID': cid_info['cid'],
            'CID Type': cid_info['type'].upper(),
            'Device ID': device.get('device_id', ''),
            'Hostname': device.get('hostname', ''),
            'OS Version': device.get('os_version', ''),
            'Platform': device.get('platform_name', ''),
            'Last Seen': device.get('last_seen', ''),
            'Status': device.get('status', ''),
            'Host Groups': ', '.join(group_names) if group_names else 'None',
            'Prevention Policy': prevention_policy_name,
            'Prevention Status': prevention_status if prevention_policy_id else 'None',
            'Response Policy': response_policy_name,
            'Response Status': response_status if response_policy_id else 'None',
            'Sensor Update Policy': sensor_policy_name,
            'Sensor Update Status': sensor_status if sensor_policy_id else 'None',
            'Agent Version': device.get('agent_version', ''),
            'Service Provider': device.get('service_provider', ''),
            'Service Provider Account ID': device.get('service_provider_account_id', ''),
        }

        rows.append(row)

    return rows


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Export CrowdStrike devices, groups, and policies to CSV'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to credentials config file'
    )
    parser.add_argument(
        '--client-id',
        type=str,
        help='Falcon API Client ID'
    )
    parser.add_argument(
        '--client-secret',
        type=str,
        help='Falcon API Client Secret'
    )
    parser.add_argument(
        '--base-url',
        type=str,
        default='https://api.crowdstrike.com',
        help='Falcon API base URL'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output CSV file path (default: devices_export_TIMESTAMP.csv)'
    )
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Export all CIDs without prompting'
    )

    args = parser.parse_args()

    print_header("FLIGHT CONTROL - DEVICES & POLICIES EXPORT", width=80, color=Colors.SUCCESS)

    # Get credentials
    client_id, client_secret, base_url, source = get_credentials_smart(
        config_path=args.config,
        client_id=args.client_id,
        client_secret=args.client_secret,
        base_url=args.base_url
    )

    if not client_id or not client_secret:
        print_error("No credentials provided!")
        print()
        print("Please provide credentials via one of these methods:")
        print("  1. Config file: --config config/credentials.json")
        print("  2. CLI args: --client-id <id> --client-secret <secret>")
        print("  3. Environment variables: FALCON_CLIENT_ID, FALCON_CLIENT_SECRET")
        sys.exit(1)

    from utils.formatting import print_credentials_source
    print_credentials_source(source)

    # Authenticate
    print_info("Authenticating to Falcon API...")

    try:
        flight_control = FlightControl(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url
        )
        print_success("Authentication successful!")
    except Exception as e:
        print_error(f"Authentication failed: {str(e)}")
        sys.exit(1)

    # Get all CIDs
    parent, children = get_all_cids(flight_control)

    if not parent:
        print_error("Failed to retrieve CID information")
        sys.exit(1)

    # Select CIDs
    if args.non_interactive:
        selected_cids = [parent] + children
        print_info(f"Non-interactive mode: exporting all {len(selected_cids)} CID(s)")
    else:
        selected_cids = select_cids_to_export(parent, children)

    if not selected_cids:
        print_warning("No CIDs selected")
        sys.exit(0)

    # Prepare output file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = args.output or f"devices_export_{timestamp}.csv"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

    print_header("EXPORTING DEVICE DATA", width=80)

    all_rows = []
    total_devices = 0

    for idx, cid_info in enumerate(selected_cids, 1):
        print()
        print(f"{Colors.HIGHLIGHT}▶ Processing: {cid_info['name']} ({cid_info['type'].upper()}){Colors.RESET}")

        # Authenticate with specific CID if it's a child
        if cid_info['type'] == 'child':
            hosts = Hosts(
                client_id=client_id,
                client_secret=client_secret,
                base_url=base_url,
                member_cid=cid_info['cid']
            )
            host_group = HostGroup(
                client_id=client_id,
                client_secret=client_secret,
                base_url=base_url,
                member_cid=cid_info['cid']
            )
            prevention = PreventionPolicy(
                client_id=client_id,
                client_secret=client_secret,
                base_url=base_url,
                member_cid=cid_info['cid']
            )
            response_policy = ResponsePolicies(
                client_id=client_id,
                client_secret=client_secret,
                base_url=base_url,
                member_cid=cid_info['cid']
            )
            sensor_update = SensorUpdatePolicies(
                client_id=client_id,
                client_secret=client_secret,
                base_url=base_url,
                member_cid=cid_info['cid']
            )
        else:
            hosts = Hosts(
                client_id=client_id,
                client_secret=client_secret,
                base_url=base_url
            )
            host_group = HostGroup(
                client_id=client_id,
                client_secret=client_secret,
                base_url=base_url
            )
            prevention = PreventionPolicy(
                client_id=client_id,
                client_secret=client_secret,
                base_url=base_url
            )
            response_policy = ResponsePolicies(
                client_id=client_id,
                client_secret=client_secret,
                base_url=base_url
            )
            sensor_update = SensorUpdatePolicies(
                client_id=client_id,
                client_secret=client_secret,
                base_url=base_url
            )

        # Get devices
        print_info("  Querying devices...")
        device_ids = get_devices_for_cid(hosts, cid_info)
        print_success(f"  Found {len(device_ids)} device(s)")

        if not device_ids:
            print_warning(f"  No devices found for {cid_info['name']}")
            continue

        # Get device details
        print_info("  Retrieving device details...")
        devices = get_device_details(hosts, device_ids)
        print_success(f"  Retrieved details for {len(devices)} device(s)")

        # Get host groups (pass devices to collect all group IDs)
        print_info("  Loading host groups...")
        host_groups = get_host_groups(host_group, devices)
        print_success(f"  Loaded {len(host_groups)} host group(s)")

        # Get policies
        print_info("  Loading policies...")
        policies = get_policies(prevention, response_policy, sensor_update)
        policy_count = len(policies['prevention']) + len(policies['response']) + len(policies['sensor_update'])
        print_success(f"  Loaded {policy_count} policie(s)")

        # Convert to CSV rows
        print_info("  Converting to CSV format...")
        rows = export_cid_to_csv(cid_info, devices, host_groups, policies)
        all_rows.extend(rows)
        total_devices += len(rows)
        print_success(f"  Processed {len(rows)} device(s)")

        # Progress
        print_progress(idx, len(selected_cids), prefix="Overall progress", suffix=f"({cid_info['name'][:30]})")

    # Write CSV
    print()
    print_info(f"Writing CSV file: {output_file}")

    if all_rows:
        fieldnames = [
            'CID Name', 'CID', 'CID Type', 'Device ID', 'Hostname', 'OS Version', 'Platform',
            'Last Seen', 'Status', 'Host Groups', 'Prevention Policy', 'Prevention Status',
            'Response Policy', 'Response Status', 'Sensor Update Policy', 'Sensor Update Status',
            'Agent Version', 'Service Provider', 'Service Provider Account ID'
        ]

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)

        print_success(f"CSV file created successfully!")
    else:
        print_warning("No data to export")

    # Summary
    print_summary_box(
        "EXPORT COMPLETE",
        {
            'CIDs processed': len(selected_cids),
            'Total devices exported': total_devices,
            'Output file': output_file,
        },
        width=80
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Export interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
