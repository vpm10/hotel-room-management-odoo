from odoo import fields, models


class FoodOrderTransient(models.Model):
    _name = 'food.order'
    _description = 'Food order'

    name = fields.Char(readonly=True)
    quantity = fields.Integer()
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self:
                                 self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    price = fields.Monetary(readonly=True)
    image = fields.Binary()

    def add_to_cart(self):
        record_ids = self.env['order.food'].search([])
        for record in record_ids:
            record.write({
                'order_list_ids': [(0, 0, {
                    'name': self.name,
                    'quantity': self.quantity,
                    'unit_price': self.price
                }
                )]
            })
        record_ids = self.env['guest.details'].search([])
        for record in record_ids:
            record.write({
                'payment_calculation_ids': [(0, 0, {
                    'name': self.name,
                    'quantity': self.quantity,
                    'unit_price': self.price
                }
                                    )]
            })
