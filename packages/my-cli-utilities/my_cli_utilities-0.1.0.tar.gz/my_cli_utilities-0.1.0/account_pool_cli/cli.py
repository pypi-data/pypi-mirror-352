# -*- coding: utf-8 -*-

import httpx
import asyncio
import fire
import json
import random 


class AccountPoolCli:
    """
    A CLI tool to interact with the Account Pool service.
    Provides commands to fetch random accounts, specific account details by ID,
    or specific account details by main number.
    env_name defaults to 'webaqaxmn' if not provided for relevant commands.
    """

    async def _fetch_random_account_async(self, env_name: str, account_type: str):
        # Base part of the URL
        base_url = "https://account-pool-mthor.int.rclabenv.com/accounts"
        # Dictionary of query parameters; httpx will automatically handle URL encoding for these
        params = {"envName": env_name, "accountType": account_type}
        try:
            async with httpx.AsyncClient() as client:
                # Pass query conditions using the params argument
                response = await client.get(base_url, params=params)
                response.raise_for_status()  # If the request fails (status code 4xx or 5xx), an HTTPStatusError exception will be raised
                print(f"Request successful! Status code: {response.status_code}")
                # Assume the response is in JSON format
                try:
                    parsed_json = response.json()  # Parse JSON first
                    accounts_list = parsed_json.get(
                        "accounts"
                    )  # More safely get the 'accounts' list

                    if accounts_list:  # Check if the list exists and is not empty
                        random_account = random.choice(
                            accounts_list
                        )  # Randomly select an account
                        print("Randomly selected account information:")
                        # Print the entire randomly selected account dictionary (user previously changed to print the whole object)
                        print(json.dumps(random_account, indent=2, ensure_ascii=False))
                    else:
                        print(
                            "No matching accounts found, or the 'accounts' list is empty."
                        )

                except (
                    json.JSONDecodeError,
                    TypeError,
                    KeyError,
                ) as e:  # Removed IndexError because we now check the list first
                    print(f"Failed to parse JSON or extract account information: {e}")
                    print("Attempting to print raw response text:")
                    print(response.text)
                    if not isinstance(e, json.JSONDecodeError):
                        try:
                            print(
                                "Parsed JSON structure (may be incomplete or not as expected):"
                            )
                            print(
                                json.dumps(
                                    response.json(), indent=2, ensure_ascii=False
                                )
                            )
                        except Exception as dump_e:
                            print(
                                f"Error occurred while trying to print parsed JSON: {dump_e}"
                            )

        except httpx.HTTPStatusError as exc:
            print(
                f"Request failed, HTTP status code: {exc.response.status_code}, Error message: {exc.response.text}"
            )
        except httpx.RequestError as exc:
            print(f"An error occurred during the request: {exc}")

    def get_random_account(self, account_type: str, env_name: str = "webaqaxmn"):
        """
        Fetches a random account from the Account Pool based on environment and account type.

        Args:
            account_type (str): Account type (e.g., \'\'\'kamino2(CI-Common-4U,mThor,brand=1210,packageId=26,packageVersion=1,pipeline=rc+glp)\'\'\').
            env_name (str, optional): Environment name. Defaults to "webaqaxmn".
        """
        asyncio.run(self._fetch_random_account_async(env_name, account_type))

    async def _fetch_account_by_id_async(self, account_id: str, env_name: str):
        # Construct URL with account_id in the path and env_name as a query parameter
        url = f"https://account-pool-mthor.int.rclabenv.com/accounts/{account_id}"
        params = {"envName": env_name}

        print(
            f"Fetching details for account ID {account_id} in env {env_name}..."
        )  # Added print for clarity
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()  # Raise an exception for bad status codes
                print(
                    f"Request for ID {account_id} successful! Status code: {response.status_code}"
                )
                try:
                    account_details = response.json()
                    print("Account details:")
                    # Print the formatted JSON response
                    print(json.dumps(account_details, indent=2, ensure_ascii=False))
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON response for ID {account_id}: {e}")
                    print("Raw response text:")
                    print(response.text)
        except httpx.HTTPStatusError as exc:
            print(
                f"Request for ID {account_id} failed, HTTP status code: {exc.response.status_code}, Error message: {exc.response.text}"
            )
            print("Raw response text (on error):")
            print(exc.response.text)
        except httpx.RequestError as exc:
            print(f"An error occurred during the request for ID {account_id}: {exc}")

    def get_account_by_id(self, account_id: str, env_name: str = "webaqaxmn"):
        """
        Fetches specific account details by its ID and environment name.

        Args:
            account_id (str): The _id of the account to fetch.
            env_name (str, optional): Environment name. Defaults to "webaqaxmn".
        """
        asyncio.run(self._fetch_account_by_id_async(account_id, env_name))

    async def _fetch_info_by_main_number_async(self, main_number: str, env_name: str):
        # Ensure main_number is treated as a string for string operations
        main_number_str = str(main_number)
        # Automatically prepend '+' if not present
        if not main_number_str.startswith("+"):
            main_number_str = "+" + main_number_str

        base_url = "https://account-pool-mthor.int.rclabenv.com/accounts"
        params_initial_lookup = {"envName": env_name, "mainNumber": main_number_str}
        print(
            f"Looking up account ID for main number {main_number_str} in env {env_name}..."
        )
        try:
            async with httpx.AsyncClient() as client:
                response_initial = await client.get(
                    base_url, params=params_initial_lookup
                )
                response_initial.raise_for_status()
                try:
                    parsed_json = response_initial.json()
                    accounts_list = parsed_json.get("accounts")
                    if accounts_list:
                        account_summary = accounts_list[0]
                        retrieved_account_id = account_summary.get("_id")
                        if retrieved_account_id:
                            print(
                                f"Found account ID: {retrieved_account_id}. Fetching details..."
                            )
                            await self._fetch_account_by_id_async(
                                retrieved_account_id, env_name
                            )
                        else:
                            print(
                                f"Account found for main number {main_number_str}, but it does not contain an '_id' field."
                            )
                            print("Account summary found:")
                            print(
                                json.dumps(
                                    account_summary, indent=2, ensure_ascii=False
                                )
                            )
                    else:
                        print(
                            f"No account found for main number {main_number_str} in environment {env_name}."
                        )
                except (json.JSONDecodeError, TypeError, KeyError, IndexError) as e:
                    print(
                        f"Failed to parse JSON or extract account ID from initial lookup: {e}"
                    )
                    print("Attempting to print raw response text from initial lookup:")
                    print(response_initial.text)
                    if not isinstance(e, json.JSONDecodeError):
                        try:
                            print(
                                "Parsed JSON structure from initial lookup (may be incomplete or not as expected):"
                            )
                            print(
                                json.dumps(
                                    response_initial.json(),
                                    indent=2,
                                    ensure_ascii=False,
                                )
                            )
                        except Exception as dump_e:
                            print(
                                f"Error occurred while trying to print parsed JSON from initial lookup: {dump_e}"
                            )
        except httpx.HTTPStatusError as exc:
            print(
                f"Initial lookup for main number {main_number_str} failed, HTTP status code: {exc.response.status_code}, Error message: {exc.response.text}"
            )
            print("Raw response text (on error):")
            print(exc.response.text)
        except httpx.RequestError as exc:
            print(
                f"An error occurred during the initial lookup for main number {main_number_str}: {exc}"
            )

    def info(self, main_number: str, env_name: str = "webaqaxmn"):
        """
        Fetches specific account details by its mainNumber.
        This first looks up the account by mainNumber to get its _id, then fetches full details using the _id.
        If main_number is provided without a leading '+', it will be added automatically.

        Args:
            main_number (str): The mainNumber of the account to fetch (e.g., 12495002020 or +12495002020).
            env_name (str, optional): Environment name. Defaults to "webaqaxmn".
        """
        asyncio.run(self._fetch_info_by_main_number_async(main_number, env_name))


def main_cli_function():
    fire.Fire(AccountPoolCli)

if __name__ == "__main__":
    main_cli_function()