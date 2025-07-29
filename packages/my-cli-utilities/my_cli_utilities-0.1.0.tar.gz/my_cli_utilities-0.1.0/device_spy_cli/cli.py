# -*- coding: utf-8 -*-


import json
import fire
import httpx

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
        try:
            with httpx.Client() as client:
                response = client.get(DEVICE_ASSETS_ENDPOINT)
                response.raise_for_status()
                device_assets = response.json().get("data", [])
                for device_asset in device_assets:
                    if device_asset.get("udid") == udid:
                        return device_asset.get("location")
        except httpx.RequestError as e:
            print(f"Error fetching device assets: {e}")
        except json.JSONDecodeError:
            print("Error decoding JSON from device assets response.")
        return None

    def _get_host_alias(self, host_ip):
        try:
            with httpx.Client() as client:
                response = client.get(HOSTS_ENDPOINT)
                response.raise_for_status()
                hosts = response.json().get("data", [])
                for host in hosts:
                    if host.get("hostname") == host_ip:
                        return host.get("alias")
        except httpx.RequestError as e:
            print(f"Error fetching hosts: {e}")
        except json.JSONDecodeError:
            print("Error decoding JSON from hosts response.")
        return None

    def info(self, udid: str):
        """Queries and displays detailed information for a specific device.

        Args:
            udid (str): The Unique Device Identifier (UDID) of the device to query.
        """
        try:
            with httpx.Client() as client:
                response = client.get(ALL_DEVICES_ENDPOINT)
                response.raise_for_status()
                devices = response.json().get("data", [])
                for device_data in devices:
                    if udid == device_data.get("udid"):
                        device_info = device_data.copy()
                        original_hostname = device_info.get("hostname")

                        device_info["hostname"] = self._get_host_alias(
                            original_hostname
                        )

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
                print(f"Device with UDID '{udid}' not found.")
        except httpx.RequestError as e:
            print(f"Error fetching all devices: {e}")
        except json.JSONDecodeError:
            print("Error decoding JSON from all devices response.")

    def available_devices(self, platform: str):
        """Lists available (not locked, not simulator) devices for a given platform.

        Args:
            platform (str): The platform to filter by (e.g., "android", "ios").
        """
        try:
            with httpx.Client() as client:
                response = client.get(ALL_DEVICES_ENDPOINT)
                response.raise_for_status()
                all_devices = response.json().get("data", [])
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

        except httpx.RequestError as e:
            print(f"Error fetching available devices: {e}")
        except json.JSONDecodeError:
            print("Error decoding JSON from available devices response.")

    def get_host_ip(self, query_string: str):
        """Finds host IP address(es) based on a query string.

        The query string is matched against host information fields like alias or hostname.

        Args:
            query_string (str): The string to search for within host information.
        """
        try:
            with httpx.Client() as client:
                response = client.get(HOSTS_ENDPOINT)
                response.raise_for_status()
                hosts = response.json().get("data", [])
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

        except httpx.RequestError as e:
            print(f"Error fetching hosts for IP lookup: {e}")
        except json.JSONDecodeError:
            print("Error decoding JSON from hosts response for IP lookup.")


def main_ds_function():
    fire.Fire(DeviceSpyCli)


# if __name__ == '__main__':
# main_ds_function() # Keep this commented out for library use
