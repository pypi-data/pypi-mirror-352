# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class RMASupplier(models.Model):
    _name = "rma_supplier"
    _description = "RMA Supplier"
    _inherit = ["rma_supplier", "rma_order_mixin"]

    # pylint: disable=pointless-statement
    def _prepare_refund_data(self):
        _super = super(RMASupplier, self)
        result = _super._prepare_refund_data()
        result["move_type"] = "in_refund"
        return result
