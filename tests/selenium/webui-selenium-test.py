#!/usr/bin/env python

# -*- coding: utf-8 -*-

# selenium.common.exceptions.ElementNotInteractableException: requires >= selenium-3.4.0


# CAUTION:
# This test requires IDs in the WebUI that are not public (yet). Therefore it will not run!

import logging, os, re, sys, unittest, time
from   datetime import datetime, timedelta
from   selenium import webdriver
from   selenium.common.exceptions import *
from   selenium.webdriver.common.by import By
from   selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from   selenium.webdriver.common.keys import Keys
from   selenium.webdriver.support import expected_conditions as EC
from   selenium.webdriver.support.ui import Select, WebDriverWait
#from selenium.webdriver.remote.remote_connection import LOGGER
from   time import sleep



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
        #self.driver.implicitly_wait(4)

        self.wait = WebDriverWait(self.driver, 10)


        # take base url, but remove last /
        self.base_url = base_url.rstrip('/')

        self.verificationErrors = []
        self.accept_next_alert = True

# The tests.
    def test_login(self):
        self.login()
        self.logout()
    
    def test_menue(self):
        driver = self.driver
        self.driver.get(self.base_url + "/")
        self.login()
        self.wait_and_click(By.ID, "menu-topnavbar-director")
        self.wait_and_click(By.ID, "menu-topnavbar-schedule")
        self.wait_and_click(By.LINK_TEXT, "Scheduler status")
        self.wait_and_click(By.ID, "menu-topnavbar-storage")
        self.wait_and_click(By.ID, "menu-topnavbar-client")
        self.wait_and_click(By.ID, "menu-topnavbar-restore")    
        self.wait_and_click(By.XPATH, "//a[contains(@href, '/dashboard/')]", By.XPATH, "//div[@id='modal-001']//button[.='Close']")
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
        # This tests functionality depends on existence of job id 161.
        # It won't run if job 161 does not exit or isn't rerunnable.
        driver = self.driver
        driver.get(self.base_url + "/")
        self.login()
        self.wait_and_click(By.ID, "menu-topnavbar-job")
        self.wait_and_click(By.XPATH, "//a[contains(@href, '/bareos-webui/job/index?action=rerun&jobid=161')]")
        self.wait_and_click(By.ID, "menu-topnavbar-dashboard", By.XPATH, "//div[@id='modal-002']/div/div/div[3]/button")
        self.logout()

    def test_restore(self):

        # LOGGING IN:
        self.login()

        # CHANGING TO RESTORE TAB:
        self.wait_and_click(By.ID, "menu-topnavbar-restore") 
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

        # LOGOUT:
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


# Methods used by tests.
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

        self.wait_and_click(By.CSS_SELECTOR, "a.dropdown-toggle")
        self.wait_and_click(By.LINK_TEXT, "Logout")
        sleep(self.sleeptime)

    def wait_for_element(self, by, value, starttime = None):
        logger = logging.getLogger()
        element = None
        #if starttime is None:
             #starttime = datetime.now()
        #seconds = (datetime.now() - starttime).total_seconds()
        #logger.info("waiting for %s %s (%ds)", by, value, seconds)
        #while (seconds < self.maxwait) and (element is None):
            #try:
                #tmp_element = self.driver.find_element(by, value)
                #if tmp_element.is_displayed():
                    #element = tmp_element
            #except ElementNotInteractableException:
                #sleep(self.waittime)
                #logger.info("%s %s not interactable", by, value)
            #except NoSuchElementException:
                #sleep(self.waittime)
                #logger.info("%s %s not existing", by, value)
            #except ElementNotVisibleException:
                #sleep(self.waittime)
                #logger.info("%s %s not visible", by, value)
            #seconds = (datetime.now() - starttime).total_seconds()
        #if element:
            #logger.info("%s %s loaded after %ss." % (by, value, seconds))
            #sleep(self.sleeptime)
        #else:
            #logger.warning("Timeout while loading %s %s (%d s)", by, value, seconds)
        wait = WebDriverWait(self.driver, 10) 
        element = self.wait.until(EC.element_to_be_clickable((by, value)))
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
            element = self.wait_for_element(by, value, starttime)
            try:
                element.click()
            except WebDriverException as e:
                #logger.info("WebDriverException while clicking %s %s", by, value)
                logger.info("WebDriverException: %s", e)
                #logger.exception(e)
                sleep(self.waittime)
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
    debugging = os.environ.get('BAREOS_DEBUG')
    if debugging=='on':
        logging.basicConfig(filename='webui-selenium-test.log', format='%(levelname)s %(module)s.%(funcName)s: %(message)s', level=logging.DEBUG)
    else:
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
