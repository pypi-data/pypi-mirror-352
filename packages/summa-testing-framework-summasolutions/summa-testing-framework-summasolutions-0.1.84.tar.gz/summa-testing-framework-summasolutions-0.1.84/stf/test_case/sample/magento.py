from stf.test_case.magento import MagentoTestCase


class TestCase(MagentoTestCase):

    def test_success_sample(self):
        try:
            self.assertTrue(True)
        except AssertionError as e:
            raise AssertionError(self.generateExceptionReport(e))

    def test_fail_sample(self):
        try:
            self.assertTrue(False)
        except AssertionError as e:
            raise AssertionError(self.generateExceptionReport(e))