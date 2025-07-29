# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RMACustomer(models.Model):
    _name = "rma_customer"
    _description = "RMA Customer"
    _inherit = ["rma_order_mixin"]

    type = fields.Selection(
        string="Type",
        default="customer",
    )
    operation_id = fields.Many2one(
        domain=[
            ("direction", "=", "customer"),
        ],
    )
    line_ids = fields.One2many(
        comodel_name="rma_customer_line",
        inverse_name="order_id",
    )
