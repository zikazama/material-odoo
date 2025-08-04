# Material Registration - Panduan Pembelajaran Kode

## Deskripsi Proyek
Material Registration adalah modul Odoo untuk manajemen registrasi material dan supplier. Modul ini menyediakan sistem CRUD lengkap dengan REST API untuk mengelola material dan supplier dalam lingkungan bisnis.

## Struktur Proyek

```
material-odoo/
├── __manifest__.py          # Konfigurasi modul Odoo
├── models/                  # Model data (ORM)
│   ├── material.py         # Model untuk material
│   └── supplier.py         # Model untuk supplier
├── controllers/            # Controller untuk REST API
│   ├── material_controller.py    # API endpoint untuk material  
│   └── supplier_controller.py    # API endpoint untuk supplier
├── views/                  # Interface pengguna (XML)
│   ├── material_views.xml # Tampilan untuk material
│   ├── supplier_views.xml # Tampilan untuk supplier
│   └── menu_views.xml     # Menu navigasi
├── security/               # Hak akses
│   └── ir.model.access.csv
├── data/                   # Data default
│   └── material_data.xml
├── demo/                   # Data demo
│   └── demo_data.xml
└── tests/                  # Unit tests
    ├── test_material_controller.py
    ├── test_material_model.py
    ├── test_supplier_controller.py
    └── test_supplier_model.py
```

## Penjelasan Kode Detail

### 1. Manifest File (`__manifest__.py`)

```python
{
    'name': 'Material Registration',
    'version': '14.0.1.0.0',
    'category': 'Inventory',
    'depends': ['base', 'web'],
    # ... konfigurasi lainnya
}
```

**Fungsi:**
- Mendefinisikan metadata modul Odoo
- Menentukan dependensi (`base`, `web`)
- Mengatur file-file yang akan dimuat (data, views, demo)
- Konfigurasi instalasi dan lisensi

### 2. Model Material (`models/material.py`)

#### Class Definition
```python
class Material(models.Model):
    _name = 'material.registration'
    _description = 'Material Registration'
    _order = 'material_code'
    _rec_name = 'material_name'
```

**Fungsi:**
- `_name`: Nama teknis model dalam database
- `_description`: Deskripsi model
- `_order`: Field default untuk pengurutan
- `_rec_name`: Field yang digunakan sebagai display name

#### Field Definitions
```python
material_code = fields.Char(
    string='Material Code',
    required=True,
    index=True,
    help='Unique code for the material'
)
```

**Fields yang ada:**
- `material_code`: Kode unik material (Char, required, indexed)
- `material_name`: Nama material (Char, required)
- `material_type`: Jenis material (Selection: fabric/jeans/cotton)
- `material_buy_price`: Harga beli (Float, minimal 100)
- `supplier_id`: Relasi ke supplier (Many2one)
- `supplier_name`: Nama supplier (related field, readonly)
- `price_category`: Kategori harga (computed field)

#### Computed Field
```python
@api.depends('material_buy_price')
def _compute_price_category(self):
    for material in self:
        if material.material_buy_price < 100:
            material.price_category = 'Invalid (< 100)'
        elif material.material_buy_price < 500:
            material.price_category = 'Budget (100-499)'
        # ... dst
```

**Fungsi:**
- Menghitung kategori harga berdasarkan `material_buy_price`
- Menggunakan decorator `@api.depends` untuk auto-update
- Kategorisasi: Invalid, Budget, Standard, Premium

#### Validation Constraints
```python
@api.constrains('material_code')
def _check_unique_material_code(self):
    for material in self:
        existing = self.search([
            ('material_code', '=', material.material_code),
            ('id', '!=', material.id)
        ])
        if existing:
            raise ValidationError('Material code must be unique')
```

**Validasi yang ada:**
1. **Unique Material Code**: Memastikan kode material unik
2. **Minimum Price**: Harga minimal 100
3. **Material Name**: Nama tidak boleh kosong

#### Override Methods
```python
def name_get(self):
    result = []
    for material in self:
        name = '[%s] %s' % (material.material_code, material.material_name)
        result.append((material.id, name))
    return result
```

**Methods yang di-override:**
- `name_get()`: Menampilkan format "[KODE] Nama"
- `name_search()`: Pencarian berdasarkan kode dan nama
- `create()`: Validasi tambahan saat create
- `write()`: Validasi tambahan saat update

### 3. Model Supplier (`models/supplier.py`)

#### Field Structure
```python
name = fields.Char(string='Supplier Name', required=True, index=True)
email = fields.Char(string='Email')
phone = fields.Char(string='Phone')
address = fields.Text(string='Address')
material_ids = fields.One2many('material.registration', 'supplier_id', string='Materials')
material_count = fields.Integer(compute='_compute_material_count', store=True)
```

**Relasi:**
- `material_ids`: One2many relationship ke material
- `material_count`: Computed field untuk jumlah material

#### Constraints
```python
@api.constrains('name')
def _check_unique_name(self):
    # Validasi nama supplier unik
    
@api.constrains('email')
def _check_email_format(self):
    # Validasi format email
```

**Validasi:**
- Nama supplier harus unik
- Format email harus valid (mengandung @)

#### Delete Protection
```python
def unlink(self):
    for supplier in self:
        if supplier.material_ids:
            raise ValidationError('Cannot delete supplier with associated materials')
    return super(Supplier, self).unlink()
```

**Fungsi:** Mencegah penghapusan supplier yang masih memiliki material

### 4. Material Controller (`controllers/material_controller.py`)

#### GET Materials
```python
@http.route('/api/materials', type='http', auth='user', methods=['GET'], csrf=False)
def get_materials(self, **kwargs):
    # Filtering berdasarkan material_type
    # Pagination dengan limit dan offset
    # Return JSON response
```

**Endpoint:** `GET /api/materials`
**Parameter:**
- `material_type`: Filter berdasarkan jenis (fabric/jeans/cotton)
- `limit`: Jumlah record (default: 100)
- `offset`: Skip record (default: 0)

#### GET Single Material
```python
@http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['GET'], csrf=False)
def get_material(self, material_id, **kwargs):
    material = Material.browse(material_id)
    if not material.exists():
        return self._error_response('Material not found', 404)
```

**Endpoint:** `GET /api/materials/{id}`
**Fungsi:** Mengambil data material berdasarkan ID

#### POST Create Material
```python
@http.route('/api/materials', type='json', auth='user', methods=['POST'], csrf=False)
def create_material(self, **kwargs):
    data = request.jsonrequest
    # Validasi required fields
    # Validasi material_type
    # Validasi price >= 100
    # Validasi supplier exists
    material = Material.create(data)
```

**Endpoint:** `POST /api/materials`
**Body JSON:**
```json
{
    "material_code": "string",
    "material_name": "string", 
    "material_type": "fabric|jeans|cotton",
    "material_buy_price": float,
    "supplier_id": int
}
```

#### PUT Update Material
```python
@http.route('/api/materials/<int:material_id>', type='json', auth='user', methods=['PUT'], csrf=False)
def update_material(self, material_id, **kwargs):
    # Validasi material exists
    # Validasi data yang diupdate
    # Update menggunakan write()
```

**Endpoint:** `PUT /api/materials/{id}`
**Fungsi:** Update material berdasarkan ID

#### DELETE Material
```python
@http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
def delete_material(self, material_id, **kwargs):
    # Validasi material exists
    # Simpan info sebelum delete
    # Delete menggunakan unlink()
```

**Endpoint:** `DELETE /api/materials/{id}`
**Fungsi:** Hapus material berdasarkan ID

#### Utility Methods
```python
def _error_response(self, message, status_code=400):
    data = {'success': False, 'error': message}
    response = request.make_response(json.dumps(data))
    response.status_code = status_code
    return response
```

**Fungsi:** Helper method untuk response error standar

### 5. Supplier Controller (`controllers/supplier_controller.py`)

#### Structure Sama dengan Material Controller
**Endpoints:**
- `GET /api/suppliers` - List semua supplier
- `GET /api/suppliers/{id}` - Detail supplier
- `POST /api/suppliers` - Create supplier baru
- `PUT /api/suppliers/{id}` - Update supplier
- `DELETE /api/suppliers/{id}` - Delete supplier
- `GET /api/suppliers/dropdown` - Supplier untuk dropdown

#### Special Features
```python
# Include materials information
materials_data = []
for material in supplier.material_ids:
    materials_data.append({
        'id': material.id,
        'material_code': material.material_code,
        # ... data lainnya
    })
```

**Fungsi:** Saat GET detail supplier, ikut sertakan daftar material yang dipasok

### 6. Views XML

#### Material Views (`views/material_views.xml`)

**Tree View:**
```xml
<record id="view_material_tree" model="ir.ui.view">
    <field name="arch" type="xml">
        <tree>
            <field name="material_code"/>
            <field name="material_name"/>
            <field name="material_type"/>
            <field name="material_buy_price"/>
            <field name="supplier_name"/>
            <field name="price_category"/>
        </tree>
    </field>
</record>
```

**Fungsi:** Tampilan daftar material dalam bentuk tabel

**Form View:**
```xml
<form>
    <sheet>
        <group>
            <group>
                <field name="material_code" required="1"/>
                <field name="material_name" required="1"/>
                <field name="material_type" required="1"/>
            </group>
            <group>
                <field name="material_buy_price" required="1"/>
                <field name="supplier_id" required="1"/>
                <field name="price_category" readonly="1"/>
            </group>
        </group>
    </sheet>
</form>
```

**Fungsi:** Form input/edit material dengan validasi required

**Search View:**
```xml
<search>
    <field name="material_code"/>
    <field name="material_name"/>
    <filter string="Fabric" domain="[('material_type', '=', 'fabric')]"/>
    <filter string="Budget" domain="[('material_buy_price', '>=', 100), ('material_buy_price', '&lt;', 500)]"/>
    <group string="Group By">
        <filter string="Material Type" context="{'group_by': 'material_type'}"/>
    </group>
</search>
```

**Fungsi:** 
- Search box untuk material_code dan material_name
- Filter berdasarkan material_type dan price range
- Group by material_type, supplier, price_category

**Kanban View:**
```xml
<kanban>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <strong><field name="material_code"/></strong>
                <field name="material_name"/>
                <!-- Informasi lainnya -->
            </div>
        </t>
    </templates>
</kanban>
```

**Fungsi:** Tampilan kartu untuk material dengan informasi ringkas

### 7. Security (`security/ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_material_supplier,material.supplier,model_material_supplier,base.group_user,1,1,1,1
access_material_registration,material.registration,model_material_registration,base.group_user,1,1,1,1
```

**Fungsi:**
- Memberikan hak akses CRUD (Create, Read, Update, Delete) 
- Untuk group `base.group_user` (user biasa)
- Berlaku untuk model `material.supplier` dan `material.registration`

## Alur Kerja Aplikasi

### 1. Registrasi Supplier
1. User membuka menu Suppliers
2. Klik "Create" untuk supplier baru
3. Input: nama (required), email, phone, address
4. Validasi: nama unik, email format valid
5. Save ke database

### 2. Registrasi Material
1. User membuka menu Materials
2. Klik "Create" untuk material baru
3. Input semua field required:
   - Material Code (harus unik)
   - Material Name
   - Material Type (pilih dari dropdown)
   - Material Buy Price (minimal 100)
   - Supplier (pilih dari dropdown supplier yang ada)
4. Sistem auto-compute price_category
5. Validasi semua constraints
6. Save ke database

### 3. REST API Usage
```bash
# Get all materials
GET /api/materials

# Get materials by type
GET /api/materials?material_type=fabric

# Get single material
GET /api/materials/1

# Create material
POST /api/materials
Content-Type: application/json
{
  "material_code": "FAB001",
  "material_name": "Cotton Fabric", 
  "material_type": "fabric",
  "material_buy_price": 150.00,
  "supplier_id": 1
}

# Update material
PUT /api/materials/1
{
  "material_buy_price": 200.00
}

# Delete material
DELETE /api/materials/1
```

## Fitur Utama

### 1. Data Validation
- Material code harus unik
- Material buy price minimal 100
- Supplier name harus unik
- Email format validation
- Required field validation

### 2. Computed Fields
- `price_category`: Otomatis berdasarkan harga
- `supplier_name`: Related field dari supplier
- `material_count`: Jumlah material per supplier

### 3. Relationship Management
- One2many: Supplier → Materials
- Many2one: Material → Supplier
- Cascade delete protection

### 4. Search & Filter
- Search by material code/name
- Filter by material type
- Filter by price range
- Group by various fields

### 5. Multiple View Types
- Tree view (daftar)
- Form view (input/edit)
- Kanban view (kartu)
- Search view (filter/group)

### 6. REST API
- Full CRUD operations
- JSON request/response
- Error handling dengan status codes
- Pagination support
- Authentication required

## Error Handling

### Model Level
```python
@api.constrains('material_buy_price')
def _check_minimum_price(self):
    if material.material_buy_price < 100:
        raise ValidationError('Price must be at least 100')
```

### Controller Level
```python
try:
    # Processing
except ValidationError as e:
    return request.make_response(
        json.dumps({'success': False, 'error': str(e)}),
        status=400
    )
except Exception as e:
    return request.make_response(
        json.dumps({'success': False, 'error': str(e)}),
        status=500
    )
```

## Best Practices yang Diterapkan

1. **Separation of Concerns**: Model untuk business logic, Controller untuk API
2. **Data Validation**: Multiple level validation (model constraints + controller validation)
3. **Error Handling**: Consistent error response format
4. **Documentation**: Docstring untuk setiap method
5. **Security**: Authentication required untuk semua endpoint
6. **Relationship Integrity**: Foreign key constraints dan delete protection
7. **User Experience**: Multiple view types, search, filter, pagination
8. **Code Organization**: Modular structure dengan folder terpisah

Sistem ini mendemonstrasikan implementasi lengkap modul Odoo dengan integrasi REST API yang robust dan user-friendly interface.