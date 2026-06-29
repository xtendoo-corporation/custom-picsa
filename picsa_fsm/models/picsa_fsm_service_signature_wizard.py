# Copyright 2026 Xtendoo Software SLU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import base64

from odoo import _, fields, models
from odoo.exceptions import UserError


class PicsaFSMServiceSignatureWizard(models.TransientModel):
    _name = "picsa.fsm.service.signature.wizard"
    _description = "Firma de servicio realizado PICSA"

    service_id = fields.Many2one(
        comodel_name="picsa.fsm.service",
        string="Servicio",
        required=True,
        readonly=True,
    )
    signature = fields.Binary(
        string="Firma",
        required=True,
        attachment=True,
    )

    def action_sign(self):
        self.ensure_one()
        service = self.service_id
        service.write({
            "signature": self.signature,
        })
        return {"type": "ir.actions.act_window_close"}

    def action_sign_and_send(self):
        self.ensure_one()
        self.action_sign()
        self._send_signed_report()
        return {"type": "ir.actions.act_window_close"}

    def _send_signed_report(self):
        self.ensure_one()
        order = self.service_id.fsm_order_id
        partner = order.contact_id or order.partner_id
        email_to = partner.email
        if not email_to:
            raise UserError(_("El contacto no tiene email informado."))

        report = self.env.ref("picsa_fsm.action_report_picsa_fsm_incident").sudo()
        pdf_content, dummy_format = report._render_qweb_pdf(report.id, [order.id])
        attachment = self.env["ir.attachment"].sudo().create({
            "name": "Parte de trabajo %s.pdf" % order.name,
            "type": "binary",
            "datas": base64.b64encode(pdf_content),
            "res_model": "fsm.order",
            "res_id": order.id,
            "mimetype": "application/pdf",
        })
        subject = _("Parte de trabajo %s firmado") % order.name
        body = _(
            "<p>Adjuntamos el parte de trabajo firmado correspondiente a %s.</p>"
        ) % order.name
        self.env["mail.mail"].sudo().create({
            "subject": subject,
            "body_html": body,
            "email_to": email_to,
            "attachment_ids": [(6, 0, attachment.ids)],
            "auto_delete": False,
        }).send()
