# -*- coding: utf-8 -*-
{
    'name': 'Utility Monitor',
    'version': '1.0',
    'summary': 'Track utility consumption and costs per department',
    'description': """
        Smart Energy & Utility Monitor
        ==============================
        An addon to let facility/finance teams:
        - Log monthly meter readings per department/floor
        - Auto-calculate consumption and cost
        - Set budgets and get alerts on overruns
        - View trends via Graph and Pivot views
        - Compare months / years / departments
    """,
    'category': 'Tutorials/Utility Monitor',
    'author': 'Kamal',
    'depends': ['base', 'mail', 'base_automation', 'hr'],
    'data': [
        'security/energy_security.xml',
        'security/ir.model.access.csv',
        'data/energy_automation.xml',
        'views/energy_menus.xml',
        'views/energy_meter_views.xml',
        'views/energy_reading_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
