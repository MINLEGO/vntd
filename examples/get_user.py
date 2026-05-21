"""Get detailed information about a Vinted user using their user ID."""

import vntd


def main() -> None:
    # Initialize the Vinted API client
    client = vntd.Client()

    # Fetch a user by their Vinted user ID
    # Replace the ID with a real one for testing
    user = client.get_user(80325437)

    # Print user attributes
    print("User ID:", user.id)
    print("Login:", user.login)
    print("Business account:", user.business)
    print("Items count:", user.item_count)


if __name__ == "__main__":
    main()
