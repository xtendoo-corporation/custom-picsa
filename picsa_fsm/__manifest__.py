# Copyright 2026 Xtendoo Software SLU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "PICSA FSM",
    "summary": "Personalizaciones PICSA para partes de trabajo FSM",
    "version": "17.0.1.0.0",
    "category": "Services/Work Orders",
    "author": "Xtendoo",
    "license": "AGPL-3",
    "depends": [
        "account",
        "product",
        "xtendoo_fsm",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/picsa_fsm_data.xml",
        "report/fsm_order_incident_report.xml",
        "views/fsm_order_views.xml",
        "views/fsm_menu.xml",
    ],
    "installable": True,
    "application": False,
}
