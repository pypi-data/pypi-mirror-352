# -*- coding: utf-8 -*-


import json
import fire
from my_cli_utilities_common.http_helpers import make_sync_request

BASE_URL = "https://device-spy-mthor.int.rclabenv.com"
HOSTS_ENDPOINT = BASE_URL + "/api/v1/hosts"
ALL_DEVICES_ENDPOINT = BASE_URL + "/api/v1/hosts/get_all_devices"
LABELS_ENDPOINT = BASE_URL + "/api/v1/labels/"
DEVICE_ASSETS_ENDPOINT = BASE_URL + "/api/v1/device_assets/"


class DeviceSpyCli:
    """A CLI tool to interact with the Device Spy service.

    This tool allows you to query various details about devices and hosts
    managed by the Device Spy system.
    """

    def _get_device_location_from_assets(self, udid):
        response_data = make_sync_request(DEVICE_ASSETS_ENDPOINT)
        if response_data:
            device_assets = response_data.get("data", [])
            for device_asset in device_assets:
                if device_asset.get("udid") == udid:
                    return device_asset.get("location")
        return None

    def _get_host_alias(self, host_ip):
        response_data = make_sync_request(HOSTS_ENDPOINT)
        if response_data:
            hosts = response_data.get("data", [])
            for host in hosts:
                if host.get("hostname") == host_ip:
                    return host.get("alias")
        return None

    def info(self, udid: str):
        """Queries and displays detailed information for a specific device.

        Args:
            udid (str): The Unique Device Identifier (UDID) of the device to query.
        """
        response_data = make_sync_request(ALL_DEVICES_ENDPOINT)
        if not response_data:
            return

        devices = response_data.get("data", [])
        for device_data in devices:
            if udid == device_data.get("udid"):
                device_info = device_data.copy()
                original_hostname = device_info.get("hostname")

                device_info["hostname"] = self._get_host_alias(original_hostname)

                if device_info.get("platform") == "android":
                    device_info["ip_port"] = (
                        f"{original_hostname}:{device_info.get('adb_port')}"
                    )

                location = self._get_device_location_from_assets(udid)
                if location:
                    device_info["location"] = location

                keys_to_delete = ["is_simulator", "remote_control", "adb_port"]

                for key in keys_to_delete:
                    if key in device_info:
                        del device_info[key]

                print(json.dumps(device_info, indent=2, ensure_ascii=False))
                return
        
        print(f"Device with UDID '{udid}' not found or error in fetching data.")

    def available_devices(self, platform: str):
        """Lists available (not locked, not simulator) devices for a given platform.

        Args:
            platform (str): The platform to filter by (e.g., "android", "ios").
        """
        response_data = make_sync_request(ALL_DEVICES_ENDPOINT)
        if not response_data:
            return

        all_devices = response_data.get("data", [])
        avail_devices_udids = []

        for device in all_devices:
            if (
                not device.get("is_locked")
                and not device.get("is_simulator")
                and device.get("platform") == platform
            ):
                avail_devices_udids.append(device.get("udid"))

        result = {
            "count": len(avail_devices_udids),
            "udids": avail_devices_udids,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))

    def get_host_ip(self, query_string: str):
        """Finds host IP address(es) based on a query string.

        The query string is matched against host information fields like alias or hostname.

        Args:
            query_string (str): The string to search for within host information.
        """
        response_data = make_sync_request(HOSTS_ENDPOINT)
        if not response_data:
            return

        hosts = response_data.get("data", [])
        found_host_ips = []
        for host in hosts:
            for value in host.values():
                if query_string.lower() in str(value).lower():
                    found_host_ips.append(host.get("hostname"))
                    break

        if not found_host_ips:
            print(f"No host found matching '{query_string}'.")
        elif len(found_host_ips) == 1:
            print(found_host_ips[0])
        else:
            print(json.dumps(found_host_ips, indent=2))


def main_ds_function():
    fire.Fire(DeviceSpyCli)


if __name__ == '__main__':
    main_ds_function()
