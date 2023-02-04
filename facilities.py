from odoo import fields, models


class Facility(models.Model):
    _name = 'facility'
    _description = 'Facilities'

    name = fields.Char(required=True)
