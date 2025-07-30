import json
import requests
import os
import pandas as pd


from ..models import UserData, DataCollectionConfig 


def create_dir(path):
    """
    Create directories if doesn't exists
    :param path: path of the directory
    :return: None
    """
    if not os.path.exists(path):
        os.makedirs(path)
        print("directory created")
    else:
        print("directory already exists")


def user_login(url, user_data_path):
    """
    This function allow user to login if user info already exists otherwise ask for registration
    :param url: server url
    :param user_data_path: path to the user info file
    :return: login status
    """
    if not os.path.exists(user_data_path):
        # update_registration(user_data_path)
        pass
    else:
        with open(user_data_path) as json_file:
            user_data = json.load(json_file)
        # sending login request to server
        res = requests.post(url + "login", data=json.dumps(user_data))
        res = json.loads(res.content)

        if res["status"] == "wrongpassword":
            print("Your password is worng, please enter again")
            update_local_password(user_data_path, user_data)
            return res
        elif res["status"] == "wronguser":
            print("your user name does not exists, please register")
            update_local_registration(user_data_path)
            return res
        elif res["status"] == "successful":
            print("Login successful")
            return res
        else:
            print("register again")
            update_local_registration(user_data_path)
            return res


def update_local_password(user_data_path, user_data):
    """
    This function allow user to change password if it is wrong
    :param user_data_path: path of the user info file
    :param user_data: current user data
    :return: None
    """
    print("Please enter correct password:")
    password = input()
    user_data["password"] = password
    with open(user_data_path, "w") as outfile:
        json.dump(user_data, outfile)


def update_local_registration(user_data_path):
    """
    this function update local file with user's login information
    :param user_data_path: path of the file where user info will be stored
    :return: None
    """
    print("Enter your first name")
    first_name = input()
    print("Enter your second name")
    second_name = input()
    print("Enter a password")
    password = input()
    print("Enter your preferred user name(all lower case)")
    user_name = input()
    user_data = {
        "first_name": str(first_name),
        "last_name": str(second_name),
        "password": str(password),
        "user_id": str(user_name).lower(),
    }
    with open(user_data_path, "w") as outfile:
        json.dump(user_data, outfile)


def load_info(user_data: UserData, data_collection_config: DataCollectionConfig):
    """
    This function load info files and update info dataframes with config file values
    :param config: config object of data collection
    :return: person, gesture, and session dataframes
    """
    # import json config

    # raw_data_path = path.join(CLIENT_PY_PATH, dc_config.get("RAW_DATA_PATH"))

    path_person = data_collection_config.raw_data_full_path + "info/person.csv"
    path_gesture = data_collection_config.raw_data_full_path + "info/gesture.csv"
    path_session = data_collection_config.raw_data_full_path + "info/session.csv"
    path_device = data_collection_config.raw_data_full_path + "info/device.csv"

    ## If info file doesn't exists then create new info file with data
    ## otherwise load the already existing info
    if not os.path.exists(path_person):
        person_data = pd.DataFrame(columns=["person_name"])
        person_data.to_csv(path_person)
    else:
        person_data = pd.read_csv(path_person, index_col=0)

    if not os.path.exists(path_gesture):
        gestures_data = pd.DataFrame(columns=["gesture_names"])
        gestures_data.to_csv(path_gesture)
    else:
        gestures_data = pd.read_csv(path_gesture, index_col=0)

    if not os.path.exists(path_session):
        session_data = pd.DataFrame(columns=["session_info"])
        session_data.to_csv(path_session)
    else:
        session_data = pd.read_csv(path_session, index_col=0)   

    if not os.path.exists(path_device):
        device_data = pd.DataFrame(columns=["dev_id"])
        device_data.to_csv(path_device)
    else:
        device_data = pd.read_csv(path_device, index_col=0)

    return person_data, gestures_data, session_data, device_data


def update_dataframe(df, column, value):
    """
    This function update dataframe given column name and value if that values doesn't exist
    :param df: dataframe
    :param column: name of the column
    :param value: list of values
    :return: updated dataframe
    """
    for v in value:
        if get_index(df, column, v) == "":
            df.loc[len(df)] = v
    return df


def update_dataframe_2D___unused(df, column_1, column_2, value_1, value_2):

    for idx in df[df[column_1] == value_1].index.tolist():
        if idx in df[df[column_2] == value_2].index.tolist():
            # already exists
            return df
    
    df.loc[len(df)] = [value_1,value_2]
    return df

        
def update_info(raw_data_path, person_data, gesture_data, session_data, device_data):
    """
    This function save dataframes as csv file
    :param raw_data_path: path of the raw data folder
    :param person_data: dataframe with person info
    :param gesture_data: dataframe with gesture info
    :param session_data: dataframe with session info
    :return: none
    """

    person_data.to_csv(raw_data_path + "info/person.csv")
    gesture_data.to_csv(raw_data_path + "info/gesture.csv")
    session_data.to_csv(raw_data_path + "info/session.csv")
    device_data.to_csv(raw_data_path + "info/device.csv")
    print("data saved as csv\n\n")


def get_index(df, column, data):
    """
    Function returns the index of the row for a column value
    :param df: dataframe
    :param column: name of the column
    :param data: value you are searching
    :return: index of the row
    """
    idx = df[df[column] == data].index.tolist()
    idx = str(idx).replace("[", "")
    idx = idx.replace("]", "")
    return idx


def get_value(df, column, row_idx):
    """
    Function returns the value @ column/row_idx
    :param df: dataframe
    :param column: name of the column
    :row_idx: index of the row (starting from 0)
    :return: value @ column/row_idx
    """
    try:
        return df[column][row_idx]
    except:
        return None
