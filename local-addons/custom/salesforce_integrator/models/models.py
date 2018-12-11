from odoo import models, fields, api
#from simple_salesforce import Salesforce
from openerp import _
from openerp.exceptions import Warning, ValidationError
from openerp.osv import osv


class SalesforceSettingModel(models.Model):
    _inherit = 'res.users'
    _name = 'salesforce.user'
    sf_username = fields.Char(string='Username')
    sf_password = fields.Char(string='Password')
    sf_security_token = fields.Char(string='Security Token')

    @api.model
    def create(self, values):
        return super(SalesforceSettingModel, self).create(values)