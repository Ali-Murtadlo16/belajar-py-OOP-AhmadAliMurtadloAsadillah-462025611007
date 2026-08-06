from abc import ABC, abstractmethod
import sqlite3
import datetime
class KoneksiDatabase(ABC):

    @abstractmethod
    def hubungkan(self):
        pass

    @abstractmethod
    def eksekusi_query(self, query, params=()):
        pass

    @abstractmethod
    def ambil_data(self, query, params=()):
        pass


class DatabaseSQLite(KoneksiDatabase):

    def __init__(self, nama_db="db_eperizinan.db"):
        self.nama_db = nama_db
        self.hubungkan()
        self.buat_tabel()

    def hubungkan(self):
        self.conn = sqlite3.connect(self.nama_db)
        self.cursor = self.conn.cursor()

    def buat_tabel(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbMahasiswa (
                nim TEXT PRIMARY KEY,
                namaLengkap TEXT NOT NULL,
                semester INTEGER,
                prodi TEXT,
                password TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbPerizinan (
                idIzin INTEGER PRIMARY KEY AUTOINCREMENT,
                nim TEXT,
                tujuan TEXT,
                alasan TEXT,
                waktuKeluar DATETIME,
                waktuKembali DATETIME,
                statusIzin TEXT,
                FOREIGN KEY (nim) REFERENCES tbMahasiswa(nim)
            )
        ''')
        self.conn.commit()

    def eksekusi_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def ambil_data(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
class Pengguna(ABC):
    """Kelas Induk (Parent-Class) untuk seluruh entitas pengguna."""

    def __init__(self, nama_lengkap, username):
        self._namaLengkap = nama_lengkap
        self._username = username

    @property
    def nama_lengkap(self):
        return self._namaLengkap

    @abstractmethod
    def proses_perintah_cli(self, db):
        pass


class Mahasiswa(Pengguna):
    def __init__(self, nim, nama_lengkap, semester, prodi, password):
        super().__init__(nama_lengkap, nim)
        self.__nim = nim
        self.__passwordAkun = password
        self.semester = semester
        self.prodi = prodi

    @property
    def nim(self):
        return self.__nim

    def verifikasi_password(self, pwd_input):
        return self.__passwordAkun == pwd_input

    def ajukan_perizinan(self, db, tujuan, alasan):
        waktu_sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO tbPerizinan (nim, tujuan, alasan, waktuKeluar, statusIzin) VALUES (?, ?, ?, ?, ?)"
        db.eksekusi_query(query, (self.__nim, tujuan, alasan, waktu_sekarang, 'Pending'))
        print(f"\n[SUKSES] Pengajuan izin untuk NIM {self.__nim} berhasil dikirim dengan status 'Pending'.")

    def cek_status_izin(self, db):
        query = "SELECT idIzin, tujuan, alasan, waktuKeluar, waktuKembali, statusIzin FROM tbPerizinan WHERE nim = ?"
        data = db.ambil_data(query, (self.__nim,))
        print("\n--- RIWAYAT & STATUS PERIZINAN SAYA ---")
        if not data:
            print("Belum ada riwayat perizinan.")
        for row in data:
            print(f"ID: {row[0]} | Tujuan: {row[1]} | Alasan: {row[2]} | Keluar: {row[3]} | Kembali: {row[4] or 'Belum Kembali'} | Status: {row[5]}")

    def proses_perintah_cli(self, db):
        while True:
            print(f"\n=== MENU CLI MAHASISWA ({self._namaLengkap}) ===")
            print("1. Ajukan Perizinan Keluar Kampus (#IZIN)")
            print("2. Cek Status Izin Saya")
            print("3. Logout / Keluar")
            pilihan = input("Pilih menu (1/2/3): ")

            if pilihan == '1':
                tujuan = input("Masukkan Tujuan Keluar Kampus: ")
                alasan = input("Masukkan Alasan Detail Keperluan: ")
                self.ajukan_perizinan(db, tujuan, alasan)
            elif pilihan == '2':
                self.cek_status_izin(db)
            elif pilihan == '3':
                break
            else:
                print("Pilihan tidak valid.")


class StaffDirektoratKepesantrenan(Pengguna):

    def __init__(self, id_staff, nama_lengkap, bagian):
        super().__init__(nama_lengkap, id_staff)
        self.idStaff = id_staff
        self.bagian = bagian

    def lihat_semua_izin(self, db):
        query = """
            SELECT p.idIzin, m.nim, m.namaLengkap, p.tujuan, p.waktuKeluar, p.statusIzin
            FROM tbPerizinan p
            JOIN tbMahasiswa m ON p.nim = m.nim
        """
        return db.ambil_data(query)

    def otorisasi_izin(self, db, id_izin, keputusan):
        query = "UPDATE tbPerizinan SET statusIzin = ? WHERE idIzin = ?"
        db.eksekusi_query(query, (keputusan, id_izin))
        print(f"\n[INFO] Perizinan ID {id_izin} berhasil diubah statusnya menjadi: {keputusan}")
    def proses_perintah_cli(self, db):
        while True:
            print(f"\n=== DASBOR PUSAT STAF KEPESANTRENAN ({self._namaLengkap}) ===")
            print("1. Lihat Daftar Pengajuan Izin Mahasiswa")
            print("2. Otorisasi Izin (#SETUJU / #TOLAK)")
            print("3. Logout / Keluar")
            pilihan = input("Pilih menu (1/2/3): ")

            if pilihan == '1':
                data = self.lihat_semua_izin(db)
                print("\n--- DAFTAR PERIZINAN MASUK ---")
                if not data:
                    print("Belum ada pengajuan perizinan.")
                for row in data:
                    print(f"ID Izin: {row[0]} | NIM: {row[1]} | Nama: {row[2]} | Tujuan: {row[3]} | Waktu Keluar: {row[4]} | Status: {row[5]}")
            elif pilihan == '2':
                id_izin = input("Masukkan ID Izin yang akan diproses: ")
                aksi = input("Ketik '1' untuk SETUJU atau '2' untuk TOLAK: ")
                status = 'Disetujui' if aksi == '1' else 'Ditolak'
                self.otorisasi_izin(db, id_izin, status)
            elif pilihan == '3':
                break
            else:
                print("Pilihan tidak valid.")


class SatpamGerbangKampus(Pengguna):
    """Sub-kelas Satpam / Keamanan Gerbang Kampus."""

    def __init__(self, no_pos, nama_petugas):
        super().__init__(nama_petugas, no_pos)
        self.noPosPenjaga = no_pos

    def validasi_akses_gerbang(self, db):
        query = """
            SELECT p.idIzin, m.nim, m.namaLengkap, p.tujuan, p.statusIzin
            FROM tbPerizinan p
            JOIN tbMahasiswa m ON p.nim = m.nim
            WHERE p.statusIzin = 'Disetujui'
        """
        return db.ambil_data(query)

    def catat_kepulangan(self, db, nim):
        waktu_sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "UPDATE tbPerizinan SET statusIzin = 'Selesai', waktuKembali = ? WHERE nim = ? AND statusIzin = 'Disetujui'"
        db.eksekusi_query(query, (waktu_sekarang, nim))
        print(f"\n[INFO] Mahasiswa dengan NIM {nim} tercatat telah kembali ke kampus.")

    def proses_perintah_cli(self, db):
        while True:
            print(f"\n=== MONITOR POS GERBANG UTAMA (Pos {self.noPosPenjaga}) ===")
            print("1. Lihat Daftar Mahasiswa Berizin Aktif ('Disetujui')")
            print("2. Catat Mahasiswa Kembali ke Kampus")
            print("3. Logout / Keluar")
            pilihan = input("Pilih menu (1/2/3): ")

            if pilihan == '1':
                data = self.validasi_akses_gerbang(db)
                print("\n--- DAFTAR MAHASISWA DIIZINKAN KELUAR ---")
                if not data:
                    print("Tidak ada data mahasiswa dengan izin aktif.")
                for row in data:
                    print(f"ID: {row[0]} | NIM: {row[1]} | Nama: {row[2]} | Tujuan: {row[3]} | Status: {row[4]}")
            elif pilihan == '2':
                nim_mhs = input("Masukkan NIM Mahasiswa yang kembali: ")
                self.catat_kepulangan(db, nim_mhs)
            elif pilihan == '3':
                break
            else:
                print("Pilihan tidak valid.")
def inisialisasi_data_dummy(db):
    cek = db.ambil_data("SELECT COUNT(*) FROM tbMahasiswa")
    if cek[0][0] == 0:
        db.eksekusi_query("INSERT INTO tbMahasiswa VALUES (?, ?, ?, ?, ?)",
                           ("462025611007", "Ahmad Ali Murtadlo Asadillah", 4, "Teknik Informatika", "password123"))
        db.eksekusi_query("INSERT INTO tbMahasiswa VALUES (?, ?, ?, ?, ?)",
                           ("462025611999", "Fulan bin Fulan", 2, "Teknik Informatika", "password456"))

def main():
    db = DatabaseSQLite()
    inisialisasi_data_dummy(db)

    staff_pusat = StaffDirektoratKepesantrenan("STF001", "Ustadz Ahmad", "Bagian Pengasuhan")
    satpam_pos1 = SatpamGerbangKampus("POS-01", "Komandan Satpam")

    while True:
        print("\n========================================================")
        print("   SISTEM E-PERIZINAN KELUAR KAMPUS DIGITAL (CLI) UNIDA")
        print("========================================================")
        print("1. Login sebagai Mahasiswa")
        print("2. Login sebagai Staff Direktorat Kepesantrenan")
        print("3. Login sebagai Satpam Pos Gerbang")
        print("4. Keluar Aplikasi")

        role = input("Pilih hak akses login (1-4): ")

        if role == '1':
            nim_input = input("Masukkan NIM Mahasiswa: ")
            pwd_input = input("Masukkan Password: ")

            res = db.ambil_data("SELECT nim, namaLengkap, semester, prodi, password FROM tbMahasiswa WHERE nim = ?", (nim_input,))
            if res and res[0][4] == pwd_input:
                mhs_obj = Mahasiswa(res[0][0], res[0][1], res[0][2], res[0][3], res[0][4])
                mhs_obj.proses_perintah_cli(db)
            else:
                print("[ERROR] NIM atau Password salah!")

        elif role == '2':
            id_input = input("Masukkan ID Staff (Contoh: STF001): ")
            if id_input == staff_pusat.idStaff:
                staff_pusat.proses_perintah_cli(db)
            else:
                print("[ERROR] ID Staff tidak dikenali!")

        elif role == '3':
            pos_input = input("Masukkan Kode Pos (Contoh: POS-01): ")
            if pos_input == satpam_pos1.noPosPenjaga:
                satpam_pos1.proses_perintah_cli(db)
            else:
                print("[ERROR] Kode Pos penjagaan salah!")

        elif role == '4':
            print("\nTerima kasih telah menggunakan sistem E-Perizinan CLI UNIDA Gontor.")
            break
        else:
            print("Pilihan menu tidak valid, silakan coba lagi.")


if __name__ == "__main__":
    main()
