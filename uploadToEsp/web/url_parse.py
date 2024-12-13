def url_parse(url): # Doesn't handle MBCS
    url.replace('+',' ') # Fix these first in case of encoded values 
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
    
    return data.decode('utf8')

