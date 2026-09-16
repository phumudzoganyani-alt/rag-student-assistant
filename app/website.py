import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


START_URLS = [
    "https://www.zaio.io/",
    "https://www.zaio.io/bootcamps",
    "https://www.zaio.io/fullstack-bootcamp",
]


def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        element.decompose()

    text = soup.get_text(separator=" ", strip=True)

    return " ".join(text.split())


async def fetch_page(browser, url):
    print(f"Crawling: {url}")

    page = await browser.new_page()

    try:
        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        html = await page.content()
        text = clean_text(html)

        return {
            "text": text,
            "url": url
        }

    except Exception as error:
        print(f"Error crawling {url}: {error}")
        return None

    finally:
        await page.close()


async def crawl_zaio():
    pages = []

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(
            headless=True
        )

        for url in START_URLS:

            result = await fetch_page(browser, url)

            if result and result["text"]:
                pages.append(result)

        await browser.close()

    return pages


def get_website_pages():
    return asyncio.run(crawl_zaio())


if __name__ == "__main__":

    print("Starting ZAIO website crawler...")

    pages = get_website_pages()

    print()
    print(f"Crawled {len(pages)} pages.")

    for page in pages:
        print()
        print(f"URL: {page['url']}")
        print(f"Characters: {len(page['text'])}")
        print(f"Preview: {page['text'][:300]}...")
 