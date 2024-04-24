def get_gas_prices(gas_data):
    """ Parse the Gas Prices website and find values for Okinawa. """

    import pandas as pd
    from bs4 import BeautifulSoup
    from io import StringIO
    
    tables = None
    if gas_data.status_code == 200:
        content = gas_data.text
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find_all('table')[-1]
        tables = pd.read_html(StringIO(str(table)))
    else:
        print('Failed to get the website.')

    gas_prices = tables[0].get('Okinawa') if tables is not None else None

    return gas_prices
