==Douban Book Crawler project.==

tricks

1. Let Scrapy use shadow socks proxy to get content which is blocked by GFW.
```shell
sudo apt-get install privoxy
sudo vi /etc/privoxy/config
forward-socks5 / 127.0.0.1:1080 .
sudo services privoxy restart
```
and with involke code.
```python
soup = Beautifulsoup(
					requests.get(url, timeout=5,
								proxies={'http':'http://localhost:8118'}),
					'html.parser')
```
