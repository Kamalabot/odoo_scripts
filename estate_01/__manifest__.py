# -*- coding: utf-8 -*-
{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "Your Name",
    'category': 'Tutorials/Real Estate01',
    'description': """
        A tutorial module to manage real estate properties.
        Features:
        - Create and list real estate properties
        - Classify by type (apartment, house, land) and tags
        - Submit and manage buyer offers with Accept/Refuse workflow
        - Computed fields: total area, best offer price
        - Business rules: selling price constraint, offer price validation
    """,
    # Data files are loaded in the ORDER listed here.
    # types/tags must come before the main property views (which reference them).
    # All views must come before menus (menus reference action IDs from views).
    # 'data': [
    #     'security/ir.model.access.csv',
    #     'views/estate_property_type_views.xml',
    #     'views/estate_property_views.xml',
    #     'views/estate_property_offer_views.xml',
    #     'views/estate_menus.xml',
    # ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
