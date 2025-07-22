from requests_html import HTMLSession
from old import accessSecretVersion, exchangeRates, gasPrices
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

def send_email():
    _user = accessSecretVersion.access_secret_version("EMAIL")
    _password = accessSecretVersion.access_secret_version("PASSWORD")
    _recipients = accessSecretVersion.access_secret_version("RECIPIENTS")
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
    server.login(_user, _password)

    # Send email
    server.sendmail(
    _user, 
    _recipients.split(', '), 
    message.as_string()
    )
    
    # End email server connection
    del _user, _password, _recipients
    server.quit()


# Open HTML session
with HTMLSession() as session:
    gas_data = session.get(accessSecretVersion.access_secret_version("BASE_GAS_PRICES"))
    rates_data = session.get(accessSecretVersion.access_secret_version("EXCHANGE_RATE_SITE"))
    chance = session.get(accessSecretVersion.access_secret_version("CHANCE_EXCHANGE"))
    lucky = session.get(accessSecretVersion.access_secret_version("LUCKY_EXCHANGE"))

# Get central bank exchange rate
jpy = rates_data.json().get('conversion_rate') if rates_data.status_code == 200 else 0

# Get gas prices
gas = gasPrices.get_gas_prices(gas_data)

# Add JPY equivalent
prices = [round(float(price[1:]) * jpy, 3) for price in gas.get('Per Liter')]
gas.insert(3, 'JPY Per Liter', prices)

chance_yen_rate, chance_dollar_rate, lucky_yen_rate, lucky_dollar_rate = exchangeRates.exchange_rates(chance, lucky)

send_email()
