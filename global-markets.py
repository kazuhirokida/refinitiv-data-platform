import refinitiv.dataplatform as rdp
import os
import pandas as pd
import requests
from datetime import datetime, timedelta

rdp.open_platform_session(
    os.environ.get('EIKON_API_KEY'), 
    rdp.GrantPassword(
        os.environ.get('EIKON_LOGIN_ID'), 
        os.environ.get('EIKON_LOGIN_PASS')
    )
)

equities = ['.N225','.DJI','.STOXX','.SSEC','.VIX']

currencies = ['JPY=','EURJPY=','CNY=']

treasuries = ['JP10YT=RR','US10YT=RR']

commodities = ['CLc1','GCv1']

df = pd.DataFrame()
for equity in equities:
  daily = rdp.get_historical_price_summaries(
      universe = equity, 
      interval = rdp.Intervals.DAILY,
      count=30,
      fields=['TRDPRC_1']).rename(columns={'TRDPRC_1':equity}).astype(float)
  latest = rdp.get_historical_price_summaries(
      universe = equity, 
      interval = rdp.Intervals.FIVE_MINUTES,
      count=1,
      fields=['TRDPRC_1']).rename(columns={'TRDPRC_1':equity}).astype(float)
  latest.index = latest.index.date.astype('datetime64[ns]')
  data = pd.concat([daily,latest]).rename_axis('Date').reset_index().drop_duplicates()

  change = data.diff()[equity].iloc[-1]

  if change > 0:
    direction = '↑'
  elif change < 0:
    direction = '↓'
  else:
    direction = '→'

  row = pd.DataFrame([{'Date':direction, equity:abs(change)}])

  data.Date = data.Date.dt.strftime('%Y/%m/%d')

  df = pd.concat([df,pd.concat([row,data.sort_values('Date',ascending=False)],ignore_index=True)],axis=1)

for currency in ['JPY=','EURJPY=']:
  daily = rdp.get_historical_price_summaries(
      universe = currency, 
      interval = rdp.Intervals.DAILY,
      count=30,
      fields=['BID']).rename(columns={'BID':currency}).astype(float)
  latest = rdp.get_historical_price_summaries(
      universe = currency, 
      interval = rdp.Intervals.FIVE_MINUTES,
      count=1,
      fields=['BID']).rename(columns={'BID':currency}).astype(float)
  latest.index = latest.index.date.astype('datetime64[ns]')
  data = pd.concat([daily,latest]).rename_axis('Date').reset_index().drop_duplicates()

  change = data.diff()[currency].iloc[-1]

  if change > 0:
    direction = '↓円安'
  elif change < 0:
    direction = '↑円高'
  else:
    direction = '→'

  row = pd.DataFrame([{'Date':direction, currency:abs(change)}])

  data.Date = data.Date.dt.strftime('%Y/%m/%d')

  df = pd.concat([df,pd.concat([row,data.sort_values('Date',ascending=False)],ignore_index=True)],axis=1)

daily = rdp.get_historical_price_summaries(
    universe = 'CNY=', 
    interval = rdp.Intervals.DAILY,
    count=30,
    fields=['BID']).rename(columns={'BID':'CNY='}).astype(float)
latest = rdp.get_historical_price_summaries(
    universe = 'CNY=', 
    interval = rdp.Intervals.FIVE_MINUTES,
    count=1,
    fields=['BID']).rename(columns={'BID':'CNY='}).astype(float)
latest.index = latest.index.date.astype('datetime64[ns]')
data = pd.concat([daily,latest]).rename_axis('Date').reset_index().drop_duplicates()

change = data.diff()['CNY='].iloc[-1]

if change > 0:
  direction = '↓元安'
elif change < 0:
  direction = '↑元高'
else:
  direction = '→'

row = pd.DataFrame([{'Date':direction, 'CNY=':abs(change)}])

data.Date = data.Date.dt.strftime('%Y/%m/%d')

df = pd.concat([df,pd.concat([row,data.sort_values('Date',ascending=False)],ignore_index=True)],axis=1)

for treasury in treasuries:
  daily = rdp.get_historical_price_summaries(
      universe = treasury, 
      interval = rdp.Intervals.DAILY,
      count=30,
      fields=['B_YLD_1']).rename(columns={'B_YLD_1':treasury}).astype(float)
  latest = rdp.get_historical_price_summaries(
      universe = treasury, 
      interval = rdp.Intervals.FIVE_MINUTES,
      count=1,
      fields=['BID_YIELD']).rename(columns={'BID_YIELD':treasury}).astype(float)
  latest.index = latest.index.date.astype('datetime64[ns]')
  data = pd.concat([daily,latest]).rename_axis('Date').reset_index().drop_duplicates()

  change = data.diff()[treasury].iloc[-1]

  if change > 0:
    direction = '↑'
  elif change < 0:
    direction = '↓'
  else:
    direction = '→'

  row = pd.DataFrame([{'Date':direction, treasury:abs(change)}])

  data.Date = data.Date.dt.strftime('%Y/%m/%d')

  df = pd.concat([df,pd.concat([row,data.sort_values('Date',ascending=False)],ignore_index=True)],axis=1)

for commodity in commodities:
  daily = rdp.get_historical_price_summaries(
      universe = commodity, 
      interval = rdp.Intervals.DAILY,
      count=30,
      fields=['TRDPRC_1']).rename(columns={'TRDPRC_1':commodity}).astype(float)
  latest = rdp.get_historical_price_summaries(
      universe = commodity, 
      interval = rdp.Intervals.FIVE_MINUTES,
      count=1,
      fields=['TRDPRC_1']).rename(columns={'TRDPRC_1':commodity}).astype(float)
  latest.index = latest.index.date.astype('datetime64[ns]')
  data = pd.concat([daily,latest]).rename_axis('Date').reset_index().drop_duplicates()

  change = data.diff()[commodity].iloc[-1]


  if change > 0:
    direction = '↑'
  elif change < 0:
    direction = '↓'
  else:
    direction = '→'

  row = pd.DataFrame([{'Date':direction, commodity:abs(change)}])

  data.Date = data.Date.dt.strftime('%Y/%m/%d')

  df = pd.concat([df,pd.concat([row,data.sort_values('Date',ascending=False)],ignore_index=True)],axis=1)

df = df.iloc[:31]

dic = {
    '.N225':'日経平均',
    '.DJI':'NYダウ',
    '.STOXX':'欧州（ストックス600）',
    '.SSEC':'中国（上海総合）',
    '.VIX':'VIX指数（米国株の予想変動率）',
    'JPY=':'ドル/円',
    'EURJPY=':'ユーロ/円',
    'CNY=':'ドル/元',
    'JP10YT=RR':'日本',
    'US10YT=RR':'米国',
    'CLc1':'原油（WTI）',
    'GCv1':'金（米先物）',
    'Date':''
    }

df.columns = df.columns.map(dic)

df.to_csv('data/'+datetime.today().strftime('%Y%m%d')+'_Global_Markets_Update.csv',index=False,encoding='utf-8-sig',lineterminator='\r\n')

response = requests.post(
        'https://api.mailgun.net/v3/mg.dataeditor.work/messages',
        auth=('api',os.environ.get('MAILGUN_API_KEY')),
        files=[('attachment',open('data/'+datetime.today().strftime('%Y%m%d')+'_Global_Markets_Update.csv','rb'))],
        data={'from':os.environ.get('EMAIL_SENDER'),
              'to':[os.environ.get('EMAIL_RECIPIENT1'),
                    os.environ.get('EMAIL_RECIPIENT2'),
                    os.environ.get('EMAIL_RECIPIENT3'),
                    os.environ.get('EMAIL_RECIPIENT4'),
                    os.environ.get('EMAIL_RECIPIENT5'),
                    os.environ.get('EMAIL_RECIPIENT6'),
                    os.environ.get('EMAIL_RECIPIENT7'),
                    os.environ.get('EMAIL_RECIPIENT8'),
                    os.environ.get('EMAIL_RECIPIENT9'),
                    os.environ.get('EMAIL_RECIPIENT10'),
                    os.environ.get('EMAIL_RECIPIENT11'),
                    os.environ.get('EMAIL_RECIPIENT12'),
                    os.environ.get('EMAIL_RECIPIENT13'),
                    os.environ.get('EMAIL_RECIPIENT14'),
                    os.environ.get('EMAIL_RECIPIENT15'),
                    os.environ.get('EMAIL_RECIPIENT16'),
                    os.environ.get('EMAIL_RECIPIENT17'),
                    os.environ.get('EMAIL_RECIPIENT18'),
                    os.environ.get('EMAIL_RECIPIENT19'),
                    os.environ.get('EMAIL_RECIPIENT20')],
              'subject': 'Global Markets Update '+datetime.today().strftime('%Y-%m-%d'),
              'text': 'Updated at '+(datetime.today() + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')+'JST'})

rdp.close_session()
