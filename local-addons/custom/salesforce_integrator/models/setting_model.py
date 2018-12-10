from odoo import models, fields, api
#from simple_salesforce import Salesforce
from openerp import _
from openerp.exceptions import Warning, ValidationError
from openerp.osv import osv


class SalesforceSettingModel(models.Model):
    _inherit = 'res.users'
    _name = 'salesforce.user'
    # sf_name = fields.Char(string='Name')
    sf_username = fields.Char(string='Username')
    sf_password = fields.Char(string='Password')
    sf_security_token = fields.Char(string='Security Token')

    # def test_credientials(self):
    #     try:
    #         #sf = Salesforce(username=self.sf_username, password=self.sf_password, security_token=self.sf_security_token)
    #         raise Warning('Credentials Test Successful.')
    #     except Exception as e:
    #         raise Warning(_(str(e)))

    @api.model
    def create(self, values):
        return super(SalesforceSettingModel, self).create(values)