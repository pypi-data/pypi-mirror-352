import pandas as pd

class OutputConfiguration:
    """
    Represents the configuration used for output operations.

    This class encapsulates settings and functionality specific to managing
    the configuration of data output processes. It is used to determine if
    certain configurations can be applied and to apply them to a given dataset.

    :ivar attribute1: Description of attribute1.
    :type attribute1: type
    :ivar attribute2: Description of attribute2.
    :type attribute2: type
    """

    def can_apply(self, configuration: dict):
        """
        Determines whether the given configuration is eligible for
        application based on the specified logic. This method evaluates
        the contents of the input dictionary and returns a boolean value
        indicating whether the configuration meets the required conditions.

        :param configuration: A dictionary containing configuration values
            to be checked for applicability.
        :type configuration: dict
        :return: A boolean indicating if the configuration can be applied.
        :rtype: bool
        """
        pass

    def to_output_configuration(self, configuration: dict):
        """
        Converts the given input configuration dictionary into an output configuration
        dictionary. This method processes the specified input configuration to generate
        an appropriately structured output configuration.

        :param configuration: Input configuration dictionary containing the necessary
            data to be transformed.
        :type configuration: dict
        :return: The transformed output configuration dictionary based on the input
            configuration.
        :rtype: dict
        """
        pass

    def extract_configuration_by_key(self, configuration: dict, key: str) -> dict|None:
        """
        Extracts a specific configuration from a dictionary based on a given key.

        This function searches within the 'output' section of the provided
        configuration dictionary to find a matching entry where the 'output_type'
        matches the specified key. If a match is found, the corresponding dictionary
        is returned. If the 'output' section is not present in the configuration or no
        match is found, the function returns None.

        :param configuration: A dictionary containing the data to be searched, which
            should include an 'output' key with a list of configurations.
        :param key: The key used to match the 'output_type' in the entries within the
            'output' list.
        :return: A dictionary representing the matched configuration, or None if no
            match is found.
        """

        if not 'output' in configuration:
            return None

        matched: dict|None = None

        for out in configuration['output']:
            if out['output_type'] == key:
                matched = out
                break

        return matched



class OutputWriter:
    """
    Write the output data to the target system
    """

    def write(self, data: pd.DataFrame, configuration: dict):
        """
        Writes the provided data to a destination as specified in the configuration.

        This method takes a pandas DataFrame and a dictionary containing configurations,
        and processes them to perform a write operation. The `configuration` parameter
        determines how the data will be written, including any necessary settings,
        formats, or connection details. This method encapsulates the logic for a
        write operation based on the input.

        :param data: The pandas DataFrame to be written.
        :type data: pd.DataFrame
        :param configuration: A dictionary containing the configuration parameters
            for the write operation. May include file format, destination details,
            or additional settings required for the writing process.
        :type configuration: dict
        :return: None
        """
        pass