# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move"]

    customer_rma_line_ids = fields.Many2many(
        string="RMA Customer Line",
        comodel_name="rma_customer_line",
        relation="rma_customer_line_stock_move_rel",
        column1="move_id",
        column2="line_id",
        copy=False,
    )
    supplier_rma_line_ids = fields.Many2many(
        string="RMA Supplier Line",
        comodel_name="rma_supplier_line",
        relation="rma_supplier_line_stock_move_rel",
        column1="move_id",
        column2="line_id",
        copy=False,
    )
