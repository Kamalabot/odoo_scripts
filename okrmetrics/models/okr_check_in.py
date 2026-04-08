# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OkrCheckIn(models.Model):
    _name = "okrmetrics.check_in"
    _description = "OKR Check-in"
    _order = "check_in_date desc"

    key_result_id = fields.Many2one("okrmetrics.key_result", string="Key Result", required=True, ondelete='cascade')
    check_in_date = fields.Date(string="Date", default=fields.Date.today, required=True)
    
    value = fields.Float(string="New Value", required=True)
    confidence = fields.Selection([
        ('1', 'Off Track'),
        ('2', 'At Risk'),
        ('3', 'On Track')
    ], string="Confidence", default='3')
    
    note = fields.Html(string="Note", help="What went well? What are the blockers?")
    owner_id = fields.Many2one("res.users", string="Author", default=lambda self: self.env.user)

    @api.model_create_multi
    def create(self, vals_list):
        """ 
        When a check-in is created, automatically update the current_value and confidence 
        on the parent Key Result.
        """
        check_ins = super().create(vals_list)
        for ci in check_ins:
            ci.key_result_id.write({
                'current_value': ci.value,
                'confidence': ci.confidence
            })
        return check_ins
