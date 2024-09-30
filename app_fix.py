from flask import Flask, request, jsonify
import requests
import os
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)


# Inisialisasi Firebase Admin SDK
cred = credentials.Certificate("uts-iak-firebase-adminsdk-q4jev-fb337bb7ab.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


@app.route('/check_price', methods=['POST'])
def check_price():
    data = request.json

    try:
        # Cek jumlah transaksi untuk id_log format
        transaksi_ref = db.collection('db_transaksi')
        transaksi_docs = transaksi_ref.stream()
        cek_harga_ke = sum(1 for _ in transaksi_docs) + 1  # Hitung berapa kali cek harga dilakukan sebelumnya

        # Generate id_log dengan format "SUP01RET03DIS01"
        id_log = f"SUP01RET03DIS01{cek_harga_ke:0d}"  # 000 di bagian akhir menandakan cek harga ke berapa

        # Simpan data transaksi ke db_transaksi
        new_transaction = {
            "id_log": id_log,  # Menggunakan id_log yang di-generate
            "id_retail": data["id_retail"],  
            "id_distributor": data['id_distributor'],
            "kota_tujuan": data['kota_tujuan'],
            "total_berat_barang": data['total_berat_barang'],
            "total_harga_barang": data['total_harga_barang'],
        }

        # Simpan transaksi ke koleksi db_transaksi
        transaksi_ref.document(id_log).set(new_transaction)

        # Simpan setiap produk dari cart ke db_order
        order_ref = db.collection('db_order')
        for item in data['cart']:
            order_data = {
                "id_log": id_log,  # Menggunakan id_log yang sama
                "id_produk": item['id_produk'],
                "quantity": item['quantity']
            }
            # Simpan data order ke db_order
            order_ref.add(order_data)

        # Tentukan URL API berdasarkan id_distributor
        distributor_id = data['id_distributor']
        if distributor_id == "DIS01":
            api_url = "http://159.223.41.243:8000/api/distributors6/orders/cek_ongkir"
        elif distributor_id == "DIS02":
            api_url = "http://159.223.41.243:8000/api/distributors2/orders/cek_ongkir"
        elif distributor_id == "DIS03":
            api_url = "http://159.223.41.243:8000/api/distributors3/orders/cek_ongkir"
        else:
            return jsonify({"error": "ID distributor tidak valid"}), 400

        # Cek ongkir dari distributor
        ongkir_response = requests.post(api_url, json={
            "id_log": id_log,  # Menggunakan id_log yang baru di-generate
            "kota_asal": "jakarta",  # Auto isi dengan "jakarta"
            "kota_tujuan": data['kota_tujuan'],
            "berat": data["total_berat_barang"]  # Menghitung total berat dari semua item di cart
        })

        if ongkir_response.status_code != 200:
            return jsonify({"error": "Gagal mendapatkan ongkir dari distributor"}), 400

        # Pastikan respons JSON valid
        ongkir_data = ongkir_response.json()

        # Update data transaksi dengan harga pengiriman dan lama pengiriman
        new_transaction.update({
            "harga_pengiriman": ongkir_data['harga_pengiriman'],  # Mengambil harga_pengiriman dari respons
            "lama_pengiriman": ongkir_data.get('lama_pengiriman')  # Mengambil lama_pengiriman jika ada
        })

        # Simpan transaksi ke db_transaksi dengan id_log yang dihasilkan
        transaksi_ref.document(id_log).set(new_transaction)

        return jsonify({
            "message": "Pemeriksaan harga berhasil",
            "id_log": id_log,  # Menggunakan id_log yang baru di-generate
            "harga_pengiriman": ongkir_data['harga_pengiriman'],
            "lama_pengiriman": ongkir_data.get('lama_pengiriman')
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json

    try:
        # Ambil data dari koleksi db_transaksi berdasarkan id_log
        transaction_ref = db.collection('db_transaksi').document(data['id_log'])
        transaction_doc = transaction_ref.get()

        if not transaction_doc.exists:
            return jsonify({"error": "Transaksi tidak ditemukan"}), 404

        transaction_data = transaction_doc.to_dict()

        # Ambil id_distributor dari data transaksi
        distributor_id = transaction_data.get('id_distributor')

        # Tentukan URL API berdasarkan id_distributor
        if distributor_id == "DIS01":
            api_url = "http://159.223.41.243:8000/api/distributors6/orders/fix_kirim"
        elif distributor_id == "DIS02":
            api_url = "http://159.223.41.243:8000/api/distributors2/orders/fix_kirim"
        elif distributor_id == "DIS03":
            api_url = "http://159.223.41.243:8000/api/distributors3/orders/fix_kirim"
        else:
            return jsonify({"error": "ID distributor tidak valid"}), 400

        # Melakukan pemesanan ke distributor yang sesuai
        order_response = requests.post(api_url, json={
            "id_log": data['id_log']
        })

        # Cek apakah ada error dari API distributor
        if order_response.status_code != 200:
            return jsonify({"error": "Gagal melakukan pemesanan ke distributor"}), 400

        order_data = order_response.json()

        # Membuat objek Pembelian baru
        new_purchase = {
            "id_log": data['id_log'],  # Menggunakan id_log dari transaksi
            "total_harga_barang": transaction_data['total_harga_barang'],
            "total_berat_barang": transaction_data['total_berat_barang'],
            "no_resi": order_data['no_resi'],  # Mengambil no_resi dari respons API
            "harga_pengiriman": order_data['harga_pengiriman'],
            "lama_pengiriman": order_data.get('lama_pengiriman'),  # Mengambil lama_pengiriman jika ada
            "tanggal_pembelian": firestore.SERVER_TIMESTAMP  # Menggunakan timestamp server
        }

        # Simpan pembelian baru ke Firestore
        db.collection('db_pembelian').add(new_purchase)

        return jsonify({
            "message": "Pemesanan berhasil dilakukan",
            "purchase_id": transaction_ref.id,  # Menggunakan id dari referensi
            "no_resi": order_data['no_resi'],
            "harga_pengiriman": order_data['harga_pengiriman'],
            "lama_pengiriman": order_data.get('lama_pengiriman'),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Endpoint untuk supplier
@app.route('/suppliers', methods=['GET'])
def get_suppliers():
    try:
        # Akses koleksi db_produk
        supplier_ref = db.collection('db_supplier')
        suppliers = []

        # Mendapatkan data dari setiap dokumen dalam koleksi db_produk
        for doc in supplier_ref.stream():
            supplier_data = doc.to_dict()
            supplier_data["id_supplier"] = doc.id  # Ambil semua field dari dokumen
            suppliers.append(supplier_data)

        return jsonify(suppliers), 200  # Mengembalikan semua produk dalam format JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app.route('/products', methods=['GET'])
def get_products():
    try:
        # Akses koleksi db_produk
        products_ref = db.collection('db_produk')
        products = []

        # Mendapatkan data dari setiap dokumen dalam koleksi db_produk
        for doc in products_ref.stream():
            product_data = doc.to_dict()  # Ambil semua field dari dokumen
            product_data['id_produk'] = doc.id
            products.append(product_data)

        return jsonify(products), 200  # Mengembalikan semua produk dalam format JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app.route('/update_stock', methods=['POST'])
def update_stock():
    data = request.json

    try:
        # Ambil no_resi dan id_distributor dari input POST
        no_resi = data.get('no_resi')
        id_distributor = data.get('id_distributor')  # Ambil id_distributor
        if not no_resi:
            return jsonify({"error": "no_resi harus diisi"}), 400
        if not id_distributor:
            return jsonify({"error": "id_distributor harus diisi"}), 400

        # Tentukan URL API berdasarkan id_distributor
        if id_distributor == "DIS01":
            api_url = f"http://159.223.41.243:8000/api/distributors6/status/{no_resi}"
        elif id_distributor == "DIS02":
            api_url = f"http://159.223.41.243:8000/api/distributors2/status/{no_resi}"
        elif id_distributor == "DIS03":
            api_url = f"http://159.223.41.243:8000/api/distributors3/status/{no_resi}"
        else:
            return jsonify({"error": "ID distributor tidak valid"}), 400

        # Ambil order berdasarkan id_log
        order_ref = db.collection('db_order').where('id_log', '==', data['id_log']).get()
        
        if not order_ref:
            return jsonify({"error": "Order tidak ditemukan"}), 404

        order_data = order_ref[0].to_dict()  # Mengambil data order pertama

        # Cek status pengiriman menggunakan no_resi dan API yang sesuai
        status_response = requests.get(api_url)
        status_data = status_response.json()

        if status_data.get('status') == "On The Way":
            # List untuk menyimpan stok yang diperbarui
            updated_stocks = []

            # Kurangi stok dari db_produk untuk setiap id_produk di db_order
            for order in order_ref:
                produk_ref = db.collection('db_produk').document(order.to_dict()['id_produk'])
                produk_doc = produk_ref.get()

                if produk_doc.exists:
                    # Mengurangi stok
                    stock_sekarang = produk_doc.to_dict().get('stock', 0)
                    new_stock = stock_sekarang - order.to_dict()['quantity']

                    # Update stok di db_produk
                    produk_ref.update({"stock": new_stock})

                    # Menambahkan stok yang diperbarui ke dalam list
                    updated_stocks.append({
                        "id_produk": order.to_dict()['id_produk'],
                        "new_stock": new_stock
                    })
                else:
                    return jsonify({"error": f"Produk dengan id {order.to_dict()['id_produk']} tidak ditemukan"}), 404

            # Update status di db_pembelian
            pembelian_ref = db.collection('db_pembelian').where('id_log', '==', db.document(f'db_transaksi/{data["id_log"]}')).get()
            
            if pembelian_ref:
                # Update status di pembelian
                for pembelian in pembelian_ref:
                    pembelian.reference.update({
                        "status": status_data.get('status')
                    })

                return jsonify({
                    "message": "Stok berhasil diperbarui dan status pengiriman diperbarui di db_pembelian",
                    "updated_stocks": updated_stocks,
                    "status_pengiriman": status_data.get('status')
                }), 200
            else:
                return jsonify({"error": "Pembelian dengan id_log tersebut tidak ditemukan"}), 404
        else:
            return jsonify({"error": "Status pengiriman tidak 'On The Way'"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)