"""Search for business sellers on Vinted.

Demonstrates the two-tier access pattern for user data:
- ad.user: cached partial user info from search (no extra HTTP requests)
- client.get_user(id): full user profile with advanced fields (explicit HTTP call)
"""

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
        seller_type=vntd.SellerType.ALL,
        price=(5, 50),
    )

    # Basic user info from search — no extra HTTP requests
    for ad in result.ads[:5]:
        user = ad.user
        if user:
            print(
                f"Seller: {user.login} | "
                f"Profile: {user.profile_url} | "
                f"Photo: {user.photo_url} | "
                f"Business: {user.business}"
            )

    # Full user data via client.get_user() — explicit and intentional
    if result.ads:
        ad = result.ads[0]
        if ad.user:
            full_user = client.get_user(ad.user.id)
            print(f"\n--- Full profile for {full_user.login} ---")
            print(f"Feedback score: {full_user.feedback_score}")
            print(f"Items listed: {full_user.item_count}")
            print(f"Followers: {full_user.followers_count}")


if __name__ == "__main__":
    main()
