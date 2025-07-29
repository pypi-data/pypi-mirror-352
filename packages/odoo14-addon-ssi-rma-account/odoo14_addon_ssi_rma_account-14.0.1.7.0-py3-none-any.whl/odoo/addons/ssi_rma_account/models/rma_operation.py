# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RMAOperation(models.Model):
    _name = "rma_operation"
    _inherit = ["rma_operation"]

    refund_policy_id = fields.Many2one(
        comodel_name="rma_policy",
        string="Refund Policy",
        required=False,
        ondelete="restrict",
    )
    journal_id = fields.Many2one(
        string="Refund Journal",
        comodel_name="account.journal",
    )
    usage_id = fields.Many2one(
        string="Account Usage",
        comodel_name="product.usage_type",
    )
