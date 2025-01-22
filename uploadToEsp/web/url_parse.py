def url_parse(url): # Doesn't handle MBCS
    #print(f"url_parse url:{url}")
    url = url.replace('+',' ') # Fix these first in case of encoded values 
    #print(f"url_parse url:{url} '+' replaced")
    l = len(url)
    data = bytearray()
    i = 0
    while i < l:
        if url[i] != '%':
            d = ord(url[i])
            i += 1
        
        else:
            d = int(url[i+1:i+3], 16)
            i += 3
        
        data.append(d)
    #print(f"url_parse data:{data}")
    return data.decode('utf8')
