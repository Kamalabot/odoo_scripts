# -*- coding: utf-8 -*-
from odoo import fields, models


class EstatePropertyTag(models.Model):
    """
    A descriptive label that can be applied to multiple properties simultaneously.
    Examples: Beachfront, Renovated, Pet-Friendly, City Center.

    DB Layer:
    ---------
    - Creates table: estate_property_tag(id, name, color, create_uid, write_uid, ...)
    - The Many2many relationship with estate.property creates an additional
      auto-generated junction/association table:
        estate_property_tag_estate_property_rel(estate_property_id, estate_property_tag_id)
      This is the standard SQL pattern for M:N relationships.
    - Odoo manages the junction table automatically — no Python code needed for it.

    View Layer:
    -----------
    - Appears as colored pill badges on the property form using widget="many2many_tags"
    - The 'color' field (integer 0-11) maps to Odoo's built-in color palette
      and drives the badge background color in the UI.
    """

    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = "name"

    name = fields.Char(string="Tag Name", required=True)

    # Integer field (0–11) that maps to Odoo's color palette.
    # Used by the 'many2many_tags' widget via options="{'color_field': 'color'}"
    color = fields.Integer(string="Color Index")
