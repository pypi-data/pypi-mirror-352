__all__ = ['Client', 'collect', 'print_info', 'prepare', 'read_csv_as_json']

import sys
from os import path
import requests
import json
import datetime
import zipfile
import pickle as pickle
from .utilities import create_dir
from .models import UserData, ClientConfig, DataCollectionConfig
from .Data_Collection import prepare

from .Data_Collection import collect, print_info, prepare, read_csv_as_json


class Client:

    user_data: UserData
    cli_config: ClientConfig
    data_collection_config: DataCollectionConfig

    def __init__(self, user_data: UserData, config: ClientConfig, data_collection_config: DataCollectionConfig):

        self.user_data = user_data
        self.cli_config = config
        self.data_collection_config = data_collection_config
        
        # self.res = self.cli_config.get("RES")
        
    @property
    def url(self) -> str:
        return self.cli_config.SERVER_URL if self.cli_config.SERVER_URL[-1] == "/" else self.cli_config.SERVER_URL + "/"

    def test_connection(self):
        """
        The function make get request to teh server to get server version
        :return : server status
        :return : server version
        """

        # sending get request to the server
        res_version = requests.get(self.url + "version")
        print("SERVER IS ALIVE, SERVER VERSION: ", res_version.text)
        print("\n")

    def send_data(self):
        """
        This function send raw data to server
        :return: None
        """
        list_of_data, empty_session = prepare(self.cli_config.TRAINING_SESSIONS, self.data_collection_config)

        if not list_of_data:
            print("ERROR: Invalid Sessions list")
            return
        
        if empty_session:
            print("WARNING: One or more session has no gesture!!!")
            return

        # prepare data to send
        data = {
            "data": list_of_data,
            "auth_key": self.user_data.auth_key
        }

        # sending post request with raw data to server
        res_upload = requests.post(self.url + "upload", data=json.dumps(data))
        
        print("status: {}".format(res_upload.status_code)) 
        print("content: " + res_upload.content.decode("utf-8")) 
        print("mimetype: " + res_upload.headers['content-type']) 
        print("\n\n")

    def train_model(self):
        """
        The function make post request to server for training a new model
        """
        
        # prepare data to send
        training_request = {
            "sessions": self.cli_config.MODEL_SESSIONS,
            "model_name": self.cli_config.MODEL_NAME,
            "gestures": self.cli_config.MODEL_GESTURES,
            "split_ratio": self.cli_config.MODEL_SPLIT_RATIO,
            "auth_key": self.user_data.auth_key
        }
        
        # sending post request to the server
        res_training = requests.post(
            self.url + "training", data=json.dumps(training_request)
        )

        print("status: {}".format(res_training.status_code)) 
        print("content: " + res_training.content.decode("utf-8")) 
        print("mimetype: " + res_training.headers['content-type']) 
        print("\n\n")

    def download_model(self):
        """
        The function make post request to server for downloading a previously trained model
        """
        
        # prepare data to send
        download_request = {
            "model_name": self.cli_config.MODEL_NAME,
            "auth_key": self.user_data.auth_key
        }
                
        # sending post request to the server
        res_download = requests.post(
            self.url + "download", data=json.dumps(download_request)
        )
        
        if res_download.status_code == 200:
            # get answer and store model to files
            self.save_model(res_download.content)

            print("model save in ", self.cli_config.MODEL_DATA_PATH)
            print("\n\n")
           
        elif res_download.status_code == 201:
            print("No model downloaded")
            print("\n\n")
        
        else:
            print("status: {}".format(res_download.status_code)) 
            print("content: " + res_download.content.decode("utf-8")) 
            print("mimetype: " + res_download.headers['content-type']) 
            print("\n\n")

    def save_model(self, zip_data):
        """
        save model and info.txt in a folder named same as training id
        :param model: trained model
        :param encoder: one hot encoder object
        :return:
        """

        create_dir(self.cli_config.model_data_full_path)

        # with open(path.join(self.cli_config.model_data_full_path, "info.txt"), "w") as fl:
        #     fl.write(
        #         str(self.cli_config.__dict__)
        #         + " \ndata and time:"
        #         + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #     )

        # with open(path.join(self.cli_config.model_data_full_path, "info.json"), "w") as json_info:
        #     info: dict = self.cli_config.__dict__
        #     info["datetime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #     json.dump(info, json_info, indent=4)

        # save zip file
        with open(path.join(self.cli_config.model_data_full_path, "model.zip"), "wb") as f:
            f.write(zip_data)

        # unzip it
        with zipfile.ZipFile(path.join(self.cli_config.model_data_full_path, "model.zip"), "r") as zip_obj:
            zip_obj.extractall(path=self.cli_config.model_data_full_path)