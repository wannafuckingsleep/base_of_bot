import os

platform_tokens: dict = {
    "tg": "",
    "vk": ""
}

# DataBase
host = "localhost"
base_user = ""
base_pass = ""
base_charset = "utf8mb4"

# local test
product_server = False
path_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = path_dir + '/logs'
if not os.path.isdir(path_dir + "/logs"):
    os.mkdir(path_dir + "/logs")
