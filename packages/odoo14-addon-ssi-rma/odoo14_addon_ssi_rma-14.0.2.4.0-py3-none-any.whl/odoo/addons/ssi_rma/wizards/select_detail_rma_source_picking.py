# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SelectDetailRmaSourcePicking(models.TransientModel):
    _name = "select_detail_rma_source_picking"
    _description = "Select Detail RMA Source Picking"

    wizard_id = fields.Many2one(
        string="Wizard",
        comodel_name="select_rma_source_picking",
        ondelete="cascade",
        required=True,
    )
    stock_valuation_layer_id = fields.Many2one(
        string="Stock Valuation Layer",
        comodel_name="stock.valuation.layer",
        required=True,
    )
    product_id = fields.Many2one(
        related="stock_valuation_layer_id.product_id",
    )
    currency_id = fields.Many2one(
        related="stock_valuation_layer_id.currency_id",
    )
    unit_cost = fields.Monetary(
        related="stock_valuation_layer_id.unit_cost",
    )
    origin_qty = fields.Float(
        string="Origin Qty.",
        compute="_compute_origin_qty",
        compute_sudo=True,
    )
    rma_qty = fields.Float(
        string="RMA Qty.",
        required=True,
        default=0.0,
    )

    @api.constrains(
        "rma_qty",
    )
    def _constrains_rma_qty(self):
        for record in self.sudo():
            if record.rma_qty > record.origin_qty:
                str_msg = _("RMA Qty. exceed origin Qty.")
                raise UserError(str_msg)

    @api.depends(
        "stock_valuation_layer_id",
    )
    def _compute_origin_qty(self):
        for record in self:
            result = 0.0
            if record.stock_valuation_layer_id:
                result = abs(record.stock_valuation_layer_id.quantity)
            record.origin_qty = result

    def action_confirm(self):
        for record in self.sudo():
            record._confirm()

    def _confirm(self):
        self.ensure_one()
