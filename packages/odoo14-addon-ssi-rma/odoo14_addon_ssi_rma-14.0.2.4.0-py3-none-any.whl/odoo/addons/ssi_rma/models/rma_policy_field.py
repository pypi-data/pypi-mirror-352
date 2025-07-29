# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class RMAPolicyField(models.Model):
    _name = "rma_policy_field"
    _description = "RMA Policy Field"
    _inherit = ["mixin.master_data"]
