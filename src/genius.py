import logging
import re
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


def get_lyrics(track_name: str, artist_name: str) -> str | None:
    """Scrape lyrics from Genius using a headless browser, or None if not found."""
    query = quote_plus(f"{track_name} {artist_name}")
    search_url = f"https://genius.com/search?q={query}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()

            page.goto(search_url, timeout=15000)

            # Find the first link ending in -lyrics (Genius lyrics URL pattern)
            lyrics_url = page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                const hit = links.find(a =>
                    a.href.includes('genius.com') && a.href.endsWith('-lyrics')
                );
                return hit ? hit.href : null;
            }""")

            if not lyrics_url:
                # Wait a bit for JS-rendered results and retry once
                page.wait_for_timeout(3000)
                lyrics_url = page.evaluate("""() => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    const hit = links.find(a =>
                        a.href.includes('genius.com') && a.href.endsWith('-lyrics')
                    );
                    return hit ? hit.href : null;
                }""")

            if not lyrics_url:
                logger.info("No Genius results for '%s' by '%s'.", track_name, artist_name)
                return None

            logger.info("Fetching lyrics from %s", lyrics_url)
            page.goto(lyrics_url, timeout=15000)
            page.wait_for_selector('[data-lyrics-container="true"]', timeout=10000)

            containers = page.query_selector_all('[data-lyrics-container="true"]')
            if not containers:
                logger.warning("No lyrics containers found on Genius page: %s", lyrics_url)
                return None

            lines = [container.inner_text() for container in containers]
            lyrics = "\n".join(lines).strip()
            lyrics = re.sub(r"\n{3,}", "\n\n", lyrics)

            return lyrics if lyrics else None

        except Exception:
            logger.warning("Genius scraping failed for '%s'.", track_name, exc_info=True)
            return None
        finally:
            browser.close()
