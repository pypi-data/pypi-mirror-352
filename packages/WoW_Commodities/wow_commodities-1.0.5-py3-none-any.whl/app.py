import pandas as pd
import argparse
import os
import sys
from src.get_commodities import get_commodities
from src.get_token import get_token
from src.region_locale import region_locale

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='wow-commodities',
        description=('Retrieve auction house commodities data from '
                     'a selected region.'),
        epilog=('This application comes with no warrant of any kind. '
        'Use at your own risk.')
    )
    parser.add_argument('id', help=('Client ID from Blizzard API Access.'),
                    type=str)
    parser.add_argument('secret', help=('Client Secret from Blizzard '
                                        'API Access.'),
                    type=str)
    parser.add_argument('path', help=('Path of file to save the data in '
                    '(e.g: C:\\User\\username\\Downloads\\data.csv.xz).'),
                    type=str)
    parser.add_argument('-r','--region',
                        help='Region to retrieve data from. Default to us.',
                        choices=['us', 'eu', 'kr', 'tw', 'cn'],
                        default='us', type=str)
    parser.add_argument('-l','--locale',
                        help=('Locale for the specified region. '
                              'Default to en_US.'),
                        choices=[
                            'en_US', 'es_MX', 'pt_BR', 'en_GB',
                            'es_ES', 'fr_FR', 'ru_RU', 'de_DE',
                            'pt_PT', 'it_IT', 'ko_KR', 'zh_TW',
                            'zh_CN'],
                        default='en_US',
                    type=str)
    args = parser.parse_args()

    if args.locale not in region_locale[args.region]:
        sys.exit(f'Region {args.region} does not accept {args.locale} locale. '
             f'Please choose between {region_locale[args.region]}.')
    
    if args.region == 'cn':
        URL = 'https://gateway.battlenet.com.cn/data/wow/'
    else:
        URL = f'https://{args.region}.api.blizzard.com/data/wow/'
    LOCALE: str = f'{args.locale}'
    TOKEN: str = get_token(args.id, args.secret, args.region)

    if os.path.splitext(args.path)[1] != 'xz':
        args.path += ".xz"

    data = get_commodities(URL, LOCALE, TOKEN, args.path)

    if data:
        id: list[int] = []
        item: list[int] = []
        quantity: list[int] = []
        unit_price: list[int] = []
        time_left: list[str] = []
        for i in range(len(data['auctions'])):
            id.append(data['auctions'][i]['id'])
            item.append(data['auctions'][i]['item']['id'])
            quantity.append(data['auctions'][i]['quantity'])
            unit_price.append(data['auctions'][i]['unit_price'])
            time_left.append(data['auctions'][i]['time_left'])

        try:
            pd.DataFrame(
                {'ID': id,
                'Item': item,
                'Quantity': quantity,
                'Unit Price': unit_price,
                'Time Left': time_left}
            ).to_csv(args.path, index=False)
        except PermissionError:
            sys.exit('Cannot save file. Permission denied.')

if __name__ == "__main__":
    main()
