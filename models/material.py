# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Material(models.Model):
    _name = 'material.registration'
    _description = 'Material Registration'
    _order = 'material_code'
    _rec_name = 'material_name'

    material_code = fields.Char(
        string='Material Code',
        required=True,
        index=True,
        help='Unique code for the material'
    )
    material_name = fields.Char(
        string='Material Name',
        required=True,
        help='Name of the material'
    )
    material_type = fields.Selection([
        ('fabric', 'Fabric'),
        ('jeans', 'Jeans'),
        ('cotton', 'Cotton'),
    ], string='Material Type', required=True, help='Type of material')
    
    material_buy_price = fields.Float(
        string='Material Buy Price',
        required=True,
        digits=(16, 2),
        help='Purchase price of the material (minimum 100)'
    )
    supplier_id = fields.Many2one(
        'material.supplier',
        string='Related Supplier',
        required=True,
        ondelete='restrict',
        help='Supplier of this material'
    )
    supplier_name = fields.Char(
        related='supplier_id.name',
        string='Supplier Name',
        readonly=True,
        store=True
    )

    # Additional computed fields for better UX
    price_category = fields.Char(
        string='Price Category',
        compute='_compute_price_category',
        store=True
    )

    @api.depends('material_buy_price')
    def _compute_price_category(self):
        """Compute price category based on buy price."""
        for material in self:
            if material.material_buy_price < 100:
                material.price_category = 'Invalid (< 100)'
            elif material.material_buy_price < 500:
                material.price_category = 'Budget (100-499)'
            elif material.material_buy_price < 1000:
                material.price_category = 'Standard (500-999)'
            else:
                material.price_category = 'Premium (1000+)'

    @property
    def safe_supplier_name(self):
        try:
            return self.supplier_id.name if self.supplier_id else None
        except Exception:
            return None

    @property
    def safe_price_category(self):
        try:
            return self.price_category if self.price_category else None
        except Exception:
            return None

    @api.constrains('material_code')
    def _check_unique_material_code(self):
        """Ensure material code is unique."""
        for material in self:
            if material.material_code:
                existing = self.search([
                    ('material_code', '=', material.material_code),
                    ('id', '!=', material.id)
                ])
                if existing:
                    raise ValidationError(_(
                        'Material code must be unique. '
                        'A material with code "%s" already exists.'
                    ) % material.material_code)

    @api.constrains('material_buy_price')
    def _check_minimum_price(self):
        """Validate that material buy price is >= 100."""
        for material in self:
            if material.material_buy_price < 100:
                raise ValidationError(_(
                    'Material buy price must be at least 100. '
                    'Current price: %.2f'
                ) % material.material_buy_price)

    @api.constrains('material_name')
    def _check_material_name(self):
        """Validate material name is not empty."""
        for material in self:
            if not material.material_name or not material.material_name.strip():
                raise ValidationError(_('Material name cannot be empty.'))

    @api.model
    def create(self, vals):
        """Override create to add additional validations."""
        # Ensure all required fields are present
        required_fields = ['material_code', 'material_name', 'material_type', 
                          'material_buy_price', 'supplier_id']
        for field in required_fields:
            if not vals.get(field):
                raise ValidationError(_('Field "%s" is required.') % field)
        
        return super(Material, self).create(vals)

    def write(self, vals):
        """Override write to add additional validations."""
        # If updating price, validate it
        if 'material_buy_price' in vals and vals['material_buy_price'] < 100:
            raise ValidationError(_(
                'Material buy price must be at least 100. '
                'Attempted price: %.2f'
            ) % vals['material_buy_price'])
        
        return super(Material, self).write(vals)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Override name_search to search by code and name."""
        args = args or []
        if name:
            materials = self.search([
                '|',
                ('material_code', operator, name),
                ('material_name', operator, name)
            ] + args, limit=limit)
            return materials.name_get()
        return super(Material, self).name_search(name, args, operator, limit)

    def name_get(self):
        """Override name_get to show code and name."""
        result = []
        for material in self:
            name = '[%s] %s' % (material.material_code, material.material_name)
            result.append((material.id, name))
        return result

    @api.model
    def get_materials_by_type(self, material_type=None):
        """Method to get materials filtered by type (for API usage)."""
        domain = []
        if material_type:
            domain = [('material_type', '=', material_type)]
        
        materials = self.search(domain)
        return materials.read([
            'material_code', 'material_name', 'material_type',
            'material_buy_price', 'supplier_name'
        ])

    def get_material_summary(self):
        """Get summary information for a material. Return None if data tidak valid."""
        self.ensure_one()
        try:
            return {
                'id': self.id,
                'material_code': self.material_code,
                'material_name': self.material_name,
                'material_type': self.material_type,
                'material_buy_price': self.material_buy_price,
                'supplier_name': self.safe_supplier_name,
                'price_category': self.safe_price_category,
                'create_date': self.create_date.isoformat() if self.create_date else None,
                'write_date': self.write_date.isoformat() if self.write_date else None,
            }
        except Exception:
            return None 