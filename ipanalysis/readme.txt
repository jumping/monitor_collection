1. download GeoIP
wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz
gunzip GeoIP.dat.gz

2. python lib
easy_install pygeoip

3. download country to continent
wget -N http://dev.maxmind.com/static/csv/codes/country_continent.csv
