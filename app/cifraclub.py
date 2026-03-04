"""CifraClub Module - Optimized for speed"""

import os
import logging
from functools import lru_cache
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException

logger = logging.getLogger(__name__)

CIFRACLUB_URL = "https://www.cifraclub.com.br/"
SELENIUM_URL = os.getenv("SELENIUM_URL", "http://selenium:4444/wd/hub")

# --- Driver Singleton ---
# We keep a single WebDriver connection alive for ALL requests.
# This eliminates the overhead of creating a new browser session (~2-5 seconds) per request.
_driver = None

def _get_driver():
    """Returns the shared WebDriver, creating it if needed."""
    global _driver
    try:
        # Quick sanity check — if driver died, this will raise
        if _driver is not None:
            _driver.title  # will throw if session is dead
        if _driver is None:
            raise WebDriverException("No driver yet")
    except WebDriverException:
        logger.info("Creating new Selenium driver session...")
        _driver = webdriver.Remote(SELENIUM_URL, DesiredCapabilities.FIREFOX)
        _driver.implicitly_wait(5)
    return _driver

# --- In-Memory Cache ---
# Stores scraping results keyed by (artist, song).
# Avoids re-scraping the same song on subsequent requests.
_cache: dict = {}

def _get_cache_key(artist: str, song: str) -> str:
    return f"{artist.lower()}::{song.lower()}"


class CifraClub:
    """CifraClub scraper — reuses a shared Selenium driver and caches results."""

    def cifra(self, artist: str, song: str) -> dict:
        """Lê a página HTML e extrai a cifra e meta dados da música."""
        key = _get_cache_key(artist, song)

        # Return cached result immediately if available
        if key in _cache:
            logger.info(f"Cache HIT for {artist}/{song}")
            return _cache[key]

        logger.info(f"Cache MISS for {artist}/{song} — scraping...")
        url = CIFRACLUB_URL + artist + "/" + song
        result = {'cifraclub_url': url}

        driver = _get_driver()
        try:
            driver.get(url)
            self._get_details(driver, result)
            self._get_cifra(driver, result)
        except Exception as e:
            # Invalidate the driver so next request gets a fresh one
            global _driver
            try:
                driver.quit()
            except Exception:
                pass
            _driver = None
            raise ValueError(f"Failed to extract cifra from {url}: {str(e)}")

        _cache[key] = result
        return result

    def _get_details(self, driver, result):
        """Obtêm os meta dados da música"""
        content = driver.find_element(By.CLASS_NAME, 'cifra').get_attribute('outerHTML')
        soup = BeautifulSoup(content, 'html.parser')
        result['name'] = soup.find('h1', class_='t1').text
        result['artist'] = soup.find('h2', class_='t3').text

        img_tag = soup.find('div', class_='player-placeholder')
        if img_tag and img_tag.img:
            cod = img_tag.img['src'].split('/vi/')[1].split('/')[0]
            result['youtube_url'] = f"https://www.youtube.com/watch?v={cod}"

    def _get_cifra(self, driver, result):
        """Obtêm a cifra da música e converte para json"""
        content = driver.find_element(By.CLASS_NAME, 'cifra_cnt').get_attribute('outerHTML')
        soup = BeautifulSoup(content, 'html.parser')
        result['cifra'] = soup.find('pre').text.split('\n')

