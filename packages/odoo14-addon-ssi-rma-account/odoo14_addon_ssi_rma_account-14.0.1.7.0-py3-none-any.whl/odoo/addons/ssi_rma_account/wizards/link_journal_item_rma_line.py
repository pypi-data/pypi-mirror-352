# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class LinkJournalItemRmaLine(models.TransientModel):
    _name = "link_journal_item_rma_line"
    _description = "Link Journal Item To RMA Line"

    @api.model
    def _default_model_id(self):
        model_name = self.env.context.get("active_model", False)
        criteria = [("model", "=", model_name)]
        return self.env["ir.model"].search(criteria)[0].id

    model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
        default=lambda self: self._default_model_id(),
    )
    allowed_account_move_line_ids = fields.Many2many(
        string="Allowed Journal Items",
        comodel_name="account.move.line",
        compute="_compute_allowed_account_move_line_ids",
        compute_sudo=True,
    )
    account_move_line_ids = fields.Many2many(
        string="Journal Items",
        comodel_name="account.move.line",
        relation="rel_link_journal_item_2_rma_line",
        column1="wizard_id",
        column2="account_move_line_id",
    )

    @api.depends(
        "model_id",
    )
    def _compute_allowed_account_move_line_ids(self):
        for record in self:
            line_id = self.env.context.get("active_id", False)
            rma_line = self.env[self.model_id.model].browse(line_id)

            criteria = [
                ("product_id", "=", rma_line.product_id.id),
                ("move_id.state", "=", "posted"),
                (
                    "move_id.partner_id.commercial_partner_id.id",
                    "=",
                    rma_line.order_id.partner_id.id,
                ),
                ("journal_id", "=", rma_line.order_id.journal_id.id),
            ]
            result = self.env["account.move.line"].search(criteria).ids
            record.allowed_account_move_line_ids = result

    def action_confirm(self):
        for record in self.sudo():
            record._confirm()

    def _confirm(self):
        self.ensure_one()
        line_id = self.env.context.get("active_id", False)
        rma_line = self.env[self.model_id.model].browse(line_id)
        account_move_lines = []
        for sm in self.account_move_line_ids:
            account_move_lines.append((4, sm.id))
        rma_line.write(
            {
                "account_move_line_ids": account_move_lines,
            }
        )
