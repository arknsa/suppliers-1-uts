from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import requests
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In your routes, use logger.error() instead of print() for error logging

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inisialisasi Firebase Admin SDK
cred = credentials.Certificate("uts-iak-firebase-adminsdk-q4jev-fb337bb7ab.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

class User:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
    
    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    user_doc = db.collection('db_user').document(user_id).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return User(user_id, user_data['username'])
    return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            # Cari user berdasarkan username
            users_ref = db.collection('db_user')
            query = users_ref.where('username', '==', username).limit(1).get()

            if not query:
                flash('Username tidak ditemukan.', 'danger')
                return redirect(url_for('login'))

            user_doc = next(iter(query), None)
            if not user_doc:
                flash('Username tidak ditemukan.', 'danger')
                return redirect(url_for('login'))

            user_data = user_doc.to_dict()

            # Verifikasi password
            if user_data['password'] == password:
                user_obj = User(user_doc.id, username)
                login_user(user_obj)
                flash('Login berhasil!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Password salah.', 'danger')
                return redirect(url_for('login'))

        except Exception as e:
            print(f"Error during login: {e}")
            flash('Terjadi kesalahan saat login.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Anda telah keluar.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

# Koleksi untuk produk
product_ref = db.collection('db_produk')

@app.route('/manage_product')
def manage_product():
    product_ref = db.collection('db_produk')
    try:
        products = []
        for doc in product_ref.stream():
            product = doc.to_dict()
            product['id_produk'] = doc.id
            products.append(product)
        return render_template('manage_product.html', products=products)
    except Exception as e:
        print(f"Error in manage_product: {e}")
        return "An error occurred", 500

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            # Cek jumlah produk yang sudah ada untuk format ID
            products_ref = db.collection('db_produk')
            product_docs = products_ref.stream()
            product_count = sum(1 for _ in product_docs) + 1  # Hitung berapa produk yang sudah ada

            # Generate id_produk dengan format "PROD{number}"
            new_product_id = f"PROD{product_count:03d}"  # 04d untuk memastikan selalu 4 digit, misalnya PROD0001

            # Buat dictionary produk baru
            new_product = {
                'id_produk': new_product_id,
                'nama_produk': request.form['nama_produk'],
                'kategori': request.form['kategori'],
                'stock': int(request.form['stock']),
                'stock_minimum': int(request.form['stock_minimum']),
                'stock_maximum': int(request.form['stock_maximum']),
                'harga': float(request.form['harga']),
                'berat': float(request.form['berat']),
                'height': float(request.form['height']),
                'width': float(request.form['width']),
                'genre': request.form['genre'],
                'warna': request.form['warna'],
                'deskripsi': request.form['deskripsi'],
                'link_gambar_barang': request.form['link_gambar_barang']
            }
            
            # Tambahkan produk ke koleksi Firestore dengan ID yang baru dibuat
            products_ref.document(new_product_id).set(new_product)

            return redirect(url_for('manage_product'))

        except Exception as e:
            print(f"Error at add_product: {e}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    return render_template('add_product.html')

@app.route('/edit_product/<string:id_produk>', methods=['GET', 'POST'])
def edit_product(id_produk):
    try:
        product_doc = product_ref.document(id_produk)
        product = product_doc.get()
        
        if not product.exists:
            flash('Produk tidak ditemukan', 'danger')
            return redirect(url_for('manage_product'))

        if request.method == 'POST':
            updated_data = {
                'nama_produk': request.form['nama_produk'],
                'kategori': request.form['kategori'],
                'stock': int(request.form['stock']),
                'stock_minimum': int(request.form['stock_minimum']),
                'stock_maximum': int(request.form['stock_maximum']),
                'harga': float(request.form['harga']),
                'berat': float(request.form['berat']),
                'height': float(request.form['height']),
                'width': float(request.form['width']),
                'genre': request.form['genre'],
                'warna': request.form['warna'],
                'deskripsi': request.form['deskripsi'],
                'link_gambar_barang': request.form['link_gambar_barang']
            }
            product_doc.update(updated_data)
            flash('Produk berhasil diperbarui', 'success')
            return redirect(url_for('manage_product'))

        product_data = product.to_dict()
        product_data['id_produk'] = id_produk  # Tambahkan id_produk ke data
        return render_template('edit_product.html', product=product_data)
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        return redirect(url_for('manage_product'))
    
@app.route('/delete_product/<string:id_produk>', methods=['POST'])
def delete_product(id_produk):
    try:
        product_ref.document(id_produk).delete()
        flash('Produk berhasil dihapus', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan saat menghapus produk: {str(e)}', 'danger')
    return redirect(url_for('manage_product'))

@app.route('/view_product/<string:id_produk>', methods=['GET'])
def view_product(id_produk):
    try:
        product = product_ref.document(id_produk).get()
        if not product.exists:
            flash('Produk tidak ditemukan', 'danger')
            return redirect(url_for('manage_product'))
        product_data = product.to_dict()
        product_data['id_produk'] = id_produk
        return render_template('view_product.html', product=product_data)
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        return redirect(url_for('manage_product'))
    
pembelian_ref = db.collection('db_pembelian')

from datetime import datetime
import pytz

@app.route('/manage_pembelian')
def manage_pembelian():
    pembelian_ref = db.collection('db_pembelian')
    try:
        pembelians = []
        for doc in pembelian_ref.stream():
            pembelian = doc.to_dict()

            # Extract the actual id_log from the Firestore reference
            id_log_ref = pembelian.get('id_log')
            if isinstance(id_log_ref, firestore.DocumentReference):
                # Mengambil bagian terakhir dari path referensi (ID log)
                id_log = id_log_ref.id
                pembelian['id_log'] = id_log

                # Query db_transaksi untuk mendapatkan id_distributor berdasarkan id_log
                transaksi_ref = db.collection('db_transaksi').document(id_log)
                transaksi_doc = transaksi_ref.get()
                
                if transaksi_doc.exists:
                    transaksi_data = transaksi_doc.to_dict()
                    pembelian['id_distributor'] = transaksi_data.get('id_distributor')

                    # Tentukan URL API berdasarkan id_distributor
                    id_distributor = pembelian['id_distributor']
                    no_resi = pembelian.get('no_resi', '')  # Pastikan ada field no_resi di pembelian
                    
                    if id_distributor == "DIS01":
                        api_url = f"http://159.223.41.243:8000/api/status/{no_resi}"
                    elif id_distributor == "DIS02":
                        api_url = f"http://143.244.170.95:8000/api/status/{no_resi}"
                    elif id_distributor == "DIS03":
                        api_url = f"http://159.223.41.243:8000/api/status/{no_resi}"
                    else:
                        api_url = None
                    
                    # Ambil status pengiriman dari API jika URL valid
                    if api_url:
                        try:
                            status_response = requests.get(api_url)
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                pembelian['status'] = status_data.get('status', 'Status tidak ditemukan')
                            else:
                                pembelian['status'] = f"Error: {status_response.status_code}"
                        except Exception as e:
                            pembelian['status'] = f"API Error: {str(e)}"
                    else:
                        pembelian['status'] = "ID distributor tidak valid"
                else:
                    pembelian['id_distributor'] = 'Tidak ditemukan'
                    pembelian['status'] = 'Tidak ditemukan'

            # Konversi tanggal_pembelian dari UTC ke zona waktu Jakarta
            if 'tanggal_pembelian' in pembelian:
                timestamp = pembelian['tanggal_pembelian']
                if isinstance(timestamp, datetime):
                    # Zona waktu UTC
                    utc_time = timestamp.replace(tzinfo=pytz.UTC)
                    # Konversi ke zona waktu Jakarta (WIB)
                    jakarta_tz = pytz.timezone('Asia/Jakarta')
                    jakarta_time = utc_time.astimezone(jakarta_tz)
                    pembelian['tanggal_pembelian'] = jakarta_time.strftime('%Y-%m-%d %H:%M:%S %Z')

            pembelian['id_pembelian'] = doc.id
            pembelians.append(pembelian)

        return render_template('manage_pembelian.html', pembelians=pembelians)
    except Exception as e:
        print(f"Error in manage_pembelian: {e}")
        return "An error occurred", 500


    
@app.route('/detail_pembelian/<string:id_pembelian>', methods=['GET'])
def detail_pembelian(id_pembelian):
    try:
        pembelian = pembelian_ref.document(id_pembelian).get()
        if not pembelian.exists:
            flash('Pembelian tidak ditemukan', 'danger')
            return redirect(url_for('manage_pembelian'))
        pembelian_data = pembelian.to_dict()
        pembelian_data['id_pembelian'] = id_pembelian
        return render_template('detail_pembelian.html', pembelian=pembelian_data)
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        return redirect(url_for('manage_pembelian'))
    
@app.route('/api/check_price', methods=['POST'])
def check_price():
    data = request.json

    try:
        # Cek jumlah transaksi untuk id_log format
        transaksi_ref = db.collection('db_transaksi')
        # transaksi_docs = transaksi_ref.stream()
        # Konversi 'id_retail' dan 'id_distributor' ke integer jika belum integer
        id_retail = data['id_retail']
        id_distributor = data['id_distributor']

        # Ambil semua dokumen dari transaksi yang cocok
        transaksi_docs = db.collection('db_transaksi').where('id_retail', '==', id_retail).where('id_distributor', '==', id_distributor).stream()

        # Hitung berapa kali cek harga dilakukan sebelumnya
        cek_harga_ke = sum(1 for _ in transaksi_docs) + 1

        # Generate id_log dengan format "SUP01RET02DIS03" dengan RET dan DIS berdasarkan input
        id_log = f"SUP01{id_retail}DIS{id_distributor}{cek_harga_ke:0d}" #di bagian akhir menandakan cek harga ke berapa

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
            api_url = "http://143.244.170.95:8000/api/distributor5/orders/cek_ongkir"
        elif distributor_id == "DIS03":
            api_url = "http://159.223.41.243:8000/api/distributors6/orders/cek_ongkir"
        else:
            return jsonify({"error": "ID distributor tidak valid"}), 400

        # Cek ongkir dari distributor
        ongkir_response = requests.post(api_url, json={
            "id_log": id_log,  # Menggunakan id_log yang baru di-generate
            "kota_asal": "Jakarta",  # Auto isi dengan "jakarta"
            "kota_tujuan": data['kota_tujuan'],
            "berat": data["total_berat_barang"]  # Menghitung total berat dari semua item di cart
            # "quantity": sum(item['quantity'] for item in data['cart'])  # Menghitung total quantity dari semua item di cart
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



@app.route('/api/place_order', methods=['POST'])
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

        # Cek apakah id_log sudah ada di db_pembelian
        existing_purchase = db.collection('db_pembelian').where('id_log', '==', transaction_ref).get()
        if existing_purchase:
            return jsonify({"error": "Pemesanan dengan id_log ini sudah dilakukan sebelumnya."}), 400

        # Tentukan URL API berdasarkan id_distributor
        if distributor_id == "DIS01":
            api_url = "http://159.223.41.243:8000/api/distributors6/orders/fix_kirim"
        elif distributor_id == "DIS02":
            api_url = "http://143.244.170.95:8000/api/distributor5/orders/fix_kirim"
        elif distributor_id == "DIS03":
            api_url = "http://159.223.41.243:8000/api/distributors6/orders/fix_kirim"
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
            "id_log": transaction_ref,  # Menggunakan id_log dari transaksi
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
@app.route('/api/suppliers', methods=['GET'])
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
    

@app.route('/api/products', methods=['GET'])
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
            api_url = f"http://159.223.41.243:8000/api/status/{no_resi}"
        elif id_distributor == "DIS02":
            api_url = f"http://143.244.170.95:8000/api/status/{no_resi}"
        elif id_distributor == "DIS03":
            api_url = f"http://159.223.41.243:8000/api/status/{no_resi}"
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

        if status_data.get('status') == "On The Way" or status_data.get('status') == "Kurir mengirim paket":
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