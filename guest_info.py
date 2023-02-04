from odoo import fields, models


class GuestInfo(models.Model):
    _name = 'guest.info'
    _description = 'Guest Info'

    guest_id = fields.Many2one('res.partner', string="Guest", copy=False)
    rec_id = fields.Many2one('guest.details')
    gender = fields.Selection(string='Gender',
                              selection=[('male', 'Male'),
                                         ('female', 'Female')])
    age = fields.Integer()
