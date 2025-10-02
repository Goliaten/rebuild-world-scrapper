from multiprocessing import Pool
import os
import time
from typing import List
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from tqdm import tqdm


def get_chapter_urls(driver: webdriver.Chrome, url: str) -> List[str]:
    driver.get(url)
    urls = [
        x.get_attribute("href")
        for x in driver.find_elements(By.CLASS_NAME, "chapter-group__list-item-link")
    ]
    return urls


def get_chapter(driver: webdriver.Chrome, url: str) -> WebElement:
    driver.get(url)
    data = driver.find_elements(By.CLASS_NAME, "chapter__article")
    return data[0]


def parse_save_chapter(data: WebElement, output_dir: str):
    headline_class = "chapter__headline"
    chapter_class = "chapter__content"

    headline: WebElement = data.find_element(By.CLASS_NAME, headline_class)
    title = headline.find_element(By.TAG_NAME, "h1").text
    keep_chars = (" ", ",")
    file_title = "".join(c for c in title if c.isalnum() or c in keep_chars).rstrip()

    if f"{file_title}.md" in os.listdir(output_dir):
        return

    chapter: WebElement = data.find_element(By.CLASS_NAME, chapter_class)

    texts: List[WebElement] = chapter.find_element(
        By.XPATH, "./child::*"
    ).find_elements(By.XPATH, "./child::*")

    texts = [x for x in texts if x.tag_name in ("p", "hr")]

    out = ""
    for text in texts:
        if text.tag_name == "p":
            if not text.text.strip():
                continue
            out += text.text.strip() + "\n\n"

        elif text.tag_name == "hr":
            out += "- - -\n\n"

    with open(os.path.join(output_dir, f"{file_title}.md"), "w") as file:
        file.write(out)


def check_for_new_chapters():
    raise NotImplementedError


def get_driver() -> webdriver.Chrome:
    driver = webdriver.Chrome()
    return driver


def main():
    url = "https://www.divinedaolibrary.com/story/rebuild-world/"
    output_dir = "chapters"
    try:
        os.mkdir(output_dir)
    except:  # noqa: E722
        pass

    driver = get_driver()
    chapter_urls = get_chapter_urls(driver, url)

    for chapter_url in tqdm(chapter_urls):
        chapter = get_chapter(driver, chapter_url)
        parse_save_chapter(chapter, output_dir)


if __name__ == "__main__":
    main()
