# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RMAOperation(models.Model):
    _name = "rma_operation"
    _description = "RMA Operation"
    _inherit = ["mixin.master_data"]

    direction = fields.Selection(
        string="Direction",
        selection=[
            ("customer", "RMA Customer"),
            ("supplier", "RMA Supplier"),
        ],
        required=True,
        default="customer",
    )
    receipt_policy_id = fields.Many2one(
        comodel_name="rma_policy",
        string="Receipt Policy",
        required=True,
        ondelete="restrict",
    )
    delivery_policy_id = fields.Many2one(
        comodel_name="rma_policy",
        string="Delivery Policy",
        required=True,
        ondelete="restrict",
    )
    rma_supplier_policy_id = fields.Many2one(
        comodel_name="rma_policy",
        string="RMA Supplier Policy",
        required=True,
        ondelete="restrict",
    )
    allowed_route_template_ids = fields.Many2many(
        comodel_name="rma_route_template",
        string="Allowed Route Template",
        relation="rel_rma_operation_2_rma_route_template",
    )
    default_route_template_id = fields.Many2one(
        comodel_name="rma_route_template",
        string="Default Route Template",
        ondelete="restrict",
    )
    source_picking_type_category_selection_method = fields.Selection(
        default="domain",
        selection=[("manual", "Manual"), ("domain", "Domain"), ("code", "Python Code")],
        string="Source Picking Type Category Selection Method",
        required=True,
    )
    source_picking_type_category_ids = fields.Many2many(
        comodel_name="picking_type_category",
        string="Source Picking Type Category",
        relation="rel_rma_operation_2_source_picking_type_category",
    )
    source_picking_type_category_domain = fields.Text(
        default="[]", string="Source Picking Type Category Domain"
    )
    source_picking_type_category_python_code = fields.Text(
        default="result = []", string="Source Picking Type Category Python Code"
    )

    source_picking_type_selection_method = fields.Selection(
        default="domain",
        selection=[("manual", "Manual"), ("domain", "Domain"), ("code", "Python Code")],
        string="Source Picking Type Selection Method",
        required=True,
    )
    source_picking_type_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        string="Source Picking Type",
        relation="rel_rma_operation_2_source_picking_type",
    )
    source_picking_type_domain = fields.Text(
        default="[]", string="Source Picking Type Domain"
    )
    source_picking_type_python_code = fields.Text(
        default="result = []", string="Source Picking Type Python Code"
    )
