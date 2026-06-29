# Copyright 2026 Xtendoo Software SLU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models, _


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    picsa_service_ids = fields.One2many(
        comodel_name="picsa.fsm.service",
        inverse_name="fsm_order_id",
        string="Servicios Realizados",
    )
    picsa_service_count = fields.Integer(
        string="Servicios Realizados",
        compute="_compute_picsa_counts",
    )
    incident_ids = fields.One2many(
        comodel_name="fsm.incident",
        inverse_name="fsm_order_id",
        string="Incidencias",
    )
    incident_count = fields.Integer(
        string="Incidencias",
        compute="_compute_picsa_counts",
    )
    latest_incident_id = fields.Many2one(
        comodel_name="fsm.incident",
        string="Última Incidencia",
        compute="_compute_picsa_counts",
    )

    def _compute_picsa_counts(self):
        for order in self:
            order.picsa_service_count = len(order.picsa_service_ids)
            order.incident_count = len(order.incident_ids)
            order.latest_incident_id = order.incident_ids[:1]

    def action_create_incident(self):
        self.ensure_one()
        incident = self.env["fsm.incident"].create({
            "name": _("%s - Incidencia") % self.name,
            "fsm_order_id": self.id,
            "responsible_id": self.responsible_id.user_id.id if self.responsible_id.user_id else self.env.user.id,
            "incident_date": fields.Datetime.now(),
        })
        return {
            "type": "ir.actions.act_window",
            "name": _("Incidencia"),
            "res_model": "fsm.incident",
            "res_id": incident.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_view_incidents(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "name": _("Incidencias"),
            "res_model": "fsm.incident",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.incident_ids.ids)],
            "context": {
                "default_fsm_order_id": self.id,
            },
        }
        if len(self.incident_ids) == 1:
            action.update({
                "view_mode": "form",
                "res_id": self.incident_ids.id,
            })
        return action
