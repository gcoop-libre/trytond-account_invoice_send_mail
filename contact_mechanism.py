# This file is part of contract_nube module.

from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['ContactMechanism']


class ContactMechanism:
    __name__ = 'party.contact_mechanism'
    __metaclass__ = PoolMeta

    administration_email = fields.Boolean('Adm. E-Mail', states={
        'invisible': Eval('type') != 'email',
        'readonly': ~Eval('active', True),
        }, depends=['value', 'type', 'active'])

    @staticmethod
    def default_administration_email():
        return False

    def on_change_type(self):
        super(ContactMechanism, self).on_change_type()
        self.administration_email = False
