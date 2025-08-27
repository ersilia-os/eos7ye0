import os
import sys
import requests
import csv
import socket
import time

def wait_for_server(host, port, timeout=60, extra_wait=10):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=5):
                break
        except OSError:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Server {host}:{port} not available after {timeout} seconds")
            time.sleep(1)
    time.sleep(extra_wait)

input_file = sys.argv[1]
output_file = sys.argv[2]

root = os.path.dirname(os.path.abspath(__file__))

PORT = 8000

wait_for_server("0.0.0.0", PORT, timeout=60, extra_wait=10)

with open(input_file, "r") as f:
    reader = csv.reader(f)
    next(reader)
    smiles_list = [r[0] for r in reader]

baseUrl = "http://0.0.0.0:{0}".format(PORT)

api = '/api/fh'
url = baseUrl + api
data = []
batch_size = 50
for i in range(0, len(smiles_list), batch_size):
    batch = smiles_list[i:i+batch_size]
    param = {'SMILES': batch}
    response = requests.post(url, json=param)
    if response.status_code == 200:
        batch_data = response.json()['data']['data']
        data.extend(batch_data)
    else:
        raise RuntimeError(f"Request failed with status code {response.status_code}: {response.text}")

columns_0 = [
    "Colloidal aggregators",
    "FLuc inhibitors",
    "Blue fluorescence",
    "Green fluorescence",
    "Reactive compounds",
    "Promiscuous compounds",
    "Other assay interference",
]

columns_1 = [
    "ALARM_NMR_index",
    "BMS_index",
    "Chelator_Rule_index",
    "GST_FHs_Rule_index",
    "His_FHs_Rule_index",
    "Luciferase_Inhibitor_Rule_index",
    "NTD_index",
    "PAINS_index",
    "Potential_Electrophilic_Rule_index",
    "Lilly_index",
]

run_columns_file = os.path.abspath(os.path.join(root, '..', 'columns', 'run_columns.csv'))
header = []
with open(run_columns_file, "r") as f:
    reader = csv.reader(f)
    next(reader)
    for r in reader:
        header += [r[0]]

R = []
for d in data:
    r = [d[c] for c in columns_0]
    for c in columns_1:
        r += [len(d[c])]
    R += [r]

input_len = len(smiles_list)
output_len = len(R)

assert input_len == output_len

with open(output_file, "w") as f:
    writer = csv.writer(f)
    writer.writerow(header)  # header
    for o in R:
        writer.writerow(o)
