import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import speedtest
import os
import platform
import threading
import subprocess
try:
    import ollama
    OLLAMA_VAR = True
except ImportError:
    OLLAMA_VAR = False

class SistemYoneticiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem, Asistan & Qwen Nano Pro")
        self.root.geometry("500x780")
        self.root.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Üst Başlık
        lbl_baslik = ttk.Label(root, text="🚀 Kali Nano Control Center", font=("Arial", 15, "bold"))
        lbl_baslik.pack(pady=10)
        
        # --- QWEN AI ASİSTAN (NANO + SYSTEM PROMPT) ---
        lf_ai = ttk.LabelFrame(root, text=" 🤖 Yerel AI (Qwen2:0.5b Nano + Kural Seti) ")
        lf_ai.pack(fill="x", padx=20, pady=5)
        
        self.entry_ai = ttk.Entry(lf_ai, width=38)
        self.entry_ai.pack(side="left", padx=5, pady=8)
        self.entry_ai.insert(0, "RAM neden patlıyor?")
        
        btn_sor = ttk.Button(lf_ai, text="Sor", command=self.ai_sor)
        btn_sor.pack(side="left", padx=5, pady=8)
        
        self.txt_ai_cvp = tk.Text(root, height=4, width=58)
        self.txt_ai_cvp.pack(padx=20, pady=2)
        self.txt_ai_cvp.insert("1.0", "Qwen çıktısı burada görünecek...")
        self.txt_ai_cvp.config(state="disabled")

        # --- GÜNLÜK PRATİK: IBAN / ŞABLON ---
        lf_gunluk = ttk.LabelFrame(root, text=" ⚡ Günlük Pratik (Tek Tık Kopyala) ")
        lf_gunluk.pack(fill="x", padx=20, pady=5)
        
        self.entry_sablon = ttk.Entry(lf_gunluk, width=38)
        self.entry_sablon.insert(0, "TR00 0000 0000 0000 0000 0000 00")
        self.entry_sablon.pack(side="left", padx=5, pady=8)
        
        btn_kopya = ttk.Button(lf_gunluk, text="Kopyala", command=self.panoya_kopyala)
        btn_kopya.pack(side="left", padx=5, pady=8)

        # --- DONANIM & GÜÇ YÖNETİMİ ---
        lf_sarj = ttk.LabelFrame(root, text=" 🔋 Donanımsal Güç Yönetimi ")
        lf_sarj.pack(fill="x", padx=20, pady=5)
        
        self.lbl_batarya_durum = ttk.Label(lf_sarj, text="Batarya Durumu: Ölçülüyor...", font=("Arial", 9))
        self.lbl_batarya_durum.pack(pady=3)
        
        self.guc_modu = tk.StringVar(value="Dengeli")
        self.combo_mod = ttk.Combobox(lf_sarj, textvariable=self.guc_modu, values=["Maksimum Performans", "Dengeli", "Süper Tasarruf"], state="readonly", width=30)
        self.combo_mod.pack(pady=3)
        self.combo_mod.bind("<<ComboboxSelected>>", self.gercek_guc_modu_uygula)
        
        # --- FPS / OYUN & ARKA PLAN BOOST ---
        lf_fps = ttk.LabelFrame(root, text=" 🎮 Performans & FPS Boost ")
        lf_fps.pack(fill="x", padx=20, pady=5)
        
        btn_fps = ttk.Button(lf_fps, text="🚀 FPS / Arka Plan Temizliği Yap", command=self.fps_boost_uygula)
        btn_fps.pack(pady=8)

        # --- İNTERNET VE HIZ BÖLÜMÜ ---
        lf_internet = ttk.LabelFrame(root, text=" 🌐 İnternet & Ağ Optimizasyonu ")
        lf_internet.pack(fill="x", padx=20, pady=5)
        
        self.btn_hiz_testi = ttk.Button(lf_internet, text="Hız Testi Yap", command=self.hiz_testi_baslat)
        self.btn_hiz_testi.pack(side="left", padx=10, pady=8)
        
        self.lbl_hiz_sonuc = ttk.Label(lf_internet, text="⬇️ -- | ⬆️ -- Mbps", font=("Arial", 9, "bold"))
        self.lbl_hiz_sonuc.pack(side="left", padx=5)
        
        btn_optimize = ttk.Button(lf_internet, text="DNS Temizle", command=self.ag_optimize_et)
        btn_optimize.pack(side="right", padx=10, pady=8)
        
        self.batarya_guncelle()

    def ai_sor(self):
        if not OLLAMA_VAR:
            messagebox.showerror("Hata", "ollama kütüphanesi yok! 'pip install ollama' yapmalısın.")
            return
        soru = self.entry_ai.get()
        self.txt_ai_cvp.config(state="normal")
        self.txt_ai_cvp.delete("1.0", "end")
        self.txt_ai_cvp.insert("1.0", "Qwen düşünüyor...")
        self.txt_ai_cvp.config(state="disabled")
        threading.Thread(target=self._ai_worker, args=(soru,), daemon=True).start()

    def _ai_worker(self, soru):
        try:
            sys_talimat = (
                "Sen 'Kali' adlı emektar bir PC'nin (i5-4200U, 4GB RAM) yerel sistem asistanısın. "
                "Kurallar: 1) Asla destan yazma, maksimum 2-3 cümle. 2) Teknik ve net ol, saçma/uydurma bilgi verme. "
                "3) Samimi Türkçe konuş."
            )
            
            resp = ollama.chat(
                model='qwen2:0.5b', 
                messages=[
                    {'role': 'system', 'content': sys_talimat},
                    {'role': 'user', 'content': soru}
                ]
            )
            cvp = resp['message']['content']
        except Exception as e:
            cvp = f"Hata: {e}"
        
        def guncelle():
            self.txt_ai_cvp.config(state="normal")
            self.txt_ai_cvp.delete("1.0", "end")
            self.txt_ai_cvp.insert("1.0", cvp)
            self.txt_ai_cvp.config(state="disabled")
        self.root.after(0, guncelle)

    def panoya_kopyala(self):
        metin = self.entry_sablon.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(metin)
        self.root.update()
        messagebox.showinfo("Pano", "✅ Metin panoya kopyalandı!")

    def batarya_guncelle(self):
        batarya = psutil.sensors_battery()
        if batarya:
            yuzde = int(batarya.percent)
            takili_mi = "Fişe Takılı" if batarya.power_plugged else "Bataryada"
            txt = f"Şarj: %{yuzde} ({takili_mi})"
            
            if yuzde < 20 and not batarya.power_plugged and self.guc_modu.get() != "Süper Tasarruf":
                txt += " - ⚠️ Kritik Seviye!"
                self.guc_modu.set("Süper Tasarruf")
                self.gercek_guc_modu_uygula()
                
            self.lbl_batarya_durum.config(text=txt)
        else:
            self.lbl_batarya_durum.config(text="Batarya algılanamadı (Masaüstü PC).")
        self.root.after(5000, self.batarya_guncelle)

    def gercek_guc_modu_uygula(self, event=None):
        secilen_mod = self.guc_modu.get()
        if platform.system() != "Windows":
            return

        if secilen_mod == "Maksimum Performans":
            subprocess.run("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", shell=True)
        elif secilen_mod == "Dengeli":
            subprocess.run("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e", shell=True)
        elif secilen_mod == "Süper Tasarruf":
            subprocess.run("powercfg /setactive a1841308-3541-4fab-bc81-f71556f20b4a", shell=True)
            kapatilacaklar = ["discord.exe", "spotify.exe", "epicgameslauncher.exe"]
            sum(1 for p in psutil.process_iter(['name']) if p.info['name'] and p.info['name'].lower() in kapatilacaklar and self._safe_term(p))

    def _safe_term(self, p):
        try:
            p.terminate()
            return True
        except:
            return False

    def fps_boost_uygula(self):
        if platform.system() != "Windows":
            messagebox.showerror("Hata", "Bu özellik sadece Windows'ta çalışır.")
            return

        subprocess.run("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", shell=True)
        arkaplan_copu = ["searchindexer.exe", "OneDrive.exe", "Skype.exe", "Teams.exe"]
        temizlenen = sum(1 for p in psutil.process_iter(['name']) if p.info['name'] and p.info['name'].lower() in [x.lower() for x in arkaplan_copu] and self._safe_term(p))
        messagebox.showinfo("FPS / Boost Tamamlandı", f"✅ Yüksek Performans aktif.\n🗑️ {temizlenen} arka plan hizmeti temizlendi.")

    def ag_optimize_et(self):
        if platform.system() == "Windows":
            os.system("ipconfig /flushdns")
            messagebox.showinfo("Başarılı", "Windows DNS önbelleği temizlendi!")

    def hiz_testi_baslat(self):
        self.btn_hiz_testi.config(state="disabled")
        self.lbl_hiz_sonuc.config(text="Test ediliyor...")
        threading.Thread(target=self.hiz_testi_yap, daemon=True).start()

    def hiz_testi_yap(self):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            indirme = st.download() / 1_000_000
            yukleme = st.upload() / 1_000_000
            sonuc_txt = f"⬇️ {indirme:.1f} | ⬆️ {yukleme:.1f} Mbps"
        except:
            sonuc_txt = "Test başarısız."
        
        self.root.after(0, lambda: self.lbl_hiz_sonuc.config(text=sonuc_txt))
        self.root.after(0, lambda: self.btn_hiz_testi.config(state="normal"))

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemYoneticiApp(root)
    root.mainloop()