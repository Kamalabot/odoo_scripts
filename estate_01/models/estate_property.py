# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    """
    Represents a real estate property listed for sale.

    DB Layer:
    ---------
    Maps to PostgreSQL table: estate_property
    System columns added by Odoo: id, active, create_uid, write_uid, create_date, write_date
    Relational columns added by this class:
      - property_type_id (INTEGER FK → estate_property_type.id)   [Many2one]
      - tag_ids creates junction table                             [Many2many]
      - offer_ids is virtual — no column here, FK is on offer side [One2many]
    Computed fields (total_area, best_price) have NO stored column (store=False by default).

    View Layer:
    -----------
    - Header buttons: Sell, Cancel (type="object" → calls action_sell / action_cancel)
    - Status bar widget shows the workflow: New → Offer Received → Offer Accepted → Sold
    - Tags shown as colored pill badges (widget="many2many_tags")
    - Offers tab: inline editable list of all offers with Accept/Refuse icon buttons
    - Computed fields shown as readonly in the form
    """

    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "name"

    # -------------------------------------------------------------------------
    # Basic Fields
    # -------------------------------------------------------------------------

    name = fields.Char(string="Property Name", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")

    date_availability = fields.Date(
        string="Available From",
        copy=False,
        default=lambda self: fields.Date.today(),
    )

    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)

    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")

    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")

    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        help="The direction the garden faces.",
    )

    state = fields.Selection(
        string="Status",
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ],
        required=True,
        copy=False,
        default='new',
    )

    active = fields.Boolean(string="Active", default=True)

    # -------------------------------------------------------------------------
    # Relational Fields
    # -------------------------------------------------------------------------

    # Many2one: adds property_type_id INTEGER FK column in estate_property table.
    # Acts like a dropdown in the UI; navigates to the estate.property.type record.
    property_type_id = fields.Many2one(
        comodel_name="estate.property.type",
        string="Property Type",
    )

    # Many2many: NO column on this table.
    # Odoo auto-creates a junction table:
    #   estate_property_tag_estate_property_rel(estate_property_id, estate_property_tag_id)
    # SQL: SELECT tag.* FROM estate_property_tag tag
    #        JOIN estate_property_tag_estate_property_rel rel ON rel.estate_property_tag_id = tag.id
    #       WHERE rel.estate_property_id = <self.id>
    tag_ids = fields.Many2many(
        comodel_name="estate.property.tag",
        string="Tags",
    )

    # One2many: virtual — no column on this table.
    # 'inverse_name' is the Many2one field on estate.property.offer that points back here.
    # SQL: SELECT * FROM estate_property_offer WHERE property_id = <self.id>
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_id",
        string="Offers",
    )

    # -------------------------------------------------------------------------
    # Computed Fields — no DB column (store=False by default)
    # -------------------------------------------------------------------------

    # Recalculated whenever living_area or garden_area changes
    total_area = fields.Integer(
        string="Total Area (sqm)",
        compute="_compute_total_area",
    )

    # Recalculated whenever any offer's price changes (dot-notation dependency)
    best_price = fields.Float(
        string="Best Offer",
        compute="_compute_best_price",
    )

    # -------------------------------------------------------------------------
    # Compute Methods
    # -------------------------------------------------------------------------

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        """
        @api.depends registers which fields trigger this recompute.
        'self' is always a recordset — loop even when editing a single record.
        This is because Odoo batches ORM operations for performance.
        """
        for prop in self:
            prop.total_area = prop.living_area + prop.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        """
        Dot-notation 'offer_ids.price' means: re-run this whenever any
        offer linked to this property has its price changed.
        mapped('price') returns a Python list of all price values.
        max(..., default=0) avoids ValueError when there are no offers.
        """
        for prop in self:
            prop.best_price = max(prop.offer_ids.mapped("price"), default=0)

    # -------------------------------------------------------------------------
    # Constraint
    # -------------------------------------------------------------------------

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        """
        Runs on every save where selling_price or expected_price is written.
        Odoo validates THIS AFTER the record is written to DB (inside a transaction)
        — if this raises, the transaction is rolled back.
        The float_compare check avoids floating-point precision issues.
        Guard: only validate once selling_price is actually set (> 0).
        """
        for prop in self:
            if (
                prop.selling_price > 0
                and prop.expected_price > 0
                and prop.selling_price < 0.9 * prop.expected_price
            ):
                raise UserError(
                    "The selling price cannot be lower than 90% of the expected price.\n"
                    f"Expected: {prop.expected_price:,.2f} — Minimum allowed: "
                    f"{0.9 * prop.expected_price:,.2f}"
                )

    # -------------------------------------------------------------------------
    # Button Action Methods
    # -------------------------------------------------------------------------

    def action_sell(self):
        """
        Triggered by the 'Sell' button in the form header (type="object").
        Odoo routes the HTTP call to this method via the controller.
        Returns True (or an action dict) to complete the RPC call cleanly.
        """
        for prop in self:
            if prop.state == 'canceled':
                raise UserError("A canceled property cannot be sold.")
            prop.state = 'sold'
        return True

    def action_cancel(self):
        """
        Triggered by the 'Cancel' button in the form header (type="object").
        Guards against canceling an already sold property.
        """
        for prop in self:
            if prop.state == 'sold':
                raise UserError("A sold property cannot be canceled.")
            prop.state = 'canceled'
        return True
