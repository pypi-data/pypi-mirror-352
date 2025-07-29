# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RMAPolicyRule(models.Model):
    _name = "rma_policy_rule"
    _description = "RMA Policy Rule"

    policy_id = fields.Many2one(
        comodel_name="rma_policy",
        string="RMA Policy",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(string="Sequence", required=True, default=10)
    operator = fields.Selection(
        string="Operator",
        selection=[
            ("-", "-"),
            ("+", "+"),
        ],
        required=True,
        default="+",
    )
    policy_field_id = fields.Many2one(
        comodel_name="rma_policy_field", required=True, ondelete="restrict"
    )
