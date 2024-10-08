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
[UTS-SUPPLIER1](https://app.swaggerhub.com/apis-docs/SriRanita/dokumentasi-api_modul_supplier_ban/1.0.0)

### Step by Step Pengunaan Web Suppliers 1: <br>

1. Akses web suppliers 1 di: http://167.99.238.114:8000/
2. Login menggunakan akun admin, berikut informasinya: <br> username: admin_supplier <br> password: duar123 <br>
3. Adapun databse yang kami gunakan terdiri dari table berikut:
<br> a. db_produk (id_produk, nama_produk, kategori, stok, stok_min, stok_max, harga, berat, height, width, genre, warna, deskripsi, gambar, aksi)
<br> b. db_transaksi (id_distributor, id_log, id_retail, kota_tujuan, harga_pengiriman, lama_pengiriman, total_berat_barang, total_harga_barang)
<br> c. db_pembelian (id_log, harga_pengiriman, lama_pengiriman, no_resi, tanggal_pembelian, total_berat_barang, total_harga_barang
<br> d. db_user (username, password)
<br> e. db_order (id_log, id_produk, quantity)
<br> f. db_supplier (nama, alamat, kontak)

5. Adapun beberapa API yang kami gunakan yaitu:
<br> a. GET /api/suppliers
<br> Return : 
{
    "id": "SUP01",
    "alamat": "Jakarta",
    "nama": "Supplier Ban",
     “contact” : “81234567”
} <br>
<br> b. GET /api/products <br> Return : 
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
    } <br>
<br> c. POST /api/check_price
<br> input: 
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
<br> output:
{
    "harga_pengiriman": 121000.0,
    "id_log": "SUP01RET03DIS0196",
    "lama_pengiriman": "2 hari",
    "message": "Pemeriksaan harga berhasil"
} <br>
<br> d. POST /api/place_order
<br> input:
{
    "id_log": "SUP01RET03DIS0196"
}
<br> output:
{
    "harga_pengiriman": 121000.0,
    "lama_pengiriman": "2 hari",
    "message": "Pemesanan berhasil dilakukan",
    "no_resi": "LESS02R01PK001",
    "purchase_id": "SUP01RET03DIS0196"
}

### Project ini dibuat oleh:
1. Abdullah Muhammad Idris - 162012133064
2. Sri Ranita - 162112133003
3. Rafli Maulana Firmansyah - 162112133064
4. Nafisahika Putri Herra - 164221039
5. Arkan Syafiq At'taqy - 164221062
6. Ananda Alvin Bernerdian Hartono - 164221096
