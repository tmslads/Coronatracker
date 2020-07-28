from telegram import InlineKeyboardButton

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
