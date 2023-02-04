from odoo import fields, models


class FoodCategory(models.Model):
    _name = 'food.category'
    _description = 'Food category'

    name = fields.Char(required=True)
