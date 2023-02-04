from odoo import fields, models, api


class OrderList(models.Model):
    _name = 'order.list'
    _description = 'Order list'

    name = fields.Char(readonly=True)
    description = fields.Char()
    quantity = fields.Float()
    company_id = fields.Many2one('res.company',
                                 default=lambda self:
                                 self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    unit_price = fields.Monetary()
    sub_total = fields.Monetary(compute='_compute_sub_total')
    order_food_id = fields.Many2one('order.food')
    food_order_id = fields.Many2one('food.order')

    @api.depends('quantity', 'unit_price')
    def _compute_sub_total(self):
        for rec in self:
            if rec.quantity and rec.unit_price:
                rec.sub_total = rec.quantity * rec.unit_price
            else:
                rec.sub_total = False

