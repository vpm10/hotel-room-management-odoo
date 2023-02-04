from odoo import fields, models, api


class OrderFood(models.Model):
    _name = 'order.food'
    _description = 'Food order'
    _rec_name = 'room_number_id'

    room_number_id = fields.Many2one('guest.details')
    guest = fields.Many2one(related='room_number_id.guest_id')
    order_time = fields.Datetime(string="Ordered Time",
                                 default=fields.Datetime.now(), readonly=True)
    category_ids = fields.Many2many('food.category', string='Categories')
    category_id = fields.Many2one('food.category')
    company_id = fields.Many2one('res.company',
                                 default=lambda self:
                                 self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    total_amount = fields.Monetary(compute='_compute_amount')
    food_item_ids = fields.One2many('food.item', 'order_food_id')
    order_list_ids = fields.One2many('order.list', 'order_food_id')

    @api.onchange('category_ids')
    def relation(self):
        self.write({
            'food_item_ids': [(5, 0)]
        })
        lines = []
        if self.category_ids:
            for rec in self.category_ids:
                food = self.env['food.item'].search(
                    [('category_id', '=', rec.name)]
                )
                for line in food:
                    val = (0, 0, {
                        'name': line.name,
                        'category_id': line.category_id,
                        'price': line.price,
                        'image': line.image
                    })
                    lines.append(val)
                    # print(lines)
        self.write({'food_item_ids': lines})

    def _compute_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.order_list_ids.mapped('sub_total'))
