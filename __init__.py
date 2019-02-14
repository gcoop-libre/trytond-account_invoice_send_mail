# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import invoice
from . import send_invoice
from . import contact_mechanism


def register():
    Pool.register(
        send_invoice.SendInvoiceReportStart,
        contact_mechanism.ContactMechanism,
        module='account_invoice_send_mail', type_='model')
    Pool.register(
        invoice.InvoiceReport,
        module='account_invoice_send_mail', type_='report')
    Pool.register(
        send_invoice.SendInvoiceReport,
        module='account_invoice_send_mail', type_='wizard')
