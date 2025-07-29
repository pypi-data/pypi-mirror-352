# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RMARouteTemplate(models.Model):
    _name = "rma_route_template"
    _description = "RMA Route Template"
    _inherit = ["mixin.master_data"]

    inbound_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="In Bound Route",
        required=True,
        ondelete="restrict",
    )
    outbound_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Out Bound Route",
        required=True,
        ondelete="restrict",
    )
    inbound_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="In Bound Warehouse",
        required=True,
        ondelete="restrict",
    )
    outbound_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Out Bound Warehouse",
        required=True,
        ondelete="restrict",
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="RMA Location",
        required=True,
        ondelete="restrict",
    )
    partner_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Partner Location",
        required=False,
        ondelete="restrict",
    )
    customer_to_supplier = fields.Boolean(
        string="The customer will send to the supplier", default=False
    )
    supplier_to_customer = fields.Boolean(
        string="The supplier will send to the customer", default=False
    )
