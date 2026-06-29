# Copyright 2026 Xtendoo Software SLU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PicsaFSMService(models.Model):
    _name = "picsa.fsm.service"
    _description = "Servicio realizado PICSA"
    _order = "id asc"

    fsm_order_id = fields.Many2one(
        comodel_name="fsm.order",
        string="Parte de Trabajo",
        required=True,
        ondelete="cascade",
        index=True,
    )
    technician_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Técnico Asignado",
    )
    date_start = fields.Datetime(string="Fecha Inicio")
    date_end = fields.Datetime(string="Fecha Fin")
    intervention_method = fields.Selection(
        selection=[
            ("onsite", "Presencial"),
            ("remote", "Remoto"),
            ("phone", "Telefónico"),
            ("email", "Email"),
            ("other", "Otro"),
        ],
        string="Método Intervención",
    )
    km = fields.Float(string="Km")
    notes = fields.Text(string="Descripción")
    signature = fields.Binary(
        string="Firma",
        attachment=True,
        copy=False,
    )
    state = fields.Selection(
        selection=[
            ("draft", "En edición"),
            ("in_progress", "En Proceso"),
            ("to_invoice", "A facturar"),
            ("to_close", "A cerrar"),
            ("done", "Cerrada"),
        ],
        string="Estado",
        default="draft",
        required=True,
    )

    def init(self):
        self.env.cr.execute("""
            UPDATE picsa_fsm_service
               SET state = 'to_close'
             WHERE state = 'cancelled'
        """)

    @api.model_create_multi
    def create(self, vals_list):
        services = super().create(vals_list)
        services.mapped("fsm_order_id").filtered(
            lambda order: order.incident_state == "study"
        ).write({"incident_state": "in_process"})
        return services

    def write(self, vals):
        closed_services = self.filtered(lambda service: service.state == "done")
        allowed_closed_fields = {"state", "signature"}
        if closed_services and (
            set(vals) - allowed_closed_fields or vals.get("state") not in (None, "draft")
        ):
            raise UserError(_(
                "No se puede modificar un servicio cerrado. "
                "Pulsa Reabrir para volver a editarlo."
            ))
        return super().write(vals)

    def action_reopen(self):
        self.write({"state": "draft"})
        return True

    def action_open_signature_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Firmar Servicio"),
            "res_model": "picsa.fsm.service.signature.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_service_id": self.id,
            },
        }
