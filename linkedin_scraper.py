import os
import random
import time
from typing import List, Dict, Tuple

from playwright.sync_api import sync_playwright, Page, Browser

from config import (
    LINKEDIN_SEARCH_URL,
    STATE_FILE,
    VIEWPORT,
    HEADLESS,
)
from parsers import (
    extract_title_company_from_card,
    extract_description_from_page,
    job_mentions_no_sponsorship,
)


def open_linkedin_with_state() -> Tuple[Browser, Page]:
    """Launch Chromium with saved LinkedIn session and navigate to search URL."""
    if not os.path.exists(STATE_FILE):
        raise RuntimeError(
            f"{STATE_FILE} not found. Run save_state.py first to log in and save your LinkedIn session."
        )

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=HEADLESS, args=["--start-maximized"])

    context = browser.new_context(storage_state=STATE_FILE, viewport=VIEWPORT)
    page = context.new_page()

    page.goto(LINKEDIN_SEARCH_URL)
    page.wait_for_timeout(5000)  # initial load buffer

    return browser, page


def scrape_current_page(
    page: Page, page_index: int, start_job_id: int
) -> Tuple[List[Dict], int]:
    """
    Scrape the current LinkedIn search results page.

    Returns:
        (rows, next_job_id)
    """
    print(f"\n=== Scraping page {page_index} ===")
    rows: List[Dict] = []
    job_id = start_job_id

    # Get all job cards on the left
    job_cards = page.query_selector_all('div[data-view-name="job-search-job-card"]')
    print(f"Found {len(job_cards)} job cards on page {page_index}")

    for idx, card in enumerate(job_cards, start=1):
        try:
            # Click the card to load the details on the right
            button = card.query_selector('div[role="button"]') or card
            button.scroll_into_view_if_needed()
            button.click()

            # Wait for the right-side job details panel
            try:
                page.wait_for_selector(
                    'section[data-view-name="job-details"]',
                    timeout=10000,
                )
            except Exception:
                page.wait_for_timeout(5000)  # fallback

            # Title & company from left-side card
            title, company = extract_title_company_from_card(card, idx)

            # Description from right-side detail pane
            description = extract_description_from_page(page)

            # Canonical link (or current URL fallback)
            link_el = page.query_selector('link[rel="canonical"]')
            link = (
                link_el.get_attribute("href")
                if link_el and link_el.get_attribute("href")
                else page.url
            )

            print(f"[{idx}] {title} at {company}")

            if not description:
                print("  -> No description, skipping.")
                continue

            if "intern" in title.lower():
                print("  -> Mentions intern. Skipping.")
                continue

            if job_mentions_no_sponsorship(description):
                print("  -> Mentions no sponsorship / citizens-only. Skipping.")
                continue

            rows.append(
                {
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "link": link,
                    "description": description,
                }
            )
            job_id += 1

            # Human-ish delay
            time.sleep(random.uniform(1.6, 3.4))

        except Exception as e:
            print(f"Error on job card {idx} on page {page_index}: {e}")
            continue

    return rows, job_id


def click_next_page(page: Page) -> bool:
    """
    Click the 'Next' button in LinkedIn pagination.

    Returns:
        True if we successfully clicked to a next page,
        False if there is no next page.
    """
    try:
        next_button = page.query_selector(
            'button[data-testid="pagination-controls-next-button-visible"]'
        )
        if not next_button:
            print("No 'Next' button found. Probably last page.")
            return False

        # We can check for disabled state if needed (aria-disabled, etc.)
        # For now, try clicking and rely on absence as termination.
        next_button.scroll_into_view_if_needed()
        next_button.click()

        # Wait a bit for new results to load
        page.wait_for_timeout(random.randint(3000, 5000))

        return True

    except Exception as e:
        print(f"Error while trying to click 'Next': {e}")
        return False
