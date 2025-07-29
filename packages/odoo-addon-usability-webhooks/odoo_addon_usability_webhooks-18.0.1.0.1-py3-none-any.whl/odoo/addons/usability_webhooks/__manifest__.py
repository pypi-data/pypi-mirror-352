# Copyright 2022 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "REST API for Webhook",
    "version": "18.0.1.0.1",
    "license": "AGPL-3",
    "category": "Tools",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/ecosoft-odoo/ecosoft-addons",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/config_parameter.xml",
        "data/ir_cron.xml",
        "views/api_log.xml",
    ],
}
