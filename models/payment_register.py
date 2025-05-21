from odoo import models, api
from odoo.exceptions import UserError
import json
from datetime import date, datetime
import pprint

class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _create_payments(self):
        payments = super()._create_payments()
        #raise UserError("payment created:\n%s"% pprint.pformat(payments.read()))
        for payment in payments:
            journal = payment.journal_id
            if journal.type != 'cash':
                continue

            StatementLine = self.env['account.bank.statement.line']

            # Determine if payment is cash in or out
            amount = payment.amount_signed
            #raise UserError("payment :\n%s"% pprint.pformat(payment.read()))

            # Check if a matching unlinked line already exists (avoid duplication)
            existing_line = StatementLine.search([
                ('journal_id', '=', journal.id),
                ('date', '=', payment.date),
                ('amount', '=', amount),
                ('partner_id', '=', payment.partner_id.id),
                ('statement_id', '=', False),
            ], limit=1)
            #raise UserError("statement line retrieved:\n%s"% pprint.pformat(existing_line.read()))
            #  if no matching statement line create one
            if not existing_line:
                #raise UserError("payment line retrieved:\n%s"% pprint.pformat(payment.read()))
                StatementLine.create({
                    'journal_id': journal.id,
                    'payment_ref': payment.ref or payment.name,
                    'amount': amount,
                    'partner_id': payment.partner_id.id,
                    'date': payment.date,
                })

        return payments
