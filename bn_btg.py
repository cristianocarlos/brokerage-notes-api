from models import Trade, BrokerageNote
from database import db_insert
from bn_base import format_br_date_to_db, resolve_auction_date, resolve_settlement_date

def trades(content: str):
    print('\n--------------')
    print('-- Negócios --')
    print('--------------\n')
    page_content = content
    page_lines = page_content.split('\n')
    for i, pl in enumerate(page_lines):
        if pl.find('1-BOVESPA') > -1: # quebra
            line_parts = pl.split(' ')
            line_parts_length = len(line_parts)
            pos_oc = pl.find('OPCAO DE COMPRA')
            pos_ov = pl.find('OPCAO DE VENDA')
            pos_ec = pl.find('EXERC OPC COMPRA')
            pos_ev = pl.find('EXERC OPC VENDA')
            pos_v = pl.find('VISTA')
            trad_opti_exer=None
            if pos_oc > -1:
                trade_broker = 'btg-o'
                trade_market = 'option'
                trade_type = 'swing-trade'
                base_len = pos_oc + 15 + 7 # caracteres na string 7 do " 10/22 "
                trade_ticker = pl[base_len : base_len + 8].strip()
            elif pos_ov > -1:
                trade_broker = 'btg-o'
                trade_market = 'option'
                trade_type = 'swing-trade'
                base_len = pos_ov + 14 + 7
                trade_ticker = pl[base_len : base_len + 8].strip()
            elif pos_ec > -1:
                trade_broker = 'btg'
                trade_market = 'option'
                trade_type = 'auto'
                base_len = pos_ec + 17
                trad_opti_exer = pl[base_len : base_len + 9].strip()
                trade_ticker = trad_opti_exer[0:4]
            elif pos_ev > -1:
                trade_broker = 'btg'
                trade_market = 'option'
                trade_type = 'auto'
                base_len = pos_ev + 16
                trad_opti_exer = pl[base_len : base_len + 9].strip()
                trade_ticker = trad_opti_exer[0:4]
            else:
                trade_broker = 'btg'
                trade_market = 'asset'
                trade_type = 'swing-trade'
                base_len = pos_v + 5
                trade_ticker = pl[base_len : base_len + 7].strip()
                if trade_ticker.endswith('F'): trade_ticker = trade_ticker[0:-1] # elimina o F que indica fracionado
            trade_price = line_parts[line_parts_length - 3]\
                .replace('.', '')\
                .replace(',', '.')
            trade_type = 'day-trade' if line_parts[line_parts_length - 5] == 'D' else trade_type
            trade_quantity = line_parts[line_parts_length - 4]
            trade_date = format_br_date_to_db(resolve_auction_date(page_content))
            trade_ticker = trade_ticker.strip()
            if trade_ticker.endswith('F'): trade_ticker = trade_ticker[-1:] #
            print(
                trade_date,
                line_parts[1],
                trade_ticker,
                trade_type,
                trade_quantity,
                trade_price,
            )
            model = Trade(
                trad_date = trade_date,
                trad_oper = line_parts[1],
                trad_type = trade_type,
                trad_tick = trade_ticker,
                trad_qtty = trade_quantity,
                trad_valu = trade_price,
                trad_mark = trade_market,
                trad_brok = trade_broker,
                trad_opti_exer = trad_opti_exer,
            )
            db_insert(model)

def brokerage_notes(content: str):
    print('\n---------------------')
    print('-- Brokerage notes --')
    print('---------------------\n')
    page_content = content
    is_opcoes = page_content.find('OPCAO DE') > -1
    label_irrf = 'I.R.R.F. s/ operações, base R$ '
    items = {
        'brno_taxl_v1': 'Taxa de liquidação ', # nota antiga
        'brno_taxr_v1': 'Taxa de Registro ', # nota antiga
        'brno_iss_v1': 'ISS* (SÂO PAULO) ', # nota antiga
        'brno_valu': 'Valor líquido das operações ',
        'brno_taxl': 'Taxa de liquidação/CCP ',
        'brno_taxr': 'Taxa de registro ',
        'brno_emol': 'Emolumentos ',
        'brno_trat': 'Taxa de Transferencia de Ativos ',
        'brno_clea': 'Clearing ',
        'brno_iss': 'ISS* (SÃO PAULO - SP) ',
        'brno_irrf': label_irrf,
    }
    values = {}
    for db_column, label in items.items():
        pos_label = page_content.find(label)
        pos_bl = page_content[pos_label:].find('\n')
        raw_line = page_content[pos_label:pos_label + pos_bl].strip()
        multiply = -1 if raw_line[-1:] == 'D' else 1
        value = (raw_line
                 .replace(label, '')
                 .replace(' D', '')
                 .replace(' C', '')
                 .replace('.', '')
                 .replace(',', '.')
                 )
        if label == label_irrf:
            value_parts = value.split(' ')
            if len(value_parts) > 1: value = value_parts[1]
        if  db_column == 'brno_valu':
            value = float(value) * multiply
        print(db_column, '=', value)
        values[db_column] = value
    model = BrokerageNote(
        brno_date = format_br_date_to_db(resolve_auction_date(page_content)),
        brno_seda = format_br_date_to_db(resolve_settlement_date(page_content)),
        brno_brok = 'btg-o' if is_opcoes else 'btg',
        brno_valu = values['brno_valu'],
        brno_taxl = values['brno_taxl'] or values['brno_taxl_v1'],
        brno_taxr = values['brno_taxr'] or values['brno_taxr_v1'],
        brno_emol = values['brno_emol'],
        brno_trat = values['brno_trat'] or 0,
        brno_clea = values['brno_clea'],
        brno_iss = values['brno_iss'] or values['brno_iss_v1'],
        brno_irrf = values['brno_irrf'],
    )
    db_insert(model)
