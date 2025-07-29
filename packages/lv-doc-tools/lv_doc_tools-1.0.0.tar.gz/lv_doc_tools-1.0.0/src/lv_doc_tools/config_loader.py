"""
Doc Generator
==============

An object that handles creating docs for labview projects.



"""
from pathlib import Path, PureWindowsPath, PurePosixPath
import os
import json


class Doc_Config_Loader:
    """
    This class loads and populates config file for lv_doc_tool libraries. 
    It populates paths with defaults if none given in config file.
    

    :param config_path: a path to a configuration json file, e.g. config.json

    The config is a dictionary with the following fields:

    .. code:: python

        "PATHS": {
        "ROOT": "PATH_TO_PROJECT_FOLDER",
	    "LV_PROJ": "THE_PROJECT.lvproj",
	    "TESTS": "RELATIVE PATH TO TESTS",
	    "OUTPUT": "relative_path_to_output_folder",
	    "CARAYA": "Absolute Path_to_Caraya_toolkit",
	    "TEST_XML": "relative path to test xml output",
	    "DOC_SOURCE": "relative path to additional adoc files, e.g converted xml",
	    "ANTIDOC_CONFIG":"rel_path_to_antidoc.config"
        },
        "TEST_ITEMS": [list of test VIs],
        "EMAIL": "info@resonatesystems.com.au",
        "AUTHOR": "Resonate Systems",
        "PAGE_TITLE": "A string"

    """

    def __init__(self, config):
        """
        Constructor method, the following fields in config are required

        * 'config': either dictonary with config (loaded already from json) 
                    or Path to the config file, e.g. config.json
        """
        if isinstance(config, (Path, str, PureWindowsPath, PurePosixPath)):
            if os.path.exists(config):
                try:
                    with open(config, "r", encoding="utf-8") as config_file:
                        config_dict = json.load(config_file)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from config file: {e}")
                    raise
            else:
                raise FileNotFoundError(f"Config file not found: {config}")
        elif isinstance(config, dict):
            config_dict = config
        else:
            raise TypeError("Config must be a path to a JSON file or a dictionary.")
        
        try:
            self.add_config_paths(config_dict["PATHS"])
            self.add_attributes(config_dict)
        except Exception as e:
            print(f"Config error: {e}")
            raise

    def add_config_paths(self, config):
        """
        Create Path() objects from the config paths dictionary.
        Set default values if items not present
        Raise error if mandatory items not present, e.g lv_proj_path

        """
        paths = {}
        self.root = Path(config["ROOT"]).resolve()

        if "LV_PROJ" in config.keys():
            paths['lv_proj'] = self.root.joinpath(Path(config["LV_PROJ"]))

        if "TESTS" in config.keys():
            # Where tests can be found relative to root
            paths['tests'] = self.root.joinpath(Path(config["TESTS"]))
        else:
            paths['tests'] = self.root.joinpath(Path("Tests"))

        if "OUTPUT" in config.keys():
            # OUTPUT pqth is where the build docs land, relative to root
            paths['output'] = self.root.joinpath(Path(config["OUTPUT"]))

        if "CARAYA" in config.keys():
            # Where teh carya CLI engine lives.
            paths['caraya'] = Path(config["CARAYA"])
        else:
            paths['caraya'] = PureWindowsPath(
                "C:\\Program Files\\National Instruments\\LabVIEW 2025\\vi.lib\\addons\\_JKI Toolkits\\Caraya\\CarayaCLIExecutionEngine.vi",
            )

        if "TEST_XML" in config.keys():
            # TEST_XML_PATH is where the caryaya test app saves xml output. Relative to output_path
            paths['test_xml'] = paths['tests'].joinpath(Path(config["TEST_XML"]))

        if "DOC_SOURCE" in config.keys():
            # DOC_SOURCE_PATH is where adoc files land, realtive to the root path.
            paths['doc_source'] = self.root.joinpath(Path(config["DOC_SOURCE"]))

        if "ANTIDOC_CONFIG" in config.keys():
            # The antidoc config file, as saved using the antidoc app, relative to root
            paths['antidoc_config'] = self.root.joinpath(
                Path(config["ANTIDOC_CONFIG"])
            )
        else:
            paths['antidoc_config'] = paths['lv_proj'].stem + ".config"

        if "ADOC_THEME" in config.keys():
            # The antidoc config file, as saved using the antidoc app, relative to root
            paths['adoc_theme'] = self.root.joinpath(
                Path(config["ADOC_THEME"])
            )

        self.paths = paths

    def add_attributes(self, config):
        """
        Handle non pathitems from the config.
        Set defaults if items are missing
        """
        if "AUTHOR" in config.keys():
            self.author = config["AUTHOR"]
        else:
            self.author = "Resonate Systems"

        if "EMAIL" in config.keys():
            self.email = config["EMAIL"]
        else:
            self.email = "info@resonatesystems.com.au"

        if "TITLE" in config.keys():
            self.title = config["TITLE"]
        else:
            self.title = f"Documentation For {config['PATHS']['LV_PROJ']}"

        if "TESTS" in config.keys():
            # Names of test vi's, relative to TESTS_PATH
            self.tests = [self.paths['tests'].joinpath(x) for x in config["TESTS"]]
        else:
            self.tests = []

        if "CONFLUENCE" in config.keys():
            self.confluence = config['CONFLUENCE']

    