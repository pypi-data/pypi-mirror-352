# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RMAPolicy(models.Model):
    _name = "rma_policy"
    _description = "RMA Policy"
    _inherit = ["mixin.master_data"]

    rma_type = fields.Selection(
        string="Applicable on RMA Type",
        selection=[
            ("customer", "Customer"),
            ("supplier", "Supplier"),
            ("both", "Both"),
        ],
        required=True,
        default="customer",
    )
    rule_ids = fields.One2many(
        comodel_name="rma_policy_rule", inverse_name="policy_id", string="Rules"
    )

    def _compute_quantity(self, rma_line_id):
        self.ensure_one()
        qty = 0.0
        for rule in self.rule_ids:
            if rule.operator == "+":
                qty += getattr(rma_line_id, rule.policy_field_id.code)
            elif rule.operator == "-":
                qty -= getattr(rma_line_id, rule.policy_field_id.code)
        return qty
