# Copyright 2026 Xtendoo Software SLU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class FSMIncident(models.Model):
    _name = "fsm.incident"
    _description = "Incidencia FSM"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "incident_date desc, id desc"

    name = fields.Char(
        string="Nombre de Incidencia",
        required=True,
        tracking=True,
    )
    fsm_order_id = fields.Many2one(
        comodel_name="fsm.order",
        string="Parte de Trabajo",
        required=True,
        ondelete="cascade",
        index=True,
    )
    responsible_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsable",
        tracking=True,
        domain=[("share", "=", False)],
    )
    incident_date = fields.Datetime(
        string="Fecha de Incidencia",
        default=fields.Datetime.now,
        tracking=True,
    )
    incident_type = fields.Selection(
        selection=[
            ("technical", "Técnica"),
            ("material", "Material"),
            ("customer", "Cliente"),
            ("scheduling", "Planificación"),
            ("other", "Otra"),
        ],
        string="Tipo de Incidencia",
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ("open", "Abierta"),
            ("in_progress", "En Proceso"),
            ("done", "Resuelta"),
            ("cancelled", "Cancelada"),
        ],
        string="Estado",
        default="open",
        required=True,
        tracking=True,
    )
    active = fields.Boolean(default=True)
