"""Search for items on Vinted using filters."""

import vntd


def main() -> None:
    # Initialize the Vinted API client
    client = vntd.Client()

    # Perform a search with various filters
    result = client.search(
        text="robe",  # Search keyword
        page=1,
        limit=24,  # Max results per page
        sort=vntd.Sort.NEWEST,  # Sort by newest items
        price=(5, 30),  # Price range in euros
        brand_ids=[53, 54],  # Optional brand IDs
    )

    # Display summary of each item
    for ad in result.ads:
        print(f"{ad.id} | {ad.url} | {ad.title} | {ad.price}€ | Seller: {ad.user}")


if __name__ == "__main__":
    main()
