# -*- coding: utf-8 -*-
from odoo import models, fields

class EnergyMeter(models.Model):
    _name = "energy.meter"
    _description = "Energy Meter"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Meter Name", required=True, tracking=True)
    ref = fields.Char(string="Reference/Serial", tracking=True)
    utility_type = fields.Selection([
        ('electricity', 'Electricity'),
        ('water', 'Water'),
        ('gas', 'Gas'),
        ('diesel', 'Diesel')
    ], string="Utility Type", required=True, tracking=True)
    unit = fields.Selection([
        ('kwh', 'kWh'),
        ('litre', 'Litre'),
        ('cubic_meter', 'Cubic Meter')
    ], string="Unit of Measure", required=True, tracking=True)
    department_id = fields.Many2one("hr.department", string="Department", tracking=True)
    location = fields.Char(string="Location", tracking=True)
    
    currency_id = fields.Many2one("res.currency", string="Currency", default=lambda self: self.env.company.currency_id, tracking=True)
    rate = fields.Monetary(string="Rate per Unit", currency_field="currency_id", tracking=True)
    monthly_budget = fields.Monetary(string="Monthly Budget", currency_field="currency_id", tracking=True)
    
    reading_ids = fields.One2many("energy.reading", "meter_id", string="Readings")
    active = fields.Boolean(default=True, tracking=True)
