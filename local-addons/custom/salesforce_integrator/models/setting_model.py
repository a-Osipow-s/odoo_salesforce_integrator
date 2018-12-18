from odoo import models, fields, api
from odoo.addons.queue_job.job import job
from simple_salesforce import Salesforce, SalesforceLogin
from openerp import _
import logging


class SalesforceCustomers(models.Model):
    _name = 'salesforce.customer'

    name = fields.Char(string="Name")
    comment = fields.Char(string="Comment")
    street = fields.Char(string="street")
    city = fields.Char(string="city")
    phone = fields.Char(string="phone")
    website = fields.Char(string="website")
    fax = fields.Char(string="fax")
    zip = fields.Char(string="zip")
    country = fields.Char(string="country")


class SalesforceOrders(models.Model):
    _name = 'salesforce.orders'

    name = fields.Char(string="Order")
    customer = fields.Char(string="Customer")
    state = fields.Char(string="Status")
    date_order = fields.Date(string="Effective Date")

class SalesForceImporter(models.Model):
    _name = 'salesforce.connector'

    _logger = logging.getLogger('SalesForceImporter_logger')
    field_name = fields.Char(sring="salesforce connector")
    sales_force = None

    username = 'toni@mail.ru'
    password = 'Vasykrab123'
    security_token = 'spAsycjVt9iBA56mXwFxRuRoD'

    def async_import_customers(self):
        self.env['salesforce.connector'].with_delay().add_customers_from_sales_force()

    def async_import_orders(self):
        self.env['salesforce.connector'].with_delay().import_sale_orders()


    @api.multi
    def connect_to_salesforce(self):
        try:
            session_id, instance = SalesforceLogin(
                username='toni@mail.ru',
                password='Vasykrab123',
                security_token='spAsycjVt9iBA56mXwFxRuRoD')
            sales_force = Salesforce(instance=instance, session_id=session_id)
            self._logger.info('successfully connect to sales_force. sales_force= %s' % self.sales_force)
            return sales_force
        except Exception as e:
            Warning(_(str(e)))

    @api.multi
    @job
    def add_customers_from_sales_force(self, customer_id=None):
        self.sales_force = self.connect_to_salesforce()
        query = "select id, name, shippingStreet, ShippingCity,Website, ShippingPostalCode, shippingCountry, fax, phone, Description from account"
        customers = []

        if customer_id:
            query = query + " where id='%s'" % customer_id

        contacts = self.sales_force.query(query=query)["records"]
        partner_model = self.env["salesforce.customer"]
        old_customers = partner_model.search([])
        old_customers_name = [customer.name for customer in old_customers]

        for customer in contacts:
            if customer["Name"] in old_customers_name:
                customers.append(partner_model.search([("name", "=", customer["Name"])]))
                continue

            customer_data = dict()
            customer_data["name"] = customer["Name"] if customer["Name"] else ""
            customer_data["street"] = customer["ShippingStreet"] if customer["ShippingStreet"] else ""
            customer_data["city"] = customer["ShippingCity"] if customer["ShippingCity"] else ""
            customer_data["phone"] = customer["Phone"] if customer["Phone"] else ""
            customer_data["comment"] = customer['Description'] if customer['Description'] else ""
            customer_data['website'] = customer["Website"] if customer["Website"] else ""
            customer_data["fax"] = customer["Fax"] if customer["Fax"] else ""
            customer_data["zip"] = customer["ShippingPostalCode"] if customer["ShippingPostalCode"] else ""
            customer_data["country"] = customer['ShippingCountry'] if customer['ShippingCountry'] else ""

            curr_customer = self.env["salesforce.customer"].create(customer_data)
            customers.append(curr_customer)

        self.env.cr.commit()
        return customers

    @job
    def import_sale_orders(self):
        try:
            self.sales_force = self.connect_to_salesforce()
            orders = self.sales_force.query("select id , AccountId, EffectiveDate, orderNumber, status from Order")['records']
            self._logger.info(orders)
            order_model = self.env["salesforce.orders"]
            order_name = [order.name for order in order_model.search([])]
            order_data = []

            for order in orders:
                if order["OrderNumber"] in order_name:
                    continue

                customer = self.add_customers_from_sales_force(order['AccountId'])[0]
                temp_order = {
                    "name": order["OrderNumber"],
                    "state": "draft" if order['Status'] == 'Draft' else 'sale',
                    "customer": customer.name,
                    "date_order": order['EffectiveDate']
                }

                order_data.append(temp_order)
                self.env["salesforce.orders"].create(temp_order)

            self.env.cr.commit()
            return order_data
        except Exception as e:
            raise Warning(_(str(e)))