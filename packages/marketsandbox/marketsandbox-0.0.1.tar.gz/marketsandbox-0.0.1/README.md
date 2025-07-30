
# market sandbox

This web application lets you create users and buy and sell resources with both market orders and limit orders. This package is an api which contains simple functions to interface with the backend server. 


## A simple example
```
import marketsandbox as ms

# make a session key which can be any string you choose
SK = 'hamster'
ms.create_session(session_key=SK)

# create a resource called carrot and a person called Ham Solo who starts with $200
ms.create_resource(session_key=SK, resource_type='carrot')
ms.create_person(session_key=SK, name='Ham Solo', money=200.00)

# give Ham Solo 30 carrots to start
ms.deliver_resource(session_key=SK, name='Ham Solo', resource_type='carrot', quantity=30)

# Ham Solo wants to sell 10 carrots for $1.25 each
ms.sell_limit_order(session_key=SK, name='Ham Solo', resource_type='carrot', quantity=10, price=1.25)

# Get the lowest price for sale on the market
ask_price = ms.get_ask_price(session_key=SK, resource_type='carrot')
print(ask_price) # -> 1.25
```

## Installation

```
pip install marketsandbox
```


## API

Note: all functions will return None if there is an error.

#### Perform an action

```
session_key = ms.create_session(session_key)
```

```
resource_id = ms.create_resource(session_key, resource_type)
```

```
person_id = ms.create_person(session_key, name, money, resource_dict)
# an example resource_dict is {'carrot': 30, 'potato': 5}
```

```
b_success = ms.deposit(session_key, name, money)
```

```
b_success = ms.withdraw(session_key, name, money)
```

```
b_success = ms.deliver_resource(session_key, name, resource_type, quantity)
# gives some resources to a person
```

```
b_success = ms.receive_resource(session_key, name, resource_type, quantity)
# takes some resources from a person
```

```
sell_id = ms.sell_limit_order(session_key, name, resource_type, quantity, price)
```

```
buy_id = ms.buy_limit_order(session_key, name, resource_type, quantity, price)
```

```
b_success = ms.sell_market_order(session_key, name, resource_type, quantity)
# sell immediately for the highest price (bid price) available on the market
```

```
b_success = ms.buy_market_order(session_key, name, resource_type, quantity)
# buy immediately for the lowest price (ask price) available on the market
```

```
b_success = ms.cancel_sell_limit_order(session_key, order_id)
```

```
b_success = ms.cancel_buy_limit_order(session_key, order_id)
```


#### Get the current state

```
ask_price = ms.get_ask_price(session_key, resource_type, quantity)
# gets the lowest a seller is willing to accept
```

```
bid_price = ms.get_bid_price(session_key, resource_type, quantity)
# gets the highest a buyer is willing to pay
```

```
money, resource_dict = ms.get_assets(session_key, name)
```

```
people_list = ms.get_people(session_key)
```

```
resource_list = ms.get_resources(session_key)
```

```
sell_orders = ms.get_sell_limit_orders(session_key, resource_type)
# returns a list of dictionaries sorted by price from low to high
```

```
buy_orders = ms.get_buy_limit_orders(session_key, resource_type)
# returns a list of dictionaries sorted by price from high to low
```

```
(supply_price_list, supply_quantity_list, 
 demand_price_list, demand_quantity_list) = ms.get_supply_and_demand_chart_data(session_key, resource_type)
# returns supply and demand information needed to make a supply vs demand chart
```



## Website

Anything you do from this package can also be viewed on the website by plugging in the same session key <br>
https://mariusfacktor.github.io/market_simulator/



## How the market operates

The sell limit orders are put onto the market and sorted by price from low to high, and similarily the buy limit orders and put onto the market and sorted by price from high to low. If there is price overlap between the lowest sell order and highest buy order, the orders will transact automatically. Market orders will execute immediately if there is enough supply on the market to fulfill the request. 


A person can create a sell limit order with a quantity greater than they currently own. If this occurs, an internal field called quanity_available will keep track of how much the seller actually has and the order will only transact up to that quantity. Similarily, a person can create a buy order with a total dollar amount greater than their account balance, but the order will stop transacting once they can no longer afford to buy more. 

