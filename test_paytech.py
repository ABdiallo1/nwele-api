import requests

# Remplace par les clés visibles sur ton interface PayTech (image_cc5e7d.jpg)
API_KEY = "4708a871b0d511a24050685ff7abfab2e68c69032e1b3d2913647ef46ed656f2"
API_SECRET = "17cb57b72f679c40ab29eedfcd485bea81582adb770882a78525abfdc57e6784"

def tester_paytech_mali():
    url = "https://paytech.sn/api/payment/request-payment"
    
    headers = {
        "API_KEY": API_KEY,
        "API_SECRET": API_SECRET,
        "Content-Type": "application/json"
    }

    # Données pour une course de taxi à 500 FCFA
    payload = {
        "item_name": "Course Taxi Bamako",
        "item_price": "500",
        "currency": "XOF",
        "ref_command": "TAXI_MALI_101", # ID unique de la course
        "command_name": "Paiement Course Taxi",
        "env": "test", # Change en 'live' quand tu auras ton NIF
        "ipn_url": "https://nwele-api.onrender.com/api/paytech-webhook/",
        "success_url": "https://nwele-api.onrender.com/api/verifier-statut/",
        "cancel_url": "https://nwele-api.onrender.com/"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()

        if res_data.get('success') == 1:
            print("✅ SUCCÈS ! Lien généré :")
            print(res_data.get('redirect_url'))
        else:
            print(f"❌ ERREUR : {res_data.get('errors')}")
            
    except Exception as e:
        print(f"❌ ERREUR RÉSEAU : {e}")

tester_paytech_mali()