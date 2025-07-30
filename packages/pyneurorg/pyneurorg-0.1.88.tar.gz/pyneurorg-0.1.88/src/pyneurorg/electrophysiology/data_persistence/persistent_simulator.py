syn._pyneurorg_model_name = model_name
syn._pyneurorg_model_params = current_model_params
# Armazenar descrição da regra de conexão
if connect_condition: syn._pyneurorg_connect_rule = f"condition: {connect_condition}"
elif connect_prob: syn._pyneurorg_connect_rule = f"prob: {connect_prob}"
elif connect_n: syn._pyneurorg_connect_rule = f"n: {connect_n}"
else: syn._pyneurorg_connect_rule = "all-to-all (default)"