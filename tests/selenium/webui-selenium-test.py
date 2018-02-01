#!/usr/bin/env python

# -*- coding: utf-8 -*-

# selenium.common.exceptions.ElementNotInteractableException: requires >= selenium-3.4.0

import logging, os, re, sys, unittest
from   datetime import datetime, timedelta
from   selenium import webdriver
from   selenium.common.exceptions import *
       #WebDriverException, ElementNotInteractableException, ElementNotVisibleException, TimeoutException, NoAlertPresentException, NoSuchElementException
from   selenium.webdriver.common.by import By
from   selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from   selenium.webdriver.common.keys import Keys
from   selenium.webdriver.support import expected_conditions as EC
from   selenium.webdriver.support.ui import Select, WebDriverWait
import selenium.webdriver.support.ui as ui
#from selenium.webdriver.remote.remote_connection import LOGGER
from   time import sleep



class WebuiSeleniumTest(unittest.TestCase):

    browser = 'firefox'
    base_url = "http://127.0.0.1/bareos-webui"
    username = "admin"
    password = "secret"
    client = 'bareos-fd'
    restorefile = '/usr/sbin/bconsole'
    # path to store logging files
    logpath = os.getcwd()
    # slow down test for debugging
    sleeptime = 0.0
    # max seconds to wait for an element
    maxwait = 10
    # time to wait before trying again
    waittime = 0.1


    def setUp(self):
        # Configure the logger, for information about the timings set it to INFO
        # Selenium driver itself will write additional debug messages when set to DEBUG
        #logging.basicConfig(filename='webui-selenium-test.log', level=logging.DEBUG)
        #logging.basicConfig(filename='webui-selenium-test.log', level=logging.INFO)
        logging.basicConfig(
                filename='%s/webui-selenium-test.log' % (self.logpath),
                format='%(levelname)s %(module)s.%(funcName)s: %(message)s',
                level=logging.INFO
        )
        self.logger = logging.getLogger()
        
        self.logger.info("======================= Testing %(levelname)s %(funcName)s =======================")

        if self.browser == "chrome":
            # This might be another path, especially when on OS X.
            self.driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
        if self.browser == "firefox":
            d = DesiredCapabilities.FIREFOX
            d['loggingPrefs'] = { 'browser':'ALL' }
            fp = webdriver.FirefoxProfile()
            fp.set_preference('webdriver.log.file', self.logpath + '/firefox_console.log')
            self.driver = webdriver.Firefox(capabilities=d, firefox_profile=fp)

        self.driver.implicitly_wait(1)

        # used as timeout for selenium.webdriver.support.expected_conditions (EC)
        self.wait = WebDriverWait(self.driver, self.maxwait)

        # take base url, but remove last /
        self.base_url = base_url.rstrip('/')

        self.verificationErrors = []

    def test_login(self):
        self.login()
        self.logout()

    def test_menue(self):
        driver = self.driver

        self.driver.get(self.base_url + "/")

        self.login()
        self.wait_for_url_and_click("/director/")
        self.wait_for_url_and_click("/schedule/")
        self.wait_for_url_and_click("/schedule/status/")
        self.wait_for_url_and_click("/storage/")
        self.wait_for_url_and_click("/client/")
        self.wait_for_url_and_click("/restore/")
        self.wait_and_click(By.XPATH, "//a[contains(@href, '/dashboard/')]", By.XPATH, "//div[@id='modal-001']//button[.='Close']")
        self.logout()

    def test_restore(self):

        # LOGGING IN:
        self.login()

        # CHANGING TO RESTORE TAB:
        self.wait_for_url_and_click("/restore/")
        self.wait_and_click(By.XPATH, "(//button[@data-id='client'])", By.XPATH, "//div[@id='modal-001']//button[.='Close']")
        
        # SELECTING CLIENT:
        # Selects the correct client
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
        # switch to dashboard to prevent that modals are open
        self.wait_and_click(By.XPATH, "//a[contains(@href, '/dashboard/')]", By.XPATH, "//div[@id='modal-002']//button[.='Close']")
        #self.assertRegexpMatches(self.close_alert_and_get_its_text(), r"^Oops, something went wrong, probably too many files.")
        self.close_alert_and_get_its_text()

        # LOGOUT:
        self.logout()
    
    def test_run_default_job(self):
        driver = self.driver
        driver.get(self.base_url + "/")
        self.login()
        self.wait_and_click(By.ID, "menu-topnavbar-job")
        self.wait_and_click(By.LINK_TEXT, "Run")
        self.wait_and_click(By.XPATH, "(//button[@type='button'])[2]")
        self.wait_and_click(By.XPATH, "//form[@id='runjob']/div/div/div/div/div/ul/li[3]/a/span")
        Select(driver.find_element_by_id("job")).select_by_visible_text("backup-bareos-fd")
        self.wait_and_click(By.ID, "submit")
        self.wait_and_click(By.ID, "menu-topnavbar-dashboard")
        self.logout()
    
    def test_run_configured_job(self):

        driver = self.driver
        driver.get(self.base_url + "/")
        self.login()
        self.wait_and_click(By.ID, "menu-topnavbar-job")
        self.wait_and_click(By.LINK_TEXT, "Run")
        self.wait_and_click(By.XPATH, "(//button[@type='button'])[2]")
        self.wait_and_click(By.XPATH, "//form[@id='runjob']/div/div/div/div/div/ul/li[3]/a/span")
        Select(driver.find_element_by_id("job")).select_by_visible_text("backup-bareos-fd")
        self.wait_and_click(By.XPATH, "(//button[@type='button'])[3]")
        self.wait_and_click(By.XPATH, "//form[@id='runjob']/div/div[2]/div/div/div/ul/li[3]/a/span")
        Select(driver.find_element_by_id("client")).select_by_visible_text(client)
        Select(driver.find_element_by_id("fileset")).select_by_visible_text("SelfTest")
        driver.find_element_by_xpath("(//button[@type='button'])[5]").click()
        driver.find_element_by_link_text("File").click()
        Select(driver.find_element_by_id("storage")).select_by_visible_text("File")
        self.wait_and_click(By.XPATH, "(//button[@type='button'])[6]")
        self.wait_and_click(By.XPATH, "//form[@id='runjob']/div/div[5]/div/div/div/ul/li[4]/a/span")
        self.wait_and_click(By.XPATH, "(//button[@type='button'])[7]")
        self.wait_and_click(By.XPATH, "//form[@id='runjob']/div/div[6]/div/div/div/ul/li[4]/a")
        driver.find_element_by_id("priority").clear()
        driver.find_element_by_id("priority").send_keys("5")
        driver.find_element_by_css_selector("span.glyphicon.glyphicon-calendar").click()
        self.wait_and_click(By.XPATH, "//div[@id='when-datepicker']/div/div/div[2]/div/table/tr/td[3]/a/span")
        self.wait_and_click(By.XPATH, "//div[@id='when-datepicker']/div/div/div[2]/div/table/tr/td[3]/a/span")
        self.wait_and_click(By.CSS_SELECTOR, "span.input-group-addon")
        self.wait_and_click(By.ID, "submit");
        self.wait_and_click(By.ID, "menu-topnavbar-dashboard")
        self.logout()
        
    def test_rerun_job(self):
        ### HARDCODED XPATHS; WILL FAIL
        driver = self.driver
        driver.get(self.base_url + "/")
        self.login()
        self.wait_and_click(By.ID, "menu-topnavbar-client")
        self.wait_and_click(By.LINK_TEXT, self.client)
        self.wait_and_click(By.XPATH, "//div[2]/div/div/div[2]/div/div[2]/div[2]/table/tbody/tr/td/a")
        self.wait_and_click(By.CSS_SELECTOR, "span.glyphicon.glyphicon-repeat")
        self.wait_and_click(By.ID, "menu-topnavbar-dashboard", By.XPATH, "//div[@id='modal-002']/div/div/div[3]/button")
        self.logout()
    
    def test_client_disabling(self):
        driver = self.driver
        driver.get(self.base_url + "/")
        self.login()
        # Disables client 1 and goes back to the dashboard.
        self.wait_and_click(By.ID, "menu-topnavbar-client")
        self.wait_and_click(By.XPATH, "(//a[@id='btn-1'])[2]")
        self.wait_and_click(By.ID, "menu-topnavbar-client")
        self.wait_and_click(By.CSS_SELECTOR, "span.glyphicon.glyphicon-remove")
        self.wait_and_click(By.ID, "menu-topnavbar-dashboard",By.CSS_SELECTOR, "div.modal-footer > button.btn.btn-default")
        # Enables client 1, goes back to dashboard and logs out.
        self.wait_and_click(By.ID, "menu-topnavbar-client")
        self.wait_and_click(By.XPATH, "(//a[@id='btn-1'])[3]")
        self.wait_and_click(By.ID, "menu-topnavbar-dashboard", By.CSS_SELECTOR, "div.modal-footer > button.btn.btn-default")
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
        # while ("/dashboard/" not in self.driver.current_url):
        #     sleep(self.waittime)
        ui.WebDriverWait(self.driver, self.maxwait).until(EC.invisibility_of_element_located((By.ID, 'spinner')))
        
        
    def logout(self):
        self.wait_and_click(By.LINK_TEXT, username)
        ui.WebDriverWait(self.driver, self.maxwait).until(EC.visibility_of_element_located((By.LINK_TEXT, "Logout")))
        self.wait_and_click(By.LINK_TEXT, "Logout")        
        sleep(self.sleeptime)
        
    def wait_for_element(self, by, value):
        logger = logging.getLogger()
        element = None
        while element is None:
            try:
                element = ui.WebDriverWait(self.driver, self.maxwait).until(EC.visibility_of_element_located((by, value)))
            except TimeoutException:
                logger.info("waiting for %s %s", by, value)
        return element    

    def wait_and_click(self, by, value, modal_by=None, modal_value=None):
        logger = logging.getLogger()
        element = None
        starttime = datetime.now()
        seconds = 0.0
        while seconds < self.maxwait:          
            if modal_by and modal_value:
                try:
                    self.driver.find_element(modal_by, modal_value).click()
                except:
                    logger.info("skipped modal: %s %s not found", modal_by, modal_value)
                else:
                    logger.info("closing modal %s %s", modal_by, modal_value)
            logger.info("waiting for %s %s (%ss)", by, value, seconds)
            try:
                self.driver.find_element(by, value).click()
            except WebDriverException or NoSuchElementException as e:
                logger.info("WebDriverException while clicking: %s", e)
                sleep(self.waittime) 
            else:
                return
            seconds = (datetime.now() - starttime).total_seconds()

        logger.error("failed to click %s %s", by, value)
        raise e

    def wait_for_url_and_click(self, url):
        logger = logging.getLogger()
        value="//a[contains(@href, '%s')]" % url
        # wait for page to be loaded
        starttime = datetime.now()
        seconds = 0.0
        while seconds < self.maxwait:
            element = self.wait_and_click(By.XPATH, value)
            if (url in self.driver.current_url):
                logger.info("%s is loaded (%d s)", url, (datetime.now() - starttime).total_seconds())
                return element
            logger.info("waiting for url %s to be loaded", url)
            sleep(self.sleeptime)
            seconds = (datetime.now() - starttime).total_seconds()
            logger.info("Waiting: %s", seconds)
        raise ("Timeout while waiting for url %s (%d s)", url, seconds)
        # raise "Timeout while waiting for url %s (%d s)", url, seconds

    def close_alert_and_get_its_text(self, accept=True):
        logger = logging.getLogger()

        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
        except NoAlertPresentException:
            return

        if accept:
            alert.accept()
        else:
            alert.dismiss()

        logger.debug( 'alert message: %s' % (alert_text))

        return alert_text

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
     


if __name__ == "__main__":
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

    client = os.environ.get('BAREOS_CLIENT_NAME')
    if client:
        WebuiSeleniumTest.client = client

    restorefile = os.environ.get('BAREOS_RESTOREFILE')
    if restorefile:
        WebuiSeleniumTest.restorefile = restorefile

    logpath = os.environ.get('BAREOS_LOG_PATH')
    if logpath:
        WebuiSeleniumTest.logpath = logpath

    sleeptime = os.environ.get('BAREOS_DELAY')
    if sleeptime:
        WebuiSeleniumTest.sleeptime = float(sleeptime)

    unittest.main()