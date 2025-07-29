"""
Doc Generator
==============

An object that handles creating docs for labview projects.



"""
from pathlib import Path, PureWindowsPath
from lv_doc_tools.caraya_parser import Caraya_Parser
import subprocess
from sys import platform
from atlassian import Confluence
import re
import time
import datetime
import os
LV_DOCS_DIR = Path(__file__).parent.resolve()

print(f"\n\n{LV_DOCS_DIR}\n\n")
LV_DOCS_DIR = Path(__file__).parent.resolve()

print(f"\n\n{LV_DOCS_DIR}\n\n")


class Doc_Generator:
    """
    This class hqndles the generation of documents from LabView source files.
    It uses both antidoc and asciidoctor-pdf.
    It allows the users to include additional sources from the Caraya test output.

    :param config: a dictionary of configuration parameters.

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
	    "ANTIDOC_CONFIG_PATH":"rel_path_to_antidoc.config",
            "ADOC_THEME": "rel_path_to_theme.yml" defaults to RS_theme.yml
        },
        "TEST_ITEMS": [list of test VI names],
        "TEST_ITEMS": [list of test VI names],
        "EMAIL": "info@resonatesystems.com.au",
        "AUTHOR": "Resonate Systems",
        "TITLE": "A string"
        "ADOC_ATTR":{"docnumber":A_String,
                     "vnumber":A_string },
        "CONFLUENCE":{
	    "SPACE_KEY":"A_SPACE_KEY",
	    "IMAGE_DIR":"Image_dir_relative_to_output_path",
	    "CONFLUENCE_URL" : "https://resonatesystems.atlassian.net/wiki",
	    "USERNAME" : "john.hancock@resonatesystems.com.au",
	    "API_TOKEN" : a_string
	    "SPACE_KEY" : a_string
        }

        "TITLE": "A string"
        "ADOC_ATTR":{"docnumber":A_String,
                     "vnumber":A_string },
        "CONFLUENCE":{
	    "SPACE_KEY":"A_SPACE_KEY",
	    "IMAGE_DIR":"Image_dir_relative_to_output_path",
	    "CONFLUENCE_URL" : "https://resonatesystems.atlassian.net/wiki",
	    "USERNAME" : "john.hancock@resonatesystems.com.au",
	    "API_TOKEN" : a_string
	    "SPACE_KEY" : a_string
        }


    """

    def __init__(self, config):
        """
        Constructor method, the following fields in config are required

        * 'ROOT'
        * 'LV_PROJ_PATH'
        *
        """
        try:
            self.add_config_paths(config["PATHS"])
            self.add_attributes(config)
        except Exception as e:
            print(f"Config error: {e}")
            raise
        # Set the head source file
        head_file = self.paths['lv_proj'].stem + ".adoc"
        self.head_file = self.paths['output'].joinpath(head_file)
       

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
            paths['caraya'] = self.root.joinpath(Path(config["CARAYA"]))
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

        if "ANTIDOC_CONFIG_PATH" in config.keys():
            # The antidoc config file, as saved using the antidoc app, relative to root
            paths['antidoc_config'] = self.root.joinpath(
                Path(config["ANTIDOC_CONFIG_PATH"])
            )
        else:
            paths['antidoc_config'] = paths['lv_proj'].stem + ".config"

        if "ADOC_THEME" in config.keys():
            paths['adoc_theme'] = self.root.joinpath(
                Path(config["ADOC_THEME"])
            )
        else:
            paths['adoc_theme'] = LV_DOCS_DIR.joinpath("RS_theme.yml")
            

        if "ADOC_THEME" in config.keys():
            paths['adoc_theme'] = self.root.joinpath(
                Path(config["ADOC_THEME"])
            )
        else:
            paths['adoc_theme'] = LV_DOCS_DIR.joinpath("RS_theme.yml")
            
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
            
        if "ADOC_ATTR" in config.keys():
            self.adoc_attr = config['ADOC_ATTR']
        else:
            self.adoc_attr = None


    def make_antidoc_command(self):
        """
        Create the CLI command needed to run antidoc and crete build source files
        """
        gcli_command = [
            "g-cli",
            "--lv-ver",
            "2025",
            "antidoc",
            "--",
            "-addon",
            "lvproj",
            "-pp",
            f"'{self.paths['lv_proj']}'",
            "-t",
            self.title,
            "-out",
            f"'{(self.paths['output'])}'",
            "-e",
            self.email,
            "-a",
            self.author,
            "-configpath",
            f"'{self.root.joinpath(self.paths['antidoc_config'])}'",
        ]
        self.antidoc_command = gcli_command

    def make_ascii_doctor_command(self):
        """
        Create the  ascii doctor command to convert .adoc files to pdf
        """

        cmd = ["asciidoctor-pdf"]

        cmd.append('-D')
        cmd.append(f"'{self.paths['output']}'")
        
        cmd.append('--theme')
        cmd.append(f"'{self.paths['adoc_theme']}'")

        #cmd.append '' ADD OTHER ARGS HERE
        cmd.append(f"'{self.head_file}'")  # .replace('\\','/').replace('C:', '/c'))
        self.ascii_doctor_command = cmd
        print(cmd)

    def run_command(self, cmd):
        """
        Run a system command, this uses os.system
        :TODO: check behaviour again with subprocess()

        """

        if platform == "linux" or platform == "linux2" or platform == "darwin":
            # OS X or Linux
            print(cmd)
        elif platform == "win32":
            # Windows...
            try:
                # proc = subprocess.run(cmd) #, check=True)
                cmd_str = " ".join(cmd)
                print(f"\n\n{cmd_str}\n\n")
                os.system(cmd_str)

            except Exception as err:
                print("Error running CLI command")
                raise

    def tweak_adocs(self):
        """
        Alter the vanilla adocs generated by antidoc

        Currently it removes legal notices and wovalab in title, also sets TOC depth.
        """
        tmp_file = self.paths['output'].joinpath("tmp.adoc")
        # Remove the gratuitous wovalabs text
        #
        ptns = [
            "^Antidoc v[0-9.]+;(.*)",  # get the text after the antidoc statement
            "^:toclevels: (2)",  # get the toc level line
            "== Legal Information",  # get the start of legal info
        ]
        # read in head file
        with open(self.head_file, "r") as orig:
            with open(tmp_file, "w+") as new:
                if self.adoc_attr:
                    for k,v in self.adoc_attr.items():
                        new.write(f":{k}: {v}\n")
                
                if self.adoc_attr:
                    for k,v in self.adoc_attr.items():
                        new.write(f":{k}: {v}\n")
                
                for line in orig:
                    m = re.match("^Antidoc v[0-9.]+;(.*)", line)
                    if m:
                        new.write(m[1] + "\n")
                        continue
                    m = re.match("^:toclevels:", line)
                    if m:
                        new.write(":toclevels: 4\n")
                        continue
                    m = re.match("^== Legal Information", line)
                    if m:
                        break
                    else:
                        new.write(line)
        Path(tmp_file).replace(self.head_file)

    def add_sources(self, sources, header_text="\n== Appendix\n"):
        """
        Add include statments to head adoc file
        to include the sources

        Optionally allows a new section title.
        """
        print(f"Head File is {str(self.head_file)}")
        print(f"Added sources are: {sources}")
        with open(self.head_file, "a+") as fh:
            fh.write(header_text)
            for src in sources:
                fh.write(f"include::{str(src)}[leveloffset=+1]\n")

    def run_caraya_tests(self):
        """
        Runs the Caraya tests using the G-CLI command line interface
        and generates XML test reports into the XML path.
        """
        if platform == "win32":
            #clean up the test xml folder
            if self.paths['test_xml'].exists():
                for item in self.paths['test_xml'].iterdir():
                    if item.is_file():
                        item.unlink()
            else:   
                # Create the test xml folder if it doesn't exist
                self.paths['test_xml'].mkdir(parents=True, exist_ok=True)
            
            #run tests for each defined test item vi/project etc
            for iTest_item in self.config["TEST_ITEMS"]:
                iTestPath = self.paths['tests'].joinpath(iTest_item)
                #if iTestPath is a directory, run the tests in that directory
                if iTestPath.is_dir():
                    testFiles = [x for x in iTestPath.glob("*.vi")]
                    testFolder = iTestPath.name
                #if iTestPath is a file, run the tests in that file
                else:
                    testFiles = [iTestPath]
                    testFolder = iTestPath.parent.name
                for iTestFile in testFiles:
                    gcli_command = [
                        "g-cli", "--lv-ver", "2025",
                        self.paths['caraya'],
                        "--","-s",str(iTestFile),
                        "-x",str(self.paths['test_xml'].joinpath(f"{testFolder}_{iTestFile.stem}.xml"))
                    ]
                    subprocess.run(gcli_command, check=True)                                                                                                                                                                                                                                                                                                                                        
                    print(f"Test Report for {str(iTestPath)} generated successfully.")
        else:
            print(f"Caraya tests not run on {platform} - only windows supported")


    def build_docs(self):
        """
        Based on config values build the docs
        1. Build adoc from LV proj - antidoc_command
        2. Run Caraya tests and generate XML output
        3. Convert XML test outputs to adoc
        5. Tweak adoc output to remove unwanted material and update style
        5. Add test report adoc content
        6. Generate required outputs,  PDF

        :TODO: Add some switching here to control what happens based on config flags
        """

        # . 1 Run the anti doc command - this yields adoc files in output_path along with Image and Include directory
        self.make_antidoc_command()
        try:
            self.run_command(self.antidoc_command)
            print(f"\n\nRunning:\n {self.antidoc_command}\n\n")
            print(f"\n\nRunning:\n {self.antidoc_command}\n\n")
        except Exception as err:
            print(self.antidoc_command)
            print(err)

        # 2. Run the caraya tests and generate XML output
        #self.run_caraya_tests()
        print("\nTHE TESTS WERE NOT RUN!\n")

        # 3. Convert XML in test output to adoc - yields adoc files in DOC_SOURCE_PATH
        # if platform == "win32":
        #     # create dictionary of tests
        #     out_file = self.paths['doc_source'].joinpath("test_results.adoc")
        #     out_file.parents[0].mkdir(parents=True, exist_ok=True)
        #     CarayaObject = Caraya_Parser(self.paths['test_xml'], out_file)
        #     CarayaObject.process_xml_files()
        # else:
        #     print(f"xml to adoc\n{self.paths['test_xml']}\n{self.paths['doc_source']}")

        # 4. Tweak adoc source - Adjust head adoc file 
        self.tweak_adocs()

        # 5. Add in test report content from DOC_SOURCE_PATH
        sources = [x for x in self.paths['doc_source'].glob("*Test*.adoc")]
        self.add_sources(sources, header_text="")
       
        # 6. Run asciidoctor
        self.make_ascii_doctor_command()
        print(f"\n\nASCII DOC PDF: {self.ascii_doctor_command}\n\n")
        try:
            self.run_command(self.ascii_doctor_command)
        except Exception as err:
            print(self.ascii_doctor_command)
            print(err)

    def publish_to_confluence(self):
        """
        Push HTML output to confluence
        """

        confluence = Confluence(
                    url=self.confluence["URL"],
                    username=self.confluence["USERNAME"],
                    password=self.confluence["API_TOKEN"])
        print("Authenticated Successfully")

        self.space_key = self.confluence["SPACE_KEY"]
        self.title = self.confluence["PAGE_TITLE"] 

        for filename in os.listdir(self.paths['output']):
            if filename.endswith(".pdf"):
                pdf_file_path = os.path.join(self.paths['output'], filename)
                    # Check if the Confluence page exists
                #Getting Metadata
                pdf_title=os.path.splitext(filename)[0]
                creation_time=os.path.getctime(pdf_file_path)
                modified_time=os.path.getmtime(pdf_file_path)
                date_created=datetime.datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
                date_modified=datetime.datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")

                metadata_table = f"""
                <table>
                    <tbody>
                        <tr><th>Title</th><td>{pdf_title}</td></tr>
                        <tr><th>Date Created</th><td>{date_created}</td></tr>
                        <tr><th>Date modified</th><td>{date_modified}</td></tr>
                    </tbody>
                </table>
                <p>The PDF document is attached to this page.</p>
                """
                page_id = None
                if confluence.page_exists(self.space_key, self.title):
                    existing_page = confluence.get_page_by_title(
                        self.space_key, self.title
                    )
                    if existing_page:
                        page_id = existing_page["id"]
                        confluence.update_page(
                            page_id=page_id,
                            title=self.title,
                            body=metadata_table,
                            representation="storage"
                        )
                else:
                    # Create a new page and get its ID
                    created_page = confluence.create_page(
                        space=self.space_key,
                        title=self.title,
                        body=metadata_table,
                        representation="storage"
                    )
                    page_id = created_page["id"]
                    print("New page created.")
                response = confluence.attach_file(
                    filename=pdf_file_path,
                    name="Doc.pdf",
                    content_type="application/pdf",
                    page_id=page_id,
                )
                print("PDF file attached and updated to Confluence successfully")
