import requests
import json

locations = {'Oxford':330217,'Reading':330396}

def getForecast(name, location):
    url =  const("http://dataservice.accuweather.com/forecasts/v1/daily/1day/%s?apikey=Kh2fOXMXIZS1geBmXqKnstfbbmOpW8up&metric=true")
    r = requests.get(url%location)
    d = r.json()
    f = d['DailyForecasts'][0]
    print('%s - High:%.1f Low:%.1f Day:%s Night:%s'%
          (name
           ,f['Temperature']['Maximum']['Value']
           ,f['Temperature']['Minimum']['Value']
           ,f['Day']['IconPhrase']
           ,f['Night']['IconPhrase'])
          )

for k in locations.keys():
    getForecast(k, locations[k])
