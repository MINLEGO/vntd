"""Get detailed information about a Vinted item using its ID."""

import vntd


def main() -> None:
    # Initialize the Vinted API client
    client = vntd.Client()

    # Fetch an item by its Vinted ID (replace with a real one for testing)
    ad = client.get_ad("8975084387")

    # Print basic information about the item
    print("Title:", ad.title)
    print("Price:", ad.price)
    print("Brand:", ad.brand)
    print("Description:", ad.description)

    # Print information about the user who posted the item
    print("User info:", ad.user)


if __name__ == "__main__":
    main()
