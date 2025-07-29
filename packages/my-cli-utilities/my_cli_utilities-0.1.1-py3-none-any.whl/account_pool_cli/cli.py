# -*- coding: utf-8 -*-

import asyncio
import fire
import json
import random
from my_cli_utilities_common.http_helpers import make_async_request

ACCOUNT_POOL_BASE_URL = "https://account-pool-mthor.int.rclabenv.com"
ACCOUNTS_ENDPOINT = f"{ACCOUNT_POOL_BASE_URL}/accounts"

class AccountPoolCli:
    """
    A CLI tool to interact with the Account Pool service.
    Provides commands to fetch random accounts, specific account details by ID,
    or specific account details by main number.
    env_name defaults to 'webaqaxmn' if not provided for relevant commands.
    """

    async def _fetch_random_account_async(self, env_name: str, account_type: str):
        params = {"envName": env_name, "accountType": account_type}
        print(f"Fetching random account for type '{account_type}' in env '{env_name}'...")
        
        response_data = await make_async_request(ACCOUNTS_ENDPOINT, params=params)
        
        if not response_data:
            # Error already printed by make_async_request
            return

        # print(f"Request successful! Status code: {response.status_code}") # Covered by helper or less verbose
        try:
            accounts_list = response_data.get("accounts")
            if accounts_list:
                random_account = random.choice(accounts_list)
                print("Randomly selected account information:")
                print(json.dumps(random_account, indent=2, ensure_ascii=False))
            else:
                print("No matching accounts found, or the 'accounts' list is empty.")
        except (TypeError, KeyError) as e: # JSONDecodeError is handled by make_async_request
             # This specific error handling for parsing might be less needed if make_async_request handles JSON well
             # However, structure of JSON (missing 'accounts' key) is still a concern here.
            print(f"Failed to extract account information from response data: {e}")
            print("Raw data received:", json.dumps(response_data, indent=2, ensure_ascii=False) if isinstance(response_data, dict) else str(response_data))


    def get_random_account(self, account_type: str, env_name: str = "webaqaxmn"):
        """Fetches a random account from the Account Pool.

        Args:
            account_type (str): Account type (e.g., 'kamino2(CI-Common-4U,mThor,brand=1210)').
            env_name (str, optional): Environment name. Defaults to "webaqaxmn".
        """
        asyncio.run(self._fetch_random_account_async(env_name, account_type))

    async def _fetch_account_by_id_async(self, account_id: str, env_name: str):
        url = f"{ACCOUNTS_ENDPOINT}/{account_id}"
        params = {"envName": env_name}
        print(f"Fetching details for account ID {account_id} in env {env_name}...")
        
        account_details = await make_async_request(url, params=params)
        
        if account_details:
            # print(f"Request for ID {account_id} successful!") # Less verbose
            print("Account details:")
            print(json.dumps(account_details, indent=2, ensure_ascii=False))
        # else: error already printed by make_async_request

    def get_account_by_id(self, account_id: str, env_name: str = "webaqaxmn"):
        """Fetches specific account details by its ID.

        Args:
            account_id (str): The _id of the account to fetch.
            env_name (str, optional): Environment name. Defaults to "webaqaxmn".
        """
        asyncio.run(self._fetch_account_by_id_async(account_id, env_name))

    async def _fetch_info_by_main_number_async(self, main_number: str, env_name: str):
        main_number_str = str(main_number)
        if not main_number_str.startswith("+"):
            main_number_str = "+" + main_number_str

        params_initial_lookup = {"envName": env_name, "mainNumber": main_number_str}
        print(f"Looking up account ID for main number {main_number_str} in env {env_name}...")
        
        response_data = await make_async_request(ACCOUNTS_ENDPOINT, params=params_initial_lookup)
        
        if not response_data:
            return

        try:
            accounts_list = response_data.get("accounts")
            if accounts_list:
                # Assuming the first account in the list is the one we want for mainNumber lookup
                account_summary = accounts_list[0]
                retrieved_account_id = account_summary.get("_id")
                if retrieved_account_id:
                    print(f"Found account ID: {retrieved_account_id}. Fetching details...")
                    # Call the _fetch_account_by_id_async directly, as it now handles its own printing
                    await self._fetch_account_by_id_async(retrieved_account_id, env_name)
                else:
                    print(f"Account found for main number {main_number_str}, but it does not contain an '_id' field.")
                    print("Account summary found:", json.dumps(account_summary, indent=2, ensure_ascii=False))
            else:
                print(f"No account found for main number {main_number_str} in environment {env_name}.")
        except (TypeError, KeyError, IndexError) as e: # JSONDecodeError handled by make_async_request
            print(f"Failed to parse or extract account ID from initial lookup: {e}")
            print("Raw data received:", json.dumps(response_data, indent=2, ensure_ascii=False) if isinstance(response_data, dict) else str(response_data))

    def info(self, main_number: str, env_name: str = "webaqaxmn"):
        """Fetches account details by mainNumber (looks up ID first).

        Args:
            main_number (str): The mainNumber (e.g., '12495002020' or '+12495002020').
            env_name (str, optional): Environment name. Defaults to "webaqaxmn".
        """
        asyncio.run(self._fetch_info_by_main_number_async(main_number, env_name))

def main_cli_function():
    fire.Fire(AccountPoolCli)

if __name__ == "__main__":
    main_cli_function()