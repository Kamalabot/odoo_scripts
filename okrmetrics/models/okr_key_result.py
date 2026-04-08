# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OkrKeyResult(models.Model):
    _name = "okrmetrics.key_result"
    _description = "OKR Key Result"

    name = fields.Char(string="Key Result", required=True)
    objective_id = fields.Many2one("okrmetrics.objective", string="Objective", required=True, ondelete='cascade')
    
    start_value = fields.Float(string="Start Value", default=0.0)
    target_value = fields.Float(string="Target Value", required=True)
    current_value = fields.Float(string="Current Value", default=0.0)
    
    # Progress bar float
    progress = fields.Float(string="Progress %", compute="_compute_progress", store=True)
    
    unit = fields.Char(string="Unit", placeholder="e.g. %, $M, Users", required=True)
    
    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.user)
    
    confidence = fields.Selection([
        ('1', 'Off Track'),
        ('2', 'At Risk'),
        ('3', 'On Track')
    ], string="Status", default='3')

    check_in_ids = fields.One2many("okrmetrics.check_in", "key_result_id", string="Check-ins")

    @api.depends('start_value', 'target_value', 'current_value')
    def _compute_progress(self):
        for kr in self:
            span = kr.target_value - kr.start_value
            if span == 0:
                kr.progress = 0.0
            else:
                # Assuming target > start. If target is less (e.g. reducing bounce rate), logic would flip.
                prog = ((kr.current_value - kr.start_value) / span) * 100
                kr.progress = max(0.0, min(100.0, prog))
