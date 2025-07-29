# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class LinkStockMoveRmaLine(models.TransientModel):
    _name = "link_stock_move_rma_line"
    _description = "Link Stock Move To RMA Line"

    @api.model
    def _default_model_id(self):
        model_name = self.env.context.get("active_model", False)
        criteria = [("model", "=", model_name)]
        return self.env["ir.model"].search(criteria)[0].id

    model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
        default=lambda self: self._default_model_id(),
    )
    allowed_stock_move_ids = fields.Many2many(
        string="Allowed Stock Moves",
        comodel_name="stock.move",
        compute="_compute_allowed_stock_move_ids",
        compute_sudo=True,
    )
    stock_move_ids = fields.Many2many(
        string="Stock Moves",
        comodel_name="stock.move",
        relation="rel_link_stock_move_2_rma_line",
        column1="wizard_id",
        column2="stock_move_id",
    )

    @api.depends(
        "model_id",
    )
    def _compute_allowed_stock_move_ids(self):
        for record in self:
            line_id = self.env.context.get("active_id", False)
            rma_line = self.env[self.model_id.model].browse(line_id)

            criteria = [
                ("product_id", "=", rma_line.product_id.id),
                ("state", "=", "done"),
                (
                    "picking_id.partner_id.commercial_partner_id.id",
                    "=",
                    rma_line.order_id.partner_id.id,
                ),
            ]

            if record.model_id.model == "rma_customer_line":
                rma_customer_in_type_id = self.env.ref(
                    "ssi_rma.picking_category_cri"
                ).id
                rma_customer_out_type_id = self.env.ref(
                    "ssi_rma.picking_category_cro"
                ).id
                criteria += [
                    ("customer_rma_line_ids", "=", False),
                    "|",
                    (
                        "picking_id.picking_type_category_id.id",
                        "=",
                        rma_customer_in_type_id,
                    ),
                    (
                        "picking_id.picking_type_category_id.id",
                        "=",
                        rma_customer_out_type_id,
                    ),
                ]
            else:
                rma_supplier_in_type_id = self.env.ref(
                    "ssi_rma.picking_category_sri"
                ).id
                rma_supplier_out_type_id = self.env.ref(
                    "ssi_rma.picking_category_sro"
                ).id
                criteria += [
                    ("supplier_rma_line_ids", "=", False),
                    "|",
                    (
                        "picking_id.picking_type_category_id.id",
                        "=",
                        rma_supplier_in_type_id,
                    ),
                    (
                        "picking_id.picking_type_category_id.id",
                        "=",
                        rma_supplier_out_type_id,
                    ),
                ]
            result = self.env["stock.move"].search(criteria).ids
            record.allowed_stock_move_ids = result

    def action_confirm(self):
        for record in self.sudo():
            record._confirm()

    def _confirm(self):
        self.ensure_one()
        line_id = self.env.context.get("active_id", False)
        rma_line = self.env[self.model_id.model].browse(line_id)
        stock_moves = []
        for sm in self.stock_move_ids:
            stock_moves.append((4, sm.id))
        rma_line.write(
            {
                "stock_move_ids": stock_moves,
            }
        )
