from odoo import models, fields, api

class SaleOrderInherited(models.Model):
    _name = 'test_module'

    AntonModule = fields.Char(string="this is string")
    inventor_id = fields.Integer()