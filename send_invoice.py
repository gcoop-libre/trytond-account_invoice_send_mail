# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from .send_mail import SendEmail

from trytond.model import fields, ModelView
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.wizard import Wizard, StateView, Button, StateTransition
from trytond.transaction import Transaction
import logging

__all__ = ['SendInvoiceReport', 'SendInvoiceReportStart']

logger = logging.getLogger(__name__)


class SendInvoiceReportStart(ModelView):
    'Send Invoice Start'
    __name__ = 'account_invoice_send_mail.send_invoice.start'

    party = fields.Many2One('party.party', 'Party', required=True,
        readonly=True)
    to_addr = fields.Many2One('party.contact_mechanism', 'Mail',
                           domain=[
                               ('party', '=', Eval('party')),
                               ('type', '=', 'email'),
                           ], depends=['party'], required=True)

    @staticmethod
    def default_party():
        Invoice = Pool().get('account.invoice')
        invoice = Invoice(Transaction().context['active_id'])
        return invoice.party.id


class SendInvoiceReport(Wizard, SendEmail):
    'SendInvoiceReport'
    __name__ = 'account_invoice_send_mail.send_invoice'

    @classmethod
    def __setup__(cls):
        super(SendInvoiceReport, cls).__setup__()
        cls._error_messages.update({
            'wrong_state':
            u'Factura en estado %(state)s. No puede ser enviada',
            'no_rechazado':
            u'La factura no tiene transacciones rechazadas.',
            'send_invoice_error':
            u'Error al enviar la factura %(exception)s.',
        })

    start = StateView('account_invoice_send_mail.send_invoice.start',
        'account_invoice_send_mail.send_invoice_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'send_invoice', 'tryton-ok', True),
            ])
    send_invoice = StateTransition()

    @classmethod
    def get_voucher(cls, invoice):
        pool = Pool()
        Voucher = pool.get('account.voucher')
        VoucherReport = pool.get('account.voucher', type='report')
        vouchers = []
        for payment_line in invoice.payment_lines:
            if payment_line.origin and payment_line.origin.__class__ == Voucher:
                vouchers.append(payment_line.origin)
        type_, data, print_, name = VoucherReport.execute(
            [vo.id for vo in vouchers], {})
        name = name.replace(" ", "").lower()
        return (data, '%s.%s' % (name, type_))

    def transition_send_invoice(self):
        pool = Pool()
        Invoice = pool.get('account.invoice')
        try:
            Voucher = pool.get('account.voucher')
        except KeyError:
            Voucher = None

        invoice = Invoice(Transaction().context['active_id'])
        if invoice:
            if invoice.state not in ['posted', 'paid']:
                self.raise_user_error('wrong_state', {
                        'state': invoice.state.capitalize(),
                        })
            try:
                logger.info("factura: %s numero: %s customer: %s" %
                    (str(invoice.id), invoice.number, invoice.party.name))
                (file_data, filename) = self.get_report(invoice)
                voucher_data = voucher_filename = None
                if Voucher and invoice.state == 'paid' and not invoice.annulled:
                    (voucher_data, voucher_filename) = self.get_voucher(invoice)
                self.send_email(invoice, file_data, filename,
                    voucher_data, voucher_filename)
            except Exception, e:
                logger.error('error when sending invoice to client %s', str(e),
                    exc_info=True)
                self.raise_user_error('send_invoice_error', {
                        'exception': repr(e),
                        })
        return 'end'
