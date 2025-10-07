from models import Trade, BrokerageNote
from database import db_insert
from bn_base import format_br_date_to_db, resolve_auction_date, resolve_settlement_date

def trades(content: str):
    print('\n--------------')
    print('-- Negócios --')
    print('--------------\n')
    page_content = content
    is_infra = page_content.find('B3 RF') > -1 or page_content.find('7-BOVESPA') > -1
    page_lines = page_content.split('\n')
    for i, pl in enumerate(page_lines):
        if pl.find('B3 R') > -1 or pl.find('BOVESPA') > -1:  # quebra
            line_parts = pl.split(' ')
            line_parts_length = len(line_parts)
            pos_safe_ref = pl.find('VISTA')
            trade_price = line_parts[line_parts_length - 3] \
                .replace('.', '') \
                .replace(',', '.')
            # trade_type = 'day-trade' if line_parts[line_parts_length - 5] == 'D' else 'swing-trade'
            trade_quantity = line_parts[line_parts_length - 4]
            trade_date = format_br_date_to_db(resolve_auction_date(page_content))
            trade_ticker = pl[pos_safe_ref + 5:pl.find(' CI ')].strip()
            raw_operation = pl[pos_safe_ref - 4:pos_safe_ref].strip() # tem muitas falhas no layout, então obtem um conjunto de strings contendo C ou V
            trade_operation = '.'
            match raw_operation:
                case 'A C' | 'CIX' | 'DCO' | 'O C':
                    trade_operation = 'C'
                case 'A V' | 'VIX' | 'DVO' | 'O V':
                    trade_operation = 'V'
            print(
                trade_date,
                trade_ticker,
                trade_quantity,
                trade_price,
                trade_operation,
                '...',
                pl,
            )

            model = Trade(
                trad_date=trade_date,
                trad_oper=trade_operation,
                trad_type='swing-trade',
                trad_tick=trade_ticker,
                trad_qtty=trade_quantity,
                trad_valu=trade_price,
                trad_mark='asset',
                trad_brok='itau-i' if is_infra else 'itau',
            )
            db_insert(model)

def brokerage_notes(content: str):
    print('\n---------------------')
    print('-- Brokerage notes --')
    print('---------------------\n')
    page_content = content
    is_infra = page_content.find('B3 RF') > -1 or page_content.find('7-BOVESPA') > -1
    label_irrf = 'I.R.R.F. s/ operações, base R$ '
    label_irrf_v1 = 'I.R.R.F. s/ operações. Base R$ '
    label_irrf_v2 = 'I.R.R.F s/operações. Base R$ '
    items = {
        'brno_taxl_v1': 'Taxa de liquidação ', # nota antiga
        'brno_iss_v1': 'ISS(SÃO PAULO) ', # nota antiga
        'brno_clea_v1': 'Corretagem ', # nota antiga
        'brno_irrf_v1': label_irrf_v1, # nota antiga
        'brno_irrf_v2': label_irrf_v2, # nota antiga
        'brno_valu': 'Valor líquido das operações ',
        'brno_taxl': 'Taxa de liquidação/CCP ',
        'brno_taxr': 'Taxa de Registro ',
        'brno_emol': 'Emolumentos ',
        'brno_trat': 'Taxa de Transferência de Ativos ',
        'brno_clea': 'Clearing ',
        'brno_iss': 'ISS ( SÃO PAULO ) ',
        'brno_irrf': label_irrf,
    }
    values = {}
    for db_column, label in items.items():
        pos_label = page_content.find(label)
        pos_bl = page_content[pos_label:].find('\n')
        raw_line = page_content[pos_label:pos_label + pos_bl].strip()
        multiply = -1 if raw_line[-1:] == 'D' else 1
        value = (page_content[pos_label:pos_label + pos_bl]
                 .replace(label, '')
                 .replace(' D', '')
                 .replace(' C', '')
                 .replace('.', '')
                 .replace(',', '.')
                 )
        if label == label_irrf or label == label_irrf_v1 or label == label_irrf_v2:
            value_parts = value.split(' ')
            if len(value_parts) > 1: value = value_parts[1]
        if  db_column == 'brno_valu':
            value = float(value) * multiply
        print(db_column, '=', value)
        values[db_column] = value
    model = BrokerageNote(
        brno_date=format_br_date_to_db(resolve_auction_date(page_content)),
        brno_seda=format_br_date_to_db(resolve_settlement_date(page_content)),
        brno_brok='itau-i' if is_infra else 'itau',
        brno_valu=values['brno_valu'],
        brno_taxl=values['brno_taxl'] or values['brno_taxl_v1'],
        brno_taxr=values['brno_taxr'],
        brno_emol=values['brno_emol'],
        brno_trat=values['brno_trat'] or 0,
        brno_clea=values['brno_clea'] or values['brno_clea_v1'],
        brno_iss=values['brno_iss'] or values['brno_iss_v1'],
        brno_irrf=values['brno_irrf'] or values['brno_irrf_v1'] or values['brno_irrf_v2'] or 0,
    )
    db_insert(model)
