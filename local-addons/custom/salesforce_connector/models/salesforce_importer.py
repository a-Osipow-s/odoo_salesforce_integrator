from odoo import models, fields, api
from simple_salesforce import Salesforce
from openerp import _
from openerp.osv import osv
from openerp.exceptions import Warning


class SalesForceImporter(models.Model):
    _name = 'salesforce.connector'
    sales_force = None
    field_name = fields.Char('salesforce_connector')
    # selection = fields.Selection([
    #     ('import_customers', 'Import Customers'),
    #     ('import_sale_orders', 'Import Sale Orders'),
    #     ("export_products", 'Export Product')
    # ], string='Select Import/Export Option')
    # history_id = fields.One2many('sync.history', 'order_id', copy=True)
    history_line = fields.One2many('sync.history', 'sync_id', copy=True)
    customers = fields.Boolean('Import Customers')
    sales_orders = fields.Boolean('Import Sale Orders')
    products = fields.Boolean('Export Products')

    def sync_data(self):
        """

        :return:
        """
        if self.customers or self.products or self.sales_orders:
            self.import_data()
        else:
            raise Warning(_("No Option Checked.",))
        # documents_link = self.env["sync.history"]
        # documents_link.create({"no_of_products_sync": 2,
        #                        "sync_id": 1})
        # self.env.cr.commit()

    def connect_to_salesforce(self):
        """
        """
        try:
            username = self.env.user.sf_username
            password = self.env.user.sf_password
            security_token = self.env.user.sf_security_token
            self.sales_force = Salesforce(username=username, password=password,
                                          security_token=security_token)
        except Exception as e:
            Warning(_(str(e)))

    def import_data(self):
        """

        :return:
        """
        success_message = "Customers Added: {} and {} updated.\n" \
                          "SalesOrders Added: {} and {} updated.\n" \
                          "Products Exported: {} and {} updated.\n"
        data_dictionary = {}
        # None if self.sales_force else self.connect_to_salesforce()
        if self.sales_force is None:
            raise Warning(_("Kindly provide Salesforce credentails for odoo user",))
        if self.customers:
            data_dictionary["customers"] = self.add_customers_from_sales_force()
        if self.sales_orders:
            data_dictionary["sales_orders"] = self.import_sale_orders()
        if self.products:
            data_dictionary["products"] = []
        raise osv.except_osv(_("Sync Details!"), _(success_message.format(len(data_dictionary["customers"]),
                                                                          0,
                                                                          len(data_dictionary["sales_orders"]),
                                                                          0,
                                                                          len(data_dictionary['products']),
                                                                          0)), )

    def import_customers(self):
        """

        :return:
        """
        try:
            return self.add_customers_from_sales_force()
        except Exception as e:
            raise Warning(_(str(e)))

    def import_sale_orders(self):
        """

        :return:
        """
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

    def add_order_products_in_product_model(self, order_id):
        """

        :return:
        """
        try:
            order_products_data = []
            order_lines = self.sales_force.query("select Pricebookentry.Product2Id , listprice, Quantity from "
                                                 "orderitem where orderid='%s'" % str(order_id))["records"]
            product_model = self.env["product.template"]
            old_products = product_model.search([])
            old_products_default_code = [product.default_code for product in old_products]
            for order_line in order_lines:
                product_id = order_line["PricebookEntry"]["Product2Id"]
                product_data = self.sales_force.query("select productCode, name, description from product2"
                                                      " where id='%s'" % str(product_id))["records"][0]
                if product_data["ProductCode"] in old_products_default_code:
                    order_products_data.append((product_model.search([('default_code', '=', product_data["ProductCode"])]),
                                                order_line["Quantity"]))
                    continue
                temp = dict()
                temp["name"] = product_data["Name"]
                temp["description"] = product_data["Description"]
                temp["default_code"] = product_data["ProductCode"]
                temp["list_price"] = order_line['ListPrice']
                temp["invoice_policy"] = "delivery"
                product_details = product_model.create(temp)
                order_products_data.append((product_details, order_line["Quantity"]))
            self.env.cr.commit()
            return order_products_data
        except Exception as e:
            raise Warning(_(str(e)))

    # def import_accounts(self):
    #     """
    #     Import Bank accounts from Sales force.
    #     """
    #     try:
    #         account_model = self.env['account.journal']
    #         old_accounts = account_model.search([])
    #         ac counts = self.sales_force.query("select id, accountnumber from account where accountnumber != ''")["records"]
    #         old_account_numbers = [account.name for account in old_accounts]
    #         for account in accounts:
    #             if account["AccountNumber"] in old_account_numbers:
    #                 continue
    #             temp = dict()
    #             temp["name"] = account["AccountNumber"]
    #             temp["code"] = 'sale'
    #             temp["type"] = 'bank'
    #             account_model.create(temp)
    #         self.env.cr.commit()
    #         raise Warning(_("Accounts are imported from Salesforce"))
    #     except Exception as e:
    #         raise Warning(_(str(e)))

    def get_product_id(self, tempalte_id):
        """

        """
        product = self.env["product.product"].search([("product_tmpl_id", '=', tempalte_id)])
        return product.id

    def add_customers_from_sales_force(self, customer_id=None):
        """

        """
        query = "select id, name, shippingStreet, ShippingCity,Website, ShippingPostalCode, shippingCountry, fax, phone, Description from account %s"
        extend_query = ''
        customers_detail_list = []
        if customer_id:
            extend_query = "where id='%s'" % customer_id
        contacts = self.sales_force.query(query % extend_query)["records"]
        partner_model = self.env["res.partner"]
        old_customers = partner_model.search([])
        old_customers_name = [customer.name for customer in old_customers]
        for customer in contacts:
            if customer["Name"] in old_customers_name:
                customers_detail_list.append(partner_model.search([("name", "=", customer["Name"])]))
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
            country = self.add_country(customer['ShippingCountry'])
            customer_data["country_id"] = country[0].id if country else ''
            customer_detail = partner_model.create(customer_data)
            self.env.cr.commit()
            self.add_child_customers(customer['Id'], customer_detail.id)
            customers_detail_list.append(customer_detail)
        self.env.cr.commit()
        return customers_detail_list

    @api.one
    def add_country(self, country_name):
        """

        :return:
        """
        country_model = self.env["res.country"]
        country = country_model.search([('name', 'ilike', country_name)], limit=1)
        return country

    def add_child_customers(self, customer_id, parent_id):
        """

        :return:
        """
        query = "select name, mailingaddress, mailingpostalcode, mailingcountry, phone,email,fax,mobilephone," \
                "description from Contact where accountid='%s'"
        customers_detail_list = []
        contacts = self.sales_force.query(query % customer_id)["records"]
        partner_model = self.env["res.partner"]
        old_customers = partner_model.search([])
        old_customers_name = [customer.name for customer in old_customers]
        for customer in contacts:
            if customer["Name"] in old_customers_name:
                continue
            customer_data = dict()
            customer_data["name"] = customer["Name"] if customer["Name"] else ""
            customer_data["street"] = customer["MailingAddress"]["street"] if customer["MailingAddress"] else ""
            customer_data["city"] = customer["MailingAddress"]["city"] if customer["MailingAddress"] else ""
            customer_data["phone"] = customer["Phone"] if customer["Phone"] else ""
            customer_data["email"] = customer["Email"] if customer["Email"] else ""
            customer_data["fax"] = customer["Fax"] if customer["Fax"] else ""
            customer_data["mobile"] = customer["MobilePhone"] if customer["MobilePhone"] else ""
            customer_data["zip"] = customer["MailingPostalCode"] if customer["MailingPostalCode"] else ""
            customer_data["parent_id"] = parent_id
            customer_data["type"] = "invoice"
            customer_data["comment"] = customer['Description'] if customer['Description'] else ""
            country = self.add_country(customer['MailingCountry'])
            customer_data["country_id"] = country[0].id if country else ''
            customer_detail = partner_model.create(customer_data)
            customers_detail_list.append(customer_detail)
        self.env.cr.commit()

    def export_products(self):
        """


        """
        try:
            products = self.get_products_not_in_salesforce()
            product_data = [{"Name": product["name"],
                            "Description":product["description"] if product["description"] else '',
                             "ProductCode":product["default_code"] if product["default_code"] else '',
                             "IsActive": True} for product in products]
            product_price = [product["list_price"] for product in products]
            counter = 0
            while 1:
                buffer = product_data[counter*200: (counter+1)*200]
                price_buffer = product_price[counter*200: (counter+1)*200]
                price_book = []
                if len(buffer) == 0:
                    break
                product_buffer = self.sales_force.bulk.Product2.insert(buffer)
                for product, price in zip(product_buffer, price_buffer):
                    if product["success"]:
                        price_book.append({"Pricebook2Id": self.get_standard_pricebook_id(),
                                           "Product2Id": product["id"],
                                           "UnitPrice": price,
                                           "IsActive": True})
                self.sales_force.bulk.PriceBookEntry.insert(price_book)
                counter += 1
            raise Warning(_("Products are exported to Salesforce from Odoo"))
        except Exception as e:
            raise Warning(_(str(e)))

    def get_products_not_in_salesforce(self):
        """

        :return:
        """
        filtered_products = []
        products = self.env["product.product"].search([])
        old_products = self.sales_force.query("select name, productCode from product2")["records"]
        p_filter = {str(p["Name"]) + str(p["ProductCode"] if p["ProductCode"] else "") for p in old_products}
        for product in products:
            product_filter = str(product["name"]) + str(product["default_code"] if product["default_code"] else "")
            if product_filter not in p_filter:
                filtered_products.append(product)
        return filtered_products

    def get_standard_pricebook_id(self):
        """

        """
        pricebook_detail = self.sales_force.query("select id from pricebook2 where name = 'Standard Price Book'")["records"]
        if pricebook_detail:
            return pricebook_detail[0]["Id"]
        pricebook_detail = self.sales_force.PriceBook2.create({"name": 'Standard Price Book',
                                                               "IsActive": True})
        return pricebook_detail["id"]

    def create_html_file(self, data_dictionary):
        """

        :param data_dictionary:
        :return:
        """
        


class Dropboxlinks(models.Model):

    _name = 'sync.history'
    _order = 'sync_date desc'
    sync_id = fields.Many2one('salesforce.connector', string='Partner Reference', required=True, ondelete='cascade',
                              index=True, copy=False)
    sync_date = fields.Datetime('Sync Date', readonly=True, required=True, default=fields.Datetime.now)
    no_of_orders_sync = fields.Integer('Sync Products', readonly=True)
    no_of_products_sync = fields.Integer('Sync Products', readonly=True)
    no_of_customers_sync = fields.Integer('Sync Customers', readonly=True)
    document_link = fields.Char('Document Link', readonly=True)


