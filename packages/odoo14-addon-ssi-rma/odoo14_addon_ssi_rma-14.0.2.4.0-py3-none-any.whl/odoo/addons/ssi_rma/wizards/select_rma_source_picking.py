# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SelectRmaSourcePicking(models.TransientModel):
    _name = "select_rma_source_picking"
    _description = "Select RMA Source Picking"

    @api.model
    def _default_model_id(self):
        model_name = self.env.context.get("active_model", False)
        criteria = [("model", "=", model_name)]
        return self.env["ir.model"].search(criteria)[0].id

    @api.model
    def _default_order_id(self):
        return self.env.context.get("active_id", False)

    model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
        default=lambda self: self._default_model_id(),
    )
    order_id = fields.Integer(
        string="RMA Order ID",
        default=lambda self: self._default_order_id(),
    )
    picking_id = fields.Many2one(
        string="# Source Picking",
        comodel_name="stock.picking",
    )
    allowed_stock_picking_ids = fields.Many2many(
        string="Allowed Stock Pickings",
        comodel_name="stock.picking",
        compute="_compute_allowed_stock_picking_ids",
        compute_sudo=True,
    )
    detail_ids = fields.One2many(
        string="Details",
        comodel_name="select_detail_rma_source_picking",
        inverse_name="wizard_id",
    )

    @api.depends(
        "model_id",
    )
    def _compute_allowed_stock_picking_ids(self):
        for record in self:
            rma = self.env[record.model_id.model].browse(record.order_id)
            criteria = [
                ("partner_id.commercial_partner_id.id", "=", rma.partner_id.id),
                ("state", "=", "done"),
                "|",
                (
                    "picking_type_category_id",
                    "in",
                    rma.allowed_source_picking_type_category_ids.ids,
                ),
                ("picking_type_id", "in", rma.allowed_source_picking_type_ids.ids),
            ]
            result = self.env["stock.picking"].search(criteria).ids
            record.allowed_stock_picking_ids = result

    def action_reload_detail(self):
        for record in self.sudo():
            result = record._reload_detail()
        return result

    def action_confirm(self):
        for record in self.sudo():
            record._confirm()

    def _confirm(self):
        self.ensure_one()
        rma = self.env[self.model_id.model].browse(self.order_id)
        rma.write(
            {
                "source_picking_id": self.picking_id.id,
            }
        )
        rma.line_ids.unlink()
        detail_data = []
        for detail in self.detail_ids.filtered(lambda r: r.rma_qty > 0.0):
            data = {
                "product_id": detail.product_id.id,
                "name": detail.product_id.display_name,
                "uom_quantity": detail.rma_qty,
                "uom_id": detail.product_id.uom_id.id,
                "price_unit": detail.unit_cost,
                "source_stock_move_id": detail.stock_valuation_layer_id.stock_move_id.id,
            }
            detail_data.append((0, 0, data))
        rma.write(
            {
                "line_ids": detail_data,
            }
        )

    def _reload_detail(self):
        self.ensure_one()
        self.detail_ids.unlink()
        for svl in self.picking_id.stock_valuation_layer_ids.filtered(
            lambda r: r.quantity != 0.0
        ):
            data = {
                "stock_valuation_layer_id": svl.id,
                "wizard_id": self.id,
            }
            self.env["select_detail_rma_source_picking"].create(data)
        wizard = self.env.ref("ssi_rma.select_rma_source_picking_action").read()[0]
        wizard.update(
            {
                "res_id": self.id,
                "active_id": self.env.context.get("active_id", False),
                "active_model": self.env.context.get("active_model", False),
            }
        )
        return wizard
