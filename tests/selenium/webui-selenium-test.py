#!/usr/bin/env python

# -*- coding: utf-8 -*-

# selenium.common.exceptions.ElementNotInteractableException: requires >= selenium-3.4.0

import logging, os, re, sys, unittest
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from time import sleep



class WebuiSeleniumTest(unittest.TestCase):

    browser = 'firefox'
    base_url = "http://127.0.0.1/bareos-webui"
    username = "admin"
    password = "secret"
    client = 'bareos-fd'
    restorefile = '/usr/sbin/bconsole'
    # slow down test for debugging
    sleeptime = 0.0
    # max seconds to wait for an element
    maxwait = 10
    # time to wait before trying again
    waittime = 0.1

    def setUp(self):
        self.logger = logging.getLogger()

        if self.browser == "chrome":
            #d = DesiredCapabilities.CHROME
            #d['loggingPrefs'] = { 'browser':'ALL' }
            self.driver = webdriver.Chrome('/usr/local/lib/chromium-browser/chromedriver')
        if self.browser == "firefox":
            d = DesiredCapabilities.FIREFOX
            d['loggingPrefs'] = { 'browser':'ALL' }
            fp = webdriver.FirefoxProfile()
            fp.set_preference('webdriver.log.file', os.getcwd() + '/firefox_console.log')
            self.driver = webdriver.Firefox(capabilities=d, firefox_profile=fp)

        # take base url, but remove last /
        self.base_url = base_url.rstrip('/')

        self.verificationErrors = []
        self.accept_next_alert = True



    def test_login(self):
        self.login()
        self.logout()



    def test_menue(self):
        driver = self.driver

        self.driver.get(self.base_url + "/")

        self.login()
        self.wait_for_url_and_click('/director/')
        self.wait_for_url_and_click("/schedule/")
        self.wait_for_url_and_click("/schedule/status/")
        self.wait_for_url_and_click("/storage/")
        self.wait_for_url_and_click("/client/")
        self.wait_for_url_and_click("/restore/")
        self.logout()



    def test_restore(self):

        # LOGGING IN:
        self.login()

        # CHANGING TO RESTORE TAB:
        self.wait_for_url_and_click("/restore/")
        
        # SELECTING CLIENT:
        # Selects the correct client
        self.wait_and_click(By.XPATH, "(//button[@data-id='client'])")
        self.wait_and_click(By.LINK_TEXT, self.client)
        
        # FILE-SELECTION:
        # Clicks on file and navigates through the tree
        # by using the arrow-keys.
        pathlist = self.restorefile.split('/')
        for i in pathlist[:-1]:
            self.wait_for_element(By.XPATH, "//a[contains(text(),'%s/')]" % i).send_keys(Keys.ARROW_RIGHT)
        self.wait_for_element(By.XPATH, "//a[contains(text(),'%s')]" % pathlist[-1]).click()

        # CONFIRMATION:
        # Clicks on 'submit'
        self.wait_and_click(By.XPATH, "//input[@id='submit']")
        # Confirms alert that has text "Are you sure ?"
        self.assertRegexpMatches(self.close_alert_and_get_its_text(), r"^Are you sure[\s\S]$")

        # TODO: next modal, job run message

        # LOGOUT:
        self.logout()


    def login(self):
        driver = self.driver

        driver.get(self.base_url + "/auth/login")
        Select(driver.find_element_by_name("director")).select_by_visible_text("localhost-dir")

        driver.find_element_by_name("consolename").clear()
        driver.find_element_by_name("consolename").send_keys(self.username)
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys(self.password)
        driver.find_element_by_xpath("(//button[@type='button'])[2]").click()
        driver.find_element_by_link_text("English").click()
        driver.find_element_by_xpath("//input[@id='submit']").click()
        while ("/dashboard/" not in self.driver.current_url):
            sleep(self.waittime)

    def logout(self):
        # TODO:
        # dismiss modals. Occurs when client with no jobs is selected first.
        #try:
            #self.logger.info("closing modal")
            ##self.driver.switch_to_alert().dismiss()
            #self.close_alert_and_get_its_text()
            #time.sleep(t+5)
        #except NoAlertPresentException:
            #self.logger.info("skipped closing alert: none present")
        self.wait_and_click(By.CSS_SELECTOR, "a.dropdown-toggle")
        self.wait_and_click(By.LINK_TEXT, "Logout")
        sleep(self.sleeptime)



    def wait_for_url(self, what):
        value="//a[contains(@href, '%s')]" % what
        return self.wait_for_element(By.XPATH, value)


        
    def wait_for_element(self, by, value, starttime = None):
        logger = logging.getLogger()
        element = None
        if starttime is None:
             starttime = datetime.now()
        seconds = (datetime.now() - starttime).total_seconds()
        logger.info("waiting for %s %s (%ds)", by, value, seconds)
        while (seconds < self.maxwait) and (element is None):
            try:
                tmp_element = self.driver.find_element(by, value)
                if tmp_element.is_displayed():
                    element = tmp_element
            except ElementNotInteractableException:
                sleep(self.waittime)
                logger.info("%s %s not interactable", by, value)
            except NoSuchElementException:
                sleep(self.waittime)
                logger.info("%s %s not existing", by, value)
            except ElementNotVisibleException:
                sleep(self.waittime)
                logger.info("%s %s not visible", by, value)
            seconds = (datetime.now() - starttime).total_seconds()
        if element:
            logger.info("%s %s loaded after %ss." % (by, value, seconds))
            sleep(self.sleeptime)
        else:
            logger.warning("Timeout while loading %s %s (%d s)", by, value, seconds)
        return element


    def wait_for_url_and_click(self, what):
        value="//a[contains(@href, '%s')]" % what
        return self.wait_and_click(By.XPATH, value)


    def wait_and_click(self, by, value):
        logger = logging.getLogger()
        element = None
        starttime = datetime.now()
        seconds = 0.0
        while (datetime.now() - starttime).total_seconds() < self.maxwait:
            logging.info("waiting for %s %s (%ss)", by, value, seconds)
            element = self.wait_for_element(by, value, starttime)
            try:
                element.click()
            except WebDriverException:
                sleep(self.waittime)
                logger.info("WebDriverException while clicking %s %s", by, value)
            else:
                return element
            seconds = (datetime.now() - starttime).total_seconds()
        logger.error("failed to click %s %s", by, value)
        return


    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True



    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        except NoAlertPresentException:
            pass
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
        


if __name__ == "__main__":
    # Configure the logger, for information about the timings set it to INFO
    # Selenium driver itself will write additional debug messages when set to DEBUG
    #logging.basicConfig(filename='webui-selenium-test.log', level=logging.DEBUG)
    #logging.basicConfig(filename='webui-selenium-test.log', level=logging.INFO)
    logging.basicConfig(filename='webui-selenium-test.log', format='%(levelname)s %(module)s.%(funcName)s: %(message)s', level=logging.INFO)
    logger = logging.getLogger()

    # Get attributes as environment variables,
    # if not available or set use defaults.
    browser = os.environ.get('BAREOS_BROWSER')
    if browser:
        WebuiSeleniumTest.browser = browser

    base_url = os.environ.get('BAREOS_BASE_URL')
    if base_url:
        WebuiSeleniumTest.base_url = base_url.rstrip('/')

    username = os.environ.get('BAREOS_USERNAME')
    if username:
        WebuiSeleniumTest.username = username

    password = os.environ.get('BAREOS_PASSWORD')
    if password:
        WebuiSeleniumTest.password = password

    client = os.environ.get('BAREOS_CLIENT')
    if client:
        WebuiSeleniumTest.client = client

    restorefile = os.environ.get('BAREOS_RESTOREFILE')
    if restorefile:
        WebuiSeleniumTest.restorefile = restorefile

    sleeptime = os.environ.get('BAREOS_DELAY')
    if sleeptime:
        WebuiSeleniumTest.sleeptime = float(sleeptime)

    unittest.main()
