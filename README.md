# vntd

**Unofficial client for the Vinted API.**
**Fork of [lbc](https://pypi.org/project/lbc/) by [etienne-hd](https://pypi.org/user/etienne-hd/)**

```python
import vntd

client = vntd.Client()

result = client.search(
    text="robe",
    page=1,
    limit=20,
    sort=vntd.Sort.NEWEST,
    price=(5, 30),
)

for ad in result.ads:
    print(ad.url, ad.title, ad.price, ad.user)
```

*vntd is not affiliated with, endorsed by, or in any way associated with Vinted or its services. Use at your own risk.*

## Installation
Required **Python 3.10+**
```bash
pip install vntd
```

## Usage

### Client
```python
import vntd

client = vntd.Client()
```

### Search
```python
result = client.search(
    text="robe",
    page=1,
    limit=24,
    sort=vntd.Sort.RELEVANCE,
    price=(10, 40),
    brand_ids=[53, 54],
)
```

### Search with URL
```python
result = client.search(
    url="https://www.vinted.fr/catalog?search_text=robe&order=newest_first&price_from=5&price_to=30",
    page=1,
    limit=24,
)
```

### Get Item
```python
ad = client.get_ad("8975084387")
print(ad.title, ad.price, ad.user)
```

### Get User
```python
user = client.get_user(80325437)
print(user.login, user.feedback_score, user.item_count)
```

### Proxy
```python
proxy = vntd.Proxy(host="127.0.0.1", port=12345)
client = vntd.Client(proxy=proxy)
```

## Notes
Vinted does not expose Leboncoin-style radius/region filters or professional store data (SIRET). Use Vinted-native filters such as `price`, `brand_ids`, and `seller_type` instead.
