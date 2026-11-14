cd /workspace/jpf-dashboard/tmp
for s in btc eth sol near fet usdc; do S=$(echo $s|tr a-z A-Z); curl -s https://api.coinbase.com/v2/prices/$S-USD/spot -o ${s}_spot.json; curl -s https://api.exchange.coinbase.com/products/$S-USD/stats -o ${s}_stats.json; done
curl -s https://api.gold-api.com/price/XAU -o gold.json
UA='Mozilla/5.0'
curl -s -A "$UA" "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?range=5d&interval=1d" -o y_CLF.json
curl -s -A "$UA" "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=5d&interval=1d" -o y_GSPC.json
curl -s -A "$UA" "https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX?range=5d&interval=1d" -o y_TNX.json
curl -s "https://api.open-meteo.com/v1/forecast?latitude=49.09263&longitude=-122.57717&current=temperature_2m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max&timezone=America/Vancouver&forecast_days=7" -o weather_om.json
for f in btc_spot gold y_CLF y_GSPC y_TNX weather_om near_stats; do echo $f; head -c 120 $f.json;echo; done
