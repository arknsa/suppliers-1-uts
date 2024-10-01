## Alur Kerja Modul Supplier 1 (Ban)

1.⁠ ⁠Informasi Supplier
Supplier membuat profile supplier mengenai produk yang diperjualbelikan

2.⁠ ⁠Informasi Daftar Produk
Supplier membuat daftar produk yang tersedia untuk dibeli retailer. Informasi ini mencakup nama produk,  ketersediaan stok, gambar produk, dan lainnya. Selain itu ¬¬supplier juga memiliki fitur untuk mengupdate informasi produk seperti menambahkan, mengedit, menghapus, dan melihat.

3.⁠ ⁠Pembelian oleh Retail 
Supplier menerima data pembelian dari retail untuk mengecek harga dan lama pengiriman. 

4.⁠ ⁠Informasi Pengiriman ke Distributor
Setelah mendapatkan data pembelian dari retail, supplier mengirimkan data pengiriman ke distributor untuk diperhitungkan ongkos kirim.  Data yang dikirim mencakup kota_asal, kota_tujuan, berat, dan id_log sebagai identitas pesanan

5.⁠ ⁠Informasi Ongkos Kirim dari Distributor
Supplier mendapatkan informasi harga_pengiriman dan lama_pengiriman dari distributor

6.⁠ ⁠Konfirmasi Pembelian dari Retail
Jika retail sudah terkonfirmasi membeli produk supplier, maka supplier akan mengirimkan id_transaksi untuk diproses pengiriman serta pembuatan nomor resi

7.⁠ ⁠Informasi Status Pengiriman
Setelah mendapatkan nomor resi yang dikirim oleh distributor, supplier dan retail dan memeriksa status pengiriman 

8.⁠ ⁠Update Ketersediaan Stok
Supplier dapat mengatur ketersediaan produk berdasarkan statur pembelian yang sedang dikirim melalui status pengiriman.

Dokumentasi API Modul Supplier 1 (Ban)
Dokumentasi mengenai penggunakan endpoint dapat diakses melalui link berikut : 
https://app.swaggerhub.com/apis-docs/SriRanita/dokumentasi-api_modul_supplier_ban/1.0.0﻿# UTS-SUPPLIER1

### Step by step: <br>
1. akses web suppliers 1 di: http://167.99.238.114:8000/
2. login menggunakan akun admin, username: admin_supplier, password: duar123
3. adapun beberapa API yang kami gunakan yaitu:
a. GET /api/suppliers
Return : 
{
    "id": "SUP01",
    "alamat": "Jakarta",
    "nama": "Supplier Ban",
     “contact” : “81234567”
}

b. GET /api/products
Return : 
{
        "berat": 0.61,
        "deskripsi ": "Genio Ban Luar 20 x 1.75 157 berukuran 20 yang cocok menggantikan ban luar sepeda dengan ukuran 20 x 1.75. Fitur: ukuran 20 inci, bahan rubber, jenis ban wire, traction yang baik.",
        "genre": "Road bike",
        "harga": 60000,
        "height": 20,
        "id_produk": "111",
        "kategori": "Ban Luar",
        "link_gambar_barang": "https://icubic-space.sgp1.digitaloceanspaces.com/app/public/ss/lib/pro/img/2024/09/genio-ban-luar-20-x-175-157-1-1726038482.jpg",
        "nama_produk": "Genio Ban Luar 20 x 1.75 157",
        "stock": 71,
        "stock_maximum": 150,
        "stock_minimun": 10,
        "warna ": "hitam",
        "width": 1.75
    }

c. POST /api/check_price
input: 
{
    "cart":[
        {
            "id_produk" : "PROD002",
            "quantity" : 7
        },
        {
            "id_produk" : "PROD001",
            "quantity" : 5
        }
    ],
    "id_retail" : "RET02",
    "id_distributor" : "DIS02",
    "total_harga_barang" : 50000,
    "total_berat_barang" : 70,
    "kota_tujuan" : "ngawi"
}

output:
{
    "harga_pengiriman": 121000.0,
    "id_log": "SUP01RET03DIS0196",
    "lama_pengiriman": "2 hari",
    "message": "Pemeriksaan harga berhasil"
}

