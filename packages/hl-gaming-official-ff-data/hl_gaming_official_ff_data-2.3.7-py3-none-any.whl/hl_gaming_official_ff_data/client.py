import requests

class HLFFClient:
    # Private API URL — not exposed in error messages
    _BASE_URL = "https://hl-gaming-official-main-api-beige.vercel.app/api"

    def __init__(self, api_key, region="pk"):
        if not api_key:
            raise ValueError("🔑 API key is missing. Please provide your HL Gaming Official API key.")
        self.api_key = api_key
        self.region = region

    def get_player_data(self, player_uid, user_uid, region=None):
        """
        Fetches Free Fire player data securely from HL Gaming Official API.

        Args:
            player_uid (str): Free Fire player ID.
            user_uid (str): Your user ID for tracking purposes.
            region (str, optional): Country code (default is 'pk').

        Returns:
            dict: JSON response from HL Gaming Official API.

        Raises:
            ValueError: If required inputs are missing.
            Exception: Friendly error with API-provided details (if available).
        """
        if not player_uid:
            raise ValueError("🚫 Player UID is required. Example: '9351564274'")
        if not user_uid:
            raise ValueError("🚫 User UID is required. This helps track your API usage.")

        use_region = region if region else self.region

        params = {
            "sectionName": "AllData",
            "PlayerUid": player_uid,
            "region": use_region,
            "useruid": user_uid,
            "api": self.api_key
        }

        try:
            response = requests.get(self._BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            try:
                # Try to extract and include exact API error message from the JSON response
                error_details = response.json()
                raise Exception(
                    "📡 HL Gaming API returned an error (4xx/5xx).\n"
                    "🔁 Please check your API key, Player UID, and Region.\n"
                    "❗ Error Details from API:\n"
                    f"{error_details}\n"
                    "📚 Docs: https://www.hlgamingofficial.com/p/api.html\n"
                    "🆘 Help: https://www.hlgamingofficial.com/p/contact-us.html"
                )
            except Exception:
                # If no valid JSON returned
                raise Exception(
                    "📡 HL Gaming API returned an unknown error.\n"
                    f"💬 HTTP Error: {http_err}\n"
                    "📚 Docs: https://www.hlgamingofficial.com/p/api.html\n"
                    "🆘 Contact: https://www.hlgamingofficial.com/p/contact-us.html"
                )

        except requests.exceptions.RequestException:
            raise Exception(
                "⚠️ Network issue occurred while connecting to HL Gaming API.\n"
                "📶 Please check your internet connection.\n"
                "📚 API Info: https://www.hlgamingofficial.com/p/api.html"
            )

        except Exception as e:
            raise Exception(
                f"❗ An unexpected error occurred in HL Gaming Official API client.\n"
                f"💡 Details: {str(e)}\n"
                "🆘 Support: https://www.hlgamingofficial.com/p/contact-us.html"
            )
