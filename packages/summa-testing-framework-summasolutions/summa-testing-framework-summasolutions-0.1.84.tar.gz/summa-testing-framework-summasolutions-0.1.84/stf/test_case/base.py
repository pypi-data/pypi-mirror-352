import unittest
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from appium import webdriver as AppiumWebdriver
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# import Faker

default_hub_host = 'selenium-hub:4444'


def get_driver(browser, hub_host):
    if (browser == 'chrome'):
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1920x1080')
        options.add_argument('ignore-certificate-errors')
        options.add_argument("incognito")
        options.add_argument("start-maximized")
        #capabilities = DesiredCapabilities.CHROME.copy()
        driver = webdriver.Remote(
            command_executor="http://%s/wd/hub" % (hub_host),
            options=options
        )

        return driver

    if (browser == 'firefox'):
        options = webdriver.FirefoxOptions()
        options.add_argument('-width=1920')
        options.add_argument('-height=1080')
        options.set_preference("geo.prompt.testing", True)
        options.set_preference("geo.prompt.testing.allow", False)
        #capabilities = DesiredCapabilities.FIREFOX.copy()

        driver = webdriver.Remote(
            command_executor="http://%s/wd/hub" % (hub_host),
            options=options
        )

        return driver

    if (browser == 'android'):
        desired_caps = dict(
            platformName='Android',
            # platformVersion='10',
            automationName='uiautomator2',
            deviceName='Android Emulator',
        )

        driver = webdriver.Remote(
            "http://%s/wd/hub" % (hub_host),
            desired_caps
        )

        return driver

    raise ValueError('Browser not supported')


def get_hub_host(config):
    if 'hub_host' in config and config['hub_host'] is not None:
        return config['hub_host']

    return default_hub_host


class BaseTestCase(unittest.TestCase):
    def __init__(self, testname, config, environment, browser):
        super(BaseTestCase, self).__init__(testname)
        BaseTestCase.environment = environment
        BaseTestCase.config = config[environment]
        BaseTestCase.browser = browser

    @classmethod
    def setUpClass(cls):
        hub_host = get_hub_host(cls.config)
        cls.driver = get_driver(cls.browser, hub_host)

        # cls.faker = Faker(['es_MX', 'en_US'])

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.reset()
        self.driver.get(self.config['url'])

    def takeScreenshot(self, test_name):
        print(self.__class__.__name__)

    #     self.driver.get_screenshot_as_file();

    def generateExceptionReport(self, exception):
        driver = self.driver
        screenshot = driver.get_screenshot_as_base64()
        #console_log = driver.get_log('browser')
        #console_log_string = json.dumps(console_log)
        #formatedException = '''
        #<p class="lead">{0}</p>
        #
        #<h4>Browser Screenshot</h4>
        #<img src="data:image/png;base64,{1}">
        #
        #<h5>Browser Console</h5>
        #<code>{2}</code>
        #'''.format(exception, screenshot, console_log_string)
        
        formatedException = '''
        <p class="lead">{0}</p>
        
        <h4>Browser Screenshot</h4>
        <img src="data:image/png;base64,{1}">
        '''.format(exception, screenshot)

        self.reset()
        return formatedException

    def generateException(self, exception):
        driver = self.driver
        screenshot = driver.get_screenshot_as_base64()
        #console_log = driver.get_log('browser')
        #console_log_string = json.dumps(console_log)

        exception.browser_screenshot = screenshot
        #exception.browser_console_log = console_log_string

        return exception

    def reset(self):
        # Function to click edit address checkbox
        driver = self.driver
        driver.delete_all_cookies()
        driver.refresh()

    def basic_click(self, xpath, ref='', wait=None):
        driver = self.driver
        if wait is None:
            wait = WebDriverWait(driver, self.config['time_to_sleep'])
        else:
            wait = WebDriverWait(driver, wait)
        success = True
        try:
            basic_click = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            basic_click.click()
        except:
            success = False

        return self.assertTrue(success, "No fue posible el click basico en " + str(ref))

    def script_click(self, xpath, ref='', wait=None):
        driver = self.driver
        if wait is None:
            wait = WebDriverWait(driver, self.config['time_to_sleep'])
        else:
            wait = WebDriverWait(driver, wait)
        success = True

        try:
            script_click = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("(arguments[0]).click();", script_click)

        except:
            success = False

        return self.assertTrue(success, "No fue posible el script click en " + str(ref))

    def script_click_after(self, xpath):
        script = f"""
        var xpath = "{xpath}";
        var element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (element) {{
            element.click();
        }} else {{
            console.log("No se encontró ningún elemento con el XPath especificado.");
        }}
        """
        self.driver.execute_script(script)

    def fill_input(self, xpath, input, ref='', wait=None):
        driver = self.driver
        if wait is None:
            wait = WebDriverWait(driver, self.config['time_to_sleep'])
        else:
            wait = WebDriverWait(driver, wait)
        success = True

        try:
            fill_input = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            fill_input.send_keys(input)

        except:
            success = False

        return self.assertTrue(success, "No fue posible el llenar el input en " + str(ref))

    def fill_dropdown_input(self, xpath, input, ref='', wait=None):
        driver = self.driver
        if wait is None:
            wait = WebDriverWait(driver, self.config['time_to_sleep'])
        else:
            wait = WebDriverWait(driver, wait)
        success = True

        try:
            drop_input = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            drop_input.send_keys(input)
            time.sleep(3)
            drop_input.send_keys('\ue015')
            drop_input.send_keys(u'\ue007')
            time.sleep(3)

        except:
            success = False

        return self.assertTrue(success, "No fue posible el llenar el input en " + str(ref))

    def verify_existence(self, xpath, ref='', wait=None):
        driver = self.driver
        if wait is None:
            wait = WebDriverWait(driver, self.config['time_to_sleep'])
        else:
            wait = WebDriverWait(driver, wait)
        success = True

        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        except:
            success = False

        return self.assertTrue(success, "No fue posible verificar la existencia de " + str(ref))

    def switch_to_frame(self, xpath, ref='', wait=None):
        driver = self.driver
        if wait is None:
            wait = WebDriverWait(driver, self.config['time_to_sleep'])
        else:
            wait = WebDriverWait(driver, wait)
        success = True
        try:
            iframe = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            driver.switch_to.frame(iframe)
        except:
            success = False

        return self.assertTrue(success, "No fue posible el cambio de iframe en " + str(ref))

    def switch_out_frame(self, wait=None):
        driver = self.driver
        if wait is None:
            wait = WebDriverWait(driver, self.config['time_to_sleep'])
        else:
            wait = WebDriverWait(driver, wait)
        success = True
        try:
            driver.switch_to.default_content()
        except:
            success = False

        return self.assertTrue(success, "No fue posible salir del iframe ")

    def clear_input(self, xpath):
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True
        try:
            input_field = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            input_field.clear()
        except:
            success = False

        return self.assertTrue(success, "No se pude limpiar el input")
    def env_test(self, ruta_archivo=".env"):
        # Cargar las variables de entorno desde el archivo .env
        datos = {}
        with open(ruta_archivo, "r") as env_file:
            lines = env_file.readlines()
        # Acceder a los valores mediante las claves
        for line in lines:
            if "=" in line:
                key, value = line.strip().split("=")
                datos[key] = value
        return datos