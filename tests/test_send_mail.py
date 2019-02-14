import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class SendMailTestCase(ModuleTestCase):
    'SendMailTestCase module'
    module = 'account_invoice_send_mail'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            SendMailTestCase))
    return suite
