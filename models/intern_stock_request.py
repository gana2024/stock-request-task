from odoo import models, fields, api, _
from odoo.exceptions import ValidationError , UserError
from datetime import datetime

class    InternStockRequest(models.Model):
    _name = 'intern.stock.request'

    name = fields.Char(string="Request Number", required=True, copy=False, readonly=True, default='New')
    requested_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user)
    date_requested = fields.Date(string='Date Requested', default=fields.Date.context_today, readonly=True)
    product_id = fields.Many2one('product.product', string='Products', required=True)
    product_uom_qty = fields.Float(string='Quantity', required=True)
    available_qty = fields.Float(string="Available Quantity", compute="_compute_available_qty", store=False,
                                 readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done')
    ], string='Status', default='draft')
    picking_id = fields.Many2one('stock.picking', string='Stock Picking', readonly=True)
    note = fields.Text(string='Note')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.request.sequence') or '/'
        return super().create(vals)

    def reorder_sequence(self):
        records = self.search([], order='create_date asc')
        counter = 1
        for rec in records:
            new_name = f"SR/{str(counter).zfill(4)}"
            rec.write({'name': new_name})
            counter += 1

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_done(self):
        for request in self:
            if request.state != 'approved':
                raise UserError("You can only mark done approved requests.")

            picking_type = self.env.ref('stock.picking_type_internal')

            source_location = self.env.ref('stock.stock_location_stock')
            dest_location = self.env.ref('stock_request_task.stock_location_stock_request_zone')

            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'location_id': source_location.id,
                'location_dest_id': dest_location.id,
                'origin': request.name,
            })
            self.picking_id = picking.id


            self.env['stock.move'].create({
                'name': request.name,
                'product_id': request.product_id.id,
                'product_uom': request.product_id.uom_id.id,
                'product_uom_qty': request.product_uom_qty,
                'picking_id': picking.id,
                'location_id': source_location.id,
                'location_dest_id': dest_location.id,
            })

            request.state = 'done'

    @api.depends('product_id')
    def _compute_available_qty(self):
        for rec in self:
            if rec.product_id:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', rec.product_id.id),
                    ('location_id', '=', self.env.ref('stock.stock_location_stock').id)
                ])
                rec.available_qty = sum(quants.mapped('quantity'))
            else:
                rec.available_qty = 0.0


