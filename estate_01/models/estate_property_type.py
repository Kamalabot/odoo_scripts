# -*- coding: utf-8 -*-
from odoo import fields, models


class EstatePropertyType(models.Model):
    """
    Represents a category for a real estate property (e.g. Apartment, House, Land).

    DB Layer:
    ---------
    - Creates table: estate_property_type(id, name, create_uid, write_uid, ...)
    - 'property_ids' is a One2many: it does NOT add a column here.
      The FK lives on estate_property.property_type_id.
      Odoo resolves it at query time:
        SELECT * FROM estate_property WHERE property_type_id = <this.id>

    View Layer:
    -----------
    - Shown on the form of estate.property as a dropdown (Many2one widget)
    - Has its own list + form views accessible via the Settings menu
    - The form shows an inline list of all properties of this type (One2many tab)
    """

    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "name"  # records sorted alphabetically by default

    name = fields.Char(string="Type Name", required=True)

    # One2many: the reverse of the Many2one on estate.property.
    # 'inverse_name' is the field on the "many" side that points back here.
    # No column is added to this table; Odoo queries estate_property WHERE property_type_id = self.id
    property_ids = fields.One2many(
        comodel_name="estate.property",
        inverse_name="property_type_id",
        string="Properties",
    )
