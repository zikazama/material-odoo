Backend Odoo Test

Kebutuhan client adalah membuat sebuah modul Odoo 14 yang didalamnya berfungsi
untuk melakukan registrasi material yang akan dijual. Informasi yang harus dibutuhkan
client adalah:
1. Material Code
2. Material Name
3. Material Type (dropdown 3 pilihan: Fabric, Jeans, Cotton)
4. Material Buy Price
5. Related Supplier (dropdown : Nama supplier)
Seluruh informasi tersebut harus terisi, dan untuk material buy price tidak boleh nilainya
< 100.

Selain itu client juga harus dapat:
1. Melihat seluruh materials yang telah dibuat, Client juga harus dapat memfilter
berdasarkan Material Type
2. Melakukan update terhadap satu material
3. Melakukan delete terhadap satu material
Tugas Anda, sebagai Backend adalah:
1. Membuat ERD dari kebutuhan Client tersebut
2. Membuat Models
3. Membuat Controllers (Membuat REST API untuk requirement diatas
menggunakan Controllers)
4. Membuat Unit testing