

    # @api.one
    # def add_country(self, country_name):
    #     """
    #
    #     :return:
    #     """
    #     country_model = self.env["res.country"]
    #     country = country_model.search([('name', 'ilike', country_name)], limit=1)
    #     return country

    # def add_child_customers(self, customer_id, parent_id):
    #     query = "select name, mailingaddress, mailingpostalcode, mailingcountry, phone,email,fax,mobilephone," \
    #             "description from Contact where accountid='%s'"
    #     customers_detail_list = []
    #     contacts = self.sales_force.query(query % customer_id)["records"]
    #     partner_model = self.env["res.partner"]
    #     old_customers = partner_model.search([])
    #     old_customers_name = [customer.name for customer in old_customers]
    #     for customer in contacts:
    #         if customer["Name"] in old_customers_name:
    #             continue
    #         customer_data = dict()
    #         customer_data["name"] = customer["Name"] if customer["Name"] else ""
    #         customer_data["street"] = customer["MailingAddress"]["street"] if customer["MailingAddress"] else ""
    #         customer_data["city"] = customer["MailingAddress"]["city"] if customer["MailingAddress"] else ""
    #         customer_data["phone"] = customer["Phone"] if customer["Phone"] else ""
    #         customer_data["email"] = customer["Email"] if customer["Email"] else ""
    #         customer_data["fax"] = customer["Fax"] if customer["Fax"] else ""
    #         customer_data["mobile"] = customer["MobilePhone"] if customer["MobilePhone"] else ""
    #         customer_data["zip"] = customer["MailingPostalCode"] if customer["MailingPostalCode"] else ""
    #         customer_data["parent_id"] = parent_id
    #         customer_data["type"] = "invoice"
    #         customer_data["comment"] = customer['Description'] if customer['Description'] else ""
    #         country = self.add_country(customer['MailingCountry'])
    #         customer_data["country_id"] = country[0].id if country else ''
    #         customer_detail = partner_model.create(customer_data)
    #         customers_detail_list.append(customer_detail)
    #     self.env.cr.commit()

    # def export_products(self):
    #     try:
    #         products = self.get_products_not_in_salesforce()
    #         product_data = [{"Name": product["name"],
    #                         "Description":product["description"] if product["description"] else '',
    #                          "ProductCode":product["default_code"] if product["default_code"] else '',
    #                          "IsActive": True} for product in products]
    #         product_price = [product["list_price"] for product in products]
    #         counter = 0
    #         while 1:
    #             buffer = product_data[counter*200: (counter+1)*200]
    #             price_buffer = product_price[counter*200: (counter+1)*200]
    #             price_book = []
    #             if len(buffer) == 0:
    #                 break
    #             product_buffer = self.sales_force.bulk.Product2.insert(buffer)
    #             for product, price in zip(product_buffer, price_buffer):
    #                 if product["success"]:
    #                     price_book.append({"Pricebook2Id": self.get_standard_pricebook_id(),
    #                                        "Product2Id": product["id"],
    #                                        "UnitPrice": price,
    #                                        "IsActive": True})
    #             self.sales_force.bulk.PriceBookEntry.insert(price_book)
    #             counter += 1
    #         raise Warning(_("Products are exported to Salesforce from Odoo"))
    #     except Exception as e:
    #         raise Warning(_(str(e)))

    # def get_products_not_in_salesforce(self):
    #     """
    #
    #     :return:
    #     """
    #     filtered_products = []
    #     products = self.env["product.product"].search([])
    #     old_products = self.sales_force.query("select name, productCode from product2")["records"]
    #     p_filter = {str(p["Name"]) + str(p["ProductCode"] if p["ProductCode"] else "") for p in old_products}
    #     for product in products:
    #         product_filter = str(product["name"]) + str(product["default_code"] if product["default_code"] else "")
    #         if product_filter not in p_filter:
    #             filtered_products.append(product)
    #     return filtered_products
    #
    # def get_standard_pricebook_id(self):
    #     """
    #
    #     """
    #     pricebook_detail = self.sales_force.query("select id from pricebook2 where name = 'Standard Price Book'")["records"]
    #     if pricebook_detail:
    #         return pricebook_detail[0]["Id"]
    #     pricebook_detail = self.sales_force.PriceBook2.create({"name": 'Standard Price Book',
    #                                                            "IsActive": True})
    #     return pricebook_detail["id"]