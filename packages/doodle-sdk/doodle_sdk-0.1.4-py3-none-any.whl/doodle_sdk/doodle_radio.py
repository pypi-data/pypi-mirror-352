import requests
import json
import re
import warnings
import time
import base64
import os
from typing import Dict
from . import stats
from . import settings


class Doodle:

    def __init__(self, ip: str = None, user: str = None, password: str = None):
        """Creates an instance of the Doodle class

        Args:
            ip: IP address of the Doodle
            user: username of the Doodle
            password: password of the Doodle

        Returns:
            Instance of Doodle class

        Raises:
            None
        """
        
        self._ip = ip
        self._user = user
        self._password = password
        self._url = None
        self._token = None

        # Radio Settings
        self._channel = None
        self._frequency = None
        self._channel_width = None
        self._submodel = None
        self._parent_model = None
        self._availible_models = None
        self._availible_frequencies = None

        # Disable warnings for self-signed certificates
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        self._session = requests.Session()

    def connect(self, ip: str = None, user: str = None, password: str = None) -> bool:
        """Connects to the Doodle and attempts to get the rpc session token

        Args:
            ip: IP address of the Doodle (required to connect)
            user: username of the Doodle
            password: password of the Doodle

        Returns:
            True if connection is successful, False if not

        Raises:
            TypeError: If the IP address of the Doodle was never set
        """

        if ip: 
            self._ip = ip
        elif (not self._ip):
            raise TypeError("Must set an IP address before connecting")

        self._url = f'https://{self._ip}/ubus'

        # keep the defaults if they never specified a user / password
        if user:
            self._user = user
        elif (not self._user):
            warnings.warn("No username specified, defaulting to \"user\"")
            self._user = "user"

        if password:
            self._password = password
        elif (not self._password):
            warnings.warn("No password specified, defaulting to \"DoodleSmartRadio\"")
            self._password = "DoodleSmartRadio"

        login_payload = self._gen_login_payload(self._user, self._password)

        for attempt in range(5): # Attempts to connect to the Doodle 5 times
            try:
                response = self._session.post(self._url, json=login_payload, verify=False)
                data = response.json()

                # Extract the token
                self._token = data['result'][1]['ubus_rpc_session']
                return True
            except:
                pass

        return False
        

    def get_associated_list(self):

        self.check_token()
        assoclist_payload = self._gen_assoclist_payload(self._token)
        response = self._session.post(self._url, json=assoclist_payload, verify=False, timeout=1)
        
        if response.status_code != 200:
            response = self.retry(response, assoclist_payload, 1)
        
        stats_response = stats.translate_stat_response(response.json())
        
        return stats_response

    def get_channel(self):
        ch_info = self.get_channel_info()
        
        return ch_info[0] if ch_info else None

    def get_channel_width(self):
        ch_info = self.get_channel_info()
        
        return ch_info[1] if ch_info else None

    def get_channel_info(self):
        self.check_token()

        channel_frequency_payload = self._send_command_payload(self._token, "iw", ["wlan0", "info"])
        
        response = self._session.post(self._url, json=channel_frequency_payload, verify=False, timeout=1)
        
        if response.status_code != 200:
            response = self._retry(response, channel_frequency_payload, 10)
        
        if response.status_code != 200:
            return None

        self._channel, self._channel_width = settings.translate_channel_frequency_response(response.json())
        return self._channel, self._channel_width

    def get_frequency(self):

        self.check_token()

        fes_model_payload = self._send_command_payload(self._token, "fes_model.sh", ["get"])
        
        response = self._session.post(self._url, json=fes_model_payload, verify=False)
        data = response.json()

        # Process the result
        if 'result' in data and len(data['result']) > 1:
            stdout = data['result'][1].get('stdout', '')
            output = stdout.strip()
        else:
            raise Exception("No result found or error in execution")

        self._submodel = output

        pattern = r'^[^-]*-(\d+)(?:[v\.]|$|-)'
        match = re.match(pattern, output)
        self._frequency = int(match.group(1)) if match else 0

        return self._frequency

    def get_firmware_version(self):
        self.check_token()

        board_info_payload = self._gen_board_info_payload(self._token)

        response = self._session.post(self._url, json=board_info_payload, verify=False)
        data = response.json()

        if 'result' in data and len(data['result']) > 1:
            board_info = data['result'][1]
            firmware_version = board_info['release']['version']
            return firmware_version
        else:
            raise Exception("No result found or error in execution")

        return None

    def set_frequency(self, frequency: int):

        self.check_token()

        self.get_availible_submodels()
        self.get_availible_frequencies()
        self.get_channel_info()

        target_submodel = ''
        for sub in self._availible_models:
            if (str(frequency) in sub):
                target_submodel = sub
                break
        
        if (target_submodel == ''):
            raise Exception(f'Frequency not in list of availible submodels {self._availible_frequencies}')

        band_switching_payload = self._send_command_payload(self._token, "/usr/share/simpleconfig/band_switching.sh", 
                                    [target_submodel, str(self._channel), str(self._channel_width)])
        
        response = self._session.post(self._url, json=band_switching_payload, verify=False, timeout=10)

        if response.status_code != 200:
            response = self._retry(response, band_switching_payload, 10)
        
        return True if response.status_code != 200 else False

    def set_channel(self, ch: int):

        self.check_token()

        self.get_availible_channels()
        if (ch not in self._availible_channels):
            raise Exception(f"Channel {ch} not in list of availible channels: {self._availible_channels}")


        self.get_channel_info()
        self.get_frequency()

        band_switching_payload = self._send_command_payload(self._token, "/usr/share/simpleconfig/band_switching.sh", 
                                    [self._submodel, str(ch), str(self._channel_width)])
        
        response = self._session.post(self._url, json=band_switching_payload, verify=False, timeout=10)

        if response.status_code != 200:
            response = self._retry(response, band_switching_payload, 10)
        
        return True if response.status_code != 200 else False

    def get_availible_channels(self):
        
        self.check_token()

        freqlist_payload = self._gen_freqlist_payload(self._token)

        response = self._session.post(self._url, json=freqlist_payload, verify=False, timeout=10)

        if response.status_code != 200:
            response = self._retry(response, band_switching_payload, 10)

        data = response.json()

        if 'result' in data and len(data['result']) > 1:        
            results = data['result'][1].get('results', -1)
        else:
            raise Exception("No result found or error in execution")

        self._availible_channels = [ch_info.get('channel') for ch_info in results]

        return self._availible_channels

    def set_channel_width(self, channel_width: int):

        self.check_token()
        self.get_availible_channel_widths()

        if channel_width not in self._availible_bw:
            raise Exception(f"Bandwidth {channel_width} not in list of availible channel bandwidths: {self._availible_bw}")

        self.get_channel_info()
        self.get_frequency()

        band_switching_payload = self._send_command_payload(self._token, "/usr/share/simpleconfig/band_switching.sh", 
                                    [self._submodel, str(self._channel), str(channel_width)])
        
        response = self._session.post(self._url, json=band_switching_payload, verify=False, timeout=10)

        if response.status_code != 200:
            response = self._retry(response, band_switching_payload, 10)
        
        return True if response.status_code != 200 else False

    def get_availible_channel_widths(self):

        self.check_token()
        self.get_frequency()

        channel_widths_payload = self._send_command_payload(self._token, "/usr/sbin/info.sh", [])

        response = self._session.post(self._url, json=channel_widths_payload, verify=False, timeout=10)
        
        if response.status_code != 200:
            response = self._retry(response, channel_widths_payload, 10)

        data = response.json()

        if 'result' in data and len(data['result']) > 1:   
            models = json.loads(data['result'][1]['stdout'])['models']
        else:
            raise Exception("No result found or error in execution")

        for model in models:
            if model.get('model', '') == self._submodel:
                self._availible_bw = [(int(bw) / 1000) for bw in model['chanbw_list'].split(' ')]

        return self._availible_bw

    def get_parent_submodel(self):
        self.check_token()

        get_parent_payload = self._send_command_payload(self._token, "fes_model.sh", ["get", "parent"])

        response = self._session.post(self._url, json=get_parent_payload, verify=False, timeout=10)

        if response.status_code != 200:
            response = self._retry(response, get_parent_payload, 10)

        data = response.json()

        if 'result' in data and len(data['result']) > 1:        
            stdout = data['result'][1].get('stdout', '')
            output = stdout.strip()
        else:
            raise Exception("No result found or error in execution")

        self._parent_model = stdout
        return self._parent_model

    def get_availible_submodels(self):
        self.check_token()

        self.get_parent_submodel()

        cat_submodel_payload = self._send_command_payload(self._token, "cat", [f"/usr/share/.doodlelabs/fes/{self._parent_model}"])
        
        response = self._session.post(self._url, json=cat_submodel_payload, verify=False, timeout=10)

        if response.status_code != 200:
            response = self._retry(response, cat_submodel_payload, 10)

        data = response.json()

        if 'result' in data and len(data['result']) > 1:        
            stdout = data['result'][1].get('stdout', '')
            output = stdout.strip()
        else:
            raise Exception("No result found or error in execution")

        pattern = r'sub_model\d+="([^"]+)"'
        self._availible_models = re.findall(pattern, stdout)

        return self._availible_models

    def get_availible_frequencies(self):

        pattern = r'^[^-]*-(\d+)(?:[v\.]|$|-)'
        
        self._availible_frequencies = []

        for model in self._availible_models:
            match = re.match(pattern, model)
            self._availible_frequencies.append(int(match.group(1)) if match else 0)

        return self._availible_frequencies

    def enable_link_status_log(self):
        """Enable the link status log on the doodle radio
        
        Returns:
            True if successful, False otherwise
        """
        self.check_token()
        
        # Set the configuration
        enable_log_payload = self._send_command_payload(self._token, "uci", 
                                                       ["set", "link_status_log.@general[0].enabled=1"])
        
        response = self._session.post(self._url, json=enable_log_payload, verify=False, timeout=10)
        
        if response.status_code != 200:
            response = self._retry(response, enable_log_payload, 10)
        
        if response.status_code != 200:
            return False
        
        # Commit the changes
        commit_payload = self._send_command_payload(self._token, "uci", ["commit"])
        
        response = self._session.post(self._url, json=commit_payload, verify=False, timeout=10)
        
        if response.status_code != 200:
            response = self._retry(response, commit_payload, 10)
        
        return response.status_code == 200

    def get_link_status_log_location(self):
        """Get the latest link status log file location
        
        Returns:
            String containing the log file path if successful, None otherwise
        """
        self.check_token()
        
        log_location_payload = self._send_command_payload(self._token, "/usr/bin/link-status.sh", ["LOGS"])
        
        response = self._session.post(self._url, json=log_location_payload, verify=False, timeout=10)
        
        if response.status_code != 200:
            response = self._retry(response, log_location_payload, 10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
                
        if 'result' in data and len(data['result']) > 1:
            stdout = data['result'][1].get('stdout', '')
            return stdout.strip()
        else:
            return None

    def download_link_status_log(self, log_file_path: str, download_folder: str = "."):
        """Download the link status log file from the radio
        
        Args:
            log_file_path: Path to the log file on the radio (from get_link_status_log_location)
            download_folder: Local folder to save the file (defaults to current directory)
            
        Returns:
            String containing the local file path if successful, None otherwise
        """
        self.check_token()
        
        # Create the download folder if it doesn't exist
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        
        # Create payload to read the file with base64 encoding
        read_file_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [self._token, "file", "read", {
                "path": log_file_path,
                "base64": True
            }]
        }
        
        response = self._session.post(self._url, json=read_file_payload, verify=False, timeout=30)
        
        if response.status_code != 200:
            response = self._retry(response, read_file_payload, 30)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if 'result' in data and len(data['result']) > 1:
            file_data = data['result'][1].get('data', '')
            if file_data:
                # Decode base64 data
                try:
                    decoded_data = base64.b64decode(file_data)
                    
                    # Extract filename from path
                    filename = os.path.basename(log_file_path)
                    local_file_path = os.path.join(download_folder, filename)
                    
                    # Write the file
                    with open(local_file_path, 'wb') as f:
                        f.write(decoded_data)
                    
                    return local_file_path
                except Exception as e:
                    return None
            else:
                return None
        else:
            return None

    def check_token(self):
        if not self._token or not self._url:
            raise TypeError("Must connect to the Doodle before setting its channel")

    def _retry(self, response, payload, timeout):
        for retry in range(5):
            self.connect()
            response = self._session.post(self._url, json=payload, verify=False, timeout=timeout)

            if (response.status == 200):
                break

            time.sleep(1)

        return response


    def _gen_assoclist_payload(self, token: str):

        assoclist_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [token, "iwinfo", "assoclist", {
                "device": "wlan0"
            }]
        }

        return assoclist_payload

    def _gen_freqlist_payload(self, token: str):
        freqlist_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [token, "iwinfo", "freqlist", {"device": "wlan0"}]
        }

        return freqlist_payload

    def _gen_login_payload(self, user: str, password: str) -> Dict[str, str]:

        login_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": ["00000000000000000000000000000000", "session", "login", {"username": self._user, "password": self._password}]
        }
        return login_payload

    def _gen_board_info_payload(self, token: str):
        board_info_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [token, "system", "board", {}]
        }

        return board_info_payload

    def _send_command_payload(self, token: str, command: str, params):
        cat_submodel_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [token, "file", "exec", {
                "command": command,
                "params": params
            }]
        }

        return cat_submodel_payload