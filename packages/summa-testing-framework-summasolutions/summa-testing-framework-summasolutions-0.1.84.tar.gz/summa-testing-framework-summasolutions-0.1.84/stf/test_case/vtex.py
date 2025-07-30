from stf.test_case.base import BaseTestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import string
import random
from random import randint

import yaml
with open("xpath.yml", 'r') as ymlfile:
    xpath = yaml.full_load(ymlfile)


class VtexTestCase(BaseTestCase):

    def maximize_windows(self):
        # function for Maximize the browser window
        driver = self.driver
        driver.maximize_window()


    def refresh_windows(self):
        # function for Maximize the browser window
        driver = self.driver
        driver.refresh()

    def send_cookie(self):
        # function for Maximize the browser window
        driver = self.driver
        driver.add_cookie({self.config['test_parameters']['api']['cookie']})


    def find_simple_product(self, product):
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            search_input = wait.until(EC.element_to_be_clickable((By.XPATH, xpath['homepage']['search_bar'])))
            search_input.send_keys(product)
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath['homepage']['search_menu'])))
            search_input.send_keys(u'\ue007')

        except:
            success = False        

        return self.assertTrue(success, "Search product not working")


    def visit_positional_product_page(self, pos):
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            grid_products = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['product_list_page']['gallery'])))
            first_element = driver.find_elements(By.XPATH, xpath['product_list_page']['gallery_products'])     
            first_element[pos].click()


        except:
            success = False

        return self.assertTrue(success, "Product Page in " +str(pos)+ " was not found")

    def add_simple_product(self):
        # function to add a simple product from product page
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:

            simple_product = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['product_page']['principal_content'])))       

            add_to_cart_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath['product_page']['add_product'])))
            add_to_cart_button.click()

            wait.until(EC.visibility_of_element_located((By.XPATH, xpath['product_page']['side_bar'])))       

        except:
            success = False

        return self.assertTrue(success, "Product could not be added to cart")


    def go_to_cart(self):
        # function to go to checkout from cart
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # press checkout button
            cart_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath['product_page']['go_to_cart'])))
            cart_button.click()

            wait.until(EC.visibility_of_element_located((By.XPATH, xpath['cart']['principal_content'])))       


        except:
            success = False

        return self.assertTrue(success, "Checkout page could not be reached")

    def go_to_checkout(self):
        # function to go to checkout from cart
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # press checkout button
            checkout_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath['cart']['go_to_checkout'])))
            checkout_button.click()

            wait.until(EC.visibility_of_element_located((By.XPATH, xpath['cart']['principal_content'])))       
            wait.until(EC.visibility_of_element_located((By.XPATH, xpath['cart']['cart_totals'])))       


        except:
            success = False

        return self.assertTrue(success, "Checkout page could not be reached")


    def convert_price(self, priceText):
        # function to convert a string price to float
        sinMoneda = priceText.replace("$", "")
        notacion = sinMoneda.replace(".", "")
        notacionPunto = notacion.replace(",", ".")
        return float(notacionPunto)

    def validate_cart_totals(self):
        # function to validate totals in cart
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            table_grand_total = 0
            # wait for cart totals
            cart_totals = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['cart']['cart_totals'])))

            # sum all item subtotals from product list
            items_subtotal = 0
            product_price_list = driver.find_elements(By.XPATH, xpath['cart']['cart_totals'] + xpath['cart']['cart_totals_items'])

            for item in product_price_list:
                items_subtotal += self.convert_price(item.get_attribute('innerHTML'))


            grand_total_text = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['cart']['cart_totals'] + xpath['cart']['total_price'])))
            table_grand_total = self.convert_price(grand_total_text.get_attribute('innerHTML'))
            if items_subtotal == table_grand_total:
                pass
            else:
                raise Exception


        except:
            success = False

        return self.assertTrue(success, "Cart Grand Total doesn't match: " + str(items_subtotal) + " against " + str(table_grand_total))
