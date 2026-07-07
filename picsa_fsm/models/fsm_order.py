# Copyright 2026 Xtendoo Software SLU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    stage_display = fields.Html(
        string="Estado",
        compute="_compute_stage_display",
    )

    description = fields.Html(
        string="Servicios a realizar",
        required=True,
        tracking=False,
    )
    picsa_service_ids = fields.One2many(
        comodel_name="picsa.fsm.service",
        inverse_name="fsm_order_id",
        string="Servicios Realizados",
    )
    picsa_service_count = fields.Integer(
        string="Servicios Realizados",
        compute="_compute_picsa_counts",
    )
    invoice_count = fields.Integer(
        string="Facturas",
        compute="_compute_invoice_count",
    )
    incident_name = fields.Char(
        string="Nombre de Incidencia",
    )
    incident_responsible_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Responsable",
    )
    incident_open_date = fields.Datetime(
        string="Abierto",
        default=fields.Datetime.now,
        readonly=True,
    )
    incident_date = fields.Datetime(
        string="Fecha de Incidencia",
        default=fields.Datetime.now,
    )
    incident_type_id = fields.Many2one(
        comodel_name="picsa.fsm.incident.type",
        string="Tipo de Incidencia",
    )
    incident_update_date = fields.Datetime(
        string="Actualizado",
        related="write_date",
        readonly=True,
    )
    incident_state = fields.Selection(
        selection=[
            ("study", "En estudio"),
            ("in_process", "En proceso"),
            ("review", "En revisión"),
        ],
        string="Estado",
        default="study",
        required=True,
    )
    material_installed_ids = fields.One2many(
        comodel_name="picsa.fsm.material",
        inverse_name="fsm_order_id",
        string="Material Instalado",
        domain=[("material_type", "=", "installed")],
    )
    material_removed_ids = fields.One2many(
        comodel_name="picsa.fsm.material",
        inverse_name="fsm_order_id",
        string="Material Retirado",
        domain=[("material_type", "=", "removed")],
    )

    @api.depends("stage_id")
    def _compute_stage_display(self):
        for order in self:
            if order.stage_id:
                color = order.stage_id.color
                name = order.stage_id.name
                order.stage_display = (
                    f'<span class="badge" style="background-color: {color};">{name}</span>'
                )
            else:
                order.stage_display = False

    def _compute_picsa_counts(self):
        for order in self:
            order.picsa_service_count = len(order.picsa_service_ids)

    def _compute_invoice_count(self):
        for order in self:
            order.invoice_count = self.env["account.move"].search_count(
                order._get_picsa_invoice_domain()
            )

    def _get_picsa_invoice_domain(self):
        self.ensure_one()
        return [
            ("move_type", "=", "out_invoice"),
            ("invoice_origin", "=", self.name),
        ]

    def _get_picsa_materials_with_product(self):
        self.ensure_one()
        return (
            self.material_installed_ids | self.material_removed_ids
        ).filtered("model_id").sorted("id")

    def _prepare_picsa_sale_order_lines(self):
        self.ensure_one()
        lines = []
        for material in self._get_picsa_materials_with_product():
            product = material.model_id
            lines.append((0, 0, {
                "product_id": product.id,
                "name": product.display_name,
                "product_uom_qty": material.quantity or 1.0,
                "price_unit": product.lst_price,
            }))
        return lines

    def _get_picsa_product_customer_tax_ids(self, product):
        if not self._picsa_can_use_account_tax_records():
            return []
        self.env.cr.execute(
            """
            SELECT rel.tax_id
              FROM product_taxes_rel rel
              JOIN product_product product
                ON product.product_tmpl_id = rel.prod_id
              JOIN account_tax tax
                ON tax.id = rel.tax_id
             WHERE product.id = %s
               AND (tax.company_id IS NULL OR tax.company_id = %s)
               AND COALESCE(tax.active, TRUE)
             ORDER BY rel.tax_id
            """,
            (product.id, self.company_id.id),
        )
        return [row[0] for row in self.env.cr.fetchall()]

    def _picsa_can_use_account_tax_records(self):
        self.env.cr.execute(
            """
            SELECT EXISTS (
                SELECT 1
                  FROM information_schema.columns
                 WHERE table_name = 'account_tax'
                   AND column_name = 'aeat_equivalent_tax_id'
            )
            """
        )
        return self.env.cr.fetchone()[0]

    def _prepare_picsa_invoice_lines(self):
        self.ensure_one()
        lines = []
        for material in self._get_picsa_materials_with_product():
            product = material.model_id
            account = (
                product.property_account_income_id
                or product.categ_id.property_account_income_categ_id
            )
            if not account:
                raise UserError(_(
                    "El producto %s no tiene cuenta de ingresos configurada."
                ) % product.display_name)
            lines.append((0, 0, {
                "product_id": product.id,
                "name": product.display_name,
                "quantity": material.quantity or 1.0,
                "price_unit": product.lst_price,
                "account_id": account.id,
                "tax_ids": [(6, 0, self._get_picsa_product_customer_tax_ids(product))],
            }))
        return lines

    def _check_picsa_material_lines(self, lines):
        if not lines:
            raise UserError(_(
                "Añade al menos un producto en Material Instalado o "
                "Material Retirado antes de crear el documento."
            ))

    def action_print_order(self):
        self.ensure_one()
        return self.env.ref(
            "picsa_fsm.action_report_picsa_fsm_incident"
        ).report_action(self)

    def action_create_sale_order(self):
        self.ensure_one()
        order_lines = self._prepare_picsa_sale_order_lines()
        self._check_picsa_material_lines(order_lines)
        action = super().action_create_sale_order()
        sale_order = self.env["sale.order"].browse(action.get("res_id"))
        sale_order.write({"order_line": order_lines})
        return action

    def action_create_invoice(self):
        self.ensure_one()
        if self.invoice_count:
            raise UserError(_("Este parte de trabajo ya tiene una factura relacionada."))
        invoice_lines = self._prepare_picsa_invoice_lines()
        self._check_picsa_material_lines(invoice_lines)
        invoice = self.env["account.move"].with_user(SUPERUSER_ID).create({
            "move_type": "out_invoice",
            "partner_id": self.partner_id.id,
            "invoice_origin": self.name,
            "invoice_line_ids": invoice_lines,
        })
        return {
            "type": "ir.actions.act_window",
            "name": _("Factura"),
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": invoice.id,
            "target": "current",
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Facturas"),
            "res_model": "account.move",
            "view_mode": "tree,form",
            "domain": self._get_picsa_invoice_domain(),
            "context": {"create": False},
        }

    def init(self):
        self.env.cr.execute("""
            UPDATE fsm_order
               SET incident_state = 'study'
             WHERE incident_state IS NULL
        """)
