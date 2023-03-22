# newsScraper
Search engine scraping for media coverage data collection 

# Internal:

## Future Features
### Multiproccessing
```py
from multiprocessing import Process
```
### Block Cookie Banners & Adblock 
  - uBlock Origin
https://stackoverflow.com/questions/52153398/how-can-i-add-an-external-extension-into-selenium-chrome-python
### Better String comparison
```py
from difflib import SequenceMatcher
SequenceMatcher(None, a, b).ratio()
```

### VPN
  - OpenVPN
    ```
    sudo apt-get install openvpn unzip 

    sudo openvpn --config ../Surfshark_Config/de-fra.prod.surfshark.com_tcp.ovpn --auth-user-pass ../pass.txt
    ```
