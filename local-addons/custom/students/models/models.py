from odoo import models, fields, api
from odoo.addons.queue_job.job import job
import logging


class Person(models.Model):
    _name = 'students.person'
    _logger = logging.getLogger('person_logger')

    name = fields.Char(string="Name", required=True)
    surname = fields.Char(string="Surname", required=True)
    age = fields.Integer(string="Age")
    book_count = fields.Integer(compute='count_of_books', string="Count of books", store=True)

    books = fields.Many2many('students.book', 'rel_book')

    @api.model
    def create(self, values):
        if values['age'] < 18:
            values['age'] = 18
        record = super(Person, self).create(values)
        return record

    @api.depends('books')
    def count_of_books(self):
        for item in self:
            name = len(self.books)
            item.book_count = name


class Book(models.Model):
    _name = "students.book"
    _logger = logging.getLogger('book_logger')

    name = fields.Char(string="Book Name", require=True)
    author = fields.Char(string="Book author")

    @api.multi
    def call_async_func(self):
        self.env['students.book'].with_delay().async_func('a', k=2)

    @api.multi
    @job
    def async_func(self, a, k=None):
        self._logger.info('executed with a: %s and k: %s', a, k)