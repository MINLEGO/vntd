"""Get detailed information about a Vinted item using its ID."""

import vntd


def main() -> None:
    # Initialize the Vinted API client
    client = vntd.Client()

    # Fetch an item by its Vinted ID (replace with a real one for testing)
    ad = client.get_ad("10429595559")

    # Print basic information about the item
    print("URL", ad.url)
    print("Title:", ad.title)
    print("Price:", ad.price)
    print("Brand:", ad.brand)
    print("Description:", ad.description)
    print("Status:", ad.status)
    print("Condition:", ad.condition)

    # Print information about the user who posted the item
    print("User info:", ad.user)


if __name__ == "__main__":
    main()
