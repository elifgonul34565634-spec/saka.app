# -*- coding: utf-8 -*-
"""
Yilan Oyunu gorunumlu siber saka uygulamasi (Özel Müzik Sürümü)
Zararsizdir: tamamen sahte veri ve zamanlayici kullanir.
"""

import os
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.widget import Widget

# ===============================================================
# AYARLAR
# ===============================================================
HIZLI_TEST = False
DEBUG = False

if HIZLI_TEST:
    OYUN_SURESI = 2.0
    GLITCH_SURESI = 1.0
else:
    OYUN_SURESI = 25.0  # Normal oynama suresi (sn)
    GLITCH_SURESI = 3.0  # Ekranin gidip gelme suresi

SIYAH_EKRAN_SURESI = 5.0  # Siyah ekranda sesin calacagi toplam sure (sn)
SAHTE_EKRAN_SURESI = 15.0  # Tablonun ekranda kalma suresi (sn)
GUVENLIK_SURESI = 60

# İstediğin özel dosya adı en başta aranacak
ARKAPLAN_SES_ADAYLARI = ["ürkütücü_ses.ogg", "arkaplan.ogg", "ambient.ogg"]
KORKUTUCU_SES_ADAYLARI = ["balloonboy.ogg", "balloonboy.wav", "balloonboy.mp3"]

KLASOR = os.path.dirname(os.path.abspath(__file__))


def yol(*parcalar):
    return os.path.join(KLASOR, *parcalar)


def ses_yukle(adaylar):
    for ad in adaylar:
        dosya = yol(ad)
        if os.path.exists(dosya):
            try:
                ses = SoundLoader.load(dosya)
                if ses:
                    Logger.info("SAKA: ses yuklendi -> %s" % ad)
                    return ses, ad
            except Exception as e:
                Logger.warning("SAKA: ses acilamadi %s: %s" % (ad, e))
    Logger.warning("SAKA: ses bulunamadi -> %s" % adaylar)
    return None, None


def ses_cal(ses, ses_seviyesi=1.0, dongu=False):
    if ses:
        try:
            ses.stop()
            ses.volume = ses_seviyesi
            ses.loop = dongu
            ses.play()
        except Exception as e:
            Logger.warning("SES: çalma hatası: %s" % e)


# ===============================================================
# Oynanabilir Yılan Bileşeni
# ===============================================================
class OynanabilirYilan(Widget):
    HUCRE = 24

    def __init__(self, yemek_fonksiyonu=None, **kwargs):
        super().__init__(**kwargs)
        self.yemek_fonksiyonu = yemek_fonksiyonu
        self.yilan = []
        self.yon = (1, 0)
        self.sonraki_yon = (1, 0)
        self.yem = (0, 0)
        self.hazir = False
        self.kol = 1
        self.satir = 1

        self.ses_yemek, _ = ses_yukle(KORKUTUCU_SES_ADAYLARI)

        self.bind(size=self._hazirla)
        self.olay = Clock.schedule_interval(self.guncelle, 0.12)

    def durdur(self):
        if self.olay:
            self.olay.cancel()
            self.olay = None

    def yon_degistir(self, yeni_yon):
        if (-yeni_yon[0], -yeni_yon[1]) != self.yon:
            self.sonraki_yon = yeni_yon

    def _hazirla(self, *args):
        if self.width < 200 or self.height < 200:
            return

        yeni_kol = int(self.width // self.HUCRE)
        yeni_satir = int(self.height // self.HUCRE)

        if not self.hazir:
            self.hazir = True
            self.kol = max(5, yeni_kol)
            self.satir = max(5, yeni_satir)
            bx, by = self.kol // 2, self.satir // 2
            self.yilan = [(bx - i, by) for i in range(5)]
            self.yem_koy()

    def yem_koy(self):
        if not self.yilan or self.kol < 5:
            self.yem = (0, 0)
            return
        bas = self.yilan[0]
        for _ in range(30):
            rx = random.randint(0, self.kol - 1)
            ry = random.randint(0, self.satir - 1)
            if abs(rx - bas[0]) + abs(ry - bas[1]) >= 5:
                self.yem = (rx, ry)
                return
        self.yem = (random.randint(0, self.kol - 1), random.randint(0, self.satir - 1))

    def guncelle(self, dt):
        if not self.hazir or not self.yilan:
            return

        self.yon = self.sonraki_yon
        bas = self.yilan[0]
        yeni = ((bas[0] + self.yon[0]) % self.kol,
                (bas[1] + self.yon[1]) % self.satir)

        self.yilan.insert(0, yeni)
        if yeni == self.yem:
            self.yem_koy()
            if self.ses_yemek:
                ses_cal(self.ses_yemek, 0.4, dongu=False)
            if self.yemek_fonksiyonu:
                self.yemek_fonksiyonu()
        else:
            self.yilan.pop()

        self.ciz()

    def ciz(self):
        self.canvas.clear()
        h = self.HUCRE
        with self.canvas:
            Color(0.05, 0.1, 0.05, 1)
            Rectangle(pos=self.pos, size=self.size)
            # Yem
            Color(1, 0.2, 0.2, 1)
            Rectangle(pos=(self.x + self.yem[0] * h, self.y + self.yem[1] * h),
                      size=(h - 2, h - 2))
            # Yılan
            for i, (cx, cy) in enumerate(self.yilan):
                if i == 0:
                    Color(0.6, 1, 0.3, 1)
                else:
                    Color(0.2, 0.8, 0.2, 1)
                Rectangle(pos=(self.x + cx * h, self.y + cy * h),
                          size=(h - 2, h - 2))


# ===============================================================
# Ekran 1: Ana Menu
# ===============================================================
class MenuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        duzen = FloatLayout()

        self.arka = OynanabilirYilan()
        duzen.add_widget(self.arka)

        duzen.add_widget(Label(
            text="[b]YILAN OYUNU[/b]",
            markup=True,
            font_size="44sp",
            color=(0.6, 1, 0.3, 1),
            size_hint=(1, 0.2),
            pos_hint={"center_x": 0.5, "center_y": 0.75},
        ))

        buton = Button(
            text="Oyuna Başla",
            font_size="28sp",
            size_hint=(0.6, 0.12),
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            background_normal="",
            background_color=(0.1, 0.6, 0.1, 1),
        )
        buton.bind(on_release=self.oyuna_basla)
        duzen.add_widget(buton)
        self.add_widget(duzen)

    def oyuna_basla(self, *args):
        self.arka.durdur()
        self.manager.current = "oyun"


# ===============================================================
# Ekran 2: Oyun Ekranı -> Akış Yönetimi
# ===============================================================
class OyunEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.duzen = FloatLayout()

        self.yilan_oyun = OynanabilirYilan(yemek_fonksiyonu=self.yemek_yendi_callback)
        self.duzen.add_widget(self.yilan_oyun)

        self.skor_etiketi = Label(
            text="Skor: 0",
            font_size="20sp",
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"top": 0.95, "right": 0.95},
        )
        self.duzen.add_widget(self.skor_etiketi)

        # Telefon Yön Tuşları (D-Pad)
        btn_boyut = (65, 65)
        tus_rengi = (0.15, 0.15, 0.18, 0.85)
        yazi_rengi = (0.6, 1.0, 0.3, 1)

        self.btn_yukari = Button(text="▲", font_size="24sp", color=yazi_rengi, size_hint=(None, None), size=btn_boyut,
                                 pos_hint={"right": 0.85, "y": 0.16}, background_normal="", background_color=tus_rengi)
        self.btn_asagi = Button(text="▼", font_size="24sp", color=yazi_rengi, size_hint=(None, None), size=btn_boyut,
                                pos_hint={"right": 0.85, "y": 0.02}, background_normal="", background_color=tus_rengi)
        self.btn_sol = Button(text="◄", font_size="24sp", color=yazi_rengi, size_hint=(None, None), size=btn_boyut,
                              pos_hint={"right": 0.72, "y": 0.09}, background_normal="", background_color=tus_rengi)
        self.btn_sag = Button(text="►", font_size="24sp", color=yazi_rengi, size_hint=(None, None), size=btn_boyut,
                              pos_hint={"right": 0.98, "y": 0.09}, background_normal="", background_color=tus_rengi)

        self.btn_yukari.bind(on_release=lambda x: self.yilan_oyun.yon_degistir((0, 1)))
        self.btn_asagi.bind(on_release=lambda x: self.yilan_oyun.yon_degistir((0, -1)))
        self.btn_sol.bind(on_release=lambda x: self.yilan_oyun.yon_degistir((-1, 0)))
        self.btn_sag.bind(on_release=lambda x: self.yilan_oyun.yon_degistir((1, 0)))

        self.duzen.add_widget(self.btn_yukari)
        self.duzen.add_widget(self.btn_asagi)
        self.duzen.add_widget(self.btn_sol)
        self.duzen.add_widget(self.btn_sag)

        self.add_widget(self.duzen)

        self.arkaplan_muzigi = None
        self.korkutucu_ses = None
        self.glitch_olay = None
        self.basladi = False
        self.skor = 0

    def on_enter(self, *args):
        if self.basladi:
            return
        self.basladi = True
        App.get_running_app().kilit = True

        Clock.schedule_once(self.hazirla, 0.1)
        Clock.schedule_interval(self.skor_arttir, 1.0)

        # Oyun süresi sonunda glitch başlasın
        Clock.schedule_once(self.glitch_baslat, OYUN_SURESI)
        Clock.schedule_once(self.uygulamayi_kapat, GUVENLIK_SURESI)

    def hazirla(self, dt):
        self.arkaplan_muzigi, _ = ses_yukle(ARKAPLAN_SES_ADAYLARI)
        self.korkutucu_ses, _ = ses_yukle(KORKUTUCU_SES_ADAYLARI)

    def skor_arttir(self, dt):
        self.skor += 1
        self.skor_etiketi.text = f"Skor: {self.skor}"

    def yemek_yendi_callback(self):
        self.skor += 10
        self.skor_etiketi.text = f"Skor: {self.skor}"

    # ---------- Aşama 1: Ekranın Gidip Gelmesi (Glitch) ----------
    def glitch_baslat(self, dt):
        self.yilan_oyun.durdur()
        for w in [self.skor_etiketi, self.btn_yukari, self.btn_asagi, self.btn_sol, self.btn_sag]:
            if w.parent:
                self.duzen.remove_widget(w)

        self.glitch_olay = Clock.schedule_interval(self.glitch_dongusu, 0.15)
        Clock.schedule_once(self.siyah_ekrana_gec, GLITCH_SURESI)

    def glitch_dongusu(self, dt):
        self.duzen.clear_widgets()
        if random.choice([True, False]):
            with self.duzen.canvas:
                Color(0, 0, 0, 1)
                Rectangle(pos=self.pos, size=Window.size)
        else:
            self.duzen.add_widget(self.yilan_oyun)

    # ---------- Aşama 2: Siyah Ekran ve Sesin Başlaması ----------
    def siyah_ekrana_gec(self, dt):
        if self.glitch_olay:
            self.glitch_olay.cancel()
            self.glitch_olay = None

        self.duzen.clear_widgets()
        with self.duzen.canvas:
            Color(0, 0, 0, 1)
            Rectangle(pos=self.pos, size=Window.size)

        # Glitch bitti, tam siyah ekranda korkutucu ses çalmaya başlasın
        ses_cal(self.korkutucu_ses, ses_seviyesi=1.0, dongu=False)

        # Tablo gelmeden 2-3 saniye önce sesi kapatıp tabloya geç
        kapanis_suresi = max(1.0, SIYAH_EKRAN_SURESI - 2.5)
        Clock.schedule_once(self.sesi_kapat_ve_tabloya_gec, kapanis_suresi)

    # ---------- Aşama 3: Sesi Kapat, Tabloyu Aç ve 'ürkütücü_ses.ogg' Çal ----------
    def sesi_kapat_ve_tabloya_gec(self, dt):
        if self.korkutucu_ses:
            self.korkutucu_ses.stop()

        self.sahte_tablo_ekrani_goster(dt)

    def sahte_tablo_ekrani_goster(self, dt):
        self.duzen.clear_widgets()

        # Tablo ekrana geldiği anda özel ürkütücü ses dosyasını döngüye alarak çal
        if self.arkaplan_muzigi:
            ses_cal(self.arkaplan_muzigi, ses_seviyesi=0.9, dongu=True)

        # Kırmızımsı korkunç arka plan
        with self.duzen.canvas:
            Color(0.08, 0.0, 0.0, 1)
            Rectangle(pos=self.pos, size=Window.size)

        # Başlık Uyarısı
        baslik = Label(
            text="[b][color=ff0000]KRİTİK HATA: SİSTEM ELE GEÇİRİLDİ![/color][/b]",
            markup=True,
            font_size="22sp",
            size_hint=(1, 0.15),
            pos_hint={"center_x": 0.5, "top": 0.88},
            halign="center",
        )
        self.duzen.add_widget(baslik)

        # Şık Tablo Tasarımı (GridLayout - 2 Sütunlu)
        tablo = GridLayout(
            cols=2,
            spacing=10,
            padding=20,
            size_hint=(0.85, 0.60),
            pos_hint={"center_x": 0.5, "center_y": 0.48}
        )

        # Tablo Verileri (Parametre ve Sahte Değerler)
        veri_listesi = [
            ("IP Adresi:", "185.142.231.66 (Tespit Edildi)"),
            ("Cihaz Türü:", "Mobil / Android OS"),
            ("Telefon No:", "+90 543 *** ** 42"),
            ("Tahmini Konum:", "İstanbul / Türkiye"),
            ("Ev Adresi:", "Örnek Mah. Korku Sk. No: 66"),
            ("Durum:", "Tüm veriler buluta aktarılıyor...")
        ]

        for anahtar, deger in veri_listesi:
            lbl_anahtar = Label(
                text=f"[b][color=00ff00]{anahtar}[/color][/b]",
                markup=True,
                font_size="16sp",
                halign="left",
                valign="middle"
            )
            lbl_anahtar.bind(size=lambda w, v: setattr(w, "text_size", v))

            lbl_deger = Label(
                text=f"[color=ffff00]{deger}[/color]",
                markup=True,
                font_size="16sp",
                halign="left",
                valign="middle"
            )
            lbl_deger.bind(size=lambda w, v: setattr(w, "text_size", v))

            tablo.add_widget(lbl_anahtar)
            tablo.add_widget(lbl_deger)

        self.duzen.add_widget(tablo)

        # Tablo ekranı süresi bittikten sonra uygulamayı kapat
        Clock.schedule_once(self.uygulamayi_kapat, SAHTE_EKRAN_SURESI)

    def uygulamayi_kapat(self, dt):
        if self.arkaplan_muzigi:
            self.arkaplan_muzigi.stop()
        app = App.get_running_app()
        app.kilit = False
        app.stop()


# ===============================================================
# Ana Uygulama Sinifi
# ===============================================================
class SakaApp(App):
    kilit = False

    def build(self):
        self.title = "Yılan Oyunu"
        Window.bind(on_keyboard=self.tus_engelle)
        Window.bind(on_request_close=self.kapatmayi_engelle)

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MenuEkrani(name="menu"))
        sm.add_widget(OyunEkrani(name="oyun"))
        return sm

    def tus_engelle(self, window, key, *args):
        if key == 27 and self.kilit:
            return True
        return False

    def kapatmayi_engelle(self, *args):
        return self.kilit

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    SakaApp().run()# -*- coding: utf-8 -*-
"""
Yilan Oyunu gorunumlu siber saka uygulamasi (Özel Müzik Sürümü)
Zararsizdir: tamamen sahte veri ve zamanlayici kullanir.
"""

import os
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.widget import Widget

# ===============================================================
# AYARLAR
# ===============================================================
HIZLI_TEST = False
DEBUG = False

if HIZLI_TEST:
    OYUN_SURESI = 2.0
    GLITCH_SURESI = 1.0
else:
    OYUN_SURESI = 25.0                 # Normal oynama suresi (sn)
    GLITCH_SURESI = 3.0                # Ekranin gidip gelme suresi

SIYAH_EKRAN_SURESI = 5.0               # Siyah ekranda sesin calacagi toplam sure (sn)
SAHTE_EKRAN_SURESI = 15.0              # Tablonun ekranda kalma suresi (sn)
GUVENLIK_SURESI = 60

# İstediğin özel dosya adı en başta aranacak
ARKAPLAN_SES_ADAYLARI = ["ürkütücü_ses.ogg", "arkaplan.ogg", "ambient.ogg"]
KORKUTUCU_SES_ADAYLARI = ["balloonboy.ogg", "balloonboy.wav", "balloonboy.mp3"]

KLASOR = os.path.dirname(os.path.abspath(__file__))


def yol(*parcalar):
    return os.path.join(KLASOR, *parcalar)


def ses_yukle(adaylar):
    for ad in adaylar:
        dosya = yol(ad)
        if os.path.exists(dosya):
            try:
                ses = SoundLoader.load(dosya)
                if ses:
                    Logger.info("SAKA: ses yuklendi -> %s" % ad)
                    return ses, ad
            except Exception as e:
                Logger.warning("SAKA: ses acilamadi %s: %s" % (ad, e))
    Logger.warning("SAKA: ses bulunamadi -> %s" % adaylar)
    return None, None


def ses_cal(ses, ses_seviyesi=1.0, dongu=False):
    if ses:
        try:
            ses.stop()
            ses.volume = ses_seviyesi
            ses.loop = dongu
            ses.play()
        except Exception as e:
            Logger.warning("SES: çalma hatası: %s" % e)


# ===============================================================
# Oynanabilir Yılan Bileşeni
# ===============================================================
class OynanabilirYilan(Widget):
    HUCRE = 24

    def __init__(self, yemek_fonksiyonu=None, **kwargs):
        super().__init__(**kwargs)
        self.yemek_fonksiyonu = yemek_fonksiyonu
        self.yilan = []
        self.yon = (1, 0)
        self.sonraki_yon = (1, 0)
        self.yem = (0, 0)
        self.hazir = False
        self.kol = 1
        self.satir = 1

        self.ses_yemek, _ = ses_yukle(KORKUTUCU_SES_ADAYLARI)

        self.bind(size=self._hazirla)
        self.olay = Clock.schedule_interval(self.guncelle, 0.12)

    def durdur(self):
        if self.olay:
            self.olay.cancel()
            self.olay = None

    def yon_degistir(self, yeni_yon):
        if (-yeni_yon[0], -yeni_yon[1]) != self.yon:
            self.sonraki_yon = yeni_yon

    def _hazirla(self, *args):
        if self.width < 200 or self.height < 200:
            return

        yeni_kol = int(self.width // self.HUCRE)
        yeni_satir = int(self.height // self.HUCRE)

        if not self.hazir:
            self.hazir = True
            self.kol = max(5, yeni_kol)
            self.satir = max(5, yeni_satir)
            bx, by = self.kol // 2, self.satir // 2
            self.yilan = [(bx - i, by) for i in range(5)]
            self.yem_koy()

    def yem_koy(self):
        if not self.yilan or self.kol < 5:
            self.yem = (0, 0)
            return
        bas = self.yilan[0]
        for _ in range(30):
            rx = random.randint(0, self.kol - 1)
            ry = random.randint(0, self.satir - 1)
            if abs(rx - bas[0]) + abs(ry - bas[1]) >= 5:
                self.yem = (rx, ry)
                return
        self.yem = (random.randint(0, self.kol - 1), random.randint(0, self.satir - 1))

    def guncelle(self, dt):
        if not self.hazir or not self.yilan:
            return

        self.yon = self.sonraki_yon
        bas = self.yilan[0]
        yeni = ((bas[0] + self.yon[0]) % self.kol,
                (bas[1] + self.yon[1]) % self.satir)

        self.yilan.insert(0, yeni)
        if yeni == self.yem:
            self.yem_koy()
            if self.ses_yemek:
                ses_cal(self.ses_yemek, 0.4, dongu=False)
            if self.yemek_fonksiyonu:
                self.yemek_fonksiyonu()
        else:
            self.yilan.pop()

        self.ciz()

    def ciz(self):
        self.canvas.clear()
        h = self.HUCRE
        with self.canvas:
            Color(0.05, 0.1, 0.05, 1)
            Rectangle(pos=self.pos, size=self.size)
            # Yem
            Color(1, 0.2, 0.2, 1)
            Rectangle(pos=(self.x + self.yem[0] * h, self.y + self.yem[1] * h),
                      size=(h - 2, h - 2))
            # Yılan
            for i, (cx, cy) in enumerate(self.yilan):
                if i == 0:
                    Color(0.6, 1, 0.3, 1)
                else:
                    Color(0.2, 0.8, 0.2, 1)
                Rectangle(pos=(self.x + cx * h, self.y + cy * h),
                          size=(h - 2, h - 2))


# ===============================================================
# Ekran 1: Ana Menu
# ===============================================================
class MenuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        duzen = FloatLayout()

        self.arka = OynanabilirYilan()
        duzen.add_widget(self.arka)

        duzen.add_widget(Label(
            text="[b]YILAN OYUNU[/b]",
            markup=True,
            font_size="44sp",
            color=(0.6, 1, 0.3, 1),
            size_hint=(1, 0.2),
            pos_hint={"center_x": 0.5, "center_y": 0.75},
        ))

        buton = Button(
            text="Oyuna Başla",
            font_size="28sp",
            size_hint=(0.6, 0.12),
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            background_normal="",
            background_color=(0.1, 0.6, 0.1, 1),
        )
        buton.bind(on_release=self.oyuna_basla)
        duzen.add_widget(buton)
        self.add_widget(duzen)

    def oyuna_basla(self, *args):
        self.arka.durdur()
        self.manager.current = "oyun"


# ===============================================================
# Ekran 2: Oyun Ekranı -> Akış Yönetimi
# ===============================================================
class OyunEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.duzen = FloatLayout()

        self.yilan_oyun = OynanabilirYilan(yemek_fonksiyonu=self.yemek_yendi_callback)
        self.duzen.add_widget(self.yilan_oyun)

        self.skor_etiketi = Label(
            text="Skor: 0",
            font_size="20sp",
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"top": 0.95, "right": 0.95},
        )
        self.duzen.add_widget(self.skor_etiketi)

        # Telefon Yön Tuşları (D-Pad)
        btn_boyut = (65, 65)
        tus_rengi = (0.15, 0.15, 0.18, 0.85)
        yazi_rengi = (0.6, 1.0, 0.3, 1)

        self.btn_yukari = Button(text="▲", font_size="24sp", color=yazi_rengi, size_hint=(None, None), size=btn_boyut, pos_hint={"right": 0.85, "y": 0.16}, background_normal="", background_color=tus_rengi)
        self.btn_asagi = Button(text="▼", font_size="24sp", color=yazi_rengi, size_hint=(None, None), size=btn_boyut, pos_hint={"right": 0.85, "y": 0.02}, background_normal="", background_color=tus_rengi)
        self.btn_sol = Button(text="◄", font_size="24sp", color=yazi_rengi, size_hint=(None, None), size=btn_boyut, pos_hint={"right": 0.72, "y": 0.09}, background_normal="", background_color=tus_rengi)
        self.btn_sag = Button(text="►", font_size="24sp", color=yazi_rengi, size_hint=(None, None), size=btn_boyut, pos_hint={"right": 0.98, "y": 0.09}, background_normal="", background_color=tus_rengi)

        self.btn_yukari.bind(on_release=lambda x: self.yilan_oyun.yon_degistir((0, 1)))
        self.btn_asagi.bind(on_release=lambda x: self.yilan_oyun.yon_degistir((0, -1)))
        self.btn_sol.bind(on_release=lambda x: self.yilan_oyun.yon_degistir((-1, 0)))
        self.btn_sag.bind(on_release=lambda x: self.yilan_oyun.yon_degistir((1, 0)))

        self.duzen.add_widget(self.btn_yukari)
        self.duzen.add_widget(self.btn_asagi)
        self.duzen.add_widget(self.btn_sol)
        self.duzen.add_widget(self.btn_sag)

        self.add_widget(self.duzen)

        self.arkaplan_muzigi = None
        self.korkutucu_ses = None
        self.glitch_olay = None
        self.basladi = False
        self.skor = 0

    def on_enter(self, *args):
        if self.basladi:
            return
        self.basladi = True
        App.get_running_app().kilit = True

        Clock.schedule_once(self.hazirla, 0.1)
        Clock.schedule_interval(self.skor_arttir, 1.0)

        # Oyun süresi sonunda glitch başlasın
        Clock.schedule_once(self.glitch_baslat, OYUN_SURESI)
        Clock.schedule_once(self.uygulamayi_kapat, GUVENLIK_SURESI)

    def hazirla(self, dt):
        self.arkaplan_muzigi, _ = ses_yukle(ARKAPLAN_SES_ADAYLARI)
        self.korkutucu_ses, _ = ses_yukle(KORKUTUCU_SES_ADAYLARI)

    def skor_arttir(self, dt):
        self.skor += 1
        self.skor_etiketi.text = f"Skor: {self.skor}"

    def yemek_yendi_callback(self):
        self.skor += 10
        self.skor_etiketi.text = f"Skor: {self.skor}"

    # ---------- Aşama 1: Ekranın Gidip Gelmesi (Glitch) ----------
    def glitch_baslat(self, dt):
        self.yilan_oyun.durdur()
        for w in [self.skor_etiketi, self.btn_yukari, self.btn_asagi, self.btn_sol, self.btn_sag]:
            if w.parent:
                self.duzen.remove_widget(w)

        self.glitch_olay = Clock.schedule_interval(self.glitch_dongusu, 0.15)
        Clock.schedule_once(self.siyah_ekrana_gec, GLITCH_SURESI)

    def glitch_dongusu(self, dt):
        self.duzen.clear_widgets()
        if random.choice([True, False]):
            with self.duzen.canvas:
                Color(0, 0, 0, 1)
                Rectangle(pos=self.pos, size=Window.size)
        else:
            self.duzen.add_widget(self.yilan_oyun)

    # ---------- Aşama 2: Siyah Ekran ve Sesin Başlaması ----------
    def siyah_ekrana_gec(self, dt):
        if self.glitch_olay:
            self.glitch_olay.cancel()
            self.glitch_olay = None

        self.duzen.clear_widgets()
        with self.duzen.canvas:
            Color(0, 0, 0, 1)
            Rectangle(pos=self.pos, size=Window.size)

        # Glitch bitti, tam siyah ekranda korkutucu ses çalmaya başlasın
        ses_cal(self.korkutucu_ses, ses_seviyesi=1.0, dongu=False)

        # Tablo gelmeden 2-3 saniye önce sesi kapatıp tabloya geç
        kapanis_suresi = max(1.0, SIYAH_EKRAN_SURESI - 2.5)
        Clock.schedule_once(self.sesi_kapat_ve_tabloya_gec, kapanis_suresi)

    # ---------- Aşama 3: Sesi Kapat, Tabloyu Aç ve 'ürkütücü_ses.ogg' Çal ----------
    def sesi_kapat_ve_tabloya_gec(self, dt):
        if self.korkutucu_ses:
            self.korkutucu_ses.stop()

        self.sahte_tablo_ekrani_goster(dt)

    def sahte_tablo_ekrani_goster(self, dt):
        self.duzen.clear_widgets()

        # Tablo ekrana geldiği anda özel ürkütücü ses dosyasını döngüye alarak çal
        if self.arkaplan_muzigi:
            ses_cal(self.arkaplan_muzigi, ses_seviyesi=0.9, dongu=True)

        # Kırmızımsı korkunç arka plan
        with self.duzen.canvas:
            Color(0.08, 0.0, 0.0, 1)
            Rectangle(pos=self.pos, size=Window.size)

        # Başlık Uyarısı
        baslik = Label(
            text="[b][color=ff0000]KRİTİK HATA: SİSTEM ELE GEÇİRİLDİ![/color][/b]",
            markup=True,
            font_size="22sp",
            size_hint=(1, 0.15),
            pos_hint={"center_x": 0.5, "top": 0.88},
            halign="center",
        )
        self.duzen.add_widget(baslik)

        # Şık Tablo Tasarımı (GridLayout - 2 Sütunlu)
        tablo = GridLayout(
            cols=2,
            spacing=10,
            padding=20,
            size_hint=(0.85, 0.60),
            pos_hint={"center_x": 0.5, "center_y": 0.48}
        )

        # Tablo Verileri (Parametre ve Sahte Değerler)
        veri_listesi = [
            ("IP Adresi:", "185.142.231.66 (Tespit Edildi)"),
            ("Cihaz Türü:", "Mobil / Android OS"),
            ("Telefon No:", "+90 543 *** ** 42"),
            ("Tahmini Konum:", "İstanbul / Türkiye"),
            ("Ev Adresi:", "Örnek Mah. Korku Sk. No: 66"),
            ("Durum:", "Tüm veriler buluta aktarılıyor...")
        ]

        for anahtar, deger in veri_listesi:
            lbl_anahtar = Label(
                text=f"[b][color=00ff00]{anahtar}[/color][/b]",
                markup=True,
                font_size="16sp",
                halign="left",
                valign="middle"
            )
            lbl_anahtar.bind(size=lambda w, v: setattr(w, "text_size", v))

            lbl_deger = Label(
                text=f"[color=ffff00]{deger}[/color]",
                markup=True,
                font_size="16sp",
                halign="left",
                valign="middle"
            )
            lbl_deger.bind(size=lambda w, v: setattr(w, "text_size", v))

            tablo.add_widget(lbl_anahtar)
            tablo.add_widget(lbl_deger)

        self.duzen.add_widget(tablo)

        # Tablo ekranı süresi bittikten sonra uygulamayı kapat
        Clock.schedule_once(self.uygulamayi_kapat, SAHTE_EKRAN_SURESI)

    def uygulamayi_kapat(self, dt):
        if self.arkaplan_muzigi:
            self.arkaplan_muzigi.stop()
        app = App.get_running_app()
        app.kilit = False
        app.stop()


# ===============================================================
# Ana Uygulama Sinifi
# ===============================================================
class SakaApp(App):
    kilit = False

    def build(self):
        self.title = "Yılan Oyunu"
        Window.bind(on_keyboard=self.tus_engelle)
        Window.bind(on_request_close=self.kapatmayi_engelle)

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MenuEkrani(name="menu"))
        sm.add_widget(OyunEkrani(name="oyun"))
        return sm

    def tus_engelle(self, window, key, *args):
        if key == 27 and self.kilit:
            return True
        return False

    def kapatmayi_engelle(self, *args):
        return self.kilit

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    SakaApp().run()