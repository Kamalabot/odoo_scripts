# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    """
    An offer submitted by a buyer (res.partner) on a property.

    This is the most logic-heavy model in the addon. It demonstrates:
    - Computed fields with inverse (@api.depends)
    - Python constraints (@api.constrains)
    - ORM event hooks (create override via @api.model_create_multi)
    - Button-triggered business logic methods (action_accept, action_refuse)

    DB Layer:
    ---------
    Creates table: estate_property_offer with columns:
      id, price, status, partner_id (FK→res_partner), property_id (FK→estate_property),
      validity, date_deadline (NOT stored — computed), create_uid, write_uid, ...

    Note: 'date_deadline' has no DB column because store=True is NOT set.
    Odoo recalculates it on-the-fly from 'create_date + validity days'.

    View Layer:
    -----------
    - Shown inline as an editable list inside the property form (Offers tab)
    - Each row has Accept (✓) and Refuse (✗) icon buttons
    - Row color coding: green=accepted, red=refused via decoration-* attributes
    - Also has a standalone list view accessible from the Advertisements menu
    """

    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"  # highest offer shown first

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------

    price = fields.Float(string="Price", required=True)

    # Status is blank (pending) until explicitly accepted or refused
    status = fields.Selection(
        string="Status",
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        copy=False,  # not copied when duplicating the record
    )

    # Many2one: adds 'partner_id' FK INTEGER column → res_partner.id
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Buyer",
        required=True,
    )

    # Many2one: adds 'property_id' FK INTEGER column → estate_property.id
    property_id = fields.Many2one(
        comodel_name="estate.property",
        string="Property",
        required=True,
    )

    # How many days the offer is valid from the creation date
    validity = fields.Integer(string="Validity (days)", default=7)

    # Computed field: calculated from create_date + validity days.
    # 'compute' points to the method that sets the value.
    # 'inverse' allows the user to edit this field directly in the UI —
    #   Odoo will then call _inverse_date_deadline to back-calculate 'validity'.
    # No 'store=True' → no DB column; always recalculated dynamically.
    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )

    # -------------------------------------------------------------------------
    # Computed Field — @api.depends
    # -------------------------------------------------------------------------

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        """
        Runs whenever 'validity' or 'create_date' changes.
        'self' is a recordset — always iterate to support batch processing.
        create_date is a Datetime, so we call .date() to get just the date part.
        """
        for offer in self:
            base = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.date_deadline = base + timedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        """
        Called when the user manually edits 'date_deadline' in the UI.
        Back-calculates 'validity' so both fields stay in sync.
        Delta.days can be negative if deadline is set before today.
        """
        for offer in self:
            base = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - base).days

    # -------------------------------------------------------------------------
    # Constraint — @api.constrains
    # -------------------------------------------------------------------------

    @api.constrains("price")
    def _check_offer_price(self):
        """
        Called by Odoo after every save where 'price' is written.
        Raises UserError if the rule is violated — shown as a red warning popup.
        """
        for offer in self:
            if offer.price <= 0:
                raise UserError("An offer price must be strictly positive.")

    # -------------------------------------------------------------------------
    # ORM Event Hook — override create()
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override the ORM create() method to inject business rules:
        1. Block offers on sold properties.
        2. Require the new offer to beat the current best price.
        3. Automatically advance property state to 'offer_received'.

        @api.model_create_multi receives a list of dicts (vals_list) and must
        return the created recordset. Always call super() to do the actual INSERT.
        """
        offers = super().create(vals_list)
        for offer in offers:
            prop = offer.property_id
            if prop.state == 'sold':
                raise UserError("Cannot submit an offer on a sold property.")

            # Check against all other existing offers (excluding just-created ones)
            existing_best = max(
                prop.offer_ids.filtered(lambda o: o.id != offer.id).mapped("price"),
                default=0,
            )
            if existing_best and offer.price < existing_best:
                raise UserError(
                    f"The offer (€{offer.price:,.2f}) must be higher than "
                    f"the current best offer (€{existing_best:,.2f})."
                )

            # Advance state if still 'new'
            if prop.state == 'new':
                prop.state = 'offer_received'
        return offers

    # -------------------------------------------------------------------------
    # Button Action Methods
    # -------------------------------------------------------------------------

    def action_accept(self):
        """
        Called when the user clicks the ✓ (Accept) button on an offer row.
        XML uses type="object" and name="action_accept" to route the click here.

        Business rules:
        - Cannot accept an offer on a sold property.
        - Automatically refuses all other offers on the same property.
        - Sets property.selling_price and advances state to 'offer_accepted'.
        """
        for offer in self:
            if offer.property_id.state == 'sold':
                raise UserError("Cannot accept an offer: the property is already sold.")

            # Refuse all sibling offers on the same property
            siblings = offer.property_id.offer_ids - offer  # recordset subtraction
            siblings.write({'status': 'refused'})

            # Accept this offer and update the property
            offer.status = 'accepted'
            offer.property_id.selling_price = offer.price
            offer.property_id.state = 'offer_accepted'
        return True

    def action_refuse(self):
        """
        Called when the user clicks the ✗ (Refuse) button on an offer row.

        Business rules:
        - Marks the offer as refused.
        - If no accepted offer remains on the property, resets selling_price to 0
          and reverts state to 'offer_received'.
        """
        for offer in self:
            offer.status = 'refused'
            prop = offer.property_id
            # Check if any accepted offer still exists on this property
            still_accepted = prop.offer_ids.filtered(lambda o: o.status == 'accepted')
            if not still_accepted:
                prop.selling_price = 0.0
                prop.state = 'offer_received'
        return True
