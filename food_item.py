from odoo import fields, models


class Food(models.Model):
    _name = 'food.item'
    _description = 'Food items'

    name = fields.Char(required=True)
    category_id = fields.Many2one('food.category')
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self:
                                 self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    price = fields.Monetary(string="Price", required=True)
    image = fields.Binary('Image')
    order_food_id = fields.Many2one('order.food')
    quantity = fields.Integer()
    uom_id = fields.Many2one('uom.uom')

    def action_order_food(self):
        view = self.env['food.item'].search([])
        for rec in view:
            res = {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'food.order',
                    'target': 'new',
                    'context': {
                        'default_name': rec.name,
                        'default_price': rec.price,
                        'default_image': rec.image
                    }
                }
        return res
