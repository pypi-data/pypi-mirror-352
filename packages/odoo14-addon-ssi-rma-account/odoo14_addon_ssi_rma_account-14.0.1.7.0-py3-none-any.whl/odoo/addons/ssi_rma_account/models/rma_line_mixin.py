# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RMALineMixin(models.AbstractModel):
    _name = "rma_line_mixin"
    _inherit = [
        "rma_line_mixin",
    ]

    account_move_line_ids = fields.Many2many(
        string="Journal Item",
        comodel_name="account.move.line",
    )
    qty_to_refund = fields.Float(
        string="Qty to Refund", compute="_compute_qty_to_refund", store=True
    )
    qty_refund = fields.Float(
        string="Qty Refunded",
        compute="_compute_qty_refund",
    )
    need_refund = fields.Boolean(
        string="Need Refund",
        compute="_compute_need_refund",
        store=True,
    )
    percent_refund = fields.Float(
        string="Percent Refund",
        compute="_compute_percent_refund",
        store=True,
    )
    refund_complete = fields.Boolean(
        string="Refund Complete",
        compute="_compute_refund_complete",
        store=True,
    )

    @api.depends(
        "uom_quantity",
        "qty_refund",
    )
    def _compute_percent_refund(self):
        for record in self:
            result = 0.0
            try:
                result = record.qty_refund / record.uom_quantity
            except ZeroDivisionError:
                result = 0.0
            record.percent_refund = result

    @api.depends(
        "order_id",
        "order_id.operation_id",
    )
    def _compute_need_refund(self):
        for record in self:
            result = False
            if (
                record.order_id.operation_id
                and record.order_id.operation_id.refund_policy_id
                and len(record.order_id.operation_id.refund_policy_id.rule_ids) > 0
            ):
                result = True
            record.need_refund = result

    @api.depends(
        "need_refund",
        "percent_refund",
    )
    def _compute_refund_complete(self):
        for record in self:
            result = False
            if (
                record.need_refund and record.percent_refund == 1.0
            ) or not record.need_refund:
                result = True
            record.refund_complete = result

    @api.model
    def _get_qty_field_trigger(self):
        _super = super(RMALineMixin, self)
        result = _super._get_qty_field_trigger()
        result += ["qty_refund"]
        return result

    @api.depends(lambda self: self._get_qty_field_trigger())
    def _compute_qty_to_refund(self):
        for record in self:
            result = 0.0
            if record.order_id.operation_id.refund_policy_id:
                policy = record.order_id.operation_id.refund_policy_id
                result = policy._compute_quantity(record)
            record.qty_to_refund = result

    @api.depends(
        "account_move_line_ids",
        "account_move_line_ids.move_id.state",
        "account_move_line_ids.quantity",
    )
    def _compute_qty_refund(self):
        for record in self:
            result = 0.0
            for line in record.account_move_line_ids:
                if line.move_id.state == "posted":
                    result += line.quantity
            record.qty_refund = result

    def _create_refund_line(self, move):
        self.ensure_one()
        data = self._prepare_refund_line(move)
        AML = self.env["account.move.line"]
        line = AML.with_context(check_move_validity=False).create(data)
        line.move_id.with_context(
            check_move_validity=False
        )._move_autocomplete_invoice_lines_values()
        self.write({"account_move_line_ids": [(4, line.id)]})

    def _prepare_refund_line(self, move):
        self.ensure_one()
        account = self.product_id._get_product_account(
            usage_code=self.order_id.usage_id.code
        )
        tax_ids = self.product_id._get_product_tax(
            usage_code=self.order_id.usage_id.code
        )
        if self.order_id.refund_pricelist_id:
            product_context = dict(
                self.env.context, uom=self.uom_id and self.uom_id.id or False
            )
            final_price, rule_id = self.order_id.refund_pricelist_id.with_context(
                product_context
            ).get_product_price_rule(self.product_id, self.uom_quantity or 1.0, False)
            price = final_price
        else:
            price = self.price_unit
        data = {
            "move_id": move.id,
            "product_id": self.product_id.id,
            "name": self.name,
            "account_id": account.id,
            "quantity": self.uom_quantity,
            "product_uom_id": self.uom_id.id,
            "price_unit": price,
            "tax_ids": [(6, 0, tax_ids)],
        }
        return data
