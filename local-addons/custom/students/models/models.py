import time
from bs4 import BeautifulSoup
from odoo import models, fields, api
from odoo.addons.queue_job.job import job
import logging
import requests


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
        base_url = 'https://oz.by/books/topic16.html'
        page = 1
        books = []
        request = requests.get(base_url)
        soup = BeautifulSoup(request.text, 'html.parser')
        page_count = soup.findAll('a', {'class': 'g-pagination__list__item'})[-1].text

        self._logger.info('executed with a: %s and k: %s', a, k)

        while page <= 10: #int(page_count):
            url = base_url + '?page=' + str(page)
            request = requests.get(url)
            soup = BeautifulSoup(request.text, 'html.parser')
            all_books = soup.findAll('div', {'class': 'item-type-card__inner'})

            for item in all_books:
                book_name = item.findAll('p', {'class': 'item-type-card__title'})[0].text
                book_author = item.findAll('p', {'class': 'item-type-card__info'})[0].text
                self._logger.info(book_name)
                books.append(book_name)
                values = {
                    'name': book_name,
                    'author': book_author
                }
                self.env['students.book'].add_book(values)

            page += 1

        self._logger.info("End : %s" % time.ctime())

    @job
    def add_book(self, values):
        record = self.env['students.book'].create(values)
        return record

    @api.multi
    def delete_all_books(self):
        # records = self.env['students.book'].search([])
        id = 1
        while id < 3130:#for id in records:
            self.env["students.book"].search([('id', '=', id)]).unlink()
            id += 1
        return True