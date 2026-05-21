"""Search for business sellers on Vinted."""

import vntd


def main() -> None:
    # Initialize the Vinted API client
    client = vntd.Client()

    # Perform a search with specific filters
    result = client.search(
        text="robe",
        page=1,
        limit=24,
        sort=vntd.Sort.NEWEST,
        seller_type=vntd.SellerType.BUSINESS,
        price=(5, 50),
    )

    # Display business seller stats
    for ad in result.ads:
        user = ad.user
        if user and user.business:
            print(
                f"Seller: {user.login} | "
                f"Feedback: {user.feedback_score} | "
                f"Items: {user.item_count}"
            )


if __name__ == "__main__":
    main()
