# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _


class BuktiPotongPPhMixin(models.AbstractModel):
    _name = "l10n_id.bukti_potong_pph_mixin"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_confirm",
    ]
    _description = "Bukti Potong PPh"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_done_button = False
    _automatically_insert_done_policy_fields = False

    # Attributes related to add element on form view automatically
    _automatically_insert_multiple_approval_page = True
    _statusbar_visible_label = "draft,confirm,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    def _default_company_id(self):
        return self.env.user.company_id.id

    def _default_type_id(self):
        return False

    @api.model
    def _default_wajib_pajak_id(self):
        obj_type = self.env["l10n_id.bukti_potong_pph_type"]
        type_id = self._default_type_id()
        if not type_id:
            return False
        direction = obj_type.browse(type_id)[0].direction
        if direction == "in":
            return self.env.user.company_id.partner_id.id
        else:
            return False

    @api.model
    def _default_pemotong_pajak_id(self):
        obj_type = self.env["l10n_id.bukti_potong_pph_type"]
        type_id = self._default_type_id()
        if not type_id:
            return False
        direction = obj_type.browse(type_id)[0].direction
        if direction == "out":
            return self.env.user.company_id.partner_id.id
        else:
            return False

    @api.model
    def _default_date(self):
        return datetime.now().strftime("%Y-%m-%d")

    @api.depends(
        "line_ids",
        "line_ids.amount_tax",
    )
    def _compute_tax(self):
        for bukpot in self:
            bukpot.total_tax = 0.0
            for line in bukpot.line_ids:
                bukpot.total_tax += line.amount_tax

    @api.depends(
        "total_tax",
        "total_tax_computation",
        "manual_total_tax",
    )
    def _compute_total_tax(self):
        for record in self:
            record.total_tax_diff = record.manual_total_tax - record.total_tax
            if record.total_tax_computation == "auto":
                record.total_tax_final = record.total_tax
            else:
                record.total_tax_final = record.manual_total_tax

    type_id = fields.Many2one(
        string="Form Type",
        comodel_name="l10n_id.bukti_potong_pph_type",
        ondelete="restrict",
        required=True,
        readonly=True,
    )
    direction = fields.Selection(
        string="Type",
        related="type_id.direction",
        store=True,
        readonly=True,
    )
    allowed_journal_ids = fields.Many2many(
        string="Allowed Journals",
        comodel_name="account.journal",
        related="type_id.journal_ids",
        # compute="_compute_allowed_journal",
        store=False,
        compute_sudo=True,
    )
    allowed_tax_ids = fields.Many2many(
        string="Allowed Tax",
        comodel_name="account.tax",
        related="type_id.tax_ids",
        # compute="_compute_allowed_tax",
        store=False,
        compute_sudo=True,
    )
    allowed_account_ids = fields.Many2many(
        string="Allowed Accounts",
        comodel_name="account.account",
        related="type_id.account_ids",
        # compute="_compute_allowed_account",
        store=False,
        compute_sudo=True,
    )
    date = fields.Date(
        string="Date",
        required=True,
        default=lambda self: self._default_date(),
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    tax_period_id = fields.Many2one(
        string="Tax Period",
        comodel_name="l10n_id.tax_period",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        required=True,
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    kpp_id = fields.Many2one(
        string="KPP",
        comodel_name="res.partner",
        required=True,
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    wajib_pajak_id = fields.Many2one(
        string="Wajib Pajak",
        comodel_name="res.partner",
        required=True,
        ondelete="restrict",
        default=lambda self: self._default_wajib_pajak_id(),
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    pemotong_pajak_id = fields.Many2one(
        string="Pemotong Pajak",
        comodel_name="res.partner",
        required=True,
        ondelete="restrict",
        default=lambda self: self._default_pemotong_pajak_id(),
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    ttd_id = fields.Many2one(
        string="TTD",
        comodel_name="res.partner",
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    total_tax = fields.Float(
        string="Total Tax (Auto)",
        compute="_compute_tax",
        store=True,
        compute_sudo=True,
    )
    total_tax_computation = fields.Selection(
        string="Total Tax Computation",
        selection=[
            ("auto", "Automatic"),
            ("manual", "Manual"),
        ],
        required=True,
        default="auto",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    manual_total_tax = fields.Float(
        string="Total Tax (Manual)",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    total_tax_diff = fields.Float(
        string="Total Tax Diff.",
        compute="_compute_total_tax",
        store=True,
        compute_sudo=True,
    )
    diff_debit_account_id = fields.Many2one(
        string="Diff. Debit Account",
        comodel_name="account.account",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    diff_credit_account_id = fields.Many2one(
        string="Diff. Credit Account",
        comodel_name="account.account",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    total_tax_final = fields.Float(
        string="Total Tax",
        compute="_compute_total_tax",
        store=True,
        compute_sudo=True,
    )

    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("reject", "Rejected"),
        ],
        default="draft",
        copy=False,
    )
    line_ids = fields.One2many(
        string="Bukti Potong Line",
        comodel_name="l10n_id.bukti_potong_pph_line_mixin",
        inverse_name="bukti_potong_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    @api.depends(
        "type_id",
        "wajib_pajak_id",
        "pemotong_pajak_id",
    )
    def _compute_allowed_move_line(self):
        AML = self.env["account.move.line"]
        for record in self:
            result = []
            if record.type_id and record.wajib_pajak_id and record.pemotong_pajak_id:
                criteria = record._prepare_domain_allowed_move_lines()
                result = AML.search(criteria).ids
            record.allowed_move_line_ids = result

    def _prepare_domain_allowed_move_lines(self):
        self.ensure_one()
        result = [
            ("account_id", "=", self.account_id.id),
            ("reconciled", "=", False),
        ]
        if self.direction == "in":
            result.append(("partner_id", "=", self.pemotong_pajak_id.id))
        else:
            result.append(("partner_id", "=", self.wajib_pajak_id.id))
        return result

    allowed_move_line_ids = fields.Many2many(
        string="Allowed Move Lines",
        comodel_name="account.move.line",
        compute="_compute_allowed_move_line",
    )
    move_id = fields.Many2one(
        string="Accounting Entry",
        comodel_name="account.move",
        readonly=True,
        copy=False,
    )

    @api.model
    def _get_policy_field(self):
        res = super(BuktiPotongPPhMixin, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "done_ok",
            "cancel_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @api.onchange(
        "date",
    )
    def onchange_tax_period(self):
        obj_tax_period = self.env["l10n_id.tax_period"]
        try:
            self.tax_period_id = obj_tax_period._find_period(self.date)
        except Exception:
            self.tax_period_id = False

    @api.onchange(
        "type_id",
    )
    def onchange_policy_template_id(self):
        template_id = self._get_template_policy()
        self.policy_template_id = template_id

    @api.constrains(
        "total_tax_final",
    )
    def _constrains_total_tax_final(self):
        for record in self:
            if record.total_tax_final <= 0.0 and len(record.line_ids) > 0:
                raise UserError(_("Total tax has to be greater than 0"))

    def action_done(self):
        _super = super(BuktiPotongPPhMixin, self)
        _super.action_done()
        for bukpot in self.sudo():
            bukpot._create_aml()

    def _prepare_done_data(self):
        self.ensure_one()
        _super = super(BuktiPotongPPhMixin, self)
        result = _super._prepare_done_data()
        move = self._create_journal_entry()
        result.update(
            {
                "move_id": move.id,
            }
        )
        return result

    def _create_journal_entry(self):
        self.ensure_one()
        Move = self.env["account.move"]
        move = Move.create(self._prepare_journal_entry_data())
        return move

    def _prepare_journal_entry_data(self):
        self.ensure_one()
        data = {
            "name": self.name,
            "date": self.date,
            "journal_id": self.journal_id.id,
        }
        return data

    def _create_aml(self):
        self.ensure_one()
        pairs = []
        for line in self.line_ids:
            pairs.append(line._create_aml())

        self.move_id.action_post()

        for pair in pairs:
            pair.reconcile()

        if self.total_tax_computation == "manual" and self.total_tax_diff != 0.0:
            self._create_aml_diff()

    def action_cancel(self, cancel_reason=False):
        _super = super(BuktiPotongPPhMixin, self)
        res = _super.action_cancel(cancel_reason)
        for bukpot in self.sudo():
            bukpot.move_id.line_ids.remove_move_reconcile()
            bukpot.move_id.with_context(force_delete=True).unlink()
        return res

    def _create_aml_diff(self):
        self.ensure_one()
        AML = self.env["account.move.line"]
        AML.with_context(check_move_validity=False).create(
            self._prepare_credit_aml_diff()
        )
        AML.with_context(check_move_validity=False).create(
            self._prepare_debit_aml_diff()
        )

    def _prepare_aml_diff(self, account):
        self.ensure_one()
        name = "Taxform diff %s" % (self.name)
        amount = abs(self.total_tax_diff)
        return {
            "name": name,
            "account_id": account.id,
            "debit": amount,
            "credit": amount,
            "move_id": self.move_id.id,
        }

    def _prepare_debit_aml_diff(self):
        self.ensure_one()
        account = self._get_diff_debit_account()
        result = self._prepare_aml_diff(account)
        return result

    def _prepare_credit_aml_diff(self):
        self.ensure_one()
        account = self._get_diff_credit_account()
        result = self._prepare_aml_diff(account)
        return result

    def _get_diff_debit_account(self):
        self.ensure_one()
        if not self.diff_debit_account_id:
            error_msg = _("Debit diff. account not defined")
            raise UserError(error_msg)
        return self.diff_debit_account_id

    def _get_diff_credit_account(self):
        self.ensure_one()
        if not self.diff_credit_account_id:
            error_msg = _("Credit diff. account not defined")
            raise UserError(error_msg)
        return self.diff_credit_account_id

    @api.onchange("pemotong_pajak_id")
    def onchange_ttd_id(self):
        self.ttd_id = False

    @api.onchange("type_id", "company_id")
    def onchange_pemotong_pajak_id(self):
        self.wajib_pajak_id = self._default_pemotong_pajak_id()

    @api.onchange("type_id", "company_id")
    def onchange_wajib_pajak_id(self):
        self.wajib_pajak_id = self._default_wajib_pajak_id()
