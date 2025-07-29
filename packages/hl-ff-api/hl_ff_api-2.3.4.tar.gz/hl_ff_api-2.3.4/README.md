# HL FF API (hl_ff_api)

Official Python client for [HL Gaming Official's Free Fire API](https://www.hlgamingofficial.com/p/api.html)

## 📦 Installation

```bash
pip install hl_ff_api
```

## 🚀 Usage

```python
from hl_ff_api import HLFFClient

api_key = "your-api-key"
player_uid = "9351564274"
user_uid = "your-user-uid"
region = "pk"

client = HLFFClient(api_key=api_key, region=region)
data = client.get_player_data(player_uid=player_uid, user_uid=user_uid)

print(data)
```

## 📄 Documentation

- [API Docs](https://www.hlgamingofficial.com/p/free-fire-api-data-documentation.html)
- [Main Site](https://www.hlgamingofficial.com)

---

Developed by **Haroon Brokha**  
📧 Contact: developers@hlgamingofficial.com
