from odoo import models, fields, api

class SaleOrderInherited(models.Model):
    _inherit = 'sale.order' 

    nameee = fields.Char(string='default value')
