"""
DOM inspection script — opens Spotify playlist in a visible browser,
scrolls to the bottom, then prints the HTML of every tracklist-row so
we can identify how recommended tracks differ from real playlist tracks.

Usage: python -m scripts.inspect_dom <playlist_id>
"""

import sys


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.inspect_dom <playlist_id>")
        sys.exit(1)

    playlist_id = sys.argv[1]
    url = f"https://open.spotify.com/playlist/{playlist_id}"

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector('[data-testid="tracklist-row"]', timeout=20000)

        # Scroll to the bottom until stable
        last_bottom_id = None
        stable = 0
        while stable < 4:
            page.evaluate(
                "const r = document.querySelectorAll('[data-testid=\"tracklist-row\"]');"
                "if (r.length) r[r.length - 1].scrollIntoView({block: 'end'});"
            )
            page.wait_for_timeout(1000)
            rows = page.query_selector_all('[data-testid="tracklist-row"]')
            bottom_id = None
            for row in reversed(rows):
                link = row.query_selector('a[href*="/track/"]')
                if link:
                    href = link.get_attribute("href") or ""
                    tid = href.split("/track/")[-1].split("?")[0]
                    if tid:
                        bottom_id = tid
                        break
            stable = stable + 1 if bottom_id == last_bottom_id else 0
            last_bottom_id = bottom_id

        print(f"\n=== Bottom of playlist reached. Visible rows: {len(rows)} ===\n")

        # For each of the last 10 rows, walk up the DOM and print every
        # ancestor's tag + key attributes so we can spot where the
        # recommended section begins.
        rows = page.query_selector_all('[data-testid="tracklist-row"]')
        print(f"Total visible tracklist-row elements: {len(rows)}\n")

        print("--- Ancestor chain for last 10 rows ---\n")
        for i, row in enumerate(rows[-10:], 1):
            track_link = row.query_selector('[data-testid="internal-track-link"]')
            track_name = track_link.inner_text().strip() if track_link else "(no link)"
            ancestors = row.evaluate("""el => {
                const result = [];
                let node = el.parentElement;
                while (node && node !== document.body) {
                    result.push({
                        tag: node.tagName,
                        id: node.id || '',
                        testid: node.getAttribute('data-testid') || '',
                        classes: node.className.slice(0, 80)
                    });
                    node = node.parentElement;
                }
                return result;
            }""")
            print(f"[Row {i}] {track_name}")
            for a in ancestors[:8]:
                print(f"  <{a['tag'].lower()}"
                      + (f" id='{a['id']}'" if a['id'] else "")
                      + (f" data-testid='{a['testid']}'" if a['testid'] else "")
                      + (f" class='{a['classes']}'" if a['classes'] else "")
                      + ">")
            print()

        # Also look for any element containing the word "Recommended" anywhere
        # near the bottom of the page.
        print("--- Elements containing 'Recommended' text ---\n")
        recommended_els = page.evaluate("""() => {
            const all = document.querySelectorAll('*');
            const found = [];
            for (const el of all) {
                if (el.children.length === 0 &&
                    el.textContent.includes('Recommended')) {
                    found.push({
                        tag: el.tagName,
                        testid: el.getAttribute('data-testid') || '',
                        text: el.textContent.slice(0, 100),
                        parentTestid: el.parentElement
                            ? (el.parentElement.getAttribute('data-testid') || '')
                            : ''
                    });
                }
            }
            return found;
        }""")
        if recommended_els:
            for el in recommended_els:
                print(f"  <{el['tag'].lower()} data-testid='{el['testid']}'> \"{el['text']}\" (parent testid: '{el['parentTestid']}')")
        else:
            print("  (none found)")

        browser.close()


if __name__ == "__main__":
    main()
