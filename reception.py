from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class ReceptionManagement(models.Model):
    _name = 'guest.details'
    _description = 'Guest details'
    _inherit = 'mail.thread'
    _rec_name = 'room_id'

    name = fields.Char(readonly=True, required=True, copy=False,
                       default=lambda self: _('New'))
    guest_id = fields.Many2one('res.partner', string='Guest', required=True)
    address = fields.Char(related='guest_id.contact_address')
    number_of_guests = fields.Integer(string='Number of guests')
    check_in = fields.Datetime(string='Check in time',
                               default=fields.Datetime.now(), readonly=False)
    check_out = fields.Datetime(string='Check out time', readonly=False)
    bed = fields.Selection(
        string='Bed type', selection=[('single', 'Single Bed'),
                                      ('double', 'Double Bed'),
                                      ('dormitory', 'Dormitory')]
    )
    facilities_ids = fields.Many2many('facility', string='Facilities',
                                      copy=False)
    room_id = fields.Many2one('hotel.room', copy=False, required=True,
                              string='Room Number',
                              domain=[('state', '=', 'available')])
    rent = fields.Monetary(related='room_id.rent', string='Rent per day')
    state = fields.Selection(
        string='State', selection=[('draft', 'Draft'),
                                   ('check_in', 'Check in'),
                                   ('check_out', 'Check out'),
                                   ('cancel', 'Cancel')],
        default='draft'
    )
    expected_days = fields.Integer(default=1)
    expected_date = fields.Date(compute='_compute_expected_date')
    guest_info_ids = fields.One2many('guest.info', 'rec_id')
    guest_number = fields.Many2one('guest.info')
    attachment_count = fields.Integer()
    check_out_warning = fields.Boolean()
    late_check_out_danger = fields.Boolean()
    payment_calculation_ids = fields.One2many('payment.calculation',
                                              'reception_id')
    company_id = fields.Many2one('res.company',
                                 default=lambda self:
                                 self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    total_amount = fields.Monetary(compute='_compute_total_amount',
                                   string='Total')
    total_days = fields.Char()
    total_rent = fields.Integer()
    payment_stage = fields.Boolean()
    order_food_id = fields.Many2one('payment.calculation')
    food_amount = fields.Monetary(related='order_food_id.sub_total')

    @api.depends('expected_days', 'check_in')
    def _compute_expected_date(self):
        for rec in self:
            if rec.check_in and rec.expected_days:
                rec.expected_date = rec.check_in + \
                                    relativedelta(days=int(rec.expected_days))

            else:
                rec.expected_date = False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'guest.details') or 'New'
        res = super(ReceptionManagement, self).create(vals)
        return res

    def button_in_draft(self):
        if self.number_of_guests != len(self.guest_info_ids):
            raise ValidationError('Please provide all guest details')
        self.state = 'check_in'
        self.room_id.state = 'not_available'
        obj_attachment = self.env['ir.attachment']

        for record in self:

            record.attachment_count = obj_attachment.search_count(
                [('res_model', '=', 'guest.details'),
                 ('res_id', '=', record.id)])

            if record.attachment_count == 0:
                raise ValidationError('Please upload address proof')

    def button_in_progress(self):
        # self.check_out = fields.Datetime.now()
        self.state = "check_out"
        self.room_id.state = 'available'
        for rec in self:
            rec.total_days = (rec.check_out - rec.check_in).days
            rec.total_rent = int(rec.total_days) * rec.room_id.rent
        for record in self:
            record.write({
                'payment_calculation_ids': [(0, 0, {
                    'name': 'Rent',
                    'quantity': record.total_days,
                    'unit_price': record.rent
                })]
            })
        inv = self.env['account.move'].create({
            'partner_id': self.guest_id.id,
            'move_type': 'out_invoice',
            'payment_reference': self.id,
            'date': self.check_out,
            'invoice_line_ids': [
                (0, 0, {
                    'name': pay.name,
                    'price_unit': pay.sub_total

                }) for pay in self.payment_calculation_ids
            ],
        })
        return {
            'name': 'Invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'payment_reference': self.id,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_id': inv.id
        }

    def get_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('payment_reference', '=', self.id)],
        }

    def button_in_checkout(self):
        self.write({'state': "cancel"})

    @api.onchange('expected_date')
    def late_checkout(self):
        for rec in self:

            if rec.check_out is False and \
                    rec.expected_date < fields.Date.today():
                self.late_check_out_danger = True
            elif rec.expected_date == fields.Date.today():
                self.check_out_warning = True

    @api.onchange('bed')
    def onchange_bed(self):
        for rec in self:
            return {'domain': {'room_id': [('bed', '=', rec.bed)]}}

    @api.onchange('number_of_guests')
    def onchange_num_of_guest(self):
        for rec in self:
            if rec.number_of_guests == 1:
                self.bed = 'single'
            elif rec.number_of_guests == 2:
                self.bed = 'double'
            elif rec.number_of_guests >= 3:
                self.bed = 'dormitory'

    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(
                rec.payment_calculation_ids.mapped('sub_total'))


class StateChange(models.Model):
    _inherit = 'account.move'

    relation_id = fields.Many2one('guest.details')

    @api.constrains('payment_state')
    def _payment_stage(self):
        records = self.env['guest.details'].search([])
        for record in self:
            if record.payment_state == 'paid':
                for rec in records:
                    rec.payment_stage = True
