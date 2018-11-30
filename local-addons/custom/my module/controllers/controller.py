from odoo import http

class Academy(http.Controller):
    @http.route('/myModul/myModul/', auth='public')
    def index(self, **kw):
        return http.request
