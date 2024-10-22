# Get the weather from BBC
import gc
import requests, json
from io import StringIO
import xmltok # Requires mip.install()
import uxml2dict

mem = gc.mem_free()
print(mem)

location = 2639577

weather_rss_url = f"https://weather-broker-cdn.api.bbci.co.uk/en/forecast/rss/3day/{location}"

r = requests.get(weather_rss_url)
# Forecast now in r.text - need a Stream object to supply to xmltok
s = StringIO(r.text)
x = xmltok.tokenize(s)


# Or use r.raw which is a Stream anyway
#r = requests.get(weather_rss_url, stream=True)
#x = xmltok.tokenize(r.raw)

parsed = uxml2dict.parse(x)
"""
try:
    print(json.dumps(parsed, indent=4))
except TypeError: # json in micropython does not support keyword argument indent
    print(json.dumps(parsed))
"""
print(parsed['rss']['channel']['item'][1]['title']['#text']) # prints tomorrow, [0] today, [2] day after tomorrow

mem1 = gc.mem_free() 
print(mem1)
print((mem - mem1))
