from requests_html import HTMLSession
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from os import getenv as env
import gasPrices
import exchangeRates

load_dotenv()

gas_website = "https://pacific.afn.mil/Gas-Prices/"
rates_website = f"https://v6.exchangerate-api.com/v6/{env('EXCHANGE_RATE_API')}/pair/USD/JPY"
chance_website = "https://exchange-chancecenter.com/"
lucky_website = "https://ameblo.jp/luckyexchangeltd/"

tables = {}
user = env('EMAIL')
password = env('PASSWORD')
recipients = env('RECIPIENTS').split(',')


def send_email():
    # Message header
    message = MIMEMultipart()
    # message['To'] = recipients
    # message['From'] = user
    message['Subject'] = 'Okinawa Updates'

    # HTML formatting for DataFrame to appear as table
    html = f"""\
    <html>
        <head><b> Okinawa Updates </b></head>
        <body>
        <br>
        <b>Yen Rate: </b> {jpy}
        <br><br>
        <b>Gas Prices on Base</b><br>
        {gas.to_html(index=False)}<br>
        <br>
        <b>Chance Exchange Rates</b><br>
        {chance_yen_rate}<br>
        {chance_dollar_rate}<br>
        <br>
        <b>Lucky Exchange Rates</b><br>
        {lucky_yen_rate}<br>
        {lucky_dollar_rate}<br>
        </body>
    </html>"""

    # Message body
    message_text = MIMEText(html, 'html')
    message.attach(message_text)

    # Establish secure GMail connection
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo('Gmail')
    server.starttls()

    # Login to GMail account
    server.login(user, password)

    # Send email
    server.sendmail(user, recipients, message.as_string())

    # End email server connection
    server.quit()


# Open HTML session
with HTMLSession() as session:
    gas_data = session.get(gas_website)
    rates_data = session.get(rates_website)
    chance = session.get(chance_website)
    lucky = session.get(lucky_website)

# Get central bank exchange rate
jpy = rates_data.json().get('conversion_rate') if rates_data.status_code == 200 else 0

# Get gas prices
gas = gasPrices.get_gas_prices(gas_data)
# Add JPY equivalent
prices = [round(float(price[1:]) * jpy, 3) for price in gas.get('Per Liter')]
gas.insert(3, 'JPY Per Liter', prices)

chance_yen_rate, chance_dollar_rate, lucky_yen_rate, lucky_dollar_rate = exchangeRates.exchange_rates(chance, lucky)

send_email()
