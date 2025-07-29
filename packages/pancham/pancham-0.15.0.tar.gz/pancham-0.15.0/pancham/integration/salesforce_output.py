from io import StringIO

import pandas as pd

from .salesforce_connection import get_connection
from pancham.output_configuration import OutputConfiguration, OutputWriter

SALESFORCE_BULK = 'salesforce_bulk'

class SalesforceBulkOutputConfiguration(OutputConfiguration):

    def can_apply(self, configuration: dict):
        """
        Determines whether the Salesforce Bulk configuration can be applied
        based on the presence and validity of required keys.

        :param configuration: A dictionary containing the configuration details.
        :type configuration: dict
        :return: A boolean indicating whether the configuration is valid
                 and can be applied.
        :rtype: bool
        :raises ValueError: If the Salesforce Bulk configuration is present
                            but missing the 'object_name' key.
        """
        salesforce_configuration = self.extract_configuration_by_key(configuration, SALESFORCE_BULK)

        if salesforce_configuration is None:
            return False

        if 'object_name' not in salesforce_configuration:
            raise ValueError('SalesforceBulkOutput requires an object_name')

        return True

    def to_output_configuration(self, configuration: dict):
        """
        Converts the given configuration dictionary into an output-specific configuration
        by extracting the Salesforce configuration using a predefined key. If the Salesforce
        configuration is not set, an exception is raised.

        :param configuration: The full configuration dictionary to extract the
                              Salesforce-specific configuration from. It expects
                              a dictionary with valid Salesforce configurations stored
                              under the specific key.
        :type configuration: dict

        :return: A dictionary representing the Salesforce-specific configuration
                 extracted from the input configuration.
        :rtype: dict

        :raises ValueError: Raised when the Salesforce configuration is not found
                            in the given input dictionary.
        """
        salesforce_configuration = self.extract_configuration_by_key(configuration, SALESFORCE_BULK)

        if not salesforce_configuration:
            raise ValueError('Salesforce configuration not set')

        return salesforce_configuration


class SalesforceBulkOutputWriter(OutputWriter):

    def write(self, data: pd.DataFrame, configuration: dict):
        """
        Writes data to a Salesforce object using the Salesforce Bulk API 2.0. The method
        uses the provided configuration to determine the object name and how to handle
        successful and failed records. Data is processed in bulk and relevant handlers
        are invoked for success and failure cases.

        The data provided is first converted into a list of dictionaries representing records.
        The function then interacts with the Salesforce client, performing batch insert
        operations. After submission, success and failure handlers are employed (if configured)
        to process the resulting records.

        :param data: The data to be inserted into the Salesforce object. It is expected
            to be in the form of a pandas DataFrame.
        :type data: pd.DataFrame
        :param configuration: A dictionary containing configuration details. Must include
            the key "object_name" to specify the target Salesforce object. Additionally, keys
            for "success_handler" and "failure_handler" may define processing behaviors for
            successful and failed records.
        :type configuration: dict
        :return: None
        """
        sf = get_connection()

        data_dict = data.to_dict('records')
        object_name = configuration['object_name']
        results = sf.bulk2[object_name].insert(records = data_dict)

        for r in results:
            job_id = r['job_id']

            success_handler = self.__get_handler_configuration(configuration, 'success_handler')
            failure_handler = self.__get_handler_configuration(configuration, 'failure_handler')

            if success_handler is not None:
                success = sf.bulk2[object_name].get_successful_records(job_id)
                self.__save_handled_data(success, success_handler)

            if failure_handler is not None:
                failed = sf.bulk2[object_name].get_failed_records(job_id)
                self.__save_handled_data(failed, failure_handler)

    def __get_handler_configuration(self, configuration: dict, handler_name: str) -> dict|None:
        """
        Extracts and returns the configuration for a specific handler from
        the provided configuration dictionary. If the handler exists and has
        an 'instance' key, its configuration is returned. Otherwise, returns None.

        :param configuration: Dictionary containing configurations where
            each key represents a handler name, and its value is another
            dictionary that may include an 'instance' key.
        :type configuration: dict
        :param handler_name: The name of the handler for which the
            configuration is being retrieved.
        :type handler_name: str
        :return: The configuration dictionary for the specified handler
            if it exists and contains an 'instance' key; otherwise, None.
        :rtype: dict | None
        """
        if handler_name in configuration and 'instance' in configuration[handler_name]:
            return configuration[handler_name]

        return None

    def __save_handled_data(self, data: str, handler_configuration: dict):
        """
        Handles the saving of processed data using a configured output writer.

        This method reads data in CSV format, processes it into a pandas DataFrame, and
        writes the result using the provided output writer instance. The handler
        configuration must include the instance of an OutputWriter to determine how
        and where the data is saved.

        :param data: The string containing CSV formatted data to be handled and saved.
        :type data: str
        :param handler_configuration: A dictionary containing the configuration for the
            output writer. Must include the key 'instance' associated with an
            OutputWriter object.
        :type handler_configuration: dict
        :return: None
        """
        handler: OutputWriter = handler_configuration['instance']

        df = pd.read_csv(StringIO(data))
        handler.write(df, handler_configuration)

