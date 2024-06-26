# MHRS Randevu Bulucu

Hem ihtiyaca binaen hem de deneysel amaçlı yazılmış bir python projesidir. @enescaakir'ın C# olarak yazdığı [MHRS Otomatik Randevu](https://github.com/enescaakir/MHRS-OtomatikRandevu) projesinden esinlenilmiştir.

O projeden farkı python dilinde yazılmış olması ve otomatik randevu almak yerine uygun randevuyu bulup bildirim almak üzerine kurgulanmış olmasıdır. Zira otomatik randevu alınıp iptal edildiğinde MHRS sistemi aynı branştan randevu almanızı 15 günlüğüne engelliyor yani o branş için 15 gün içinde kesinlikle randevu alamıyorsunuz. O yüzden sadece boş slotu bulmak bu botun görevi.

30 saniye arayla girilen kriterlere göre randevu arayacaktır. Randevu bulunduğunda sesle uyarı verecektir. Eğer twilio_config.json dosyasına twilio api bilgilerinizi girerseniz randevu bulunduğunda SMS ile bildirim yapacaktır.

## Gereksinimler

Bilgisayarınızda python 3 kurulu olmalı. requests modülünü kurmanız gerekiyor:

```bash
pip install requests
```

Şayet twilio_config.json dosyasına twilio api bilgilerinizi girip SMS bildirim özelliğini aktif etmek istiyorsanız twilio kütüphanesini de kurmanız gerekir:

```bash
pip install twilio
```

Kütüphaneyi kurduktan sonra aşağıdaki komutla çalıştırabilirsiniz:

```bash
py mhrs.py
```

Boş bir zamanımda pyqt6 ile gui giydirmesi de yapabilirim belki. Ama konsoldan komut ile de gayet pratik kullanımı.

![image](https://github.com/omergorur/mhrs-randevu-bulucu/assets/102440553/d6f0e6f4-927a-45b8-bea3-c26d01c1a0cb)
Örnek ekran görüntüsü: 14 saat sorgulamadan sonra ertesi güne bir randevu buldu.

Anlık iptal durumlarında hatta slot daha uzun süre boş kalsa bile MHRS'nin sistemi size boş slot için hatırlatma yapmıyor. Bu yüzden bu tür botlara yönelmek durumunda kalıyoruz maalesef.
