from odoo import models, fields, api
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

    @api.model
    def create(self, values):
        record = super(SalesforceCustomers, self).create(values)
        return record

class SalesforceOrders(models.Model):
    _name = 'salesforce.orders'

    order = fields.Char(string="Order")
    partner_id = fields.Char(string="Customer id")
    customer = fields.Char(string="Customer")
    state = fields.Char(string="Status")
    date_order = fields.Date(string="Effective Date")

    @api.model
    def create(self, values):
        record = super(SalesforceOrders, self).create(values)
        return record

class SalesForceImporter(models.Model):
    _name = 'salesforce.connector'

    _logger = logging.getLogger('SalesForceImporter_logger')
    field_name = fields.Char(sring="salesforce connector")
    sales_force = None


    username = 'toni@mail.ru'
    password = 'Vasykrab123'
    security_token = 'spAsycjVt9iBA56mXwFxRuRoD'

    def sync_data(self):
        self.import_data()

    def import_data(self):
        data_dictionary = {}
        session_id, instance = SalesforceLogin(
            username=self.username,
            password=self.password,
            security_token=self.security_token)
        self.sales_force = Salesforce(instance=instance, session_id=session_id)
        self._logger.info('successfully connect to sales_force. sales_force= %s' % self.sales_force)

        if self.sales_force is None:
            raise Warning(_("Kindly provide Salesforce credentails for odoo user", ))
        else:
            data_dictionary["customers"] = self.add_customers_from_sales_force()
            self.import_sale_orders()

    @api.multi
    def connect_to_salesforce(self):
        try:
            username = 'toni@mail.ru'
            password = 'Vasykrab123'
            security_token = 'spAsycjVt9iBA56mXwFxRuRoD'
            session_id, instance = SalesforceLogin(
                username=username,
                password=password,
                security_token=security_token)
            self.sales_force = Salesforce(instance=instance, session_id=session_id)
            self._logger.info('successfully connect to sales_force. sales_force= %s' % self.sales_force)
        except Exception as e:
            Warning(_(str(e)))
        return True

    def import_customers(self):
        try:
            self.add_customers_from_sales_force()
        except Exception as e:
            raise Warning(_(str(e)))

    @api.multi
    def add_customers_from_sales_force(self, customer_id=None):
        self._logger.info('gurrent sales_force state: %s' % self.sales_force)
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
                continue

        for customer in contacts:
            customer_data = dict()
            customer_data["id"] = customer["Id"] if customer["Id"] else ""
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


    def import_sale_orders(self):
        try:
            orders = self.sales_force.query("select id , AccountId, EffectiveDate, orderNumber, status from Order")['records']
            self._logger.info(orders)
            order_model = self.env["salesforce.orders"]
            order_name = [order.order for order in order_model.search([])]
            order_data = []
            for order in orders:
                if order["OrderNumber"] in order_name:
                    continue
                customer = order_model.search(['id', '=', order['AccountId']])
                self._logger.warning(customer)
                temp_order = {"order": order["OrderNumber"],
                              "partner_id": "test id",
                              "state": "draft" if order['Status'] == 'Draft' else 'sale',
                              "customer": customer.name,
                              "date_order": order['EffectiveDate']}
                order_data.append(temp_order)
                self.env["salesforce.orders"].create(temp_order)
                self.env.cr.commit()

            self.env.cr.commit()
            return order_data
        except Exception as e:
            raise Warning(_(str(e)))
