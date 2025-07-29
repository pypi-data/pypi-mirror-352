
from lxml import etree
import pandas as pd
import re
from datetime import datetime
import os
from pathlib import Path
from collections import defaultdict
import glob
from lv_doc_tools.config_loader import Doc_Config_Loader

class Caraya_Parser:
    """
    Class to convert caraya xml test report to adoc format
    """

    def __init__(self,config):
        """
        Constructor for the class

        Args:
            config (dict or Path): a dictionary with config or a path to the config file
        """
        print(f"Config: {config}")
        self.config = Doc_Config_Loader(config)

        self.xml_dir = self.config.paths['test_xml']
        self.xml_files = glob.glob(os.path.join(self.xml_dir, "*.xml"))

    def process_xml_files(self):
        """
        Processes the XML files in the directory and creates an adoc file

        Args:
            None
        Returns:
            None
        """
        #build complete tree
        xml_files = glob.glob(os.path.join(self.xml_dir, "*.xml"))
        TestDfs = {}
        for file in self.xml_files:
            file = Path(file)
            testsuite_name = file.stem
            print(f"Processing file: {file} type: {type(file)}")
            
            the_tree = etree.parse(file)
            root = the_tree.getroot()
            data = []

            for testsuite in root.findall(".//testsuite"):
                # Extract the Test_COM_12XX part
                full_name = testsuite.get("name")
                id_part = full_name.split(":")[-1].replace(".vi", "")

                for testcase in testsuite.findall("testcase"):
                    assertion = testcase.get("name").strip()
                    
                    # Skip assertions that start with underscore
                    if assertion.startswith("_"):
                        continue

                    # Check if there is a <failure> child element
                    failure = testcase.find("failure")
                    result = "Fail" if failure is not None else "Pass"

                    data.append({
                        "ID": id_part,
                        "Assertion": assertion,
                        "result": result
                    })

            # Convert to DataFrame
            df = pd.DataFrame(data)
            TestDfs[testsuite_name] = df
            print(f"Test suite results for testsuite {testsuite_name}:\n{df}\n")
                    #print(f"Test name: {test.tag}, Attributes: {test.attrib}")
                    #print(f"Test name: {test.tag}, Attributes: {test.attrib}")
            #print(f"Root element: {root.tag}, Attributes: {root.attrib}")
        #write to excel

        with pd.ExcelWriter(self.config.paths['output'].joinpath("test_report.xlsx"), engine="xlsxwriter") as writer:
            for sheet_name, df in TestDfs.items():
                # Write each DataFrame to a different sheet
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        output_adoc_path = self.config.paths['output'].joinpath("test_report.adoc")
        for suite_name, df in TestDfs.items():
            # Convert DataFrame to AsciiDoc format
            adoc_content = self.dataframe_to_asciidoc_txt(df,suite_name)
            # Write to file
            if output_adoc_path.exists():
                write_mode = "a"  # Append mode
            else:
                write_mode = "w"

            with open(output_adoc_path, write_mode, encoding="utf-8") as adoc_file:
                adoc_file.write(adoc_content)
        print(f"AsciiDoc file created: {output_adoc_path}")
        # grouped_suites = self.parse_and_group_testsuites()
        # my_etree = self.build_hierarchical_xml(grouped_suites)
        # self.create_adoc(my_etree)

    def dataframe_to_asciidoc_txt(self,df,suite_name=None):
        lines = []
        headers = df.columns.tolist()
        if suite_name:
            lines.append(f"== {suite_name}\n")

        lines.append('[options="header"]')
        lines.append('|===')
        lines.append('|' + ' |'.join(headers))

        for _, row in df.iterrows():
            lines.append('|' + ' |'.join(str(cell) for cell in row))

        lines.append('|===')
        lines.append('\n\n')
        return '\n'.join(lines)



    def parse_failure_element(self,failure_element):
        """
        parses out Expected value and asserted value in failure report element, and
        returns it in a way that will fit in an adoc table fine

        Parses the message string in the failiure message.

        Args:
            failure_element (lxml.etree.Element): failure element in xml report typically an element will look like :literal:`<failure message="{Expected value: TRUE, Asserted value: FALSE}">"FAIL"</failure>`

        Returns:
            str: a string that will not break in an adoc table formatting

        """
        errorRegex = r'{Expected value: (.*), Asserted value: (.*)}'
        raw_failure_message = failure_element.get("message", "Unknown reason")
        match = re.match(errorRegex, raw_failure_message)
        if match:
            expected_value, asserted_value = match.groups()
            failure_message = f"Expected value: {expected_value} +\nAsserted value:  {asserted_value}"#the + symbol here before the newline is to make the adoc table formatting work
        else:
            failure_message = raw_failure_message
        
        return failure_message

    def create_adoc(self,tree):
        """
        Parses an xml test report file from Caraya and writes the results to an adoc file

        Args:
            xml_file (str): path to the xml file to be parsed
            output_adoc (str): path to the adoc file to be written
        Returns:
            None - but writes the adoc file to the output path
        """
        root = tree.getroot()
        mainTestGroups = root.getchildren()
        timestamp = None#init timestamp to populate with first testsuite timestamp
        with open(self.output_adoc, "w",encoding="utf-8") as adoc:
            adoc.write("= Test Results Documentation\n\n")
            for testGroup in mainTestGroups:
                mainTestSuites = testGroup.getchildren()
                group_name = testGroup.get("name")
                adoc.write(f"== {group_name}\n\n")
                for testsuite in mainTestSuites:
                    suite_name = testsuite.get("name")
                    total_tests = testsuite.get("tests")
                    errors = testsuite.get("errors")
                    failures = testsuite.get("failures")
                    test_timestamp = testsuite.get('timestamp')
                    if not timestamp:
                        timestamp = test_timestamp
                    nPassedTests = int(total_tests) - int(errors) - int(failures)

                    adoc.write(f"=== {suite_name}\n\n")
                    adoc.write(f"* Total Tests: {total_tests}\n\
                                * Passed Tests : {nPassedTests}\n")
                    errors = testsuite.get('errors')
                    if int(errors) !=0:
                        adoc.write(f"* Errors : {errors}\n")
                    failures = testsuite.get('failures')
                    if int(failures) !=0:
                        adoc.write(f"* Failures ‼: {failures}\n")

                    adoc.write("|====\n| Test Name | Status | Failure Reason \n\n")
                    
                    for testcase in testsuite.findall("testcase"):
                        test_name = testcase.get("name")
                        failure = testcase.find("failure")
                        skipped = testcase.find("skipped")
                        
                        if failure is not None:
                            status = "FAIL "
                            reason = self.parse_failure_element(failure)
                        elif skipped is not None:
                            status = "SKIPPED "
                            reason = "Test was skipped"
                        else:
                            status = "PASS "
                            reason = "-"
                        
                        adoc.write(f"| {test_name} | {status} | {reason} \n\n")
                    
                    adoc.write("|====\n\n")

            if not timestamp:
                timestamp = "1970-01-01T00:00:00"  # Default timestamp 
            # reformatting test timestamp to look more readable
            dt = datetime.fromisoformat(timestamp)
            readable_timestamp = dt.strftime("%A, %d %B %Y %I:%M:%S %p (UTC%z)")
            # writing general information for the test to the end of the file
            adoc.write(f"Tests performed using framework: {root.get('framework-name','not specified')} \
                    V:{root.get('framework-version','unknown')}\n\
                    Test run on: {readable_timestamp}\n\n")
        
        print(f"Documentation written to {self.output_adoc}")

    def get_group_key(self,testsuite_name):
            # Example: from "Test-ATOCStatus_Req" -> "Test-ATOC"
            parts = testsuite_name.split('-')
            if parts[0].lower() == "test" and len(parts) >= 2:
                # If the first part is "Test", return the second part
                return parts[1]
            else:
                return testsuite_name

    def parse_and_group_testsuites(self):
        grouped_suites = defaultdict(list)

        for file in self.xml_files:
            tree = etree.parse(file)
            root = tree.getroot()
            for testsuite in root.findall('testsuite'):
                name = testsuite.get('name')
                group = self.get_group_key(name)
                print(f"Grouping testsuite '{name}' under group '{group}'")
                grouped_suites[group].append(testsuite)

        return grouped_suites

    def build_hierarchical_xml(self,grouped_suites):
        root = etree.Element('testgroups')

        for group_name, suites in grouped_suites.items():
            group_elem = etree.SubElement(root, 'testgroup', name=group_name)
            for suite in suites:
                group_elem.append(suite)

        return etree.ElementTree(root)


# def parse_multiple_to_adoc(dict_of_xmls,outputfile,temp_XML_Folder):
#     """
#     parses a list of dictionarys of xml filepaths to one cohesive Adoc output

#     list of dictionaries should look like:
#     [{'test_name':<name>,'xml_filepath':<filepath_to_xml>},
#     {'test_name':<name>,'xml_filepath':<filepath_to_xml>},...]

#     where filepath_to_xml can be a string of pathlib.Path object
#     """
#     #temp_XML_Folder = Path(temp_XML_Folder)
#     filemode = 'w+'
#     for iXML in dict_of_xmls:
#         output_ADoc = temp_XML_Folder.joinpath(f"{iXML['test_name']}.adoc")
        
#         obj = caraya_xml_to_adoc(iXML['xml_filepath'],output_ADoc,write_header=filemode=="w+")
#         obj.create_adoc()
#         #read contents of adoc and dump into output file
#         with open(output_ADoc,'r') as adocfile:
#             adocContents = adocfile.read()
        
#         #write to output file
#         with open(outputfile,filemode) as f:
#             f.write(adocContents)
#         if filemode == 'w+':
#             filemode = 'a'#change to append after first file

    


    




if __name__ == "__main__":
    """
    runs test on example files
    """
    # baseDir = os.path.join("..","Tests","exampleFiles")
    # baseDir = os.path.abspath(baseDir)
    # TEST_REPORT_XML = os.path.join(baseDir,"exampleTestXml.xml")
    # CONVERTED_ADOC_FILEPATH = os.path.join(baseDir,"exampleTestAdoc.adoc")
    
    # xmlObject = caraya_xml_to_adoc(TEST_REPORT_XML,CONVERTED_ADOC_FILEPATH)
    # xmlObject.create_adoc()

    # parse_xml_to_adoc(TEST_REPORT_XML,CONVERTED_ADOC_FILEPATH)
    # Path to your XML files

    parser = Caraya_Parser(Path(__file__).parent.joinpath("../tests/fixtures/carara_example_xmls"), "output.adoc")
    parser.process_xml_files()
