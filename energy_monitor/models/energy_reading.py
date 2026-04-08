# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EnergyReading(models.Model):
    _name = "energy.reading"
    _description = "Energy Reading"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "reading_date desc, id desc"

    meter_id = fields.Many2one("energy.meter", string="Meter", required=True, tracking=True)
    reading_date = fields.Date(string="Reading Date", required=True, default=fields.Date.context_today, tracking=True)
    meter_value = fields.Float(string="Meter Value (Current)", required=True, tracking=True)
    
    previous_value = fields.Float(string="Previous Value", compute="_compute_consumption", store=True)
    consumption = fields.Float(string="Consumption", compute="_compute_consumption", store=True, group_operator="sum")
    
    currency_id = fields.Many2one(related="meter_id.currency_id", store=True)
    cost = fields.Monetary(string="Cost", compute="_compute_cost", store=True, group_operator="sum", currency_field="currency_id")
    
    notes = fields.Text(string="Notes", tracking=True)
    month = fields.Char(string="Month", compute="_compute_month", store=True)
    month_start = fields.Date(string="Month Start", compute="_compute_month", store=True, group_operator=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('disputed', 'Disputed')
    ], string="Status", default='draft', tracking=True)

    @api.depends('reading_date')
    def _compute_month(self):
        for record in self:
            if record.reading_date:
                record.month = record.reading_date.strftime("%B %Y")
                record.month_start = record.reading_date.replace(day=1)
            else:
                record.month = False
                record.month_start = False

    @api.depends('meter_value', 'meter_id', 'reading_date')
    def _compute_consumption(self):
        for record in self:
            if record.meter_id and record.reading_date:
                # Find the previous reading for the same meter before this date
                exclude_id = record._origin.id or (record.id if not isinstance(record.id, models.NewId) else False)
                domain = [
                    ('meter_id', '=', record.meter_id.id),
                    ('reading_date', '<', record.reading_date),
                ]
                if exclude_id:
                    domain.append(('id', '!=', exclude_id))
                previous = self.env['energy.reading'].search(
                    domain, order='reading_date desc, id desc', limit=1
                )
                
                record.previous_value = previous.meter_value if previous else 0.0
                record.consumption = record.meter_value - record.previous_value
            else:
                record.previous_value = 0.0
                record.consumption = 0.0

    @api.depends('consumption', 'meter_id.rate')
    def _compute_cost(self):
        for record in self:
            record.cost = record.consumption * record.meter_id.rate if record.meter_id else 0.0
