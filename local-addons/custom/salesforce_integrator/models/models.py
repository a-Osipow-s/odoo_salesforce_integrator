from odoo import models, fields, api
from simple_salesforce import Salesforce
from openerp import _


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
    sales_force = None

    field_name = fields.Char(sring="salesforce connector")

    def sync_data(self):
            self.import_data()

    def import_data(self):
        data_dictionary = {}
        if self.sales_force is None:
            raise Warning(_("Kindly provide Salesforce credentails for odoo user", ))
        if self.customers:
            data_dictionary["customers"] = self.add_customers_from_sales_force()
        if self.sales_orders:
            data_dictionary["sales_orders"] = self.import_sale_orders()

    def connect_to_salesforce(self):
        try:
            username = 'mycompany@mail.ru'
            password = 'admin1234'
            security_token = 'GnPAPC2gzkLr5TXllhMPgt4Mt'
            self.sales_force = Salesforce(username=username, password=password, security_token=security_token)
        except Exception as e:
            Warning(_(str(e)))

    def import_customers(self):
        try:
            self.add_customers_from_sales_force()
        except Exception as e:
            raise Warning(_(str(e)))

    def add_customers_from_sales_force(self, customer_id=None):
        query = "select id, name, shippingStreet, ShippingCity,Website, ShippingPostalCode, shippingCountry, fax, phone, Description from account %s"
        extend_query = ''
        customers = []

        if customer_id:
            extend_query = "where id='%s'" % customer_id
        contacts = self.sales_force.query(query % extend_query)["records"]
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