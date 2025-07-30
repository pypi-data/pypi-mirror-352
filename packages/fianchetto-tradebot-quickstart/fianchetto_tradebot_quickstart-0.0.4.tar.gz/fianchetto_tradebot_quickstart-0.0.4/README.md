# Getting Started!
Thanks for your interest in the Fianchetto TradeBot!
This QuickStart project is the perfect way to get started. Just follow the instructions below
and you'll be up & running in 2 minutes or less!

## Set up credentials
### 1. Create credential files
Create the files that the application needs to connect to your exchange.

### 2. Exchange Account Information
```
$> export FIANCHETTO_HOME=./src/fianchetto_tradebot_quickstart/sample
$> cp ${FIANCHETTO_HOME}/config/accounts.example.ini ${FIANCHETTO_HOME}/config/accounts.accounts.ini
```

### 3. Exchange-Specific Credentials
For the exchange(s) you'd like to use, just copy the files for your brokerage and update them
with your credentials.

#### E*Trade
```$> cp ${FIANCHETTO_HOME}/config/etrade_config.example.ini ${FIANCHETTO_HOME}/config/etrade_config.ini```

You'll need your API keys. If you don't have them, you can get them [here](https://us.etrade.com/etx/ris/apikey).

More information about the E*Trade authentication flow can be found [here](https://developer.etrade.com/getting-started).


#### Schwab
`$> cp ${FIANCHETTO_HOME}/config/etrade_config.example.ini ${FIANCHETTO_HOME}/config/schwab_config.ini`


#### IKBR
`$> cp ${FIANCHETTO_HOME}/config/ikbr_config.example.ini ${FIANCHETTO_HOME}/config/ikbr_config.ini`


Note: These files contain your sensitive credentials. Please be sure to 
not check them in. The `.gitignore` file should automatically exclude them, but please be vigilant.

## Run & Enjoy!
`$> python ./main.py`

The services should be up on the default ports.

Order Execution Service (OEX) - Port `:8080`

*Coming Soon* - Quote Service (Quotes) Port `:8081`

*Coming Soon* - Trade Identification Service (Trident) `:8082`

*Coming Soon* - Helm Service `:8083`

### Authentication

#### Getting Credentials
The example here uses E*Trade. You must already have your API keys - if you don't have them, you can get them [here](https://us.etrade.com/etx/ris/apikey).


#### Using Credentials
You will be prompted on the shell to enter the auth code.
retrieved from the browser after the redirect. This code is valid for two hours, after which
you will be prompted again.

### Sample Endpoints
#### Health Check

`$> curl -X GET localhost:8080/`

#### Get Orders

```
$> export ACCOUNT_ID = <your_account_id>
$> curl -X GET localhost:8080/api/v1/etrade/${ACCOUNT_ID}/orders`
```

#### Preview Orders

