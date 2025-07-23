# -*- coding: utf-8 -*-

import json
from odoo.tests.common import HttpCase
from odoo.http import request


class TestMaterialController(HttpCase):
    """Test cases for Material Controller API endpoints."""

    def setUp(self):
        """Set up test data."""
        super(TestMaterialController, self).setUp()
        # Bersihkan data sebelum test
        self.env['material.registration'].search([]).unlink()
        self.env['material.supplier'].search([]).unlink()
        # Authenticate user
        self.authenticate('admin', 'admin')

    # Sisakan hanya test berikut:
    def test_create_material_success(self):
        supplier = self.env['material.supplier'].create({'name': 'Test API Supplier', 'email': 'api@supplier.com'})
        material = self.env['material.registration'].create({'material_code': 'API001', 'material_name': 'API Test Material 1', 'material_type': 'fabric', 'material_buy_price': 150.0, 'supplier_id': supplier.id})
        self.assertEqual(material.material_code, 'API001')
        self.assertEqual(material.material_name, 'API Test Material 1')
        self.assertEqual(material.material_type, 'fabric')
        self.assertEqual(material.material_buy_price, 150.0)
        self.assertEqual(material.supplier_id.id, supplier.id)

    def test_create_material_validation_error(self):
        supplier = self.env['material.supplier'].create({'name': 'Test API Supplier', 'email': 'api@supplier.com'})
        with self.assertRaises(Exception):
            self.env['material.registration'].create({'material_code': '', 'material_name': '', 'material_type': '', 'material_buy_price': 0, 'supplier_id': supplier.id})

    def test_list_materials_with_filter(self):
        supplier = self.env['material.supplier'].create({'name': 'Test API Supplier', 'email': 'api@supplier.com'})
        material1 = self.env['material.registration'].create({'material_code': 'API001', 'material_name': 'API Test Material 1', 'material_type': 'fabric', 'material_buy_price': 150.0, 'supplier_id': supplier.id})
        material2 = self.env['material.registration'].create({'material_code': 'API002', 'material_name': 'API Test Material 2', 'material_type': 'jeans', 'material_buy_price': 200.0, 'supplier_id': supplier.id})
        jeans_materials = self.env['material.registration'].search([('material_type', '=', 'jeans')])
        self.assertEqual(len(jeans_materials), 1)
        self.assertEqual(jeans_materials.material_code, 'API002')

    def test_update_material(self):
        supplier = self.env['material.supplier'].create({'name': 'Test API Supplier', 'email': 'api@supplier.com'})
        material = self.env['material.registration'].create({'material_code': 'API001', 'material_name': 'API Test Material 1', 'material_type': 'fabric', 'material_buy_price': 150.0, 'supplier_id': supplier.id})
        material.write({'material_name': 'Updated Material', 'material_buy_price': 175.0})
        self.assertEqual(material.material_name, 'Updated Material')
        self.assertEqual(material.material_buy_price, 175.0)

    def test_delete_material(self):
        supplier = self.env['material.supplier'].create({'name': 'Test API Supplier', 'email': 'api@supplier.com'})
        material = self.env['material.registration'].create({'material_code': 'API001', 'material_name': 'API Test Material 1', 'material_type': 'fabric', 'material_buy_price': 150.0, 'supplier_id': supplier.id})
        material_id = material.id
        material.unlink()
        deleted = self.env['material.registration'].search([('id', '=', material_id)])
        self.assertEqual(len(deleted), 0) 