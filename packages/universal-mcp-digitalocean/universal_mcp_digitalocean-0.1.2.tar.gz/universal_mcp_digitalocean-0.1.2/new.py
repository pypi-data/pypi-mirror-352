import requests
from typing import Any, Optional, Dict

# --- Minimal Base Class (to make DigitaloceanApp work) ---
class APIApplication:
    def __init__(self, name: str, integration: Optional[Any] = None, **kwargs) -> None:
        """
        A minimal base class.
        The 'integration' object is expected to have a 'token' attribute.
        """
        self.name = name
        self.integration = integration
        self.session = requests.Session() # Use a session for connection pooling

        if self.integration and hasattr(self.integration, 'token'):
            self.session.headers.update({
                "Authorization": f"Bearer {self.integration.token}",
                "Content-Type": "application/json"
            })
        else:
            # If no integration or token, subsequent requests might fail
            # or you might want to raise an error here.
            print("Warning: APIApplication initialized without a token in integration.")


    def _get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Performs a GET request.
        """
        # Headers from the session will be used, but can be overridden by 'headers' argument
        merged_headers = self.session.headers.copy()
        if headers:
            merged_headers.update(headers)
            
        response = self.session.get(url, params=params, headers=merged_headers)
        return response

    # You might want to add _post, _put, _delete etc. for a more complete API client
    # def _post(self, url: str, json_data: Optional[Dict[str, Any]] = None, ...):
    #     ...


# --- Your DigitaloceanApp Class (as provided) ---
class DigitaloceanApp(APIApplication):
    def __init__(self, integration: Optional[Any] = None, **kwargs) -> None:
        super().__init__(name='digitalocean', integration=integration, **kwargs)
        self.base_url = "https://api.digitalocean.com"

    def account_get(self) -> Any:
        """
        Get User Information

        Returns:
            Any: A JSON object keyed on account with an excerpt of the current user account data.

        Tags:
            Account
        """
        url = f"{self.base_url}/v2/account"
        query_params = {} # No query params needed for this endpoint
        response = self._get(url, params=query_params)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()


# --- Simple Integration class to hold the token ---
class MyDOIntegration:
    def __init__(self, token: str):
        self.token = token


# --- Main script to use the class ---
if __name__ == "__main__":
    ACCESS_TOKEN = "doo_v1_e45caa4e823afb373da5c6680277a76d7c3c36f4400328f278f95a08d94bdded"

    # 1. Create an "integration" object that holds the token
    #    Your APIApplication expects the token to be accessible via this integration object.
    do_integration = MyDOIntegration(token=ACCESS_TOKEN)

    # 2. Instantiate your DigitaloceanApp
    app = DigitaloceanApp(integration=do_integration)

    # 3. Call the method
    try:
        print("Fetching DigitalOcean account info...")
        account_info = app.account_get()
        print("\nAccount Information:")
        import json
        print(json.dumps(account_info, indent=2))

    except requests.exceptions.HTTPError as e:
        print(f"\nHTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nRequest Exception: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")