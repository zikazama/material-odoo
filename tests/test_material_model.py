# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMaterialModel(TransactionCase):
    """Test cases for Material model."""

    def setUp(self):
        """Set up test data."""
        super(TestMaterialModel, self).setUp()
        self.Material = self.env['material.registration']
        self.Supplier = self.env['material.supplier']
        
        # Create test supplier
        self.test_supplier = self.Supplier.create({
            'name': 'Test Supplier',
            'email': 'test@supplier.com'
        })

    def test_create_material_success(self):
        """Test successful material creation."""
        material_data = {
            'material_code': 'MAT001',
            'material_name': 'Test Material',
            'material_type': 'fabric',
            'material_buy_price': 150.0,
            'supplier_id': self.test_supplier.id
        }
        material = self.Material.create(material_data)
        
        self.assertEqual(material.material_code, 'MAT001')
        self.assertEqual(material.material_name, 'Test Material')
        self.assertEqual(material.material_type, 'fabric')
        self.assertEqual(material.material_buy_price, 150.0)
        self.assertEqual(material.supplier_id.id, self.test_supplier.id)
        self.assertEqual(material.supplier_name, 'Test Supplier')

    def test_create_material_required_fields(self):
        """Test that all required fields are validated."""
        # Test missing material_code
        with self.assertRaises(ValidationError):
            self.Material.create({
                'material_name': 'Test Material',
                'material_type': 'fabric',
                'material_buy_price': 150.0,
                'supplier_id': self.test_supplier.id
            })
        
        # Test missing material_name
        with self.assertRaises(ValidationError):
            self.Material.create({
                'material_code': 'MAT001',
                'material_type': 'fabric',
                'material_buy_price': 150.0,
                'supplier_id': self.test_supplier.id
            })
        
        # Test missing material_type
        with self.assertRaises(ValidationError):
            self.Material.create({
                'material_code': 'MAT001',
                'material_name': 'Test Material',
                'material_buy_price': 150.0,
                'supplier_id': self.test_supplier.id
            })
        
        # Test missing material_buy_price
        with self.assertRaises(ValidationError):
            self.Material.create({
                'material_code': 'MAT001',
                'material_name': 'Test Material',
                'material_type': 'fabric',
                'supplier_id': self.test_supplier.id
            })
        
        # Test missing supplier_id
        with self.assertRaises(ValidationError):
            self.Material.create({
                'material_code': 'MAT001',
                'material_name': 'Test Material',
                'material_type': 'fabric',
                'material_buy_price': 150.0
            })

    def test_material_code_uniqueness(self):
        """Test that material codes must be unique."""
        # Create first material
        self.Material.create({
            'material_code': 'UNIQUE001',
            'material_name': 'First Material',
            'material_type': 'fabric',
            'material_buy_price': 150.0,
            'supplier_id': self.test_supplier.id
        })
        
        # Try to create second material with same code
        with self.assertRaises(ValidationError):
            self.Material.create({
                'material_code': 'UNIQUE001',
                'material_name': 'Second Material',
                'material_type': 'cotton',
                'material_buy_price': 200.0,
                'supplier_id': self.test_supplier.id
            })

    def test_minimum_price_validation(self):
        """Test that material buy price must be >= 100."""
        # Valid price should work
        material = self.Material.create({
            'material_code': 'PRICE001',
            'material_name': 'Valid Price Material',
            'material_type': 'fabric',
            'material_buy_price': 100.0,
            'supplier_id': self.test_supplier.id
        })
        self.assertEqual(material.material_buy_price, 100.0)
        
        # Price below 100 should raise error
        with self.assertRaises(ValidationError):
            self.Material.create({
                'material_code': 'PRICE002',
                'material_name': 'Invalid Price Material',
                'material_type': 'fabric',
                'material_buy_price': 99.99,
                'supplier_id': self.test_supplier.id
            })

    def test_material_type_validation(self):
        """Test material type selection validation."""
        valid_types = ['fabric', 'jeans', 'cotton']
        
        # Test all valid types
        for i, material_type in enumerate(valid_types):
            material = self.Material.create({
                'material_code': f'TYPE{i+1:03d}',
                'material_name': f'Test {material_type.title()} Material',
                'material_type': material_type,
                'material_buy_price': 150.0,
                'supplier_id': self.test_supplier.id
            })
            self.assertEqual(material.material_type, material_type)

    def test_price_category_computation(self):
        """Test price category computation."""
        # Test Budget category (100-499)
        material1 = self.Material.create({
            'material_code': 'CAT001',
            'material_name': 'Budget Material',
            'material_type': 'fabric',
            'material_buy_price': 250.0,
            'supplier_id': self.test_supplier.id
        })
        material1._compute_price_category()
        self.assertEqual(material1.price_category, 'Budget (100-499)')
        
        # Test Standard category (500-999)
        material2 = self.Material.create({
            'material_code': 'CAT002',
            'material_name': 'Standard Material',
            'material_type': 'jeans',
            'material_buy_price': 750.0,
            'supplier_id': self.test_supplier.id
        })
        material2._compute_price_category()
        self.assertEqual(material2.price_category, 'Standard (500-999)')
        
        # Test Premium category (1000+)
        material3 = self.Material.create({
            'material_code': 'CAT003',
            'material_name': 'Premium Material',
            'material_type': 'cotton',
            'material_buy_price': 1500.0,
            'supplier_id': self.test_supplier.id
        })
        material3._compute_price_category()
        self.assertEqual(material3.price_category, 'Premium (1000+)')

    def test_material_name_validation(self):
        """Test material name validation."""
        # Empty name should raise error
        with self.assertRaises(ValidationError):
            self.Material.create({
                'material_code': 'NAME001',
                'material_name': '',
                'material_type': 'fabric',
                'material_buy_price': 150.0,
                'supplier_id': self.test_supplier.id
            })
        
        # Whitespace-only name should raise error
        with self.assertRaises(ValidationError):
            self.Material.create({
                'material_code': 'NAME002',
                'material_name': '   ',
                'material_type': 'fabric',
                'material_buy_price': 150.0,
                'supplier_id': self.test_supplier.id
            })

    def test_material_update_price_validation(self):
        """Test price validation during update."""
        material = self.Material.create({
            'material_code': 'UPDATE001',
            'material_name': 'Update Test Material',
            'material_type': 'fabric',
            'material_buy_price': 200.0,
            'supplier_id': self.test_supplier.id
        })
        
        # Valid price update should work
        material.write({'material_buy_price': 300.0})
        self.assertEqual(material.material_buy_price, 300.0)
        
        # Invalid price update should raise error
        with self.assertRaises(ValidationError):
            material.write({'material_buy_price': 50.0})

    def test_material_name_search(self):
        """Test name_search functionality."""
        material1 = self.Material.create({
            'material_code': 'SEARCH001',
            'material_name': 'Cotton Fabric',
            'material_type': 'cotton',
            'material_buy_price': 150.0,
            'supplier_id': self.test_supplier.id
        })
        material2 = self.Material.create({
            'material_code': 'SEARCH002',
            'material_name': 'Denim Jeans',
            'material_type': 'jeans',
            'material_buy_price': 250.0,
            'supplier_id': self.test_supplier.id
        })
        
        # Search by code
        results = self.Material.name_search('SEARCH001')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], material1.id)
        
        # Search by name
        results = self.Material.name_search('Denim')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], material2.id)

    def test_material_name_get(self):
        """Test name_get functionality."""
        material = self.Material.create({
            'material_code': 'DISPLAY001',
            'material_name': 'Display Test Material',
            'material_type': 'fabric',
            'material_buy_price': 150.0,
            'supplier_id': self.test_supplier.id
        })
        
        name_get_result = material.name_get()
        expected_name = '[DISPLAY001] Display Test Material'
        self.assertEqual(name_get_result[0][1], expected_name)

    def test_get_materials_by_type(self):
        """Test get_materials_by_type method."""
        # Create materials of different types
        fabric_material = self.Material.create({
            'material_code': 'FABRIC001',
            'material_name': 'Fabric Material',
            'material_type': 'fabric',
            'material_buy_price': 150.0,
            'supplier_id': self.test_supplier.id
        })
        jeans_material = self.Material.create({
            'material_code': 'JEANS001',
            'material_name': 'Jeans Material',
            'material_type': 'jeans',
            'material_buy_price': 200.0,
            'supplier_id': self.test_supplier.id
        })
        
        # Test filtering by type
        fabric_results = self.Material.get_materials_by_type('fabric')
        self.assertEqual(len(fabric_results), 1)
        self.assertEqual(fabric_results[0]['material_code'], 'FABRIC001')
        
        jeans_results = self.Material.get_materials_by_type('jeans')
        self.assertEqual(len(jeans_results), 1)
        self.assertEqual(jeans_results[0]['material_code'], 'JEANS001')
        
        # Test getting all materials
        all_results = self.Material.get_materials_by_type()
        self.assertEqual(len(all_results), 2)

    def test_get_material_summary(self):
        """Test get_material_summary method."""
        material = self.Material.create({
            'material_code': 'SUMMARY001',
            'material_name': 'Summary Test Material',
            'material_type': 'cotton',
            'material_buy_price': 350.0,
            'supplier_id': self.test_supplier.id
        })
        
        summary = material.get_material_summary()
        
        self.assertEqual(summary['material_code'], 'SUMMARY001')
        self.assertEqual(summary['material_name'], 'Summary Test Material')
        self.assertEqual(summary['material_type'], 'cotton')
        self.assertEqual(summary['material_buy_price'], 350.0)
        self.assertEqual(summary['supplier_name'], 'Test Supplier')
        self.assertIn('create_date', summary)
        self.assertIn('write_date', summary) 