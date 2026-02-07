import random
import time

from config import (
    CHECKPOINT_CSV,
    PROGRESS_FILE,
    OUTPUT_XLSX,
)
from storage import (
    append_rows_to_csv,
    load_progress,
    save_progress,
    csv_to_excel,
)
from linkedin_scraper import (
    open_linkedin_with_state,
    scrape_current_page,
    click_next_page,
)


def main():
    # Open browser + LinkedIn search page
    browser, page = open_linkedin_with_state()

    # Load progress to potentially resume
    state = load_progress(PROGRESS_FILE)
    page_index = state.get("page_index", 1)
    next_job_id = state.get("next_job_id", 1)

    print(f"Resuming from page_index={page_index}, next_job_id={next_job_id}")

    # If we previously left off past page 1, fast-forward via Next
    if page_index > 1:
        print(f"Fast-forwarding to page {page_index}...")
        current = 1
        while current < page_index:
            moved = click_next_page(page)
            if not moved:
                print("Could not reach saved page index; stopping.")
                browser.close()
                return
            current += 1
            time.sleep(random.uniform(1.0, 2.0))

    try:
        while True:
            # Scrape current page
            rows, next_job_id = scrape_current_page(page, page_index, next_job_id)

            # Append to CSV after each page (checkpoint)
            if rows:
                append_rows_to_csv(rows, CHECKPOINT_CSV)
                print(
                    f"Appended {len(rows)} rows from page {page_index} "
                    f"to {CHECKPOINT_CSV}"
                )
            else:
                print(f"No rows collected from page {page_index}.")

            # Save progress after each page
            save_progress(
                PROGRESS_FILE,
                {"page_index": page_index, "next_job_id": next_job_id},
            )
            print(f"Saved progress: page_index={page_index}, next_job_id={next_job_id}")

            # Try to go to the next page
            moved = click_next_page(page)
            if not moved:
                print("No more pages. Stopping pagination.")
                break

            page_index += 1

        # Finished all pages we can reach – convert CSV → Excel
        csv_to_excel(CHECKPOINT_CSV, OUTPUT_XLSX)

    finally:
        # Make sure browser closes even if errors happen
        browser.close()
        print("Browser closed.")


if __name__ == "__main__":
    main()
