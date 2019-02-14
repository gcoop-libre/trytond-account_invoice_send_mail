try:
    from trytond.modules.account_invoice_send_mail.tests.test_send_mail import suite
except ImportError:
    from .test_send_mail import suite

__all__ = ['suite']
