# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OkrPeriod(models.Model):
    _name = "okrmetrics.period"
    _description = "OKR Tracking Period"
    _order = "date_end desc"

    name = fields.Char(string="Period Name", required=True, placeholder="e.g. Q1 2024")
    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date", required=True)
    
    state = fields.Selection([
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('closed', 'Closed')
    ], string="Status", default='upcoming', required=True)

    objective_ids = fields.One2many("okrmetrics.objective", "period_id", string="Objectives")

    @api.model
    def action_close_expired_periods(self):
        """
        Scheduled action (cron job) to auto-close periods that are past their end date.
        @api.model means it acts on the class, not a specific recordset.
        """
        today = fields.Date.today()
        expired_periods = self.search([
            ('date_end', '<', today),
            ('state', 'in', ['upcoming', 'active'])
        ])
        if expired_periods:
            expired_periods.write({'state': 'closed'})
            # We could additionally notify the owners or close inactive OKRs here.
