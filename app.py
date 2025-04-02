from flask import Flask, render_template, request, redirect, url_for
import requests
import random
import string
from bs4 import BeautifulSoup

app = Flask(__name__)

def generationLink(stringLength):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        number = request.form['number']
        pwd = request.form['password']
        num = request.form['gift_number']

        with requests.Session() as req:
            url = f'https://web.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/auth?client_id=website&redirect_uri=https%3A%2F%2Fweb.vodafone.com.eg%2Far%2FKClogin&state=286d1217-db14-4846-86c1-9539beea01ed&response_mode=query&response_type=code&scope=openid&nonce={generationLink(10)}'
            responsePageLogin = req.get(url)
            soup = BeautifulSoup(responsePageLogin.content, 'html.parser')
            getUrlAction = soup.find('form').get('action')
            headerRequest = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0'
            }
            formData = {
                'username': number,
                'password': pwd
            }
            sendUserData = req.post(getUrlAction, headers=headerRequest, data=formData)
            checkRegistry = sendUserData.url
            if 'KClogin' in checkRegistry:
                code = checkRegistry.split('code=')[1]
                formDataAccessToken = {
                    'code': code,
                    'grant_type': 'authorization_code',
                    'client_id': 'website',
                    'redirect_uri': 'https://web.vodafone.com.eg/ar/KClogin'
                }
                sendDataAccessToken = req.post('https://web.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token', headers=headerRequest, data=formDataAccessToken)
                access_token = sendDataAccessToken.json().get('access_token')

                # إرسال الطلب
                url = 'https://web.vodafone.com.eg/services/dxl/ramadanpromo/promotion'
                hd = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0'
                }
                data = '{"@type":"Promo","channel":{"id":"4"},"context":{"type":"RamdanCardDedication"},"pattern":[{"characteristics":[{"name":"BMsisdn","value":"2%s"}]}]}' % num
                r = requests.post(url, headers=hd, data=data).text
                if r == "":
                    return "Done Send your Order"
                else:
                    return "Error: Try Again Later"
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)