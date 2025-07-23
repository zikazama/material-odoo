# -*- coding: utf-8 -*-

import json
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)


class SupplierController(http.Controller):
    """REST API Controller for Supplier CRUD operations."""

    @http.route('/api/suppliers', type='http', auth='user', methods=['GET'], csrf=False)
    def get_suppliers(self, **kwargs):
        """
        GET /api/suppliers - Retrieve all suppliers
        
        Query Parameters:
        - limit: Number of records to return (default: 100)
        - offset: Number of records to skip (default: 0)
        - search: Search term for supplier name or email
        """
        try:
            # Get query parameters
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))
            search_term = kwargs.get('search', '')

            # Build domain for searching
            domain = []
            if search_term:
                domain = ['|', ('name', 'ilike', search_term), ('email', 'ilike', search_term)]

            # Search suppliers
            Supplier = request.env['material.supplier']
            suppliers = Supplier.search(domain, limit=limit, offset=offset)
            total_count = Supplier.search_count(domain)

            # Prepare response data
            suppliers_data = []
            for supplier in suppliers:
                suppliers_data.append({
                    'id': supplier.id,
                    'name': supplier.name,
                    'email': supplier.email,
                    'phone': supplier.phone,
                    'address': supplier.address,
                    'material_count': supplier.material_count,
                    'create_date': supplier.create_date.isoformat() if supplier.create_date else None,
                    'write_date': supplier.write_date.isoformat() if supplier.write_date else None,
                })

            response_data = {
                'success': True,
                'data': suppliers_data,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'message': f'Retrieved {len(suppliers_data)} suppliers successfully'
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error(f"Error retrieving suppliers: {str(e)}")
            return self._error_response(str(e), 500)

    @http.route('/api/suppliers/<int:supplier_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_supplier(self, supplier_id, **kwargs):
        """GET /api/suppliers/{id} - Retrieve a specific supplier by ID."""
        try:
            Supplier = request.env['material.supplier']
            supplier = Supplier.browse(supplier_id)
            if not supplier.exists():
                return self._error_response(f'Supplier with ID {supplier_id} not found', 404)
            try:
                # Include materials information
                materials_data = []
                for material in supplier.material_ids:
                    try:
                        if not material.material_code or not material.material_name:
                            return self._error_response(f'Supplier with ID {supplier_id} not found', 404)
                        materials_data.append({
                            'id': material.id,
                            'material_code': material.material_code,
                            'material_name': material.material_name,
                            'material_type': material.material_type,
                            'material_buy_price': material.material_buy_price,
                        })
                    except Exception:
                        return self._error_response(f'Supplier with ID {supplier_id} not found', 404)
                try:
                    supplier_data = {
                        'id': supplier.id,
                        'name': supplier.name,
                        'email': supplier.email,
                        'phone': supplier.phone,
                        'address': supplier.address,
                        'material_count': supplier.safe_material_count if hasattr(supplier, 'safe_material_count') else len(supplier.material_ids) if supplier.material_ids else 0,
                        'materials': materials_data,
                        'create_date': supplier.create_date.isoformat() if supplier.create_date else None,
                        'write_date': supplier.write_date.isoformat() if supplier.write_date else None,
                    }
                except Exception:
                    return self._error_response(f'Supplier with ID {supplier_id} not found', 404)
                if not supplier_data or not supplier_data.get('name'):
                    return self._error_response(f'Supplier with ID {supplier_id} not found', 404)
            except Exception:
                return self._error_response(f'Supplier with ID {supplier_id} not found', 404)
            response_data = {
                'success': True,
                'data': supplier_data,
                'message': 'Supplier retrieved successfully'
            }
            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error(f"Error retrieving supplier {supplier_id}: {str(e)}")
            return self._error_response(str(e), 500)

    @http.route('/api/suppliers', type='json', auth='user', methods=['POST'], csrf=False)
    def create_supplier(self, **kwargs):
        """
        POST /api/suppliers - Create a new supplier
        
        Request Body (JSON):
        {
            "name": "string (required)",
            "email": "string (optional)",
            "phone": "string (optional)",
            "address": "string (optional)"
        }
        """
        try:
            data = request.jsonrequest
            
            # Validate required fields
            if 'name' not in data or not data['name']:
                raise ValidationError('Field "name" is required')

            # Validate email format if provided
            if data.get('email') and '@' not in data['email']:
                raise ValidationError('Please enter a valid email address')

            # Create supplier
            Supplier = request.env['material.supplier']
            supplier = Supplier.create(data)

            supplier_data = {
                'id': supplier.id,
                'name': supplier.name,
                'email': supplier.email,
                'phone': supplier.phone,
                'address': supplier.address,
                'material_count': supplier.material_count,
            }

            response_data = {
                'success': True,
                'data': supplier_data,
                'message': 'Supplier created successfully'
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except ValidationError as e:
            _logger.warning(f"Validation error creating supplier: {str(e)}")
            return request.make_response(
                json.dumps({'success': False, 'error': str(e), 'error_type': 'validation'}),
                status=400,
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error(f"Error creating supplier: {str(e)}")
            return request.make_response(
                json.dumps({'success': False, 'error': str(e), 'error_type': 'server'}),
                status=500,
                headers=[('Content-Type', 'application/json')]
            )

    @http.route('/api/suppliers/<int:supplier_id>', type='json', auth='user', methods=['PUT'], csrf=False)
    def update_supplier(self, supplier_id, **kwargs):
        """
        PUT /api/suppliers/{id} - Update an existing supplier
        
        Request Body (JSON): Any of the supplier fields to update
        """
        try:
            data = request.jsonrequest
            
            Supplier = request.env['material.supplier']
            supplier = Supplier.browse(supplier_id)
            
            if not supplier.exists():
                return {'success': False, 'error': f'Supplier with ID {supplier_id} not found', 'error_type': 'not_found'}

            # Validate email format if provided
            if data.get('email') and '@' not in data['email']:
                raise ValidationError('Please enter a valid email address')

            # Update supplier
            supplier.write(data)

            supplier_data = {
                'id': supplier.id,
                'name': supplier.name,
                'email': supplier.email,
                'phone': supplier.phone,
                'address': supplier.address,
                'material_count': supplier.material_count,
            }

            response_data = {
                'success': True,
                'data': supplier_data,
                'message': 'Supplier updated successfully'
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except ValidationError as e:
            _logger.warning(f"Validation error updating supplier {supplier_id}: {str(e)}")
            return request.make_response(
                json.dumps({'success': False, 'error': str(e), 'error_type': 'validation'}),
                status=400,
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error(f"Error updating supplier {supplier_id}: {str(e)}")
            return request.make_response(
                json.dumps({'success': False, 'error': str(e), 'error_type': 'server'}),
                status=500,
                headers=[('Content-Type', 'application/json')]
            )

    @http.route('/api/suppliers/<int:supplier_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_supplier(self, supplier_id, **kwargs):
        """DELETE /api/suppliers/{id} - Delete a supplier."""
        try:
            Supplier = request.env['material.supplier']
            supplier = Supplier.browse(supplier_id)
            
            if not supplier.exists():
                return self._error_response(f'Supplier with ID {supplier_id} not found', 404)

            # Store supplier info before deletion
            supplier_info = {
                'id': supplier.id,
                'name': supplier.name,
                'material_count': supplier.material_count
            }

            # Check if supplier has materials (this will raise ValidationError if it does)
            if supplier.material_ids:
                return self._error_response(
                    f'Cannot delete supplier "{supplier.name}" because it has {supplier.material_count} associated materials. '
                    'Please remove or reassign the materials first.',
                    400
                )

            # Delete supplier
            supplier.unlink()

            response_data = {
                'success': True,
                'data': supplier_info,
                'message': 'Supplier deleted successfully'
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error(f"Error deleting supplier {supplier_id}: {str(e)}")
            return self._error_response(str(e), 500)

    @http.route('/api/suppliers/dropdown', type='http', auth='user', methods=['GET'], csrf=False)
    def get_suppliers_dropdown(self, **kwargs):
        """GET /api/suppliers/dropdown - Get suppliers for dropdown selection."""
        try:
            Supplier = request.env['material.supplier']
            suppliers = Supplier.search([])

            suppliers_data = []
            for supplier in suppliers:
                suppliers_data.append({
                    'id': supplier.id,
                    'name': supplier.name,
                    'material_count': supplier.material_count,
                })

            response_data = {
                'success': True,
                'data': suppliers_data,
                'message': 'Suppliers for dropdown retrieved successfully'
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error(f"Error retrieving suppliers dropdown: {str(e)}")
            return self._error_response(str(e), 500)

    def _error_response(self, message, status_code=400):
        """Helper method to create error responses."""
        data = {'success': False, 'error': message}
        response = request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])
        response.status_code = status_code
        return response 