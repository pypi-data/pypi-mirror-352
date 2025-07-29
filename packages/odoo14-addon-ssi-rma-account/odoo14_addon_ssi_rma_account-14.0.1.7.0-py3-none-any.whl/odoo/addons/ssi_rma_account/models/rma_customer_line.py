# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RMACustomerLine(models.Model):
    _name = "rma_customer_line"
    _inherit = [
        "rma_line_mixin",
        "rma_customer_line",
    ]

    account_move_line_ids = fields.Many2many(
        relation="rel_rma_customer_line_2_aml",
        column1="rma_line_id",
        column2="account_move_line_id",
    )
