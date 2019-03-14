# -*- coding: utf8 -*-
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import utils as eutils

from trytond.pool import Pool
from trytond.tools import get_smtp_server

import logging
logger = logging.getLogger(__name__)


class SendEmail(object):
    "SendEMail"

    @classmethod
    def get_report(cls, invoice):
        InvoiceReport = Pool().get('account.invoice', type='report')
        type_, data, print_, name = InvoiceReport.execute([invoice.id], {})
        name = name.replace(" ", "").lower()
        return (data, '%s.%s' % (name, type_))

    def send_email(self, invoice, file_data, filename,
            voucher_data=None, voucher_filename=None):
        "send_email"

        from_addr = invoice.company.party.email
        periodo = invoice.invoice_date.strftime("%m-%Y")
        code = ""

        if not from_addr:
            return

        to_addrs = []
        if hasattr(self.start, 'to_addr') and self.start.to_addr.value:
            to_addrs = [self.start.to_addr.value]

        code = invoice.party.name
        # creo el mensaje
        outer = MIMEMultipart()
        outer['Subject'] = '%s: Factura Electronica' \
            % invoice.company.party.name
        html = self.get_text_solicitud(code, periodo, invoice)

        outer['From'] = from_addr
        outer['To'] = ', '.join(to_addrs)
        outer['Date'] = eutils.formatdate()

        part2 = MIMEText(html, 'html', 'utf-8')
        outer.attach(part2)

        ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)

        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(file_data)
        # Encode the payload using Base64
        encoders.encode_base64(attachment)
        # Set the filename parameter
        attachment.add_header("Content-Disposition", "attachment",
            filename=filename)
        outer.attach(attachment)

        if voucher_data:
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(voucher_data)
            # Encode the payload using Base64
            encoders.encode_base64(attachment)
            # Set the filename parameter
            attachment.add_header("Content-Disposition", "attachment",
                filename=voucher_filename)
            outer.attach(attachment)
        try:
            server = get_smtp_server()
            server.sendmail(from_addr, to_addrs, outer.as_string())
            logger.info('sending invoice to %s' % ''.join(to_addrs))
            server.quit()
        except Exception, e:
            logger.error('SendInvoices when sending invoice to client %s',
                to_addrs, exc_info=True)
            raise Exception(str(e))

    def get_text_solicitud(self, code, periodo, invoice):
        html = """
        <html>
            <head></head>
            <style type="text/css">
            body { color: #666; font-family: Verdana; font-size: 0.75em}
            p { color: #666; font-family: Verdana;}
            h1 {color: #000; font-family: Arial;}
            h2 {color: #666; font-family: Verdana; font-size: 0.7em}
            thead {color: #666; font-family: Verdana; font-size: 0.7em}
            tbody {color: #666; font-family: Verdana; font-size: 0.7em}
            </style>
            <body>
                <p>Hola """ + invoice.party.name + """<br />
                Nos ponemos en contacto con usted, para enviarle la factura. <br />
                <table style="width:100%">
                <thead>
                <tr><h1>
                    <td><b>CLIENTE</b></td>
                    <td><b>NUMERO DE FACTURA</b></td>
                </h1></tr></thead>
                <tbody>
                <tr>
                    <td><FONT COLOR="#DF0101">""" + code + """</td>
                    <td><FONT COLOR="#DF0101">""" + invoice.number + """</td
                </tr>
                </tbody>
                </table>
                <p>Adjuntamos la Factura en PDF (Portable Document Format), para
                poder visualizarla es necesario que tenga un programa instalado.<br />
                </p>
                <p>Atentamente,<br/>
                 <a href='""" + invoice.company.party.website + """'>""" + invoice.company.party.name + """</a>
                <p>
                <h2><hr>""" + invoice.company.header + """</h2>
                </p>
                </p>
            </body>
        </html>
        """
        return html
