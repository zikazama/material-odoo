# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Supplier(models.Model):
    _name = 'material.supplier'
    _description = 'Material Supplier'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(
        string='Supplier Name',
        required=True,
        index=True,
        help='Name of the supplier'
    )
    email = fields.Char(
        string='Email',
        help='Email address of the supplier'
    )
    phone = fields.Char(
        string='Phone',
        help='Phone number of the supplier'
    )
    address = fields.Text(
        string='Address',
        help='Full address of the supplier'
    )
    material_ids = fields.One2many(
        'material.registration',
        'supplier_id',
        string='Materials',
        help='Materials provided by this supplier'
    )
    material_count = fields.Integer(
        string='Material Count',
        compute='_compute_material_count',
        store=True
    )

    @api.depends('material_ids')
    def _compute_material_count(self):
        """Compute the number of materials for this supplier."""
        for supplier in self:
            supplier.material_count = len(supplier.material_ids)

    @property
    def safe_material_count(self):
        try:
            return len(self.material_ids) if self.material_ids else 0
        except Exception:
            return 0

    @api.constrains('name')
    def _check_unique_name(self):
        """Ensure supplier name is unique."""
        for supplier in self:
            if supplier.name:
                existing = self.search([
                    ('name', '=', supplier.name),
                    ('id', '!=', supplier.id)
                ])
                if existing:
                    raise ValidationError(_('Supplier name must be unique. '
                                          'A supplier with name "%s" already exists.') % supplier.name)

    @api.constrains('email')
    def _check_email_format(self):
        """Validate email format if provided."""
        for supplier in self:
            if supplier.email and '@' not in supplier.email:
                raise ValidationError(_('Please enter a valid email address.'))

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Override name_search to search by name and email."""
        args = args or []
        if name:
            suppliers = self.search([
                '|',
                ('name', operator, name),
                ('email', operator, name)
            ] + args, limit=limit)
            return suppliers.name_get()
        return super(Supplier, self).name_search(name, args, operator, limit)

    def unlink(self):
        """Prevent deletion if supplier has materials."""
        for supplier in self:
            if supplier.material_ids:
                raise ValidationError(_(
                    'Cannot delete supplier "%s" because it has associated materials. '
                    'Please remove or reassign the materials first.'
                ) % supplier.name)
        return super(Supplier, self).unlink() 