from odoo import fields, models

class AccountMoveSendInherit(models.TransientModel):
    _inherit = 'account.move.send'

    l10n_es_edi_facturae_checkbox_xml = fields.Boolean(
        string="Generate Facturae edi file",
        default=False,
        company_dependent=True,
    )
