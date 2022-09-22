import refinitiv.dataplatform as rdp
import pandas as pd
import requests
from datetime import datetime, timedelta

rdp.open_platform_session(
    EIKON_API_KEY, 
    rdp.GrantPassword(
        EIKON_LOGIN_ID, 
        EIKON_LOGIN_PASS
    )
)

equities = ['.N225','.DJI','.STOXX','.SSEC','.VIX']

currencies = ['JPY=','EURJPY=','CNY=']

treasuries = ['JP10YT=RR','US10YT=RR']

commodities = ['CLc1','GCv1']

df = pd.DataFrame()
for equity in equities:
  data = rdp.get_historical_price_summaries(
      universe = equity, 
      interval = rdp.Intervals.DAILY,
      count=30,
      fields=['TRDPRC_1']).rename(columns={'TRDPRC_1':equity}).astype(float)

  change = data.diff().iloc[-1,0]

  if change > 0:
    direction = '↑'
  elif change < 0:
    direction = '↓'
  else:
    direction = '→'

  row = pd.DataFrame([{'Date':direction, equity:abs(change)}])

  data.index = data.index.strftime('%Y/%m/%d')

  df = pd.concat([df,pd.concat([row,data.rename_axis('Date').sort_index(ascending=False).reset_index()],ignore_index=True)],axis=1)

for currency in ['JPY=','EURJPY=']:
  data = rdp.get_historical_price_summaries(
      universe = currency, 
      interval = rdp.Intervals.DAILY,
      count=30,
      fields=['BID']).rename(columns={'BID':currency}).astype(float)

  change = data.diff().iloc[-1,0]

  if change > 0:
    direction = '↓円安'
  elif change < 0:
    direction = '↑円高'
  else:
    direction = '→'

  row = pd.DataFrame([{'Date':direction, currency:abs(change)}])

  data.index = data.index.strftime('%Y/%m/%d')

  df = pd.concat([df,pd.concat([row,data.rename_axis('Date').sort_index(ascending=False).reset_index()],ignore_index=True)],axis=1)

data = rdp.get_historical_price_summaries(
    universe = 'CNY=', 
    interval = rdp.Intervals.DAILY,
    count=30,
    fields=['BID']).rename(columns={'BID':'CNY='}).astype(float)

change = data.diff().iloc[-1,0]

if change > 0:
  direction = '↓元安'
elif change < 0:
  direction = '↑元高'
else:
  direction = '→'

row = pd.DataFrame([{'Date':direction, 'CNY=':abs(change)}])

data.index = data.index.strftime('%Y/%m/%d')

df = pd.concat([df,pd.concat([row,data.rename_axis('Date').sort_index(ascending=False).reset_index()],ignore_index=True)],axis=1)

for treasury in treasuries:
  data = rdp.get_historical_price_summaries(
      universe = treasury, 
      interval = rdp.Intervals.DAILY,
      count=30,
      fields=['B_YLD_1']).rename(columns={'B_YLD_1':treasury}).astype(float)

  change = data.diff().iloc[-1,0]

  if change > 0:
    direction = '↑'
  elif change < 0:
    direction = '↓'
  else:
    direction = '→'

  row = pd.DataFrame([{'Date':direction, treasury:abs(change)}])

  data.index = data.index.strftime('%Y/%m/%d')

  df = pd.concat([df,pd.concat([row,data.rename_axis('Date').sort_index(ascending=False).reset_index()],ignore_index=True)],axis=1)

for commodity in commodities:
  data = rdp.get_historical_price_summaries(
      universe = commodity, 
      interval = rdp.Intervals.DAILY,
      count=30,
      fields=['TRDPRC_1']).rename(columns={'TRDPRC_1':commodity}).astype(float)

  change = data.diff().iloc[-1,0]

  if change > 0:
    direction = '↑'
  elif change < 0:
    direction = '↓'
  else:
    direction = '→'

  row = pd.DataFrame([{'Date':direction, commodity:abs(change)}])

  data.index = data.index.strftime('%Y/%m/%d')

  df = pd.concat([df,pd.concat([row,data.rename_axis('Date').sort_index(ascending=False).reset_index()],ignore_index=True)],axis=1)

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

df.to_csv('Global_Markets_Update_'+datetime.today().strftime('%Y%m%d')+'.csv',index=False,encoding='utf-8-sig',line_terminator='\r\n')

response = requests.post(
        'https://api.mailgun.net/v3/mg.dataeditor.work/messages',
        auth=('api',MAILGUN_API_KEY),
        files=[('attachment',open('Global_Markets_Update_'+datetime.today().strftime('%Y%m%d')+'.csv','rb'))],
        data={'from':EMAIL_SENDER,
              'to':[EMAIL_RECIPIENT1],
              'subject': '(Test) Global Markets Update '+datetime.today().strftime('%Y-%m-%d'),
              'text': 'Updated at '+datetime.today().strftime('%Y-%m-%d %H:%M')+'UTC'})

rdp.close_session()
