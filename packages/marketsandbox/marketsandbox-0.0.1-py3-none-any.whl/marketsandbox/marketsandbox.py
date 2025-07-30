
import requests

port = 8000

# url = 'http://127.0.0.1' + ':' + str(port) + '/'
# url = 'http://34.82.55.106' + ':' + str(port) + '/'
url = 'https://market-sim.serverpit.com' + '/'



def create_session(session_key):

    data = {'session_key': session_key}

    try:
        response = requests.post(url + 'create_session', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        return_session_key = response.json()['data']['session_key']
    else:
        return_session_key = None


    return return_session_key




def create_person(session_key, name, money, resource_dict={}):

    data = {'session_key': session_key, 'name': name, 'cash': money, 'resource_dict': resource_dict}

    try:
        response = requests.post(url + 'create_person', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        person_id = response.json()['data']['person_id']
    else:
        person_id = None

    return person_id



def create_resource(session_key, resource_type):

    data = {'session_key': session_key, 'resource_type': resource_type}

    try:
        response = requests.post(url + 'new_resource', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        resource_id = response.json()['data']['resource_id']
    else:
        resource_id = None

    return resource_id




def sell_limit_order(session_key, name, resource_type, quantity, price):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity, 'price': price}


    try:
        response = requests.post(url + 'sell_order', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        order_id = response.json()['data']['order_id']
    else:
        order_id = None

    return order_id



def sell_market_order(session_key, name, resource_type, quantity):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity}


    try:
        response = requests.post(url + 'sell_now', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val



def buy_limit_order(session_key, name, resource_type, quantity, price):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity, 'price': price}


    try:
        response = requests.post(url + 'buy_order', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        order_id = response.json()['data']['order_id']
    else:
        order_id = None

    return order_id


def buy_market_order(session_key, name, resource_type, quantity):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity}


    try:
        response = requests.post(url + 'buy_now', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val



def get_ask_price(session_key, resource_type, quantity=1):
    # the lowest a seller is willing to accept

    params = {'session_key': session_key, 'resource_type': resource_type, 'quantity': quantity, 'b_sell_price': True}

    try:
        response = requests.get(url + 'get_price', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        price = response.json()['data']['price']
    else:
        price = None

    return price




def get_bid_price(session_key, resource_type, quantity=1):
    # the highest a buyer is willing to pay
    
    params = {'session_key': session_key, 'resource_type': resource_type, 'quantity': quantity, 'b_sell_price': False}

    try:
        response = requests.get(url + 'get_price', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        price = response.json()['data']['price']
    else:
        price = None

    return price




def deposit(session_key, name, money):

    data = {'session_key': session_key, 'name': name, 'dollars': money, 'b_deposit': True}


    try:
        response = requests.post(url + 'deposit_or_withdraw', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val


def withdraw(session_key, name, money):

    data = {'session_key': session_key, 'name': name, 'dollars': money, 'b_deposit': False}


    try:
        response = requests.post(url + 'deposit_or_withdraw', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val



def deliver_resource(session_key, name, resource_type, quantity):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity':quantity, 'b_deposit': True}


    try:
        response = requests.post(url + 'give_or_take_resource', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val



def receive_resource(session_key, name, resource_type, quantity):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity':quantity, 'b_deposit': False}


    try:
        response = requests.post(url + 'give_or_take_resource', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val



def get_assets(session_key, name):

    params = {'session_key': session_key, 'name': name}

    try:
        response = requests.get(url + 'get_assets', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        cash = response.json()['data']['cash']
        resource_list = response.json()['data']['resource_list']

        resource_dict = {x['type'] : x['quantity'] for x in resource_list}
    else:
        cash = None
        resource_dict = None

    return cash, resource_dict



def get_people(session_key):

    params = {'session_key': session_key}

    try:
        response = requests.get(url + 'get_people', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        person_list = response.json()['data']['people']
    else:
        person_list = None

    return person_list



def get_resources(session_key):

    params = {'session_key': session_key}

    try:
        response = requests.get(url + 'get_resources', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        resource_list = response.json()['data']['resources']
    else:
        resource_list = None

    return resource_list



def cancel_sell_limit_order(session_key, order_id):

    data = {'session_key': session_key, 'sell_id': order_id}


    try:
        response = requests.post(url + 'cancel_sell_order', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val




def cancel_buy_limit_order(session_key, order_id):

    data = {'session_key': session_key, 'buy_id': order_id}


    try:
        response = requests.post(url + 'cancel_buy_order', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val



def get_sell_limit_orders(session_key, resource_type):

    params = {'session_key': session_key, 'resource_type': resource_type, 'b_buy_orders': False, 'b_quatity_available': False}

    try:
        response = requests.get(url + 'get_orders', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        orders = response.json()['data']['orders_list']
    else:
        orders = None

    return orders



def get_buy_limit_orders(session_key, resource_type):

    params = {'session_key': session_key, 'resource_type': resource_type, 'b_buy_orders': True, 'b_quatity_available': False}

    try:
        response = requests.get(url + 'get_orders', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        orders = response.json()['data']['orders_list']
    else:
        orders = None

    return orders



def get_supply_and_demand_chart_data(session_key, resource_type):

    params = {'session_key': session_key, 'resource_type': resource_type}

    try:
        response = requests.get(url + 'get_supply_and_demand', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        supply_price_list = response.json()['data']['supply_price_list']
        supply_quantity_list = response.json()['data']['supply_quantity_list']
        demand_price_list = response.json()['data']['demand_price_list']
        demand_quantity_list = response.json()['data']['demand_quantity_list']
    else:
        supply_price_list = None
        supply_quantity_list = None
        demand_price_list = None
        demand_quantity_list = None

    return supply_price_list, supply_quantity_list, demand_price_list, demand_quantity_list




