# Material Registration Module

An Odoo 14 module for material registration and supplier management system with REST API support.

## Features

### Material Management
- Material registration with unique code validation
- Material types: Fabric, Jeans, Cotton
- Minimum price validation (>= 100)
- Automatic price categorization (Low/Medium/High)
- Material name search functionality
- Supplier relationship tracking

### Supplier Management
- Supplier registration with unique name validation
- Email format validation
- Material count tracking per supplier
- Prevent deletion of suppliers with associated materials
- Supplier search by name or email

### REST API Endpoints
- **Materials**
  - `GET /api/materials` - List all materials with optional type filtering
  - `GET /api/materials/<id>` - Get material details
  - `POST /api/materials` - Create new material
  - `PUT /api/materials/<id>` - Update material
  - `DELETE /api/materials/<id>` - Delete material
  
- **Suppliers**
  - `GET /api/suppliers` - List all suppliers
  - `GET /api/suppliers/<id>` - Get supplier details
  - `POST /api/suppliers` - Create new supplier
  - `PUT /api/suppliers/<id>` - Update supplier
  - `DELETE /api/suppliers/<id>` - Delete supplier

## Requirements
- Docker and Docker Compose
- Odoo 14.0
- PostgreSQL 13

## Installation & Setup

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd material-odoo
```

2. Start the containers:
```bash
docker-compose up -d
```

3. Access Odoo at http://localhost:8069
   - Default credentials: admin/admin
   - The module will be automatically installed

### Manual Installation

1. Copy this module to your Odoo addons directory
2. Update the module list in Odoo
3. Install "Material Registration" module from Apps menu

## Running Tests

To run the complete test suite:

```bash
docker exec material-odoo-web-1 odoo --test-enable --stop-after-init -u material_registration -d postgres --db_host db --db_user odoo --db_password odoo
```

### Test Coverage
- **27 unit tests** covering:
  - Material model validation and constraints
  - Supplier model validation and constraints
  - REST API controllers for CRUD operations
  - Business logic and computed fields

## Module Structure

```
material-odoo/
├── __manifest__.py          # Module manifest
├── __init__.py             # Module initialization
├── controllers/            # REST API controllers
│   ├── material_controller.py
│   └── supplier_controller.py
├── models/                 # Business models
│   ├── material.py
│   └── supplier.py
├── views/                  # UI views
│   ├── material_views.xml
│   ├── supplier_views.xml
│   └── menu_views.xml
├── security/              # Access rights
│   └── ir.model.access.csv
├── data/                  # Demo data
│   └── material_data.xml
├── tests/                 # Unit tests
│   ├── test_material_model.py
│   ├── test_material_controller.py
│   ├── test_supplier_model.py
│   └── test_supplier_controller.py
└── docker-compose.yml     # Docker configuration
```

## API Usage Examples

### Create Material
```bash
curl -X POST http://localhost:8069/api/materials \
  -H "Content-Type: application/json" \
  -d '{
    "material_code": "FAB001",
    "material_name": "Premium Cotton",
    "material_type": "cotton",
    "material_buy_price": 250.0,
    "supplier_id": 1
  }'
```

### Get Materials by Type
```bash
curl http://localhost:8069/api/materials?type=fabric
```

### Create Supplier
```bash
curl -X POST http://localhost:8069/api/suppliers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ABC Textiles",
    "email": "contact@abctextiles.com",
    "phone": "+1234567890",
    "address": "123 Textile Street"
  }'
```

## Development

### Running in Development Mode
The docker-compose configuration includes `--dev=all` flag for auto-reload during development.

### Code Quality
- All models include proper validation and constraints
- Comprehensive test coverage ensures reliability
- REST API follows RESTful conventions

## License
LGPL-3
