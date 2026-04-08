# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OkrObjective(models.Model):
    _name = "okrmetrics.objective"
    _description = "OKR Objective"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(string="Objective Name", required=True, tracking=True)
    
    # Rich text HTML field
    description = fields.Html(string="Description", help="Provide context on why this matters.")
    
    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.user, tracking=True)
    team_id = fields.Many2one("hr.department", string="Team/Department")
    period_id = fields.Many2one("okrmetrics.period", string="Period", required=True, tracking=True)
    
    # Self-referential hierarchy
    parent_id = fields.Many2one("okrmetrics.objective", string="Parent Objective", help="Align this OKR upward.")
    child_ids = fields.One2many("okrmetrics.objective", "parent_id", string="Aligned Objectives")
    
    # Polymorphic relation to show how fields.Reference works
    aligned_to = fields.Reference(
        selection=[
            ('okrmetrics.objective', 'Another Objective'),
            ('res.users', 'A User Context')
        ],
        string="Aligned To Ext",
        help="Example of polymorphic relation."
    )

    level = fields.Selection([
        ('company', 'Company'),
        ('team', 'Team'),
        ('individual', 'Individual')
    ], string="Level", default="individual", tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string="Status", default="draft", tracking=True)

    # Priority widget field.
    # The widget="priority" in Odoo expects a Selection with values '0','1','2','3'.
    # NOTE: _order cannot reliably sort on Selection string keys — use a separate
    # integer field if ordering by priority is needed in the future.
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'High'),
        ('2', 'Very High'),
        ('3', 'Critical')
    ], string="Priority", default='0', tracking=True)

    # Progress Tracking
    key_result_ids = fields.One2many("okrmetrics.key_result", "objective_id", string="Key Results")
    
    progress = fields.Float(string="Progress", compute="_compute_progress", store=True)
    color = fields.Integer(string="Color Index", default=0)

    @api.depends('key_result_ids.progress')
    def _compute_progress(self):
        """ Average progress of all key results """
        for obj in self:
            if obj.key_result_ids:
                total_progress = sum(obj.key_result_ids.mapped('progress'))
                obj.progress = total_progress / len(obj.key_result_ids)
            else:
                obj.progress = 0.0

    def action_activate(self):
        """Button: Draft → Active. Loops over self to support multi-record operations."""
        for obj in self:
            if obj.state == 'draft':
                obj.state = 'active'
        return True

    def action_complete(self):
        """Button: Active → Completed."""
        for obj in self:
            if obj.state == 'active':
                obj.state = 'completed'
        return True

    def action_cancel(self):
        """Button: Any → Cancelled (except already cancelled)."""
        for obj in self:
            if obj.state not in ('cancelled', 'completed'):
                obj.state = 'cancelled'
        return True
