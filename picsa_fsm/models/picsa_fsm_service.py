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
    intervention_method_id = fields.Many2one(
        comodel_name="picsa.fsm.intervention.method",
        string="Método Intervención",
        ondelete="restrict",
    )
    intervention_method = fields.Selection(
        selection=[],
        string="Método Intervención antiguo",
    )
    km = fields.Float(string="Km")
    notes = fields.Text(string="Descripción")
    signature = fields.Binary(
        string="Firma",
        attachment=True,
        copy=False,
    )
    state_id = fields.Many2one(
        comodel_name="picsa.fsm.service.state",
        string="Estado",
        default=lambda self: self._get_default_state(),
        required=True,
        ondelete="restrict",
    )
    state_code = fields.Char(
        related="state_id.code",
        string="Código Estado",
        readonly=True,
    )
    state = fields.Selection(
        selection=[],
        string="Estado antiguo",
    )

    def _get_default_state(self):
        self.env.cr.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'picsa_fsm_service_state')"
        )
        if not self.env.cr.fetchone()[0]:
            return False
        state = self.env["picsa.fsm.service.state"].search(
            [("is_default", "=", True)], limit=1
        )
        if not state:
            state = self.env["picsa.fsm.service.state"].search([], limit=1)
        return state.id

    def init(self):
        self.env.cr.execute("""
            UPDATE picsa_fsm_service
               SET state = 'to_close'
             WHERE state = 'cancelled'
        """)

    @api.model_create_multi
    def create(self, vals_list):
        services = super().create(vals_list)
        progress_stage = self.env["fsm.stage"].search([
            ("code", "=", "in_process"),
            ("company_id", "in", [self.env.company.id, False]),
        ], limit=1)
        if progress_stage:
            services.mapped("fsm_order_id").filtered(
                lambda order: order.stage_id.code == "study"
            ).write({"stage_id": progress_stage.id})
        return services

    def write(self, vals):
        closed_services = self.filtered(lambda service: service.state_code == "done")
        allowed_closed_fields = {"state_id", "signature"}
        if closed_services and (
            set(vals) - allowed_closed_fields
            or (
                vals.get("state_id")
                and self.env["picsa.fsm.service.state"].browse(vals["state_id"]).code != "draft"
            )
        ):
            raise UserError(_(
                "No se puede modificar un servicio cerrado. "
                "Pulsa Reabrir para volver a editarlo."
            ))
        return super().write(vals)

    def action_reopen(self):
        draft_state = self.env["picsa.fsm.service.state"].search(
            [("code", "=", "draft")],
            limit=1,
        )
        self.write({"state_id": draft_state.id})
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
