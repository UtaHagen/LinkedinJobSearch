from playwright.sync_api import Page, ElementHandle
import random


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


def extract_title_company_from_card(card: ElementHandle, idx: int) -> tuple[str, str]:
    """
    Extract title and company from the LEFT-SIDE job card.

    Based on the behavior you observed:
      p[0] = title
      p[1] = company
      p[2] = location (if you want it later)
    """
    p_tags = card.query_selector_all("p")

    # Optional debug on the first card
    if idx == 1:
        print(f"DEBUG: p_tags in first card = {len(p_tags)}")
        for i, p in enumerate(p_tags[:5]):
            try:
                print(f"DEBUG p[{i}]:", p.inner_text()[:120])
            except Exception:
                print(f"DEBUG p[{i}]: <error reading text>")

    title_el = p_tags[0] if len(p_tags) > 0 else None
    company_el = p_tags[1] if len(p_tags) > 1 else None

    title = title_el.inner_text().strip() if title_el else "Unknown title"
    company = company_el.inner_text().strip() if company_el else "Unknown company"

    return title, company


def extract_description_from_page(page: Page) -> str:
    """
    Extract the job description from the RIGHT-SIDE detail panel.

    Strategy:
    1. Wait for any plausible description container.
    2. Read visible text first.
    3. Try clicking '... more' ONCE, wait a bit, then reread.
    4. If the click fails, fall back to whatever text we had.
    """
    description = ""

    try:
        # Wait for any likely description container
        page.wait_for_selector(
            'span[data-testid="expandable-text-box"], '
            'div[data-view-name="job-details-description"] .show-more-less-html__markup, '
            "div.show-more-less-html__markup",
            timeout=10000,
        )

        # First, capture whatever is visible
        desc_span = page.query_selector('span[data-testid="expandable-text-box"]')
        if desc_span:
            description = desc_span.inner_text().strip()
        else:
            desc_el = page.query_selector(
                'div[data-view-name="job-details-description"] .show-more-less-html__markup'
            ) or page.query_selector("div.show-more-less-html__markup")
            if desc_el:
                description = desc_el.inner_text().strip()

        # Try to click "... more" once
        more_btn = page.query_selector('button[data-testid="expandable-text-button"]')
        if more_btn:
            try:
                more_btn.scroll_into_view_if_needed()
                more_btn.click(timeout=3000, force=True)

                # Small wait to let expansion settle (helps overlapping text issues)
                page.wait_for_timeout(random.randint(2000, 4000))

                # Re-read after expansion
                expanded_span = page.query_selector(
                    'span[data-testid="expandable-text-box"]'
                )
                if expanded_span:
                    description = expanded_span.inner_text().strip()
                else:
                    desc_el = page.query_selector(
                        'div[data-view-name="job-details-description"] .show-more-less-html__markup'
                    ) or page.query_selector("div.show-more-less-html__markup")
                    if desc_el:
                        description = desc_el.inner_text().strip()

            except Exception as click_err:
                print(
                    "  -> Couldn't reliably click '... more'; using visible description only.",
                    click_err,
                )

    except Exception as e:
        print(f"  -> Could not extract description: {e}")
        description = ""

    return description
