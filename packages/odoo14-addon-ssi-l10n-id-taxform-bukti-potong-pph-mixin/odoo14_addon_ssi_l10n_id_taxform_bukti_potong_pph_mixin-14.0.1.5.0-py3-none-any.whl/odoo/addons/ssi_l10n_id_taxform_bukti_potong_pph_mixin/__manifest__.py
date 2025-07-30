# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Indonesia - Mixin Feature for Bukti Potong PPh",
    "version": "14.0.1.5.0",
    "category": "localization",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "account",
        "ssi_transaction_mixin",
        "ssi_transaction_confirm_mixin",
        "ssi_transaction_done_mixin",
        "ssi_transaction_cancel_mixin",
        "ssi_l10n_id_taxform",
    ],
    "data": [
        "security/res_group_data.xml",
        "security/ir.model.access.csv",
        "data/data_decimal_precision.xml",
        "menu.xml",
        "views/bukti_potong_pph_type_views.xml",
        "views/bukti_potong_pph_mixin_views.xml",
    ],
}
