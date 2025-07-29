# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RMASupplier(models.Model):
    _name = "rma_supplier"
    _description = "RMA Supplier"
    _inherit = ["rma_order_mixin"]

    type = fields.Selection(
        string="Type",
        default="supplier",
    )
    operation_id = fields.Many2one(
        domain=[
            ("direction", "=", "supplier"),
        ],
    )
    line_ids = fields.One2many(
        comodel_name="rma_supplier_line",
        inverse_name="order_id",
    )
