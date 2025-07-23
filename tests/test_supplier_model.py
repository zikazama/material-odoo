# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSupplierModel(TransactionCase):
    """Test cases for Supplier model."""

    def setUp(self):
        """Set up test data."""
        super(TestSupplierModel, self).setUp()
        self.Supplier = self.env['material.supplier']

    def test_create_supplier_success(self):
        """Test successful supplier creation."""
        supplier_data = {
            'name': 'Test Supplier',
            'email': 'test@supplier.com',
            'phone': '+1234567890',
            'address': '123 Test Street, Test City'
        }
        supplier = self.Supplier.create(supplier_data)
        
        self.assertEqual(supplier.name, 'Test Supplier')
        self.assertEqual(supplier.email, 'test@supplier.com')
        self.assertEqual(supplier.phone, '+1234567890')
        self.assertEqual(supplier.address, '123 Test Street, Test City')
        self.assertEqual(supplier.material_count, 0)

    def test_create_supplier_required_name(self):
        """Test that supplier name is required."""
        with self.assertRaises(ValidationError):
            self.Supplier.create({
                'email': 'test@supplier.com',
                'phone': '+1234567890'
            })

    def test_supplier_name_uniqueness(self):
        """Test that supplier names must be unique."""
        # Create first supplier
        self.Supplier.create({'name': 'Unique Supplier'})
        
        # Try to create second supplier with same name
        with self.assertRaises(ValidationError):
            self.Supplier.create({'name': 'Unique Supplier'})

    def test_email_validation(self):
        """Test email format validation."""
        # Valid email should work
        supplier = self.Supplier.create({
            'name': 'Valid Email Supplier',
            'email': 'valid@email.com'
        })
        self.assertEqual(supplier.email, 'valid@email.com')
        
        # Invalid email should raise error
        with self.assertRaises(ValidationError):
            self.Supplier.create({
                'name': 'Invalid Email Supplier',
                'email': 'invalid-email'
            })

    def test_supplier_material_count(self):
        """Test material count computation."""
        supplier = self.Supplier.create({'name': 'Count Test Supplier'})
        self.assertEqual(supplier.material_count, 0)
        
        # Create materials for this supplier
        Material = self.env['material.registration']
        Material.create({
            'material_code': 'TEST001',
            'material_name': 'Test Material 1',
            'material_type': 'fabric',
            'material_buy_price': 150.0,
            'supplier_id': supplier.id
        })
        Material.create({
            'material_code': 'TEST002',
            'material_name': 'Test Material 2',
            'material_type': 'cotton',
            'material_buy_price': 200.0,
            'supplier_id': supplier.id
        })
        
        # Recompute and check count
        supplier._compute_material_count()
        self.assertEqual(supplier.material_count, 2)

    def test_supplier_delete_with_materials(self):
        """Test that supplier cannot be deleted if it has materials."""
        supplier = self.Supplier.create({'name': 'Supplier With Materials'})
        
        # Create a material for this supplier
        Material = self.env['material.registration']
        Material.create({
            'material_code': 'DEL001',
            'material_name': 'Delete Test Material',
            'material_type': 'jeans',
            'material_buy_price': 300.0,
            'supplier_id': supplier.id
        })
        
        # Try to delete supplier
        with self.assertRaises(ValidationError):
            supplier.unlink()

    def test_supplier_delete_without_materials(self):
        """Test that supplier can be deleted if it has no materials."""
        supplier = self.Supplier.create({'name': 'Deletable Supplier'})
        
        # Should be able to delete
        supplier.unlink()
        
        # Verify deletion
        deleted_supplier = self.Supplier.search([('name', '=', 'Deletable Supplier')])
        self.assertEqual(len(deleted_supplier), 0)

    def test_supplier_name_search(self):
        """Test name_search functionality."""
        # Create test suppliers
        supplier1 = self.Supplier.create({
            'name': 'ABC Textiles',
            'email': 'contact@abc.com'
        })
        supplier2 = self.Supplier.create({
            'name': 'XYZ Fabrics',
            'email': 'info@xyz.com'
        })
        
        # Search by name
        results = self.Supplier.name_search('ABC')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], supplier1.id)
        
        # Search by email
        results = self.Supplier.name_search('xyz.com')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], supplier2.id)
        
        # Search with no match
        results = self.Supplier.name_search('nonexistent')
        self.assertEqual(len(results), 0)

    def test_supplier_update(self):
        """Test supplier update functionality."""
        supplier = self.Supplier.create({
            'name': 'Original Name',
            'email': 'original@email.com'
        })
        
        # Update supplier
        supplier.write({
            'name': 'Updated Name',
            'email': 'updated@email.com',
            'phone': '+9876543210'
        })
        
        # Verify updates
        self.assertEqual(supplier.name, 'Updated Name')
        self.assertEqual(supplier.email, 'updated@email.com')
        self.assertEqual(supplier.phone, '+9876543210')

    def test_supplier_update_duplicate_name(self):
        """Test that updating to duplicate name raises error."""
        supplier1 = self.Supplier.create({'name': 'First Supplier'})
        supplier2 = self.Supplier.create({'name': 'Second Supplier'})
        
        # Try to update supplier2 to have same name as supplier1
        with self.assertRaises(ValidationError):
            supplier2.write({'name': 'First Supplier'}) 