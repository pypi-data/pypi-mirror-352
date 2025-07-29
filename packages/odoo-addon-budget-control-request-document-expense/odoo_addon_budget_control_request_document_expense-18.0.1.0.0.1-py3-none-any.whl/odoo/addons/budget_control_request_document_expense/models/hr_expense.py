# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class HRExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    def write(self, vals):
        """Uncommit budget for source request document."""
        res = super().write(vals)
        if vals.get("approval_state") in ("approve", "cancel", False):
            self.mapped("request_document_id").recompute_budget_move()
        return res
