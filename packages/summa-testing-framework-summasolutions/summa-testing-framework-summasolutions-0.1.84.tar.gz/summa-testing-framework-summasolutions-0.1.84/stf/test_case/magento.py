from .base import BaseTestCase

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


class MagentoTestCase(BaseTestCase):

    def click_search_icon(self):
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            search_icon = wait.until(EC.element_to_be_clickable((By.XPATH, xpath['homepage']['search_icon'])))
            search_icon.click()
        except:
            success = False

        return self.assertTrue(success, "Search icon not found")

    def check_filter(self):
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, xpath['product_page']['filter'])))
        except:
            success = False

        return self.assertTrue(success, "No se encontro el filtro")

    def visit_product_page(self, sku):
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            search_input = wait.until(EC.element_to_be_clickable((By.XPATH, xpath['homepage']['search_bar'])))
            search_input.send_keys(sku)
            search_input.submit()
            wait.until(EC.visibility_of_element_located((By.XPATH, xpath['product_page']['home_pdp'])))
            self.check_filter()

        except:
            success = False

        return self.assertTrue(success, "Product Page was not found")

    def visit_simple_product_page(self, sku):
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True
        replaced_param = self.replace_param(xpath['product_page']['simple_product'], sku)

        try:
            product = wait.until(EC.element_to_be_clickable((By.XPATH, replaced_param)))
            product.click()
            pdsp = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['simple_product_page']['spp_main_container'])))


        except:
            success = False

        return self.assertTrue(success, "Product Page was not found")

    def select_custom_param(self, attribute):
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            for attr in attribute:
                replaced_param = self.replace_param(xpath['simple_product_page']['attr_selection'], attr)
                elementAttr = wait.until(EC.element_to_be_clickable((By.XPATH, replaced_param)))
                elementAttr.click()
        except:
            success = False

        return self.assertTrue(success, "Attribute was not selected")

    def select_custom_option(self, attribute, option):
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            attribute = self.replace_param(xpath['simple_product_page']['attr_selection'], attribute)
            final_xpath = self.replace_param((attribute + xpath['simple_product_page']['option_selection']), option)
            attr_select = wait.until(EC.element_to_be_clickable((By.XPATH, final_xpath)))
            attr_select.click()
        except:
            success = False

        return self.assertTrue(success, "Custom Attribute was not selected")

    def visit_positional_product_page(self, pos):
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            elementList = driver.find_elements(By.XPATH, xpath['product_page']['all_product_list'])
            first_element = elementList[pos].find_element_by_class_name("product-item-photo")
            first_element.click()
            pdsp = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['simple_product_page']['spp_main_container'])))


        except:
            success = False

        return self.assertTrue(success, "Product Page in " + str(pos) + " was not found")

    def replace_param(self, xpath, param):
        # function to replace param
        final_xpath = xpath.replace("PARAM", param)
        return final_xpath

    def random_char(self, y):
        # function to generate random characters
        return ''.join(random.choice(string.ascii_lowercase) for x in range(y))

    def generateDocNumber(self):
        # function to generate a random document number
        return str(randint(20000000, 79999999))

    def generateMail(self):
        # function to generate a random mail address
        return 'automated_' + self.random_char(8) + str(randint(0, 999)) + '@testing.com'

    def checkout_loader(self):
        # function wait for checkout loader
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            loading_mask = wait.until(
                EC.invisibility_of_element_located((By.XPATH, xpath['common_elements']['loader'])))
        except:
            success = False

        return self.assertTrue(success, "No desaparecio el icono de carga")

    def maximize_windows(self):
        # function for Maximize the browser window
        driver = self.driver
        driver.maximize_window()

    def add_simple_product(self):
        # function to add a simple product from product page
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # add to cart
            add_to_cart_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath['simple_product_page']['add_product_button'])))
            add_to_cart_button.click()

        except:
            success = False

        return self.assertTrue(success, "Product could not be added to cart")

    def validate_product_was_added(self):
        # function to validate success message in add to cart
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # wait for success message that contains cart link
            success_message = wait.until(EC.visibility_of_element_located(
                (By.XPATH, xpath['product_page']['succes_msj'])))

        except:
            success = False

        return self.assertTrue(success, "Product was not added to cart")

    def open_minicart(self):
        # function to open minicart from header
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # press minicart button
            minicart_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath['mini_cart']['open_mini_cart'])))
            minicart_button.click()

        except:
            success = False

        return self.assertTrue(success, "Minicart could not be opened")

    def go_to_cart_from_minicart(self):
        # function to press go to cart button in minicart
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # press go to cart button
            cart_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath['mini_cart']['go_to_cart'])))
            cart_button.click()

        except:
            success = False

        return self.assertTrue(success, "Cart could not be reached")

    def convert_price(self, priceText):
        # function to convert a string price to float
        sinEspecial = priceText.replace("&nbsp;", "")
        sinMoneda = sinEspecial.replace("$", "")
        notacion = sinMoneda.replace(".", "")
        notacionPunto = notacion.replace(",", ".")
        return float(notacionPunto)

    def validate_cart_totals(self, discount_amount):
        # function to validate totals in cart
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            grand_total = 0
            table_grand_total = 0
            # wait for cart totals
            cart_totals = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['cart']['cart_totals'])))

            # sum all item subtotals from product list
            items_subtotal = 0
            product_price_list = driver.find_elements(By.XPATH, xpath['cart']['sub_total_product_list'])

            for item in product_price_list:
                items_subtotal = self.convert_price(item.get_attribute('innerHTML'))

            # obtain data from cart totals table
            subtotal_text = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['cart']['sub_total_price'])))
            table_subtotal = self.convert_price(subtotal_text.get_attribute('innerHTML'))

            # validate both subtotals against each other
            if items_subtotal == table_subtotal:
                pass
            else:
                raise Exception("Cart Subtotals don't match")

            # sum all subtotals from cart totals table
            if discount_amount > 0:
                # obtain discount data
                discount_text = wait.until(
                    EC.visibility_of_element_located((By.XPATH, xpath['cart']['discount_text'])))
                table_discount = self.convert_price(discount_text.get_attribute('innerHTML'))
            else:
                table_discount = 0
            grand_total = round(table_subtotal + table_discount, 2)

            # validate grand total
            grand_total_text = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['cart']['tota_price'])))
            table_grand_total = self.convert_price(grand_total_text.get_attribute('innerHTML'))
            if grand_total == table_grand_total:
                pass
            else:
                raise Exception


        except:
            success = False

        return self.assertTrue(success, "Cart Grand Total doesn't match: " + str(grand_total) + " against " + str(
            table_grand_total))

    def validate_checkout_cart_totals(self, form):

        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True
        cart_totals_xpath = xpath[form]['cart_totals']
        total = 0
        table_grand_total = 0
        try:
            cart_totals = wait.until(EC.visibility_of_element_located((By.XPATH, cart_totals_xpath)))
            subtotal_text = driver.find_elements(By.XPATH, cart_totals_xpath + xpath[form]['all_prices'])

            if len(subtotal_text) == 0:
                total = self.convert_price(item.get_attribute('innerHTML'))
            else:
                for item in subtotal_text:
                    total = total + self.convert_price(item.get_attribute('innerHTML'))

            grand_total_text = wait.until(EC.visibility_of_element_located(
                (By.XPATH, cart_totals_xpath + xpath['checkout']['grand_total'])))
            table_grand_total = self.convert_price(grand_total_text.get_attribute('innerHTML'))

            if total == table_grand_total:
                pass
            else:
                raise Exception


        except:
            success = False

        return self.assertTrue(success, "The sum of the elements " + str(total) + " does not match the total " + str(
            table_grand_total))

    def add_discount_coupon_in_cart(self, coupon_code):
        # function to add a discount coupon in cart
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True
        discount_form_xpath = xpath['cart']['discount_cupon_form']

        try:
            # wait for cart totals
            cart_totals = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['cart']['cart_totals'])))
            subtotal_text = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['cart']['sub_total_price'])))

            # expand coupon input
            expand_coupon = wait.until(EC.element_to_be_clickable((By.XPATH, xpath['cart']['expand_cupon'])))
            expand_coupon.click()

            # fill discount coupon
            input_coupon = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, discount_form_xpath + xpath['cart']['input_discount_cupon'])))
            input_coupon.send_keys(coupon_code)

            # press apply
            apply_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, discount_form_xpath + xpath['cart']['apply_discount_button'])))
            apply_button.click()

            # wait for success message
            coupon_success = wait.until(EC.visibility_of_element_located(
                (By.XPATH, self.replace_param(xpath['cart']['succes_msj_aplied_cupon'], coupon_code))))

        except:
            success = False

        return self.assertTrue(success, "Discount coupon could not be added")

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

        except:
            success = False

        return self.assertTrue(success, "Checkout page could not be reached")

    def select_shipping_method(self, shipping_method):
        # function to choose shipping method in checkout first step
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            self.checkout_loader()
            # wait for shipping methods
            shipping_methods_selector = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['checkout']['shipping_methods'])))

            # choose shipping_method
            shipping_selector = self.config['shipping_parameters'][shipping_method]
            shipping_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, self.replace_param(xpath['checkout']['shipping_button'], str(shipping_selector)))))
            shipping_button.click()

        except:
            success = False

        return self.assertTrue(success, "Shipping method could not be selected")

    def fill_customer_email(self, email, shipping_method):
        # function to input customer email
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        selector = self.config['shipping_parameters'][shipping_method]
        success = True

        try:
            # fill customer email
            input_email = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['fill_inputs'][selector + '_mail_input'])))
            input_email.send_keys(email)

            # continue
            continueBtn = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath['fill_inputs'][selector + '_continue_button'])))
            continueBtn.click()

        except:
            success = False

        return self.assertTrue(success, "Customer email could not be filled" + str(selector))

    def fill_pickup_data(self, customer):
        # function to fill who pick personal data in checkout forms
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True
        form_xpath = xpath['forms']['who_pick_form']
        try:
            self.fill_personal_data(form_xpath, customer)
        except:
            success = False

        return self.assertTrue(success, "Pickup personal data could not be filled")

    def fill_personal_data(self, form_xpath, customer):
        # function to fill personal data in checkout forms
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])

        # First Name
        first_name = wait.until(
            EC.visibility_of_element_located((By.XPATH, form_xpath + xpath['fill_inputs']['input_firstname'])))
        first_name.send_keys(customer['firstname'])
        # Last Name
        last_name = wait.until(
            EC.visibility_of_element_located((By.XPATH, form_xpath + xpath['fill_inputs']['input_lastname'])))
        last_name.send_keys(customer['lastname'])
        # Vat ID
        vat_id = wait.until(
            EC.visibility_of_element_located((By.XPATH, form_xpath + xpath['fill_inputs']['input_vat_id'])))
        vat_id.send_keys(customer['vat_id'])
        # Telephone Number
        telephone_number = wait.until(
            EC.visibility_of_element_located((By.XPATH, form_xpath + xpath['fill_inputs']['input_telephone'])))
        telephone_number.send_keys(customer['telephone'])

    def fill_address_data(self, form_xpath, address):
        # function to fill address data in checkout forms
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])

        # Street
        street_name = wait.until(
            EC.visibility_of_element_located((By.XPATH, form_xpath + xpath['fill_inputs']['input_street'])))
        street_name.send_keys(address['street'])
        # Street Number
        street_number = wait.until(
            EC.visibility_of_element_located((By.XPATH, form_xpath + xpath['fill_inputs']['input_street_number'])))
        street_number.send_keys(address['number'])
        # Postcode
        postal_code = wait.until(
            EC.visibility_of_element_located((By.XPATH, form_xpath + xpath['fill_inputs']['input_postcode'])))
        postal_code.send_keys(address['postcode'])
        # Region
        region = wait.until(
            EC.visibility_of_element_located((By.XPATH,
                                              form_xpath + self.replace_param(xpath['fill_inputs']['select_region'],
                                                                              str(address['region_id'])))))
        region.click()
        # City
        city = wait.until(EC.visibility_of_element_located(
            (By.XPATH, form_xpath + self.replace_param(xpath['fill_inputs']['select_city'], str(address['city'])))))
        city.click()
        # District
        disctric = wait.until(EC.visibility_of_element_located((By.XPATH, form_xpath + self.replace_param(
            xpath['fill_inputs']['select_disctrict'], str(address['disctrict'])))))
        disctric.click()

    def fill_new_shipping_address(self, customer, shipping_address):
        # function to fill new shipping address
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            shipping_form = xpath['forms']['shipping_form']
            self.checkout_loader()

            # fill personal data
            self.fill_personal_data(shipping_form, customer)

            # fill new shipping address data in the form
            self.fill_address_data(shipping_form, shipping_address)

            # confirm address
            update_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, xpath['forms']['shipping_continue_button'])))
            update_button.click()

        except:
            success = False

        return self.assertTrue(success, "Shipping address could not be filleds")

    def fill_new_billing_address(self, customer, billing_address):
        # function to fill new billing address in payment step
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            billing_form = xpath['forms']['billing_form']
            self.checkout_loader()

            # fill personal data
            self.fill_personal_data(billing_form, customer)

            # fill new billing address data in the form
            self.fill_address_data(billing_form, billing_address)

            # confirm address
            update_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, billing_form + xpath['forms']['billing_continue_button'])))
            update_button.click()

        except:
            success = False

        return self.assertTrue(success, "Billing address could not be filled")

    def select_delivery_type(self, delivery_type):
        # function to choose shipping delivery type in checkout first step after selecting shipping method: delivery
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            self.checkout_loader()

            # select delivery type
            delivery_selector = wait.until(EC.element_to_be_clickable(
                (By.XPATH, self.replace_param(xpath['checkout']['delivery_type'], delivery_type))))
            delivery_selector.click()

        except:
            success = False

        return self.assertTrue(success, "Delivery could not be selected")

    def select_store(self):
        # function to choose a store to pickup the order
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # wait for store selector list
            store_list = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['checkout']['store_list'])))

            # select store to pickup order
            store_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath['checkout']['store_button'])))
            store_button.click()

        except:
            success = False

        return self.assertTrue(success, "Store could not be selected")

    def continue_to_payment(self):
        # function to continue to payment step in checkout
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # press continue button
            continue_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath['checkout']['continue_to_payment'])))
            continue_button.click()

        except:
            success = False

        return self.assertTrue(success, "Payment page could not be reached")

    def continue_to_payment_storepickup(self):
        # function to continue to payment step in checkout when method is store pickup
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # press continue button
            continue_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath['checkout']['continue_to_payment_storepickup'])))
            continue_button.click()

        except:
            success = False

        return self.assertTrue(success, "Payment page could not be reached")

    def select_payment_method(self, payment_method):
        # function to select a payment method in payment step in checkout
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            self.checkout_loader()

            # wait for payment methods list
            payment_methods_list = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['checkout']['payment_method_list'])))

            # select payment method
            payment_selector = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, self.replace_param(xpath['checkout']['payment_selector'], payment_method))))
            payment_selector.click()

        except:
            success = False

        return self.assertTrue(success, "Payment method could not be selected")

    def fill_payment_data(self, payment_method, card, payment_plan):
        # function to fill payment data in payment method section
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # check which method has been selected
            if payment_method == 'mercadopago_custom_aggregator':
                suffix = '-ag'
                self.fill_mercadopago_card(suffix, card, payment_plan)
            if payment_method == 'mercadopago_custom':
                suffix = ''
                self.fill_mercadopago_card(suffix, card, payment_plan)
            if payment_method == 'checkmo':
                pass

        except:
            success = False

        return self.assertTrue(success, "Payment data could not be filled")

    def fill_mercadopago_card(self, suffix, card, payment_plan):
        # function to fill mercadopago credit card form
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            self.checkout_loader()

            # fill card form
            # Card Number
            card_number = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, self.replace_param(xpath['card_inputs']['card_number'], suffix))))
            card_number.send_keys(card['number'])

            # Expiration Date
            exp_month_suffix = self.replace_param(xpath['card_inputs']['expiration_month'], suffix)
            exp_month = wait.until(EC.element_to_be_clickable(
                (By.XPATH, self.replace_param(exp_month_suffix + xpath['card_inputs']['option_value'], card['month']))))
            exp_month.click()

            exp_year_suffix = self.replace_param(xpath['card_inputs']['expiration_year'], suffix)
            exp_year = wait.until(EC.element_to_be_clickable(
                (By.XPATH, self.replace_param(exp_year_suffix + xpath['card_inputs']['option_value'], card['year']))))
            exp_year.click()

            # Card Holder Name
            card_holder = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, self.replace_param(xpath['card_inputs']['card_holder_name'], suffix))))
            card_holder.send_keys(card['owner'])

            # Security Code
            security_code = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, self.replace_param(xpath['card_inputs']['security_code'], suffix))))
            security_code.send_keys(card['cvv'])

            # Holder Document Type
            doc_type = wait.until(EC.element_to_be_clickable(
                (By.XPATH, self.replace_param(xpath['card_inputs']['holder_document_type'], suffix))))
            doc_type.click()

            # Document Number
            doc_number = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, self.replace_param(xpath['card_inputs']['holder_document_number'], suffix))))
            doc_number.send_keys(card['dni'])

            # Issuer
            if card['issuer'] != 0:
                issuer_selector_suffix = self.replace_param(xpath['card_inputs']['issuer_selector'], suffix)
                issuer_selector = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, self.replace_param(issuer_selector_suffix + xpath['card_inputs']['option_value'],
                                                  payment_plan['bank']))))
                issuer_selector.click()
                # Installments
                installments_selector_suffix = self.replace_param(xpath['card_inputs']['installments_selector'], suffix)
                installments_selector = wait.until(EC.element_to_be_clickable((By.XPATH, self.replace_param(
                    installments_selector_suffix + xpath['card_inputs']['option_value'], card['issuer']))))
                installments_selector.click()

        except:
            success = False

        return self.assertTrue(success)

    def place_order(self):
        # function to place order in payment step
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            self.checkout_loader()

            # press place order button
            place_order_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, xpath['checkout']['place_order'])))
            place_order_button.click()
            self.checkout_loader()

        except:
            success = False

        return self.assertTrue(success, "Order could not be placed")

    def success_page(self):
        # function to validate success page
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # check for generated order id
            order_id = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['success_page']['order_success'])))

        except:
            success = False

        return self.assertTrue(success, "Order was not generated successfuly")

    def validate_input_error(self, msj_error, payment_method):
        # function to validate credit card error
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # check which method has been selected
            if payment_method == 'mercadopago_custom_aggregator':
                suffix = '-ag'
                error_text = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, self.replace_param(xpath['error_msj'][msj_error], suffix))))
            if payment_method == 'mercadopago_custom':
                suffix = ''
                error_text = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, self.replace_param(xpath['error_msj'][msj_error], suffix))))
            if payment_method == 'checkmo':
                pass

        except:
            success = False

        return self.assertTrue(success, "Input error not found")

    def validate_response_error(self):
        # function to validate credit card error
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            input_field = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['error_msj']['response_error'])))
        except:
            success = False

        return self.assertTrue(success, "Response error not found")

    def fill_input_field(self, input, data, payment_method):
        # function to fill input
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # check which method has been selected
            if payment_method == 'mercadopago_custom_aggregator':
                suffix = '-ag'
                input_field = wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, self.replace_param(xpath['card_inputs'][input], suffix))))
                input_field.send_keys(data)

            if payment_method == 'mercadopago_custom':
                suffix = ''
                input_field = wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, self.replace_param(xpath['card_inputs'][input], suffix))))
                input_field.send_keys(data)
            if payment_method == 'checkmo':
                pass

        except:
            success = False

        return self.assertTrue(success)

    def delete_input_field(self, input, payment_method):
        # function to fill input
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # check which method has been selected
            if payment_method == 'mercadopago_custom_aggregator':
                suffix = '-ag'
                input_field = wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, self.replace_param(xpath['card_inputs'][input], suffix))))
                input_field.clear()

            if payment_method == 'mercadopago_custom':
                suffix = ''
                input_field = wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, self.replace_param(xpath['card_inputs'][input], suffix))))
                input_field.clear()
            if payment_method == 'checkmo':
                pass

        except:
            success = False

        return self.assertTrue(success)

    def change_select_option(self, input, data, payment_method):
        # function to select input option
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # check which method has been selected
            if payment_method == 'mercadopago_custom_aggregator':
                suffix = '-ag'
                select_suffix = self.replace_param(xpath['card_inputs'][input], suffix)
                select = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, self.replace_param(select_suffix + xpath['card_inputs']['option_value'], data))))
                select.click()

            if payment_method == 'mercadopago_custom':
                suffix = ''
                select_suffix = self.replace_param(xpath['card_inputs'][input], suffix)
                select = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, self.replace_param(select_suffix + xpath['card_inputs']['option_value'], data))))
                select.click()
            if payment_method == 'checkmo':
                pass

        except:
            success = False

        return self.assertTrue(success)

    def check_unique_elements_on_list(self, unique_list):
        # function to check uniques elements on list
        return len(set(unique_list)) == len(unique_list)

    def verify_uniques_select_elements(self, input, payment_method):
        # function to select verify uniques elements on select
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True
        new_list = []
        try:
            # check which method has been selected
            if payment_method == 'mercadopago_custom_aggregator':
                suffix = '-ag'
                select_suffix = self.replace_param(xpath['card_inputs'][input], suffix)
                elementList = driver.find_elements(By.XPATH, select_suffix)

                for item in elementList:
                    new_list.append(item.get_attribute('innerHTML'))

                success = self.check_unique_elements_on_list(new_list)

            if payment_method == 'mercadopago_custom':
                suffix = ''
                select_suffix = self.replace_param(xpath['card_inputs'][input], suffix)
                elementList = driver.find_elements(By.XPATH, select_suffix)

                for item in elementList:
                    new_list.append(item.get_attribute('innerHTML'))

                success = self.check_unique_elements_on_list(new_list)
            if payment_method == 'checkmo':
                pass

        except:
            success = False

        return self.assertTrue(success, "list not equals" + str(select_suffix))

    def select_shipping_type(self, carrier):
        # Function to select shipping type
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:

            # wait for shipping type list
            shipping_list = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['checkout']['shipping_type'])))
            self.checkout_loader()
            payment_selector = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, self.replace_param(xpath['checkout']['delivery_type'], carrier))))
            payment_selector.click()
            # select carrier

        except:
            success = False
        return self.assertTrue(success, "Shipping type could not be selected")

    def select_option(self, select, data):
        # function to select option
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:

            select_suffix = self.replace_param(xpath['card_inputs']['withdrawal_piont'], select)
            select = wait.until(EC.element_to_be_clickable(
                (By.XPATH, self.replace_param(select_suffix + xpath['card_inputs']['option_value'], data))))
            select.click()

        except:
            success = False

        return self.assertTrue(success, "Select was not found")

    def select_decidir_payment(self, card, bank=""):
        # function to
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            self.checkout_loader()

            # wait for card list
            card_list = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['checkout']['decidir_card_list'])))

            # select card
            payment_selector = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath['checkout'][card])))
            payment_selector.click()

            self.checkout_loader()

            if bank:
                # wait for bank list
                card_list = wait.until(
                    EC.visibility_of_element_located((By.XPATH, xpath['checkout']['decidir_bank_list'])))

                # select bank
                payment_selector = wait.until(
                    EC.element_to_be_clickable((By.XPATH, xpath['checkout'][bank])))
                payment_selector.click()

            self.confirm_payment_plan()
        except:
            success = False

        return self.assertTrue(success, "Decidir card could not be selected")

    def fill_decidir_card(self, card):
        # function to fill mercadopago credit card form
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            self.checkout_loader()

            # fill card form

            # Card Holder Name
            card_holder = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['decidir_card_inputs']['card_holder_name'])))
            card_holder.send_keys(card['owner'])

            # Card Number
            card_number = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['decidir_card_inputs']['card_number'])))
            card_number.send_keys(card['number'])

            # Expiration Month
            card_number = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['decidir_card_inputs']['expiration_month'])))
            card_number.send_keys(card['month'])

            # Expiration Year
            card_number = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['decidir_card_inputs']['expiration_year'])))
            card_number.send_keys(card['year'])

            # Security Code
            security_code = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['decidir_card_inputs']['security_code'])))
            security_code.send_keys(card['cvv'])

            # Document Number
            doc_number = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['decidir_card_inputs']['holder_document_number'])))
            doc_number.send_keys(card['dni'])

        except:
            success = False

        return self.assertTrue(success, "Dicidir card could not be filled")

    def checkout_calendar_loader(self, shipping_type):
        # function wait for checkout loader
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        final_xpath = self.replace_param(xpath['delivery_select']['calendar_loader'], shipping_type)

        loading_mask = wait.until(EC.invisibility_of_element_located((By.XPATH, final_xpath)))

    def close_cart_sidebar(self):

        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            close_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath['cart']['close'])))
            close_button.click()

        except:
            success = False

        return self.assertTrue(success, "The cart could not be closed")

    def select_delivery_shedule(self, shipping_type):
        # Function to select delivery shedule
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:

            final_xpath = self.replace_param(xpath['delivery_select']['delivery_type'], shipping_type)
            shedule_selector = wait.until(EC.element_to_be_clickable((By.XPATH, final_xpath)))
            shedule_selector.click()

        except:
            success = False

        return self.assertTrue(success, "shedule time fail")

    def fail_page(self):
        # function to validate fail page
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # check for generated order id
            order_id = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['success_page']['order_success'])))

        except:
            success = False

        return self.assertTrue(success, "Order was not generated successfuly")

    def login(self, user, password):
        # function to open minicart from header
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # press minicart button
            account = wait.until(EC.element_to_be_clickable((By.XPATH, xpath['login']['account_icon'])))
            account.click()

            login = wait.until(EC.element_to_be_clickable((By.XPATH, xpath['login']['login_button'])))
            login.click()

            first_name = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['login']['first_name'])))
            first_name.send_keys(user)

            passw = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['login']['pass'])))
            passw.send_keys(password)

            button_login = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['login']['login_continue'])))
            button_login.click()

        except:
            success = False

        return self.assertTrue(success, "fail to login")

    def success_transbank_page(self):
        # function to validate success page
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # check for generated order id
            order_id = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['transbank_payment']['succes_page'])))

        except:
            success = False

        return self.assertTrue(success, "Order was not generated successfuly")

    def select_payment_method_transbank(self, transbank_card):
        # function to validate success page
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # check for generated order id
            payment_method = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['transbank_payment']['payment_method'])))
            payment_method.click()

            bank = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['transbank_payment']['bank'])))
            bank.click()

            payment_bank = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['transbank_payment']['payment_bank'])))
            payment_bank.click()

            card_number = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['transbank_payment']['card_number'])))
            card_number.send_keys(transbank_card['card'])

            button = wait.until(EC.visibility_of_element_located((By.XPATH, xpath['transbank_payment']['button'])))
            button.click()

            rut_client = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['transbank_payment']['rut_client'])))
            rut_client.send_keys(transbank_card['rut'])

            pass_client = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['transbank_payment']['pass_client'])))
            pass_client.send_keys(transbank_card['code'])

            transbank_button = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['transbank_payment']['transbank_button'])))
            transbank_button.click()

            payment_status = self.replace_param(xpath['transbank_payment']['payment_status'], transbank_card['status'])
            payment_status_option = wait.until(EC.visibility_of_element_located((By.XPATH, payment_status)))
            payment_status_option.click()

            continue_button = wait.until(
                EC.visibility_of_element_located((By.XPATH, xpath['transbank_payment']['continue_button'])))
            continue_button.click()

        except:
            success = False

        return self.assertTrue(success, "Transbank method could not be selected")

    def fail_page(self):
        # function to validate success page
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            # check for generated order id
            wait.until(EC.visibility_of_element_located((By.XPATH, xpath['success_page']['order_fail'])))

        except:
            success = False

        return self.assertTrue(success, "Order was not generated successfuly")

    def select_product_test(self, url):
        # Funcion que seleccionar producto desde PLP
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            final_url = self.config['url'] + url
            product = wait.until(EC.visibility_of_element_located(
                (By.XPATH, self.replace_param(xpath['product_page']['simple_product_url'], final_url))))
            product.click()
        except:
            success = False

        return self.assertTrue(success, "Order was not generated successfuly")

    def select_location(self, region, comuna):
        # function to select option
        driver = self.driver
        wait = WebDriverWait(driver, self.config['time_to_sleep'])
        success = True

        try:
            location = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@id='clickLocation']")))
            location.click()
            sidebar = wait.until(EC.visibility_of_element_located((By.XPATH, "//aside[contains(@class,'location')]")))

            select_region = wait.until(EC.element_to_be_clickable(
                (By.XPATH, self.replace_param(xpath['fill_inputs']['select_region'], region))))
            select_region.click()

            select_comuna = wait.until(EC.element_to_be_clickable(
                (By.XPATH, self.replace_param(xpath['fill_inputs']['select_comuna'], comuna))))
            select_comuna.click()

            continue_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath['checkout']['continue_to_payment'])))
            continue_button.click()



        except:
            success = False

        return self.assertTrue(success, "Select was not found")
