# Copyright 2026 Xtendoo Software SLU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class PicsaFSMIncidentType(models.Model):
    _name = "picsa.fsm.incident.type"
    _description = "Tipo de Incidencia PICSA"
    _order = "name"

    name = fields.Char(
        string="Nombre",
        required=True,
        translate=True,
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "El tipo de incidencia debe ser único."),
    ]
