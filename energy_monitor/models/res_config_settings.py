# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    
    energy_alert_email = fields.Char(
        string="Alert Email",
        config_parameter="energy_monitor.alert_email",
    )
    default_rate_electricity = fields.Float(
        string="Default Electricity Rate (Per kWh)",
        config_parameter="energy_monitor.default_rate_elec",
    )
