from models import Trade, BrokerageNote
from database import db_insert
from bn_base import format_us_date_to_db, resolve_auction_date, resolve_settlement_date

def resolve_trade_rows(content):
    trade_rows = []
    page_lines = content.split('\n')
    for i, pl in enumerate(page_lines):
        if pl.find('Principal Amount') > -1:  # quebra
            prev_pl = (page_lines[i - 1]
                       .replace(' Riskless Principal', '')
                       .replace(' Principal', '')
                       .replace(' Agency', '')
                       )
            line_parts = prev_pl.split(' ')  # a linha anterior a quebra é o registro do trade
            line_parts_length = len(line_parts)
            operation = line_parts[line_parts_length - 7]
            trade = {
                'ticker': line_parts[0],
                'operation': 'C' if operation == 'Buy' else 'V',
                'quantity': float(line_parts[line_parts_length - 4]),
                'price': float(line_parts[line_parts_length - 3]),
            }
            trade_rows.append(trade)
            # print(trade, '...', prev_pl)
    return trade_rows

def trades(content: str):
    print('\n--------------')
    print('-- Negócios --')
    print('--------------\n')
    trade_rows = resolve_trade_rows(content)
    trade_date = format_us_date_to_db(resolve_auction_date(content))
    for trade_data in trade_rows:
        trade_quantity = trade_data.get('quantity') * -1 if trade_data.get('quantity') < 0 else trade_data.get('quantity'), # na venda a quantidade vem negativa na nota
        print(
            trade_date,
            trade_data.get('ticker'),
            trade_data.get('operation'),
            trade_quantity,
            trade_data.get('price'),
        )
        model = Trade(
            trad_date=trade_date,
            trad_oper=trade_data.get('operation'),
            trad_type='swing-trade',
            trad_tick=trade_data.get('ticker'),
            trad_qtty=trade_quantity,
            trad_valu=trade_data.get('price'),
            trad_mark='asset',
            trad_brok='dw',
        )
        db_insert(model)

def brokerage_notes(content: str):
    print('\n---------------------')
    print('-- Brokerage notes --')
    print('---------------------\n')
    trade_rows = resolve_trade_rows(content)
    total_value = 0
    for trade_data in trade_rows:
        total_value += trade_data.get('quantity') * -1 * trade_data.get('price')
    auction_date = format_us_date_to_db(resolve_auction_date(content))
    settlement_date = format_us_date_to_db(resolve_settlement_date(content))
    print(
        auction_date,
        settlement_date,
        total_value,
    )
    model = BrokerageNote(
        brno_date=format_us_date_to_db(resolve_auction_date(content)),
        brno_seda=format_us_date_to_db(resolve_settlement_date(content)),
        brno_brok='dw',
        brno_valu=total_value,
    )
    db_insert(model)