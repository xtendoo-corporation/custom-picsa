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
        "xtendoo_fsm",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/fsm_order_incident_report.xml",
        "views/fsm_order_views.xml",
    ],
    "installable": True,
    "application": False,
}
