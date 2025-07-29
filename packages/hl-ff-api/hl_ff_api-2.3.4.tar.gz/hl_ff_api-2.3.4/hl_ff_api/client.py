# hl_ff_api/client.py

import requests

class HLFFClient:
    BASE_URL = "https://hl-gaming-official-main-api-beige.vercel.app/api"

    def __init__(self, api_key, region="pk"):
        self.api_key = api_key
        self.region = region

    def get_player_data(self, player_uid, user_uid, region=None):
        """
        HL Gaming Official Free Fire API se data fetch karta hai.
        Agar 'region' parameter diya gaya hai to usko use karega,
        warna client ka default region use karega.
        """
        use_region = region if region is not None else self.region

        params = {
            "sectionName": "AllData",
            "PlayerUid": player_uid,
            "region": use_region,
            "useruid": user_uid,
            "api": self.api_key
        }

        response = requests.get(self.BASE_URL, params=params)

        response.raise_for_status()  # agar error ho to exception dega
        return response.json()  # API ka JSON response return karega
