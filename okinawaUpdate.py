from requests_html import HTMLSession
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from os import getenv as env
from datetime import date
import gasPrices
import exchangeRates

load_dotenv()

gas_website = env("BASE_GAS_PRICES")
rates_website = env("EXCHANGE_RATES")
chance_website = env("CHANCE_EXCHANGE")
lucky_website = env("LUCKY_EXCHANGE")

tables = {}
user = env("EMAIL")
password = env("PASSWORD")
recipients = env("RECIPIENTS").split(',')


def send_email():
    message = MIMEMultipart()
    message['From'] = 'Okinawa Update'
    message['Subject'] = f'Okinawa Update {date.today()}'

    # HTML formatting for DataFrame to appear as table
    html = f"""\
    <html>
        <body>
        <h1>Okinawa Updates</h1>
        
        <b>Yen Rate: </b> {jpy}
        
        <h3>Gas Prices on Base</h3>
        {gas.to_html(index=False)}
        
        <h3><u>Chance Exchange Rates</u></h3>
        ＄→￥: {chance_yen_rate}<br>
        ￥→＄: {chance_dollar_rate}
        
        <h3><u>Lucky Exchange Rates</u></h3>
        ＄→￥: {lucky_yen_rate}<br>
        ￥→＄: {lucky_dollar_rate}
        </body>
    </html>"""

    # Message body
    message_text = MIMEText(html, 'html')
    message.attach(message_text)

    # Establish secure GMail connection
    server = SMTP('smtp.gmail.com:587')
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
