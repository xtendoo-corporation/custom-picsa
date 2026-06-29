# Copyright 2026 Xtendoo Software SLU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import re

from odoo import api, fields, models


class PicsaFSMInterventionMethod(models.Model):
    _name = "picsa.fsm.intervention.method"
    _description = "Método de Intervención PICSA"
    _order = "sequence, id"

    name = fields.Char(string="Nombre", required=True, translate=True)
    code = fields.Char(string="Código", required=True)
    sequence = fields.Integer(string="Secuencia", default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_uniq", "unique(code)", "El código del método debe ser único."),
    ]

    def _generate_code_from_name(self, name):
        code = re.sub(r"[^a-zA-Z0-9\s]", "", (name or "").lower())
        code = re.sub(r"\s+", "_", code.strip()) or "method"
        base_code = code
        counter = 1
        while self.search_count([("code", "=", code)]):
            code = "%s_%s" % (base_code, counter)
            counter += 1
        return code

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = self._generate_code_from_name(vals.get("name"))
        return super().create(vals_list)
