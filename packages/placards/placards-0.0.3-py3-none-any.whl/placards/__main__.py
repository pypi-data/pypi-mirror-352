import os
import logging
import asyncio

from pyppeteer import launch

from placards import config
from placards.errors import ConfigError


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
SERVER_URL = 'http://localhost:8000/'

CHROME_USER_DATA = os.getenv('CHROME_USER_DATA', '/tmp')


async def chrome():
    browser = await launch(
        headless=False,
        args=[
            # '--no-sandbox',
            '--start-maximized',
            '--start-fullscreen',
            '--no-default-browser-check',
        ],
        ignoreDefaultArgs=["--enable-automation"],
        # dumpio=True,
        executablePath='/usr/bin/google-chrome',
        userDataDir=CHROME_USER_DATA,
        defaultViewport=None,
        autoClose=False,
    )
    pages = await browser.pages()
    if len(pages):
        page = pages[0]
    else:
        page = await browser.newPage()
    return browser, page


async def goto(page, url):
    page.setDefaultNavigationTimeout(0)
    await page.goto(url, waitUntil='networkidle2')
    # await page.keyboard.press('F11')
    await page.screenshot({
        'type': 'png',
    })


async def main():
    LOGGER.debug('Loading web client...')

    try:
        url = config.SERVER_URL

    except ConfigError:
        LOGGER.error('You must configure SERVER_URL in placard.ini!')
        return

    browser, page = await chrome()
    await goto(page, url)

    while not page.isClosed():
        await asyncio.sleep(0.1)

    await browser.close()


asyncio.run(main())
