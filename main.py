from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os
import random


LINKEDIN_SEARCH_URL = "https://www.linkedin.com/jobs/search-results/?currentJobId=4368813592&eBP=BUDGET_EXHAUSTED_JOB&refId=jmJG1T2O7zwPmMz3ZAWf1Q%3D%3D&trackingId=YxElsTu3MGEaHKU9CrDALw%3D%3D&keywords=junior%20data%20engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&referralSearchId=1NXyDbgYKlOB4LC5SF%2BytQ%3D%3D&f_TPR=r86400"  # your filtered search
OUTPUT_FILE = "linkedin_jobs_raw.xlsx"
STATE_FILE = "linkedin_state.json"


def job_mentions_no_sponsorship(text: str) -> bool:
    """Return True if the description clearly says they do NOT sponsor."""
    t = text.lower()

    # “no sponsorship” style phrases
    if "sponsor" in t or "sponsorship" in t:
        if any(
            phrase in t
            for phrase in [
                "no sponsorship",
                "does not provide sponsorship",
                "cannot sponsor",
                "unable to sponsor",
                "will not sponsor",
            ]
        ):
            return True

    # “citizens/GC only” hints
    if any(
        phrase in t
        for phrase in [
            "us citizens only",
            "must be a us citizen",
            "only us citizens",
            "green card holders only",
            "permanent resident only",
        ]
    ):
        return True

    return False


def main():
    # 1. Make sure we already saved login state
    if not os.path.exists(STATE_FILE):
        raise RuntimeError(
            f"{STATE_FILE} not found. Run save_state.py first to log in and save your LinkedIn session."
        )

    rows = []

    with sync_playwright() as p:
        # 2. Launch browser
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])

        # 3. Use saved session (THIS is the key change)
        context = browser.new_context(
            storage_state=STATE_FILE, viewport={"width": 1600, "height": 900}
        )

        page = context.new_page()

        # 4. Go straight to your pre-filtered LinkedIn job search
        page.goto(LINKEDIN_SEARCH_URL)
        page.wait_for_timeout(5000)

        # 5. Get all job cards on the left side (selector may need tweaking in future)
        job_cards = page.query_selector_all('div[data-view-name="job-search-job-card"]')
        print(f"Found {len(job_cards)} job cards")

        job_id = 1

        for idx, card in enumerate(job_cards, start=1):
            try:
                # Click the job card button to load details on the right
                button = card.query_selector('div[role="button"]') or card
                button.scroll_into_view_if_needed()
                button.click()
                # Wait for the right-side job details panel to load
                try:
                    page.wait_for_selector(
                        'section[data-view-name="job-details"]',
                        timeout=10000,
                    )
                except Exception:
                    # Fallback: small fixed wait if selector never appears
                    page.wait_for_timeout(5000)

                # ---- TITLE & COMPANY FROM THE LEFT-SIDE CARD ----
                p_tags = card.query_selector_all("p")

                # Optional debug for the first card
                if idx == 1:
                    print(f"DEBUG: p_tags in first card = {len(p_tags)}")
                    for i, p in enumerate(p_tags[:5]):
                        print(f"DEBUG p[{i}]:", p.inner_text()[:120])

                title_el = p_tags[0] if len(p_tags) > 0 else None
                company_el = p_tags[1] if len(p_tags) > 1 else None
                # Location is often the 3rd p; keep if you want it
                # location_el = p_tags[2] if len(p_tags) > 2 else None

                title = title_el.inner_text().strip() if title_el else "Unknown title"
                company = (
                    company_el.inner_text().strip() if company_el else "Unknown company"
                )
                # location = location_el.inner_text().strip() if location_el else ""

                # ---- DESCRIPTION FROM THE RIGHT-SIDE DETAIL PANEL ----
                description = ""
                try:
                    # Wait for any description container to exist
                    page.wait_for_selector(
                        'span[data-testid="expandable-text-box"], '
                        'div[data-view-name="job-details-description"] .show-more-less-html__markup, '
                        "div.show-more-less-html__markup",
                        timeout=10000,
                    )

                    # First, grab whatever text is already visible (even if not fully expanded)
                    desc_span = page.query_selector(
                        'span[data-testid="expandable-text-box"]'
                    )
                    if desc_span:
                        description = desc_span.inner_text().strip()
                    else:
                        desc_el = page.query_selector(
                            'div[data-view-name="job-details-description"] .show-more-less-html__markup'
                        ) or page.query_selector("div.show-more-less-html__markup")
                        if desc_el:
                            description = desc_el.inner_text().strip()

                    # Then try to click "... more" ONCE to expand, but with a small timeout and no endless retries
                    more_btn = page.query_selector(
                        'button[data-testid="expandable-text-button"]'
                    )
                    if more_btn:
                        try:
                            more_btn.scroll_into_view_if_needed()
                            more_btn.click(timeout=3000, force=True)
                            # Give the DOM a moment to expand
                            page.wait_for_timeout(random.randint(2000, 4000))

                            # Re-read description after expand (if present)
                            expanded_span = page.query_selector(
                                'span[data-testid="expandable-text-box"]'
                            )
                            if expanded_span:
                                description = expanded_span.inner_text().strip()
                            elif desc_el := page.query_selector(
                                'div[data-view-name="job-details-description"] .show-more-less-html__markup'
                            ) or page.query_selector("div.show-more-less-html__markup"):
                                description = desc_el.inner_text().strip()
                        except Exception as click_err:
                            print(
                                "  -> Couldn't reliably click '... more'; using visible description only.",
                                click_err,
                            )
                except Exception as e:
                    print(f"  -> Could not extract description: {e}")
                    description = ""

                # Extract canonical job URL
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

                # Sponsorship filter
                if job_mentions_no_sponsorship(description):
                    print("  -> Mentions no sponsorship / citizens-only. Skipping.")
                    continue

                # Save this job
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

                # Small delay to look human
                time.sleep(random.uniform(1.6, 3.4))

            except Exception as e:
                print(f"Error on job {idx}: {e}")
                continue

        browser.close()

    if rows:
        df = pd.DataFrame(rows)
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"Saved {len(rows)} jobs to {OUTPUT_FILE}")
    else:
        print("No jobs passed the filter.")


if __name__ == "__main__":
    main()
