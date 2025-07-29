# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class RMALineMixin(models.AbstractModel):
    _name = "rma_line_mixin"
    _description = "RMA Line Mixin"
    _abstract = True
    _inherit = [
        "mixin.product_line_price",
    ]

    order_id = fields.Many2one(
        comodel_name="rma_order_mixin",
        string="RMA Order",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(string="Sequence", required=True, default=10)
    allowed_lot_ids = fields.Many2many(
        string="Allowed Lots",
        comodel_name="stock.production.lot",
        compute="_compute_allowed_lot_ids",
        store=False,
    )
    lot_id = fields.Many2one(comodel_name="stock.production.lot", string="Lot")
    source_stock_move_id = fields.Many2one(
        string="Source Stock Move",
        comodel_name="stock.move",
        readonly=True,
    )
    stock_move_ids = fields.Many2many(
        comodel_name="stock.move",
        string="Stock Moves",
        column1="line_id",
        column2="move_id",
    )
    product_id = fields.Many2one(
        required=True,
    )
    uom_id = fields.Many2one(
        required=True,
    )
    qty_to_receive = fields.Float(
        string="Qty to Receive", compute="_compute_qty_to_receive", store=True
    )
    qty_incoming = fields.Float(
        string="Qty Incoming",
        compute="_compute_qty_incoming",
    )
    qty_received = fields.Float(
        string="Qty Received", compute="_compute_qty_received", store=True
    )
    qty_to_deliver = fields.Float(
        string="Qty to Deliver", compute="_compute_qty_to_deliver", store=True
    )
    qty_outgoing = fields.Float(
        string="Qty Outgoing",
        compute="_compute_qty_outgoing",
    )
    qty_delivered = fields.Float(
        string="Qty Delivered", compute="_compute_qty_delivered", store=True
    )

    need_delivery = fields.Boolean(
        string="Need Delivery",
        compute="_compute_need_delivery",
        store=True,
    )
    percent_delivery = fields.Float(
        string="Percent Delivery",
        compute="_compute_percent_delivery",
        store=True,
    )
    delivery_complete = fields.Boolean(
        string="Delivery Complete",
        compute="_compute_delivery_complete",
        store=True,
    )
    need_reception = fields.Boolean(
        string="Need Reception",
        compute="_compute_need_reception",
        store=True,
    )
    percent_reception = fields.Float(
        string="Percent Reception",
        compute="_compute_percent_reception",
        store=True,
    )
    reception_complete = fields.Boolean(
        string="Reception Complete",
        compute="_compute_reception_complete",
        store=True,
    )
    rma_state = fields.Selection(
        related="order_id.state",
    )

    @api.model
    def _get_qty_field_trigger(self):
        result = [
            "order_id",
            "order_id.operation_id",
            "uom_quantity",
            "qty_received",
            "qty_delivered",
        ]
        return result

    @api.depends(
        "uom_quantity",
        "qty_delivered",
    )
    def _compute_percent_delivery(self):
        for record in self:
            result = 0.0
            try:
                result = record.qty_delivered / record.uom_quantity
            except ZeroDivisionError:
                result = 0.0
            record.percent_delivery = result

    @api.depends(
        "order_id",
        "order_id.operation_id",
    )
    def _compute_need_delivery(self):
        for record in self:
            result = False
            if (
                record.order_id.operation_id
                and record.order_id.operation_id.delivery_policy_id
                and len(record.order_id.operation_id.delivery_policy_id.rule_ids) > 0
            ):
                result = True
            record.need_delivery = result

    @api.depends(
        "need_delivery",
        "percent_delivery",
    )
    def _compute_delivery_complete(self):
        for record in self:
            result = False
            if (
                record.need_delivery and record.percent_delivery == 1.0
            ) or not record.need_delivery:
                result = True
            record.delivery_complete = result

    @api.depends(
        "uom_quantity",
        "qty_received",
    )
    def _compute_percent_reception(self):
        for record in self:
            result = 0.0
            try:
                result = record.qty_received / record.uom_quantity
            except ZeroDivisionError:
                result = 0.0
            record.percent_reception = result

    @api.depends(
        "order_id",
        "order_id.operation_id",
    )
    def _compute_need_reception(self):
        for record in self:
            result = False
            if (
                record.order_id.operation_id
                and record.order_id.operation_id.receipt_policy_id
                and len(record.order_id.operation_id.receipt_policy_id.rule_ids) > 0
            ):
                result = True
            record.need_reception = result

    @api.depends(
        "need_reception",
        "percent_reception",
    )
    def _compute_reception_complete(self):
        for record in self:
            result = False
            if (
                record.need_reception and record.percent_reception == 1.0
            ) or not record.need_reception:
                result = True
            record.reception_complete = result

    @api.depends(
        "product_id",
    )
    def _compute_allowed_lot_ids(self):
        for record in self:
            result = []
            if record.product_id:
                Lot = self.env["stock.production.lot"]
                result = Lot.search(
                    [
                        ("product_id", "=", record.product_id.id),
                    ]
                ).ids
            record.allowed_lot_ids = result

    @api.depends(lambda self: self._get_qty_field_trigger())
    def _compute_qty_to_receive(self):
        for record in self:
            policy = record.order_id.operation_id.receipt_policy_id
            record.qty_to_receive = policy._compute_quantity(record)

    @api.depends(
        "stock_move_ids",
        "stock_move_ids.state",
        "stock_move_ids.product_qty",
    )
    def _compute_qty_incoming(self):
        for record in self:
            states = [
                "draft",
                "waiting",
                "confirmed",
                "partially_available",
                "assigned",
            ]
            record.qty_incoming = record._get_rma_move_qty(states, "in")

    @api.depends(
        "stock_move_ids",
        "stock_move_ids.state",
        "stock_move_ids.product_qty",
    )
    def _compute_qty_received(self):
        for record in self:
            states = [
                "done",
            ]
            record.qty_received = record._get_rma_move_qty(states, "in")

    @api.depends(lambda self: self._get_qty_field_trigger())
    def _compute_qty_to_deliver(self):
        for record in self:
            policy = record.order_id.operation_id.delivery_policy_id
            record.qty_to_deliver = policy._compute_quantity(record)

    @api.depends(
        "stock_move_ids",
        "stock_move_ids.state",
        "stock_move_ids.product_qty",
    )
    def _compute_qty_outgoing(self):
        for record in self:
            states = [
                "draft",
                "waiting",
                "confirmed",
                "partially_available",
                "assigned",
            ]
            record.qty_outgoing = record._get_rma_move_qty(states, "out")

    @api.depends(
        "stock_move_ids",
        "stock_move_ids.state",
        "stock_move_ids.product_qty",
    )
    def _compute_qty_delivered(self):
        for record in self:
            states = [
                "done",
            ]
            record.qty_delivered = record._get_rma_move_qty(states, "out")

    @api.onchange(
        "product_id",
    )
    def onchange_lot_id(self):
        self.lot_id = False

    @api.onchange(
        "product_id",
        "uom_quantity",
        "uom_id",
        "pricelist_id",
        "lot_id",
    )
    def onchange_price_unit(self):
        _super = super(RMALineMixin, self)
        self.price_unit = 0.0
        Quant = self.env["stock.quant"]
        if self.lot_id and self.uom_quantity and self.uom_quantity != 0.0:
            self.price_unit = 0.0
            if self.order_id.type == "customer":
                location = self.order_id.partner_id.property_stock_customer
            else:
                location = self.order_id.route_template_id.location_id
            criteria = [
                ("product_id", "=", self.product_id.id),
                ("lot_id", "=", self.lot_id.id),
                ("location_id", "=", location.id),
            ]
            quants = Quant.search(criteria)

            if quants:
                quant = quants[-1]
                try:
                    self.price_unit = (
                        quant.with_context(bypass_location_restriction=True).value
                        / quant.quantity
                    )
                except ZeroDivisionError:
                    self.price_unit = 0.0
        else:
            _super.onchange_price_unit()

    def _get_rma_move_qty(self, states, direction):
        result = 0.0
        rma_location = self.order_id.route_template_id.location_id
        if direction == "in":
            for move in self.stock_move_ids.filtered(
                lambda m: m.state in states and m.location_dest_id == rma_location
            ):
                result += move.product_qty
        else:
            for move in self.stock_move_ids.filtered(
                lambda m: m.state in states
                and m.location_dest_id.usage in ["customer", "supplier"]
            ):
                result += move.product_qty
        return result

    def _create_reception(self):
        self.ensure_one()
        group = self.order_id.group_id
        qty = self.qty_to_receive
        values = self._get_receipt_procurement_data()

        procurements = []
        try:
            procurement = group.Procurement(
                self.product_id,
                qty,
                self.uom_id,
                values.get("location_id"),
                values.get("origin"),
                values.get("origin"),
                self.env.company,
                values,
            )

            procurements.append(procurement)
            self.env["procurement.group"].with_context(rma_route_check=[True]).run(
                procurements
            )
        except UserError as error:
            raise UserError(error)

    def _create_delivery(self):
        self.ensure_one()
        group = self.order_id.group_id
        qty = self.qty_to_deliver
        values = self._get_delivery_procurement_data()

        procurements = []
        try:
            procurement = group.Procurement(
                self.product_id,
                qty,
                self.uom_id,
                values.get("location_id"),
                values.get("origin"),
                values.get("origin"),
                self.env.company,
                values,
            )

            procurements.append(procurement)
            self.env["procurement.group"].with_context(rma_route_check=[True]).run(
                procurements
            )
        except UserError as error:
            raise UserError(error)

    def _get_receipt_procurement_data(self):
        group = self.order_id.group_id
        origin = self.order_id.name
        warehouse = self.order_id.route_template_id.inbound_warehouse_id
        location = self.order_id.route_template_id.location_id
        route = self.order_id.route_template_id.inbound_route_id
        result = {
            "name": self.order_id.name,
            "group_id": group,
            "origin": origin,
            "warehouse_id": warehouse,
            "date_planned": fields.Datetime.now(),
            "product_id": self.product_id.id,
            "product_qty": self.qty_to_receive,
            "partner_id": self.order_id.partner_id.id,
            "product_uom": self.uom_id.id,
            "location_id": location,
            "route_ids": route,
            "price_unit": self.price_unit,
            "forced_lot_id": self.lot_id and self.lot_id.id,
        }
        if self._name == "rma_customer_line":
            result.update(
                {
                    "customer_rma_line_ids": [(4, self.id)],
                }
            )
        elif self._name == "rma_supplier_line":
            result.update(
                {
                    "supplier_rma_line_ids": [(4, self.id)],
                }
            )
        return result

    def _get_delivery_procurement_data(self):
        group = self.order_id.group_id
        origin = self.order_id.name
        warehouse = self.order_id.route_template_id.outbound_warehouse_id
        route = self.order_id.route_template_id.outbound_route_id
        if self.order_id.type == "customer":
            location = (
                self.order_id.route_template_id.partner_location_id
                or self.order_id.partner_id.property_stock_customer
            )
        else:
            location = (
                self.order_id.route_template_id.partner_location_id
                or self.order_id.partner_id.property_stock_supplier
            )

        result = {
            "name": self.order_id.name,
            "group_id": group,
            "origin": origin,
            "warehouse_id": warehouse,
            "date_planned": fields.Datetime.now(),
            "product_id": self.product_id.id,
            "product_qty": self.qty_to_deliver,
            "partner_id": self.order_id.partner_id.id,
            "product_uom": self.uom_id.id,
            "location_id": location,
            "route_ids": route,
            "forced_lot_id": self.lot_id and self.lot_id.id,
        }
        if self._name == "rma_customer_line":
            result.update(
                {
                    "customer_rma_line_ids": [(4, self.id)],
                }
            )
        elif self._name == "rma_supplier_line":
            result.update(
                {
                    "supplier_rma_line_ids": [(4, self.id)],
                }
            )
        return result
