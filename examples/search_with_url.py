"""Search for items on Vinted using a full search URL."""

import vntd


def main() -> None:
    # Initialize the Vinted API client
    client = vntd.Client()

    # Perform a search using a prebuilt Vinted URL
    result = client.search(
        url="https://www.vinted.fr/catalog?search_text=robe&order=newest_first&price_from=5&price_to=20",
        page=1,
        limit=24,
    )

    # Print basic info about each item
    for ad in result.ads:
        print(f"{ad.id} | {ad.url} | {ad.title} | {ad.price}€ | Seller: {ad.user}")


if __name__ == "__main__":
    main()
