from odoo import fields, models, api


class PaymentCalcultion(models.Model):
    _name = 'payment.calculation'
    _description = 'Payment Calculation'
    _inherit = 'uom.category'

    name = fields.Char(string='Description')
    quantity = fields.Integer()
    uom_id = fields.Many2one('uom.uom')
    company_id = fields.Many2one('res.company',
                                 default=lambda self:
                                 self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    unit_price = fields.Monetary()

    sub_total = fields.Monetary(compute='_compute_sub_total')
    reception_id = fields.Many2one('guest.details')

    @api.depends('quantity', 'unit_price')
    def _compute_sub_total(self):
        for rec in self:
            if rec.quantity and rec.unit_price:
                rec.sub_total = rec.quantity * rec.unit_price
            else:
                rec.sub_total = False
