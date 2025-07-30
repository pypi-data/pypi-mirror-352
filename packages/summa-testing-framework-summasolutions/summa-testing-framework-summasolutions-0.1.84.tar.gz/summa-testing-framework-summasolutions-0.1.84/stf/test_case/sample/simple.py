from stf.test_case.magento import BaseTestCase


class TestCase(BaseTestCase):

    def test_fail(self):
        try:
            self.assertTrue(False)
        except AssertionError as e:
            raise AssertionError(self.generateExceptionReport(e))

    def test_create_new_customer(self):
        pass
