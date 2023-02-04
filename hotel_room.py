from odoo import fields, models


class HotelRoomManagement(models.Model):
    _name = 'hotel.room'
    _description = 'Hotel Room Management'
    _inherit = 'mail.thread'

    name = fields.Integer(required=True, string='Room Number')
    bed = fields.Selection(
        string='Bed type', selection=[('single', 'Single Bed'),
                                      ('double', 'Double Bed'),
                                      ('dormitory', 'Dormitory')]
    )
    available_bed = fields.Integer(string='Available Bed')
    facilities_ids = fields.Many2many('facility', string='Facilities',
                                      copy=False, required=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda self:
                                 self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    rent = fields.Monetary(string="Rent")
    state = fields.Selection(
        string='State', selection=[('available', 'Available'),
                                   ('not_available', 'Not available')
                                   ], default='available', tracking=True)
    guest_details = fields.Many2one('guest.details')
