"""Get the ads a Vinted user currently has on sale."""

import vntd


def main() -> None:
    # Initialize the Vinted API client
    client = vntd.Client()

    # Replace the ID with a real one for testing
    result = client.get_user_ads(80325437, page=1, limit=24, sort=vntd.Sort.NEWEST)

    print(f"{result.total} ads")
    for ad in result.ads:
        print(f"{ad.id} | {ad.url} | {ad.title} | {ad.price}€")


if __name__ == "__main__":
    main()
