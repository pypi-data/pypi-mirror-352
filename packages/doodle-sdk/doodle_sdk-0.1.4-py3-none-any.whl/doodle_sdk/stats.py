class RxStats():

    def __init__(self, rx_stats_dict: dict):
        for key in rx_stats_dict:
            setattr(self, key, rx_stats_dict[key])

class TxStats():

    def __init__(self, tx_stats_dict: dict):
        for key in tx_stats_dict:
            setattr(self, key, tx_stats_dict[key])

class ClientStats():

    def __init__(self, client_stat_dict: dict):
        for key in client_stat_dict:
            if key == "rx":
                setattr(self, "rx", TxStats(client_stat_dict["rx"]))
            elif key == "tx":
                setattr(self, "tx", TxStats(client_stat_dict["tx"]))
            else:
                setattr(self, key, client_stat_dict[key])

def translate_stat_response(response: dict) -> ClientStats:
    
    client_stats = []

    for result in response['result'][1]['results']:
        client_stats.append(ClientStats(result))
    
    return client_stats

