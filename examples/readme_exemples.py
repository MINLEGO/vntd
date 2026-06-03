#Client
import vntd

client = vntd.Client()

# #Search
# result = client.search(
#     text="robe",
#     page=1,
#     limit=24,
#     sort=vntd.Sort.RELEVANCE,
#     price=(10, 40),
#     brand_ids=[53, 54],
# )

# #Search with URL
# result = client.search(
#     url="https://www.vinted.fr/catalog?search_text=robe&order=newest_first&price_from=5&price_to=30",
#     page=1,
#     limit=24,
# )

#Get Item
ad = client.get_ad("9081746285")
print(ad.title, ad.price, ad.user)

#Get User
user = client.get_user(49346009)
print(user.login, user.feedback_score, user.item_count)

#Proxy
proxy = vntd.Proxy(host="127.0.0.1", port=12345)
client = vntd.Client(proxy=proxy)