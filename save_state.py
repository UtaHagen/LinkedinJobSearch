from playwright.sync_api import sync_playwright

STATE_FILE = "linkedin_state.json"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Go to LinkedIn login
        page.goto("https://www.linkedin.com/login")

        print(">>> Log in to LinkedIn in this window.")
        print(">>> After you see your feed or jobs page, press Enter in the terminal.")
        input("Press Enter here AFTER you finish logging in...")

        # Save cookies + local storage
        context.storage_state(path=STATE_FILE)
        print(f"Saved login state to {STATE_FILE}")

        browser.close()


if __name__ == "__main__":
    main()
