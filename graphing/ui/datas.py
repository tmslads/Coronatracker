import logging

from telegram import InlineKeyboardButton, Update
from telegram.ext import CallbackContext

entry_msg = "Welcome to the graph selector. Choose your option by selecting one of the buttons below:\n\n" \
            "World - World coronavirus graphs\n" \
            "Country - View graphs per country."

selection_msg = "Selection: *()*\.\nChoose the which metric to display from the below buttons:"

country_msg = "Select your country from the buttons below\.\n\nCurrent page: *()/6*"

entry_buttons = [[InlineKeyboardButton(text="The World", callback_data="OWID_WRL")],
                 [InlineKeyboardButton(text="Country list", callback_data="country")]]

graph_buttons = [[InlineKeyboardButton(text="<< Back", callback_data='back')],
                 [InlineKeyboardButton(text="Total cases", callback_data="total_cases"),
                  InlineKeyboardButton(text="New cases", callback_data="new_cases")],
                 [InlineKeyboardButton(text="Total deaths", callback_data="total_deaths"),
                  InlineKeyboardButton(text="New deaths", callback_data="new_deaths")]]

trend_buttons = [[InlineKeyboardButton(text="<< Back", callback_data='back_trends'),
                 InlineKeyboardButton(text="Log scale ", callback_data="log")]]

user_selection = {'country': None, 'trend': None, 'log': False}  # This will be used to generate graph

iso_codes = {'AFG': 'Afghanistan', 'ALB': 'Albania', 'DZA': 'Algeria', 'AGO': 'Angola', 'ARG': 'Argentina',
             'ARM': 'Armenia', 'AUS': 'Australia', 'AUT': 'Austria', 'AZE': 'Azerbaijan', 'BHS': 'Bahamas',
             'BHR': 'Bahrain', 'BGD': 'Bangladesh', 'BRB': 'Barbados', 'BLR': 'Belarus', 'BEL': 'Belgium',
             'BLZ': 'Belize', 'BEN': 'Benin', 'BMU': 'Bermuda', 'BTN': 'Bhutan', 'BOL': 'Bolivia',
             'BIH': 'Bosnia and Herzegovina', 'BWA': 'Botswana', 'BRA': 'Brazil', 'BRN': 'Brunei', 'BGR': 'Bulgaria',
             'BFA': 'Burkina Faso', 'BDI': 'Burundi', 'KHM': 'Cambodia', 'CMR': 'Cameroon', 'CAN': 'Canada',
             'CAF': 'Central African Republic', 'TCD': 'Chad', 'CHL': 'Chile', 'CHN': 'China', 'COL': 'Colombia',
             'COM': 'Comoros', 'COG': 'Congo', 'CRI': 'Costa Rica', 'HRV': 'Croatia', 'CUB': 'Cuba', 'CYP': 'Cyprus',
             'CZE': 'Czech Republic', 'COD': 'Democratic Republic of Congo', 'DNK': 'Denmark', 'DJI': 'Djibouti',
             'DMA': 'Dominica', 'DOM': 'Dominican Republic', 'ECU': 'Ecuador', 'EGY': 'Egypt', 'SLV': 'El Salvador',
             'GNQ': 'Equatorial Guinea', 'ERI': 'Eritrea', 'EST': 'Estonia', 'ETH': 'Ethiopia', 'FIN': 'Finland',
             'FRA': 'France', 'GAB': 'Gabon', 'GMB': 'Gambia', 'GEO': 'Georgia', 'DEU': 'Germany', 'GHA': 'Ghana',
             'GIB': 'Gibraltar', 'GRC': 'Greece', 'GRL': 'Greenland', 'GRD': 'Grenada', 'GUM': 'Guam',
             'GTM': 'Guatemala', 'GIN': 'Guinea', 'HTI': 'Haiti', 'HND': 'Honduras', 'HKG': 'Hong Kong',
             'HUN': 'Hungary', 'ISL': 'Iceland', 'IND': 'India', 'IDN': 'Indonesia', 'IRN': 'Iran', 'IRQ': 'Iraq',
             'IRL': 'Ireland', 'ISR': 'Israel', 'ITA': 'Italy', 'JAM': 'Jamaica', 'JPN': 'Japan', 'JOR': 'Jordan',
             'KAZ': 'Kazakhstan', 'KEN': 'Kenya', 'OWID_KOS': 'Kosovo', 'KWT': 'Kuwait', 'KGZ': 'Kyrgyzstan',
             'LAO': 'Laos', 'LVA': 'Latvia', 'LBN': 'Lebanon', 'LBR': 'Liberia', 'LBY': 'Libya', 'LIE': 'Liechtenstein',
             'LTU': 'Lithuania', 'LUX': 'Luxembourg', 'MKD': 'Macedonia', 'MDG': 'Madagascar', 'MWI': 'Malawi',
             'MYS': 'Malaysia', 'MDV': 'Maldives', 'MLI': 'Mali', 'MLT': 'Malta', 'MRT': 'Mauritania',
             'MUS': 'Mauritius', 'MEX': 'Mexico', 'MDA': 'Moldova', 'MCO': 'Monaco', 'MNG': 'Mongolia',
             'MNE': 'Montenegro', 'MAR': 'Morocco', 'MOZ': 'Mozambique', 'MMR': 'Myanmar', 'NAM': 'Namibia',
             'NPL': 'Nepal', 'NLD': 'Netherlands', 'NCL': 'New Caledonia', 'NZL': 'New Zealand', 'NIC': 'Nicaragua',
             'NER': 'Niger', 'NGA': 'Nigeria', 'NOR': 'Norway', 'OMN': 'Oman', 'PAK': 'Pakistan', 'PSE': 'Palestine',
             'PAN': 'Panama', 'PNG': 'Papua New Guinea', 'PRY': 'Paraguay', 'PER': 'Peru', 'PHL': 'Philippines',
             'POL': 'Poland', 'PRT': 'Portugal', 'PRI': 'Puerto Rico', 'QAT': 'Qatar', 'ROU': 'Romania',
             'RUS': 'Russia', 'SAU': 'Saudi Arabia', 'SEN': 'Senegal', 'SRB': 'Serbia', 'SLE': 'Sierra Leone',
             'SGP': 'Singapore', 'SVK': 'Slovakia', 'SVN': 'Slovenia', 'SOM': 'Somalia', 'ZAF': 'South Africa',
             'KOR': 'South Korea', 'SSD': 'South Sudan', 'ESP': 'Spain', 'LKA': 'Sri Lanka', 'SDN': 'Sudan',
             'SWZ': 'Swaziland', 'SWE': 'Sweden', 'CHE': 'Switzerland', 'SYR': 'Syria', 'TWN': 'Taiwan',
             'TJK': 'Tajikistan', 'TZA': 'Tanzania', 'THA': 'Thailand', 'TLS': 'Timor', 'TGO': 'Togo',
             'TTO': 'Trinidad and Tobago', 'TUN': 'Tunisia', 'TUR': 'Turkey', 'UGA': 'Uganda', 'UKR': 'Ukraine',
             'ARE': 'United Arab Emirates', 'GBR': 'United Kingdom', 'USA': 'United States', 'URY': 'Uruguay',
             'UZB': 'Uzbekistan', 'VEN': 'Venezuela', 'VNM': 'Vietnam', 'ESH': 'Western Sahara', 'YEM': 'Yemen',
             'ZMB': 'Zambia', 'ZWE': 'Zimbabwe'}

MAIN_SELECTOR, COUNTRY_SELECTOR, TREND_SELECTOR, GRAPH_OPTIONS = range(0, 4)


def trend_to_human_readable(trend: str) -> str:
    return trend.replace('_', ' ').upper()


def remove_user_data(update: Update, context: CallbackContext) -> None:
    # Commented out in case we need to delete specific items from user_data only-
    # for data in {'covid_country', 'covid_trend_pic', 'log', 'trend_data', 'country_list', 'country_page'}:
    #     del context.user_data[data]
    #     logging.info(f"Deleted {data} for {update.effective_user.full_name}!\n")
    context.user_data.clear()
    logging.info(f"All data for {update.effective_user.full_name} is deleted!\n\n")


def remove_all_user_data(context: CallbackContext) -> None:
    # print(context.dispatcher.user_data.values())
    for user in context.dispatcher.user_data.values():
        user.clear()
    logging.info(f"All data for all users is deleted!\n\n")


def generate_country_list():
    country_pages = []
    country_list = []
    col = []

    rows = 0
    columns = 0

    # Makes one page-
    # country_list = [[InlineKeyboardButton(text=country, callback_data=iso) for (country, iso), col in
    #                  zip(iso_codes.items(), range(columns))] for row in range(rows)]

    # Makes all pages-
    for iso_code, country in iso_codes.items():
        if rows < 10:
            if columns < 2:
                col.append(InlineKeyboardButton(text=country, callback_data=iso_code))
                columns += 1
            else:
                country_list.append(col)
                columns = 0
                rows += 1
                col = []
        else:
            rows = 0
            columns = 0
            country_pages.append(country_list)
            country_list = []
    else:
        country_pages.append(country_list)

    return country_pages


# def verify_list(a=generate_country_list):
#     l = a()
#     for element in l:
#         for sub in element:
#             for sub_2 in sub:
#                 print(sub_2.text)
