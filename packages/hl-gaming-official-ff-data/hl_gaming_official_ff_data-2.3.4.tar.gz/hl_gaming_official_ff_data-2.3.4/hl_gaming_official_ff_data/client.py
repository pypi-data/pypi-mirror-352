import requests

class HLFFClient:
    BASE_URL = "https://hl-gaming-official-main-api-beige.vercel.app/api"

    def __init__(self, api_key, region="pk"):
        if not api_key:
            raise ValueError("API key is required.")
        self.api_key = api_key
        self.region = region

    def get_player_data(self, player_uid, user_uid, region=None):
        """
        Fetches Free Fire player data from HL Gaming Official API.

        Args:
            player_uid (str): The Player UID from Free Fire.
            user_uid (str): Your own UID to identify requests.
            region (str, optional): Region code like 'pk', 'in', etc. Defaults to client region.

        Returns:
            dict: JSON response from API.

        Raises:
            ValueError: If required parameters are missing.
            requests.exceptions.RequestException: For network/API errors.
        """
        if not player_uid:
            raise ValueError("Player UID is required.")
        if not user_uid:
            raise ValueError("User UID is required.")

        use_region = region if region else self.region

        params = {
            "sectionName": "AllData",
            "PlayerUid": player_uid,
            "region": use_region,
            "useruid": user_uid,
            "api": self.api_key
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            raise Exception(f"HTTP Error: {http_err}. Please check your API key or input data.")
        except requests.exceptions.RequestException as req_err:
            raise Exception(f"Request failed: {req_err}. Is your internet working?")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
