from magento import MagentoTestCase
import time



class TestCase(MagentoTestCase):

    def test_to_storepickup_checkmo(self):
        try:

            # ----- Parametrizacion de datos -----

            # Producto a utilizar en el test            
            product = self.config['test_parameters']['simple_product']['sku']
            url = self.config['test_parameters']['simple_product']['url']
            customer_email = self.config['test_parameters']['registered_user']['email']
            shipping_method = 'storepickup'
            user_data = self.config['test_parameters']['registered_user']
            payment_method = self.config['test_parameters']['payment_methods']['mercadopago']
            billing_address = self.config['test_parameters']['billing_address']
            # ---- Inicio de los pasos del Test ----
            who_pick = self.config['test_parameters']['registered_user']
            # Metodo inicial para que la pantalla sea maximizada
            self.maximize_windows()
            self.visit_product_page(product)
            # time.sleep(3)

            self.select_product_test(url)
            self.checkout_loader()
            # Metodo que presiona sobre el boton de "Agregar al carrito"
            self.add_simple_product()
            # Valida el mensaje que se muestra luego de agregar un producto al carrito
            self.validate_product_was_added()
            # Presiona en el boton de "Finalizar compra" que aparece en la sidebar al agregar un producto y lleva al carrito
            self.go_to_cart_from_minicart()
            self.checkout_loader()
            self.go_to_checkout()
            self.select_shipping_method(shipping_method)
            self.fill_customer_email(customer_email, shipping_method)
            self.select_store()
            self.fill_pickup_data(who_pick)
            # self.fill_new_shipping_address(user_data, billing_address)
            self.continue_to_payment_storepickup()
            self.fill_new_billing_address(user_data, billing_address)
            self.select_payment_method(payment_method)
            # # Presiona en el boton de "Pagar"
            #self.place_order()
            # # Valida que se muestra la pagina de exito
            #self.success_page()

            time.sleep(8)
            
        except AssertionError as e:
            raise AssertionError(self.generateExceptionReport(e))