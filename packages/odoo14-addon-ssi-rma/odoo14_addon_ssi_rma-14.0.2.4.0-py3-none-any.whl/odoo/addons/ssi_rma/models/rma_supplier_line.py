# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RMASupplierLine(models.Model):
    _name = "rma_supplier_line"
    _description = "RMA Supplier Line"
    _inherit = ["rma_line_mixin"]

    order_id = fields.Many2one(comodel_name="rma_supplier", string="Order")
