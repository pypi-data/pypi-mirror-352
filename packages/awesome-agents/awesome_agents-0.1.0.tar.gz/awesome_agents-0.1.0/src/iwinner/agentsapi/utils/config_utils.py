from configparser import ConfigParser

import os
config_file = "App.ini"
class Config:
    def __init__(self):
        self.config=ConfigParser()
        # Get the absolute path to the config file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, config_file)
        print(config_path)
        self.config.read(config_path)
        print("DONE")
        print(self.config)
        if not self.config.sections():
            print("Warning: No sections found in the config file. Check the file path and format.")
        else:
            print("Config file loaded successfully.")
    def get_llm_options(self):
        print(self.config["DEFAULT"])
        ress=self.config["DEFAULT"].get("LLM_OPTIONS").split(", ")
        print(ress)
cs=Config()
cs.get_llm_options()