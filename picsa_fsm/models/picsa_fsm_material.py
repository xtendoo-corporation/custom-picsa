# Copyright 2026 Xtendoo Software SLU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class PicsaFSMMaterial(models.Model):
    _name = "picsa.fsm.material"
    _description = "Material PICSA en parte de trabajo"
    _order = "id asc"

    fsm_order_id = fields.Many2one(
        comodel_name="fsm.order",
        string="Parte de Trabajo",
        required=True,
        ondelete="cascade",
        index=True,
    )
    material_type = fields.Selection(
        selection=[
            ("installed", "Instalado"),
            ("removed", "Retirado"),
        ],
        string="Tipo",
        required=True,
        default="installed",
    )
    sequence = fields.Char(string="Nº")
    brand = fields.Char(string="Marca")
    model = fields.Char(string="Modelo")
    model_id = fields.Many2one(
        comodel_name="product.product",
        string="Modelo",
    )
    serial_number = fields.Char(string="Nº Serie")
    quantity = fields.Float(
        string="Cantidad",
        default=1.0,
    )
