"""Search for items on Vinted using filters."""

import vntd


def main() -> None:
    # Initialize the Vinted API client
    client = vntd.Client()

    # Perform a search with various filters
    result = client.search(
        text="robe",  # Search keyword
        page=3,
        limit=480,  # Max results per page
        sort=vntd.Sort.PRICE_LOW_TO_HIGH,  # Sort by newest items
        price=(5, 30),  # Price range in euros
        brand_ids=[53, 54],  # Optional brand IDs
    )

    # Display summary of each item
    for ad in result.ads:
        print(f"{ad.id} | {ad.url} | {ad.title} | {ad.price}€ ")


if __name__ == "__main__":
    main()
