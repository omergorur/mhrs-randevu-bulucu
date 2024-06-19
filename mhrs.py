import os
import requests
import locale
import time
import datetime
import json
import winsound
from twilio.rest import Client

locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
GREEN = '\033[32m'
RESET = '\033[0m'
api = "https://prd.mhrs.gov.tr/api"
sleep_time = 30

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'tr-TR',
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Headers': 'Authorization,Content-Type, Accept, X-Requested-With, remember-me',
    'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Max-Age': '3600',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://mhrs.gov.tr',
    'Referer': 'https://mhrs.gov.tr/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def upper_tr(text):
    return text.replace("i", "İ").upper().strip()


def send_sms(message_body):
    with open("twilio_config.json") as f:
        value = json.load(f)

        if value['account_sid'] != '':
            client = Client(value['account_sid'], value['auth_token'])

            message = client.messages.create(
                body=message_body,
                from_=value['twilio_phone_number'],
                to=value['target_phone_number']
            )

            print(f"Mesaj SID: {message.sid}")


def login_request(tc, parola):
    json_data = {
        'kullaniciAdi': tc,
        'parola': parola,
        'islemKanali': 'VATANDAS_WEB',
        'girisTipi': 'PAROLA',
        'captchaKey': None,
    }

    response = requests.post(f'{api}/vatandas/login', headers=headers, json=json_data).json()

    if response['success']:
        print(f"HOŞGELDİN {response['data']['kullaniciAdi']} {response['data']['kullaniciSoyadi']}")
        return response['data']['jwt']
    else:
        print(response['errors'][0]['mesaj'])
        exit()


def login():
    print("Lütfen TC Kimlik Numaranızı ve https://mhrs.gov.tr/ şifresini giriniz. E-Devlet şifresi değil!\n")
    while True:
        tc = input("TC Kimlik Numarası: ")

        if len(tc) == 11 and tc.isdigit():
            break
        else:
            print("Geçerli bir TC Kimlik Numarası girmelisiniz!")

    while True:
        parola = input("MHRS Parolası: ")

        if not (8 <= len(parola) <= 16):
            print('Parolanız en az 8, en fazla 16 karakter olmalıdır!')
        else:
            break

    return login_request(tc, parola)


def get_api_data(endpoint):
    response = requests.get(f'{api}/{endpoint}', headers=headers)
    response.raise_for_status()
    return response.json()


def display_and_select(items, title, start):
    cls()
    print(f"\n{'#' * 40}")
    print(f"####### {title.upper()} #######")
    print(f"{'#' * 40}\n")

    existing_dicts = set()
    filtered_list = []
    for d in items:
        if (d['value']) not in existing_dicts:
            existing_dicts.add((d['value']))
            filtered_list.append(d)

    for index, item in enumerate(filtered_list, start=start):
            print(f"{index} - {upper_tr(item['text'])}")
    print("")

    while True:
        selected_index = input(f"{title} numarası girin: ")
        if selected_index.isdigit() and start <= int(selected_index) < len(filtered_list) + start:
            return filtered_list[int(selected_index) - start]
        else:
            print(f"Hata: Lütfen {start} ile {len(filtered_list)} arasında bir numara giriniz.")


def select_city():
    cities = sorted(get_api_data('yonetim/genel/il/selectinput-tree'), key=lambda x: x['value'])
    selected_city = display_and_select(cities, 'İl', 1)
    return selected_city['value'], selected_city['text']


def select_district(city_id):
    districts = sorted(get_api_data(f'yonetim/genel/ilce/selectinput/{city_id}'),
                       key=lambda x: locale.strxfrm(x['text']))
    districts.insert(0, {"value": "-1", "text": "FARK ETMEZ"})
    selected_district = display_and_select(districts, 'İlçe', 0)
    return selected_district['value']


def select_branch(city_id, district_id):
    endpoint = f'kurum/kurum/kurum-klinik/il/{city_id}/ilce/{district_id}/kurum/-1/aksiyon/200/select-input'
    branches = sorted(get_api_data(endpoint)['data'], key=lambda x: locale.strxfrm(x['text']))
    selected_branch = display_and_select(branches, 'Klinik', 1)
    return selected_branch['value']


def select_hospital(city_id, district_id, branch_id):
    endpoint = f'kurum/kurum/kurum-klinik/il/{city_id}/ilce/{district_id}/kurum/-1/klinik/{branch_id}/ana-kurum/select-input'
    hospitals = sorted(get_api_data(endpoint)['data'], key=lambda x: locale.strxfrm(x['text']))
    hospitals.insert(0, {"value": "-1", "text": "FARK ETMEZ"})
    selected_hospital = display_and_select(hospitals, 'Hastane', 0)
    return selected_hospital['value']


def select_destination(city_id, district_id, hospital_id, branch_id):
    endpoint = f'kurum/kurum/muayene-yeri/ana-kurum/{hospital_id}/kurum/-1/klinik/{branch_id}/select-input'
    destinations = sorted(get_api_data(endpoint)['data'], key=lambda x: locale.strxfrm(x['text']))
    destinations.insert(0, {"value": "-1", "text": "FARK ETMEZ"})
    selected_destination = display_and_select(destinations, 'Muayene yeri', 0)
    return selected_destination['value']


def select_doctor(city_id, district_id, hospital_id, branch_id, destination_id):
    endpoint = f'kurum/hekim/hekim-klinik/hekim-select-input/anakurum/{hospital_id}/kurum/-1/klinik/{branch_id}'
    doctors = sorted(get_api_data(endpoint)['data'], key=lambda x: locale.strxfrm(x['text']))
    doctors.insert(0, {"value": "-1", "text": "FARK ETMEZ"})
    selected_doctor = display_and_select(doctors, 'Doktor', 0)
    return selected_doctor['value']


def search_appointment(city_id, district_id, branch_id, hospital_id, destination_id, doctor_id):
    cls()
    data = {
        'aksiyonId': '200',
        'mhrsHekimId': doctor_id,
        'mhrsIlId': city_id,
        'mhrsIlceId': district_id,
        'mhrsKlinikId': branch_id,
        'mhrsKurumId': hospital_id,
        'muayeneYeriId': destination_id,
        'tumRandevular': False,
        'ekRandevu': True,
        'randevuZamaniList': [],
    }

    interval = sleep_time
    while True:
        try:
            response = requests.post(f'{api}/kurum-rss/randevu/slot-sorgulama/arama',
                                     headers=headers,
                                     json=data)
            if response.status_code == 200:
                slots = response.json()
                break
            else:
                print(f"Uygun randevu bulunamadı - {datetime.datetime.now().strftime("%H:%M:%S")}")
        except requests.RequestException as e:
            print(f"Bir hata oluştu: {e}. {interval} saniye sonra tekrar denenecek.")

        time.sleep(interval)

    for slot in slots['data']['hastane']:
        slot_date = datetime.datetime.fromisoformat(slot['baslangicZamani'])
        slot_date = slot_date.strftime("%d.%m.%Y %H:%M")
        print(
            f"{GREEN}[ {slot['bosKapasite']} Randevu Bulundu ]{RESET} \t {slot['hekim']['ad']} {slot['hekim']['soyad']} \t En yakın tarih: {slot_date}")
    print("")
    print("MHRS'nin web sitesinden ya da telefon uygulamasından girip randevunuzu alabilirsiniz.")
    winsound.PlaySound('done.wav', winsound.SND_FILENAME)
    send_sms("Aradığınız kriterde uygun randevu bulundu. MHRS'ye girip alabilirsiniz.")


def main():
    cls()
    token = login()
    headers['Authorization'] = "Bearer " + token

    city_id, city_name = select_city()
    district_id = select_district(city_id)
    branch_id = select_branch(city_id, district_id)
    hospital_id = select_hospital(city_id, district_id, branch_id)
    destination_id = select_destination(city_id, district_id, hospital_id, branch_id)
    doctor_id = select_doctor(city_id, district_id, hospital_id, branch_id, destination_id)

    search_appointment(city_id, district_id, branch_id, hospital_id, destination_id, doctor_id)


if __name__ == "__main__":
    main()
