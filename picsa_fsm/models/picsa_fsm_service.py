# Copyright 2026 Xtendoo Software SLU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class PicsaFSMService(models.Model):
    _name = "picsa.fsm.service"
    _description = "Servicio realizado PICSA"
    _order = "date_start desc, id desc"
    _rec_name = "display_name"

    display_name = fields.Char(
        string="Servicio",
        compute="_compute_display_name",
    )

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
    state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("in_progress", "En Proceso"),
            ("done", "Realizado"),
            ("cancelled", "Cancelado"),
        ],
        string="Estado",
        default="draft",
        required=True,
    )

    def _compute_display_name(self):
        for service in self:
            service.display_name = "#%s - %s" % (
                service.id or "",
                service.technician_id.name or "Servicio realizado",
            )
