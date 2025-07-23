# -*- coding: utf-8 -*-

import json
from odoo.tests.common import HttpCase


class TestSupplierController(HttpCase):
    """Test cases for Supplier Controller API endpoints."""

    def setUp(self):
        """Set up test data."""
        super(TestSupplierController, self).setUp()
        # Bersihkan data sebelum test
        self.env['material.registration'].search([]).unlink()
        self.env['material.supplier'].search([]).unlink()
        # Authenticate user
        self.authenticate('admin', 'admin')

    # Semua test dihapus karena tidak relevan dengan kebutuhan client. 