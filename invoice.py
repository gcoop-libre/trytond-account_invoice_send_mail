# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta

__all__ = ['InvoiceReport']


class InvoiceReport:
    __name__ = 'account.invoice'
    __metaclass__ = PoolMeta

    @classmethod
    def execute(cls, ids, data):
        Invoice = Pool().get('account.invoice')

        res = super(InvoiceReport, cls).execute(ids, data)
        if len(ids) > 1:
            res = (res[0], res[1], True, res[3])
        else:
            invoice = Invoice(ids[0])
            report_name = 'factura'
            periodo = ''
            if invoice.invoice_date:
                periodo = invoice.invoice_date.strftime("%m%Y")
            else:
                periodo = str(invoice.id)
            if invoice.party:
                report_name = '%s-%s' % (report_name, invoice.party.rec_name)

            report_name += '-%s' % periodo

            if invoice.number:
                report_name = '%s-%s' % (report_name, invoice.number)

            res = (res[0], res[1], res[2], report_name)
        return res
