# -*- coding: utf-8 -*-
{
    'name': "Team OKR Tracker",
    'version': '1.0',
    'depends': ['base', 'mail', 'hr'],
    'author': "Your Name",
    'category': 'Human Resources/OKRs',
    'description': """
        Track Objectives and Key Results (OKRs).
        Features:
        - Company, Team, and Individual OKRs.
        - Hierarchical alignment.
        - Progress bars and priority tracking.
        - Weekly Check-ins with confidence scoring.
        - Chatter integration for discussions.
    """,
    'data': [
        'security/ir.model.access.csv',
        'security/okr_security.xml',
        'data/okr_cron.xml',
        'views/okr_period_views.xml',
        'views/okr_objective_views.xml',
        'views/okr_menus.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
