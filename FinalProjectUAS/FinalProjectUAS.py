from abc import ABC, abstractmethod
class InvalidInputError(Exception):
    pass
class DataNotFoundError(Exception):
    pass
class KoneksiDatabase(ABC):
    @abstractmethod
    def simpan_data(self, data):
        pass
    @abstractmethod
    def ambil_data(self):
        pass
class DataBaseInMemory(KoneksiDatabase):
    def __init__(self):
        self.__db = {}
    def simpan_data(self, mahasiswa):
        self.__db[mahasiswa.nim] = mahasiswa
    def ambil_data(self):
        return self.__db
    def cari_by_nim(self, nim):
        return self.__db.get(nim)
class User:
    def __init__(self, nama_lengkap: str):
        self._nama_lengkap = nama_lengkap
    @property
    def nama_lengkap(self):
        return self._nama_lengkap
class Mahasiswa(User):
    def __init__(self, nama: str, nim: str, semester: int, prodi: str, tujuan: str, alasan: str, waktu_keluar: str):
        super().__init__(nama)
        self.__nim = nim
        self.__semester = semester
        self.__prodi = prodi
        self.__tujuan = tujuan
        self.__alasan = alasan
        self.__waktu_keluar = waktu_keluar
        self.__keluar_count = 1
        self.__status_izin = "Pending"
    @property
    def nim(self):
        return self.__nim
    @property
    def semester(self):
        return self.__semester
    @property
    def prodi(self):
        return self.__prodi
    @property
    def tujuan(self):
        return self.__tujuan
    @tujuan.setter
    def tujuan(self, val):
        self.__tujuan = val
    @property
    def alasan(self):
        return self.__alasan
    @property
    def waktu_keluar(self):
        return self.__waktu_keluar
    @waktu_keluar.setter
    def waktu_keluar(self, val):
        self.__waktu_keluar = val
    @property
    def keluar_count(self):
        return self.__keluar_count
    @property
    def status_izin(self):
        return self.__status_izin
    @status_izin.setter
    def status_izin(self, status):
        self.__status_izin = status
    def catat_keluar(self):
        self.__keluar_count += 1
    def __str__(self):
        return (
            f"\n========== DATA E-PERIZINAN MAHASISWA =========="
            f"\nNama          : {self.nama_lengkap}"
            f"\nNIM           : {self.__nim}"
            f"\nSemester      : {self.__semester}"
            f"\nProdi         : {self.__prodi}"
            f"\nTujuan        : {self.__tujuan}"
            f"\nAlasan        : {self.__alasan}"
            f"\nWaktu Keluar  : {self.__waktu_keluar}"
            f"\nKeluar Count  : {self.__keluar_count}"
            f"\nStatus Izin   : {self.__status_izin}"
        )
class StafDeKaPe(User):
    def __init__(self, nama: str, id_staf: str):
        super().__init__(nama)
        self.__id_staf = id_staf
    def proses_pesan_masuk(self, mhs: Mahasiswa, setuju: bool):
        if setuju:
            mhs.status_izin = "Disetujui"
            print(f"[AKSES STAF] Izin Mahasiswa {mhs.nama_lengkap}(NIM:{mhs.nim}) Telah Disetujui")
        else:
            mhs.status_izin = "Ditolak"
            print(f"[AKSES STAF] Izin Mahasiswa {mhs.nama_lengkap}(NIM:{mhs.nim}) Telah Ditolak")
class SatpamGerbangKampus(User):
    def __init__(self, nama: str, id_satpam: str):
        super().__init__(nama)
        self.__id_satpam = id_satpam
    def verifikasi_kembali(self, mhs: Mahasiswa):
        mhs.status_izin = "Sudah Kembali"
        print(f"[POS {self.__id_satpam}] Mahasiswa {mhs.nama_lengkap}(NIM:{mhs.nim}) Terverifikasi dan Sudah Kembali")
class SistemPerizinan:
    @staticmethod
    def verifikasi_jam_malam(waktu_keluar: str) -> str:
        waktu = waktu_keluar.lower().strip()
        if waktu in ["pagi", "siang", "sore", "malam"]:
            return "Peringatan harus kembali paling lambat sebelum jam 22.00 PM"
        else:
            return "Peringatan: Anda Telah Melanggar Peraturan Kampus Silahkan Melapor Ke Pihak DKP"
    @staticmethod
    def parse_wa_command(command: str):
        parts = command.strip().split(";")
        if len(parts) < 6 or not parts[0].upper().startswith("#IZIN"):
            raise InvalidInputError("Format pesan WhatsApp tidak valid! Gunakan: #IZIN;Nama;NIM;Semester;Prodi;Tujuan;Alasan;Waktu")
        return parts
def main():
    db = DataBaseInMemory()
    staf_piket = StafDeKaPe("Ust. Ahmad", "STF-001")
    satpam_pos = SatpamGerbangKampus("Pak Budi", "SAT-001")
    print("========================================")
    print("         E-PERIZINAN UNIDA GONTOR       ")
    print("========================================")
    while True:
        print("\n=====  MAIN MENU   =====")
        print("1. Ajukan Perizinan Keluar (Simulation WA)")
        print("2. Approval Staf DeKaPe (#Setuju/ #Tolak)")
        print("3. Lihat Dasboard Rekapitulasi Harian (Monitor)")
        print("4. Verifikasi Kembali Ke kampus (Satpam)")
        print("5. Keluar Aplikasi")
        pilihan = input("Pilih menu (1-5): ").strip()
        try:
            if pilihan == "1":
                print("\n[  Tipe Input  ]")
                print("a. Format Teks WhatsApp (#IZIN;Nama;NIM;Semester;Prodi;Tujuan;Alasan;Waktu)")
                print("b. Form Interaktif")
                mode = input("Pilih mode input (a/b): ").lower().strip()
                if mode == "a":
                    raw_wa = input("Masukkan Teks WA: ")
                    data = SistemPerizinan.parse_wa_command(raw_wa)
                    nama, nim, sem, prodi = data[1], data[2], int(data[3]), data[4]
                    tujuan, alasan, waktu = data[5], data[6], data[7]
                elif mode == "b":
                    nama = input("Nama Lengkap: ").strip()
                    nim = input("NIM: ").strip()
                    sem_str = input("Semester: ").strip()
                    if not sem_str.isdigit():
                        raise InvalidInputError("Semester harus berupa angka input Integer!")
                    sem = int(sem_str)
                    prodi = input("Prodi: ").strip()
                    tujuan = input("Tujuan: ").strip()
                    alasan = input("Alasan: ").strip()
                    waktu = input("Waktu: ").strip()
                else:
                    raise InvalidInputError("Pilihan input tidak valid!")
                mhs_existing = db.cari_by_nim(nim)
                if mhs_existing:
                    mhs_existing.catat_keluar()
                    mhs_existing.tujuan = tujuan
                    mhs_existing.waktu_keluar = waktu
                    mhs_existing.status_izin = "Pending"
                    print(f"\n[INFO] Data NIM {nim} diperbarui (Pengajuan Perizinan ke--{mhs_existing.keluar_count}). Status: Pending.")
                else:
                    mhs_baru = Mahasiswa(nama, nim, sem, prodi, tujuan, alasan, waktu)
                    db.simpan_data(mhs_baru)
                    print(f"\n[SUCCESS] Pengajuan perizinan baru berhasil disimpan ke database.")
                print(SistemPerizinan.verifikasi_jam_malam(waktu))
            elif pilihan == "2":
                nim = input("\nMasukkan NIM mahasiswa yang akan diproses oleh staf: ").strip()
                mhs = db.cari_by_nim(nim)
                if not mhs:
                    raise DataNotFoundError(f"Data mahasiswa dengan NIM {nim} tidak ditemukan.")
                print(mhs)
                acc = input("Setujui perizinan? (y/n): ").lower().strip()
                is_approved = True if acc == 'y' else False
                staf_piket.proses_pesan_masuk(mhs, is_approved)
            elif pilihan == "3":
                data_semua = db.ambil_data()
                if not data_semua:
                    print("\n[DASBOR REKAP] Belum ada data perizinan terdaftar.")
                else:
                    print("\n========== DASBOR MONITORING REKAP HARIAN ==========")
                    for mhs in data_semua.values():
                        print(mhs)
            elif pilihan == "4":
                nim = input("\nMasukkan NIM Mahasiswa yang kembali ke kampus: ").strip()
                mhs = db.cari_by_nim(nim)
                if not mhs:
                    raise DataNotFoundError(f"Mahasiswa dengan NIM {nim} tidak ditemukan di logbook!")
                satpam_pos.verifikasi_kembali(mhs)
            elif pilihan == "5":
                print("Sistem E-Perizinan dihentikan. Terima kasih.")
                break
            else:
                print("Pilihan menu tidak valid, silakan coba lagi!")
        except InvalidInputError as e:
            print(f"\n[INPUT ERROR] {e}")
        except DataNotFoundError as e:
            print(f"\n[NOT FOUND ERROR] {e}")
        except Exception as e:
            print(f"\n[SYSTEM ERROR] Terjadi kesalahan sistem: {e}")
if __name__ == "__main__":
    main()
