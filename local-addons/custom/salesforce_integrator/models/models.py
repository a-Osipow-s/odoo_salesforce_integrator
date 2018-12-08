from odoo import models, fields, api
from simple_salesforce import Salesforce, SalesforceLogin
from openerp import _
import logging


class SalesforceCustomers(models.Model):
    _name = 'salesforce.customer'

    name = fields.Char(string="Name")
    comment = fields.Char(string="Comment")

    @api.model
    def create(self, values):
        record = super(SalesforceCustomers, self).create(values)
        return record


class SalesForceImporter(models.Model):
    _name = 'salesforce.connector'
    _logger = logging.getLogger('SalesForceImporter_logger')
    field_name = fields.Char(sring="salesforce connector")
    sales_force = None

    def sync_data(self):
        self.import_data()

    def import_data(self):
        data_dictionary = {}

        username = 'mycompany@mail.ru'
        password = 'admin123456'
        security_token = 'xnVi1tGutbGedB7Wzg1hTv1jT'
        session_id, instance = SalesforceLogin(
            username=username,
            password=password,
            security_token=security_token)
        self.sales_force = Salesforce(instance=instance, session_id=session_id)
        self._logger.info('successfully connect to sales_force. sales_force= %s' % self.sales_force)

        if self.sales_force is None:
            raise Warning(_("Kindly provide Salesforce credentails for odoo user", ))
        else:
            data_dictionary["customers"] = self.add_customers_from_sales_force()
        # if self.sales_orders:
        #     data_dictionary["sales_orders"] = self.import_sale_orders()

    @api.multi
    def connect_to_salesforce(self):
        try:
            username = 'mycompany@mail.ru'
            password = 'admin123456'
            security_token = 'xnVi1tGutbGedB7Wzg1hTv1jT'
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
        for customer in contacts:
            customer_data = dict()
            customer_data["name"] = customer["Name"] if customer["Name"] else ""
            customer_data["comment"] = customer['Description'] if customer['Description'] else ""

            curr_customer = self.env["salesforce.customer"].create(customer_data)
            customers.append(curr_customer)
        self.env.cr.commit()
        return customers

    def import_sale_orders(self):
        try:
            orders = self.sales_force.query("select id , AccountId,"
                                            " EffectiveDate, orderNumber, status from Order")['records']
            order_model = self.env["sale.order"]
            order_name = [order.name for order in order_model.search([])]
            order_data = []
            for order in orders:
                if order["OrderNumber"] in order_name:
                    continue
                details = self.add_order_products_in_product_model(order["Id"])
                customer = self.add_customers_from_sales_force(order['AccountId'])[0]
                temp_order = {"name": order["OrderNumber"],
                              "partner_id": customer.id,
                              "state": "draft" if order['Status'] == 'Draft' else 'sale',
                              "invoice_status": "no",
                              "confirmation_date": order['EffectiveDate'],
                              "date_order": order['EffectiveDate']}
                order_data.append(temp_order)
                sale_order = self.env["sale.order"].create(temp_order)
                self.env.cr.commit()
                for product_details, quantity in details:
                    self.env["sale.order.line"].create({'product_uom': 1,
                                                        'product_id': self.get_product_id(product_details.id),
                                                        'order_partner_id': customer.id, "order_id": sale_order.id,
                                                        "product_uom_qty": quantity})
            self.env.cr.commit()
            return order_data
        except Exception as e:
            raise Warning(_(str(e)))
