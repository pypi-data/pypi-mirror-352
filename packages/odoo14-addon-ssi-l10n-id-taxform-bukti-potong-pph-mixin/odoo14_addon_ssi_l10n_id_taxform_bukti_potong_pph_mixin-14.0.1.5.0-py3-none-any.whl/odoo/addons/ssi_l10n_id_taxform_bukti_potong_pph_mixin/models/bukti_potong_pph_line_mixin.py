# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.tools.translate import _


class BuktiPotongPPhLineMixin(models.AbstractModel):
    _name = "l10n_id.bukti_potong_pph_line_mixin"
    _description = "Bukti Potong PPh Line Mixin"
    _order = "sequence, id"

    @api.depends(
        "income_move_line_ids",
        "income_move_line_ids.debit",
        "income_move_line_ids.credit",
        "amount_computation_method",
        "manual_amount",
    )
    def _compute_amount(self):
        for line in self:
            line.amount = line.amount_tax = 0.0
            if line.amount_computation_method == "auto":
                for move_line in line.income_move_line_ids:
                    if line.bukti_potong_id.direction == "in":
                        line.amount += move_line.credit
                    else:
                        line.amount += move_line.debit
            else:
                line.amount = line.manual_amount
            if line.amount != 0.0:
                taxes = line.tax_id.compute_all(
                    line.amount,
                    line.bukti_potong_id.company_id.currency_id,
                    1.0,
                    product=False,
                    partner=False,
                )
                line.amount_tax = taxes["total_included"] - taxes["total_excluded"]

    name = fields.Char(
        string="Description",
        required=True,
        default="/",
    )
    bukti_potong_id = fields.Many2one(
        string="Bukti Potong",
        comodel_name="l10n_id.bukti_potong_pph_mixin",
        ondelete="cascade",
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
    )
    tax_id = fields.Many2one(
        string="Tax",
        comodel_name="account.tax",
        required=True,
        ondelete="restrict",
    )
    move_line_id = fields.Many2one(
        string="Move Line",
        comodel_name="account.move.line",
        required=True,
        copy=False,
        ondelete="restrict",
    )

    @api.depends(
        "move_line_id",
    )
    def _compute_allowed_income_move_line_ids(self):
        AML = self.env["account.move.line"]
        for record in self:
            result = []
            if record.move_line_id:
                criteria = [
                    ("move_id", "=", record.move_line_id.move_id.id),
                    ("id", "!=", record.move_line_id.id),
                ]
                result = AML.search(criteria).ids
            record.allowed_income_move_line_ids = result

    allowed_income_move_line_ids = fields.Many2many(
        string="Allowed Income Move Lines",
        comodel_name="account.move.line",
        compute="_compute_allowed_income_move_line_ids",
    )
    income_move_line_ids = fields.Many2many(
        string="Income Move Lines",
        comodel_name="account.move.line",
    )
    amount = fields.Float(
        string="Amount",
        compute="_compute_amount",
        store=True,
        compute_sudo=True,
    )
    amount_computation_method = fields.Selection(
        string="Amount Computation",
        selection=[
            ("auto", "Automatic"),
            ("manual", "Manual"),
        ],
        required=True,
        default="auto",
        readonly=False,
    )
    manual_amount = fields.Float(
        string="Amount (Manual)",
        readonly=False,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    amount_tax = fields.Float(
        string="Tax Amount",
        compute="_compute_amount",
        store=True,
        compute_sudo=True,
    )

    @api.onchange(
        "move_line_id",
        "tax_id",
    )
    def onchange_name(self):
        self.name = False
        if self.move_line_id and self.tax_id:
            name = "%s - %s" % (self.move_line_id.move_id.name, self.tax_id.name)
            self.name = name

    def _create_aml(self):
        self.ensure_one()
        AML = self.env["account.move.line"]
        pair = False
        debit_aml = AML.with_context(check_move_validity=False).create(
            self._prepare_tax_debit_aml_data()
        )
        credit_aml = AML.with_context(check_move_validity=False).create(
            self._prepare_tax_credit_aml_data()
        )
        pair = self._pair_aml(debit_aml, credit_aml)
        return pair

    def _pair_aml(self, debit_aml, credit_aml):
        self.ensure_one()
        result = False

        if self.bukti_potong_id.direction == "in":
            result = self.move_line_id + credit_aml
        else:
            result = self.move_line_id + debit_aml

        return result

    def _prepare_aml_data(
        self,
        account_id,
        debit,
        credit,
        partner_id=False,
    ):
        result = {
            "name": self.name,
            "account_id": account_id,
            "debit": debit,
            "credit": credit,
            "move_id": self.bukti_potong_id.move_id.id,
            "partner_id": partner_id,
        }
        return result

    def _get_debit_account(self):
        self.ensure_one()
        result = False
        if self.bukti_potong_id.direction == "in":
            result = self._select_tax_account()
        else:
            result = self.move_line_id.account_id
        return result

    def _get_credit_account(self):
        self.ensure_one()
        result = False
        if self.bukti_potong_id.direction == "out":
            result = self._select_tax_account()
        else:
            result = self.move_line_id.account_id
        return result

    def _get_debit_partner(self):
        self.ensure_one()
        result = False
        if self.bukti_potong_id.direction == "in":
            result = self.bukti_potong_id.kpp_id
        else:
            result = self.move_line_id.partner_id
        return result

    def _get_credit_partner(self):
        self.ensure_one()
        result = False
        if self.bukti_potong_id.direction == "out":
            result = self.bukti_potong_id.kpp_id
        else:
            result = self.move_line_id.partner_id
        return result

    def _prepare_tax_debit_aml_data(self):
        self.ensure_one()
        account = self._get_debit_account()
        partner = self._get_debit_partner()
        return self._prepare_aml_data(
            account_id=account.id,
            debit=self.amount_tax,
            credit=0.0,
            partner_id=partner and partner.id or False,
        )

    def _prepare_tax_credit_aml_data(self):
        self.ensure_one()
        account = self._get_credit_account()
        partner = self._get_credit_partner()
        return self._prepare_aml_data(
            account_id=account.id,
            credit=self.amount_tax,
            debit=0.0,
            partner_id=partner and partner.id or False,
        )

    def _select_tax_account(self):
        self.ensure_one()
        tax = self.tax_id
        if tax.invoice_repartition_line_ids:
            result = tax.invoice_repartition_line_ids[1].account_id
        else:
            raise UserWarning(
                _("Please configure invoice tax account for %s") % (tax.name)
            )
        return result
