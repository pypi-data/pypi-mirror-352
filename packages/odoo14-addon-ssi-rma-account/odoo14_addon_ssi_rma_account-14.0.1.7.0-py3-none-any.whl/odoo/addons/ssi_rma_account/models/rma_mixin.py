# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RMAMixin(models.AbstractModel):
    _name = "rma_order_mixin"
    _inherit = [
        "rma_order_mixin",
    ]

    journal_id = fields.Many2one(
        string="Refund Journal",
        comodel_name="account.journal",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    usage_id = fields.Many2one(
        string="Account Usage",
        comodel_name="product.usage_type",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    refund_pricelist_id = fields.Many2one(
        string="Refund Pricelist",
        comodel_name="product.pricelist",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    qty_to_refund = fields.Float(
        string="Qty To Refund",
        compute="_compute_qty_to_refund",
        store=True,
    )
    qty_refund = fields.Float(
        string="Qty Refunded",
        compute="_compute_qty_refund",
        store=True,
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
    refund_ok = fields.Boolean(
        string="Refund Ok",
        compute="_compute_refund_ok",
        store=True,
    )
    refund_complete = fields.Boolean(
        string="Refund Complete",
        compute="_compute_refund_complete",
        store=True,
    )
    resolve_ok = fields.Boolean(
        string="Resolve Ok",
        compute="_compute_resolve_ok",
        store=True,
    )
    stock_valuation_layer_ids = fields.Many2many(
        string="Stock Valuation Layers",
        comodel_name="stock.valuation.layer",
        compute="_compute_stock_valuation_layer_ids",
        store=False,
    )
    refund_ids = fields.Many2many(
        string="Refunds",
        comodel_name="account.move",
        compute="_compute_refund_document_ids",
        store=False,
        compute_sudo=True,
    )
    num_of_refund = fields.Integer(
        string="Num. of Refund",
        compute="_compute_refund_document_ids",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "line_ids",
        "line_ids.stock_move_ids",
    )
    def _compute_stock_valuation_layer_ids(self):
        for record in self:
            record.stock_valuation_layer_ids = record.mapped(
                "line_ids.stock_move_ids.stock_valuation_layer_ids"
            )

    @api.depends(
        "line_ids",
        "line_ids.account_move_line_ids",
        "line_ids.account_move_line_ids.move_id",
        "line_ids.account_move_line_ids.move_id.state",
    )
    def _compute_refund_document_ids(self):
        for record in self:
            num_of_refund = 0
            record.refund_ids = record.mapped("line_ids.account_move_line_ids.move_id")
            num_of_refund = len(
                record.refund_ids.filtered(lambda r: r.state == "posted")
            )
            record.num_of_refund = num_of_refund

    @api.depends(
        "line_ids",
        "line_ids.refund_complete",
    )
    def _compute_refund_complete(self):
        for record in self:
            result = False
            if len(record.line_ids) > 0:
                if len(record.line_ids) == len(
                    record.line_ids.filtered(lambda r: r.refund_complete)
                ):
                    result = True
            record.refund_complete = result

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
        "operation_id",
    )
    def _compute_need_refund(self):
        for record in self:
            result = False
            if (
                record.operation_id
                and record.operation_id.refund_policy_id
                and len(record.operation_id.refund_policy_id.rule_ids) > 0
            ):
                result = True
            record.need_refund = result

    @api.depends(
        "qty_to_refund",
        "state",
    )
    def _compute_refund_ok(self):
        for record in self:
            result = False
            if record.qty_to_refund > 0.0 and record.state == "open":
                result = True
            record.refund_ok = result

    @api.depends(
        "line_ids",
        "line_ids.qty_to_refund",
    )
    def _compute_qty_to_refund(self):
        for record in self:
            result = 0.0
            for line in record.line_ids:
                result += line.qty_to_refund
            record.qty_to_refund = result

    @api.depends(
        "line_ids",
        "line_ids.qty_refund",
    )
    def _compute_qty_refund(self):
        for record in self:
            result = 0.0
            for line in record.line_ids:
                result += line.qty_refund
            record.qty_refund = result

    @api.depends(lambda self: self._get_resolve_ok_trigger())
    def _compute_resolve_ok(self):
        _super = super(RMAMixin, self)
        _super._compute_resolve_ok()

    def _get_resolve_ok_trigger(self):
        _super = super(RMAMixin, self)
        result = _super._get_resolve_ok_trigger()
        result.append("refund_complete")
        return result

    @api.onchange(
        "operation_id",
    )
    def onchange_journal_id(self):
        self.journal_id = False
        if self.operation_id:
            self.journal_id = self.operation_id.journal_id

    @api.onchange(
        "operation_id",
    )
    def onchange_usage_id(self):
        self.usage_id = False
        if self.operation_id:
            self.usage_id = self.operation_id.usage_id

    def action_create_refund(self):
        for record in self.sudo():
            record._create_refund()

    def action_open_refund(self):
        for record in self.sudo():
            result = record._open_refund()
        return result

    def _open_refund(self):
        self.ensure_one()
        if self._name == "rma_customer":
            waction = self.env.ref("account.action_move_out_refund_type").read()[0]
        elif self._name == "rma_supplier":
            waction = self.env.ref("account.action_move_in_refund_type").read()[0]

        waction.update(
            {
                "domain": [("id", "in", self.refund_ids.ids)],
            }
        )
        return waction

    def _create_refund(self):
        self.ensure_one()
        data = self._prepare_refund_data()
        AccountMove = self.env["account.move"]
        move = AccountMove.create(data)
        for line in self.line_ids:
            line._create_refund_line(move)

    def _prepare_refund_data(self):
        self.ensure_one()
        currency = (
            self.refund_pricelist_id
            and self.refund_pricelist_id.currency_id
            or self.company_id.currency_id
        )
        return {
            "date": fields.Date.today(),
            "ref": self.name,
            "move_type": "out_refund",
            "journal_id": self.journal_id.id,  # TODO: Exception mechanism
            "partner_id": self.partner_id.id,
            "currency_id": currency.id,
            "invoice_user_id": False,
            "invoice_date": fields.Date.today(),
            "invoice_date_due": fields.Date.today(),
            "invoice_origin": self.name,
            "invoice_payment_term_id": False,
        }
