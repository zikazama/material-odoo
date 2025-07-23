{
    'name': 'Material Registration',
    'version': '14.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Material Registration and Management System',
    'description': """
        This module provides functionality for material registration and management.
        
        Features:
        - Material registration with validation
        - Supplier management
        - REST API for CRUD operations
        - Material filtering by type
        - Price validation (minimum 100)
        
        Requirements:
        - Material Code (unique)
        - Material Name
        - Material Type (Fabric, Jeans, Cotton)
        - Material Buy Price (>= 100)
        - Related Supplier
    """,
    'author': 'Backend Developer',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/material_data.xml',
        'views/supplier_views.xml',
        'views/material_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
} 