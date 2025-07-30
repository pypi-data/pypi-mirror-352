import multiprocessing
import logging
import glob
import pandas as pd
import re
import sys
import time
from os import path

# resource directory - need to be referenced to exe path when used with exe bundle
# if getattr(sys, "frozen", False):
#     CLIENT_PY_PATH = sys._MEIPASS
# else:
#     CLIENT_PY_PATH = path.join(path.dirname(__file__), "../")
#     sys.path.insert(0, path.join(CLIENT_PY_PATH, "utilities"))
#     sys.path.insert(0, path.join(CLIENT_PY_PATH, "hal"))
#     sys.path.insert(0, path.join(CLIENT_PY_PATH, "middleware"))
#     sys.path.insert(0, path.join(CLIENT_PY_PATH, "data_managment/utilities"))


from .utilities import create_dir, load_info, update_dataframe, get_index, update_info
from ..hal import Ble
from ..middleware import Tactigon_Recorder
from ..models import Hand

from .models import UserData, DataCollectionConfig, HAL

def collect(user_data: UserData, hal: HAL, data_collection_config: DataCollectionConfig):
    """
    This function collect raw data from device and store in files. The function uses data_collection config file
    :return: none
    """

    print_info(data_collection_config, hal, user_data)

    # load and update info data stored in dataframes
    person_data, gestures_data, session_data, device_data = load_info(user_data, data_collection_config)    

    gestures = data_collection_config.GESTURE_NAME
    person = user_data.user_id
    session = data_collection_config.SESSION_INFO

    b_hand = data_collection_config.HAND
    b_add = hal.ADDRESS
    num_sample = hal.NUM_SAMPLE
    
    # check session name
    if get_index(session_data, "session_info", session) != "":
        print("\nSession already exists. \nPlease rename it")
        print("\n\n")
        return

    ## Update dataframe with new values from config file
    person_data = update_dataframe(person_data, "person_name", [user_data.user_id])    
    gestures_data = update_dataframe(gestures_data, "gesture_names", data_collection_config.GESTURE_NAME)
    session_data = update_dataframe(session_data, "session_info", [data_collection_config.SESSION_INFO])
    device_data = update_dataframe(device_data, "dev_id", [b_add]) 

    # pipes
    rx_sensor_pipe, tx_sensor_pipe = multiprocessing.Pipe(duplex=False)
    rx_angle_pipe, tx_angle_pipe = multiprocessing.Pipe(duplex=False)

    pro_in = Ble(b_add, b_hand)

    pro_in._sensor_tx = tx_sensor_pipe
    pro_in._angle_tx = tx_angle_pipe

    print("Waiting for Tactigon connection...")
    pro_in.start()

    while not pro_in.connected:
        pass

    # loop through one gesture at a time to collect data
    for gesture in gestures:

        # creating file name based on the information from info files       
        file_name = (
            "P"
            + get_index(person_data, "person_name", person)
            + "_G"
            + get_index(gestures_data, "gesture_names", gesture)
            + "_S"
            + get_index(session_data, "session_info", session)
            + "_D"
            + get_index(device_data, "dev_id", b_add)
            + ".csv"
        )

        gesture_path = path.join(data_collection_config.raw_data_full_path, gesture)
        file_path = path.join(gesture_path, file_name)

        pro_store = Tactigon_Recorder(b_add, file_path, gesture, num_sample, rx_sensor_pipe, rx_angle_pipe)

        # create directory for gesture if not exists
        create_dir(gesture_path)

        input("Press enter to start recording: " + gesture + " ")

        # start processes
        pro_store.start()

        # clean the pipes
        while pro_store.is_ready() == False:
            while rx_sensor_pipe.poll():
                rx_sensor_pipe.recv()
            while rx_angle_pipe.poll():
                rx_angle_pipe.recv()

        print("Press enter to stop recording: " + gesture)
        input()

        # close processes
        pro_store.terminate()

    pro_in.terminate()

    # update info files
    update_info(data_collection_config.raw_data_full_path, person_data, gestures_data, session_data, device_data)


def print_info(data_collection_config: DataCollectionConfig, hal_config: HAL, user_config: UserData):
    print("**********************************************************************")
    print("                          DATA COLLECTION                             ")
    print("**********************************************************************")
    print("             Hand: " + data_collection_config.HAND.name)
    print("             User ID: " + user_config.user_id)
    print("             Session: " + data_collection_config.SESSION_INFO)
    print("**********************************************************************")
    print("**********************************************************************")


def prepare(sessions, data_collection_config: DataCollectionConfig):
    """
    This function return a list of json data corresponding to provided sessions
    :param sessions: list of session names
    :return: list of data items ( each item {"session":session, "gesture":gesture_name, "csv":df_json})
    """
    # import json config

    list_raw_data = glob.glob(data_collection_config.raw_data_full_path + "*/*.csv")

    gesture_data = pd.read_csv(data_collection_config.raw_data_full_path + "info/gesture.csv", index_col=0)
    session_data = pd.read_csv(data_collection_config.raw_data_full_path + "info/session.csv", index_col=0)
    device_data = pd.read_csv(data_collection_config.raw_data_full_path + "info/device.csv", index_col=0)

    list_of_data = []
    empty_session = False
    for session in sessions:        
        session_id = get_index(session_data, "session_info", session)        
        if len(session_id) == 0:
            empty_session = True
        else:
            # get gestures raw data
            for ls in list_raw_data:
                # find the file name from complete path
                file_name = re.findall(r"P[\d]+_G[\d]+_S[\d]+", ls)
                if len(file_name) == 0:
                    file_name = " "
                else:
                    file_name = file_name[0]                

                    # find the session id in file name
                    if session_id == file_name.split("S")[1]:
                        
                        # read file content (csv raw data as json)
                        df_json = read_csv_as_json(ls)

                        # get gest and dev id from file name
                        gesture_id = file_name.split("_")[1][1:]
                        device_id = re.findall(r"D[\d]",ls)[0].split("D")[1]

                        # find the gesture name corresponding to gesture id
                        gesture_name = gesture_data["gesture_names"].iloc[int(gesture_id)]

                        # find device MAC corresponding to dev id
                        device_MAC = device_data["dev_id"].iloc[int(device_id)]

                        list_of_data.append(
                            {
                                "session": session,
                                "gesture": gesture_name,
                                "csv": df_json,
                                "dev_id": device_MAC
                            }
                        )

    return list_of_data, empty_session


def read_csv_as_json(path):
    """
    this function read csv and return as json
    :param path: path of the csv file
    :return: dataframe as json object
    """
    df = pd.read_csv(path, index_col=0)
    df.reset_index(drop=True, inplace=True)
    return df.to_json()


# if __name__ == "__main__":
#     collect()