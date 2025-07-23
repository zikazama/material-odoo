# -*- coding: utf-8 -*-

import json
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)


class MaterialController(http.Controller):
    """REST API Controller for Material CRUD operations."""

    @http.route('/api/materials', type='http', auth='user', methods=['GET'], csrf=False)
    def get_materials(self, **kwargs):
        """
        GET /api/materials - Retrieve all materials with optional filtering
        
        Query Parameters:
        - material_type: Filter by material type (fabric, jeans, cotton)
        - limit: Number of records to return (default: 100)
        - offset: Number of records to skip (default: 0)
        """
        try:
            # Get query parameters
            material_type = kwargs.get('material_type')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = []
            if material_type and material_type in ['fabric', 'jeans', 'cotton']:
                domain = [('material_type', '=', material_type)]

            # Search materials
            Material = request.env['material.registration']
            materials = Material.search(domain, limit=limit, offset=offset)
            total_count = Material.search_count(domain)

            # Prepare response data
            materials_data = []
            for material in materials:
                materials_data.append({
                    'id': material.id,
                    'material_code': material.material_code,
                    'material_name': material.material_name,
                    'material_type': material.material_type,
                    'material_buy_price': material.material_buy_price,
                    'supplier_id': material.supplier_id.id,
                    'supplier_name': material.supplier_name,
                    'price_category': material.price_category,
                    'create_date': material.create_date.isoformat() if material.create_date else None,
                    'write_date': material.write_date.isoformat() if material.write_date else None,
                })

            response_data = {
                'success': True,
                'data': materials_data,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'message': f'Retrieved {len(materials_data)} materials successfully'
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error(f"Error retrieving materials: {str(e)}")
            return self._error_response(str(e), 500)

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_material(self, material_id, **kwargs):
        """GET /api/materials/{id} - Retrieve a specific material by ID."""
        try:
            Material = request.env['material.registration']
            material = Material.browse(material_id)
            if not material.exists():
                return self._error_response(f'Material with ID {material_id} not found', 404)
            try:
                material_data = material.get_material_summary()
                # Cek field penting None atau error
                if not material_data or not material_data.get('material_code') or not material_data.get('material_name') or not material_data.get('supplier_name'):
                    return self._error_response(f'Material with ID {material_id} not found', 404)
            except Exception:
                return self._error_response(f'Material with ID {material_id} not found', 404)
            response_data = {
                'success': True,
                'data': material_data,
                'message': 'Material retrieved successfully'
            }
            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error(f"Error retrieving material {material_id}: {str(e)}")
            return self._error_response(str(e), 500)

    @http.route('/api/materials', type='json', auth='user', methods=['POST'], csrf=False)
    def create_material(self, **kwargs):
        """
        POST /api/materials - Create a new material
        
        Request Body (JSON):
        {
            "material_code": "string",
            "material_name": "string",
            "material_type": "fabric|jeans|cotton",
            "material_buy_price": float,
            "supplier_id": int
        }
        """
        try:
            data = request.jsonrequest
            
            # Validate required fields
            required_fields = ['material_code', 'material_name', 'material_type', 
                             'material_buy_price', 'supplier_id']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f'Field "{field}" is required')

            # Validate material_type
            if data['material_type'] not in ['fabric', 'jeans', 'cotton']:
                raise ValidationError('material_type must be one of: fabric, jeans, cotton')

            # Validate price
            if float(data['material_buy_price']) < 100:
                raise ValidationError('material_buy_price must be at least 100')

            # Validate supplier exists
            Supplier = request.env['material.supplier']
            supplier = Supplier.browse(data['supplier_id'])
            if not supplier.exists():
                raise ValidationError(f'Supplier with ID {data["supplier_id"]} not found')

            # Create material
            Material = request.env['material.registration']
            material = Material.create(data)

            response_data = {
                'success': True,
                'data': material.get_material_summary(),
                'message': 'Material created successfully'
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except ValidationError as e:
            _logger.warning(f"Validation error creating material: {str(e)}")
            return request.make_response(
                json.dumps({'success': False, 'error': str(e), 'error_type': 'validation'}),
                status=400,
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error(f"Error creating material: {str(e)}")
            return request.make_response(
                json.dumps({'success': False, 'error': str(e), 'error_type': 'server'}),
                status=500,
                headers=[('Content-Type', 'application/json')]
            )

    @http.route('/api/materials/<int:material_id>', type='json', auth='user', methods=['PUT'], csrf=False)
    def update_material(self, material_id, **kwargs):
        """
        PUT /api/materials/{id} - Update an existing material
        
        Request Body (JSON): Any of the material fields to update
        """
        try:
            data = request.jsonrequest
            
            Material = request.env['material.registration']
            material = Material.browse(material_id)
            
            if not material.exists():
                return {'success': False, 'error': f'Material with ID {material_id} not found', 'error_type': 'not_found'}

            # Validate material_type if provided
            if 'material_type' in data and data['material_type'] not in ['fabric', 'jeans', 'cotton']:
                raise ValidationError('material_type must be one of: fabric, jeans, cotton')

            # Validate price if provided
            if 'material_buy_price' in data and float(data['material_buy_price']) < 100:
                raise ValidationError('material_buy_price must be at least 100')

            # Validate supplier if provided
            if 'supplier_id' in data:
                Supplier = request.env['material.supplier']
                supplier = Supplier.browse(data['supplier_id'])
                if not supplier.exists():
                    raise ValidationError(f'Supplier with ID {data["supplier_id"]} not found')

            # Update material
            material.write(data)

            response_data = {
                'success': True,
                'data': material.get_material_summary(),
                'message': 'Material updated successfully'
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except ValidationError as e:
            _logger.warning(f"Validation error updating material {material_id}: {str(e)}")
            return request.make_response(
                json.dumps({'success': False, 'error': str(e), 'error_type': 'validation'}),
                status=400,
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error(f"Error updating material {material_id}: {str(e)}")
            return request.make_response(
                json.dumps({'success': False, 'error': str(e), 'error_type': 'server'}),
                status=500,
                headers=[('Content-Type', 'application/json')]
            )

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_material(self, material_id, **kwargs):
        """DELETE /api/materials/{id} - Delete a material."""
        try:
            Material = request.env['material.registration']
            material = Material.browse(material_id)
            
            if not material.exists():
                return self._error_response(f'Material with ID {material_id} not found', 404)

            # Store material info before deletion
            material_info = {
                'id': material.id,
                'material_code': material.material_code,
                'material_name': material.material_name
            }

            # Delete material
            material.unlink()

            response_data = {
                'success': True,
                'data': material_info,
                'message': 'Material deleted successfully'
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error(f"Error deleting material {material_id}: {str(e)}")
            return self._error_response(str(e), 500)

    @http.route('/api/materials/types', type='http', auth='user', methods=['GET'], csrf=False)
    def get_material_types(self, **kwargs):
        """GET /api/materials/types - Get available material types."""
        try:
            material_types = [
                {'value': 'fabric', 'label': 'Fabric'},
                {'value': 'jeans', 'label': 'Jeans'},
                {'value': 'cotton', 'label': 'Cotton'},
            ]

            response_data = {
                'success': True,
                'data': material_types,
                'message': 'Material types retrieved successfully'
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error(f"Error retrieving material types: {str(e)}")
            return self._error_response(str(e), 500)

    def _error_response(self, message, status_code=400):
        data = {'success': False, 'error': message}
        response = request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])
        response.status_code = status_code
        return response 