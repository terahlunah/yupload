"""This module implements uploading videos on YouTube via Selenium using metadata JSON file
	to extract its title, description etc."""

import time

from typing import Optional
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import chromedriver_binary

from .Constant import *
from pathlib import Path
import logging
import platform

logging.basicConfig()


class YouTubeUploader:
    def __init__(self, video_path, title, description, tags=[], not_made_for_kids=True, visibility='private',
                 category=None):
        self.video_path = Path(video_path)
        self.title = title
        self.description = description
        self.tags = tags
        self.not_made_for_kids = not_made_for_kids
        self.visibility = visibility

        userdata_path = Path("userdata").absolute()

        options = webdriver.ChromeOptions()
        #options.add_argument('--disable-web-security')
        #options.add_argument('--allow-running-insecure-content')
        options.add_argument(f'--user-data-dir={userdata_path}')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.browser = webdriver.Chrome(options=options)
        stealth(self.browser,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.is_mac = False
        if not any(os_name in platform.platform() for os_name in ["Windows", "Linux"]):
            self.is_mac = True

    def upload(self):
        try:
            return self.__upload()
        except Exception as e:
            print(e)
            self.__quit()
            raise


    def __write_in_field(self, field, string, select_all=False):
        field.click()
        time.sleep(Constant.USER_WAITING_TIME)
        if select_all:
            if self.is_mac:
                field.send_keys(Keys.COMMAND + 'a')
            else:
                field.send_keys(Keys.CONTROL + 'a')
            time.sleep(Constant.USER_WAITING_TIME)
        field.send_keys(string)

    def __upload(self) -> (bool, Optional[str]):
        self.browser.get(Constant.YOUTUBE_URL)
        time.sleep(Constant.USER_WAITING_TIME)
        self.browser.get(Constant.YOUTUBE_UPLOAD_URL)
        time.sleep(Constant.USER_WAITING_TIME)
        absolute_video_path = str(Path.cwd() / self.video_path)
        self.browser.find_element_by_xpath(Constant.INPUT_FILE_VIDEO).send_keys(
            absolute_video_path)
        self.logger.debug('Attached video {}'.format(self.video_path))

        # if self.thumbnail_path is not None:
        #     absolute_thumbnail_path = str(Path.cwd() / self.thumbnail_path)
        #     self.browser.find_element_by_xpath(Constant.INPUT_FILE_THUMBNAIL).send_keys(
        #         absolute_thumbnail_path)
        #     change_display = "document.getElementById('file-loader').style = 'display: block! important'"
        #     self.browser.driver.execute_script(change_display)
        #     self.logger.debug(
        #         'Attached thumbnail {}'.format(self.thumbnail_path))

        wait = WebDriverWait(self.browser, 15)
        title_field = wait.until(EC.presence_of_element_located((By.ID, Constant.TEXTBOX)))
        self.__write_in_field(
            title_field, self.title, select_all=True)
        self.logger.debug('The video title was set to \"{}\"'.format(
            self.title))

        video_description = self.description
        video_description = video_description.replace("\n", Keys.ENTER)
        if video_description:
            description_field = self.browser.find_elements(By.ID, Constant.TEXTBOX)[1]
            self.__write_in_field(description_field, video_description, select_all=True)
            self.logger.debug('Description filled.')

        if self.not_made_for_kids:
            kids_section = self.browser.find_element(
                By.NAME, Constant.NOT_MADE_FOR_KIDS_LABEL)
            kids_section.find_element_by_id(Constant.RADIO_LABEL).click()
            self.logger.debug('Selected \"{}\"'.format(
                Constant.NOT_MADE_FOR_KIDS_LABEL))

        # Advanced options
        self.browser.find_element_by_xpath(Constant.MORE_BUTTON).click()
        self.logger.debug('Clicked MORE OPTIONS')

        tags_container = self.browser.find_element(By.XPATH,
                                                   Constant.TAGS_INPUT_CONTAINER)
        tags_field = tags_container.find_element_by_id(Constant.TAGS_INPUT)
        self.__write_in_field(tags_field, ','.join(
            self.tags))
        self.logger.debug(
            'The tags were set to \"{}\"'.format(self.tags))

        self.browser.find_element_by_id(Constant.NEXT_BUTTON).click()
        self.logger.debug('Clicked {} one'.format(Constant.NEXT_BUTTON))

        self.browser.find_element_by_id(Constant.NEXT_BUTTON).click()
        self.logger.debug('Clicked {} two'.format(Constant.NEXT_BUTTON))

        self.browser.find_element_by_id(Constant.NEXT_BUTTON).click()
        self.logger.debug('Clicked {} three'.format(Constant.NEXT_BUTTON))
        visibility_main_button = self.browser.find_element(By.NAME, Constant.UNLISTED_BUTTON)
        visibility_main_button.find_element_by_id(Constant.RADIO_LABEL).click()
        self.logger.debug('Made the video {}'.format(Constant.UNLISTED_BUTTON))

        video_id = self.__get_video_id()

        status_container = self.browser.find_element(By.XPATH, Constant.STATUS_CONTAINER)
        # while True:
        #     in_process = status_container.text.find_element(Constant.UPLOADED) != -1
        #     if in_process:
        #         time.sleep(Constant.USER_WAITING_TIME)
        #     else:
        #         break

        done_button = self.browser.find_element_by_id(Constant.DONE_BUTTON)

        # Catch such error as
        # "File is a duplicate of a video you have already uploaded"
        if done_button.get_attribute('aria-disabled') == 'true':
            error_message = self.browser.find_element(By.XPATH,
                                                      Constant.ERROR_CONTAINER).text
            self.logger.error(error_message)
            return False, None

        done_button.click()
        self.logger.debug(
            "Published the video with video_id = {}".format(video_id))
        time.sleep(Constant.USER_WAITING_TIME)
        self.browser.get(Constant.YOUTUBE_URL)
        self.__quit()
        return True, video_id

    def __get_video_id(self) -> Optional[str]:
        video_id = None
        try:
            video_url_container = self.browser.find_element(
                By.XPATH, Constant.VIDEO_URL_CONTAINER)
            video_url_element = video_url_container.find_element_by_xpath(Constant.VIDEO_URL_ELEMENT)
            video_id = video_url_element.get_attribute(
                Constant.HREF).split('/')[-1]
        except:
            self.logger.warning(Constant.VIDEO_NOT_FOUND_ERROR)
            pass
        return video_id

    def __quit(self):
        self.browser.quit()
