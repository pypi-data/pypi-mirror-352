import os
from typing import Union
import yaml as pyyaml

from tagmapper.mapping import Constant, Mapping, Timeseries


class Attribute:
    """
    Attribute class.

    An attribute is a defined property of a generic model.
    """

    def __init__(self, name, data):
        """Initialize an Attribute instance. NB! Does not specify any mappings

        Args:
            name (str): The name of the attribute.
            data (dict): The data for the attribute. The dictionary should contain
                the keys "identifier", "description", "alias", and "type" to set
                the corresponding attributes.

        Raises:
            ValueError: If the input data is not a dictionary.
        """
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dict")

        self.name = name
        if "identifier" in data.keys():
            self.identifier = data["identifier"]
        else:
            self.identifier = name.lower().replace(" ", "_")

        # identifier naming rule not enforced yet
        if False and self.identifier != self.identifier.replace(" ", "_"):
            raise ValueError("Invalid identifier. Whitespace is not allowed.")

        self.description = ""
        if "description" in data.keys():
            self.description = data["description"]

        self.alias = ""
        if "alias" in data.keys():
            self.alias = data["alias"]

        # Currently supports types: timeseries, constant
        self.type = ""
        if "type" in data.keys():
            self.type = data["type"]

        # Each attribute can have multiple mappings
        self.mapping = []

    def add_mapping(self, mapping: Union[Mapping, dict]):
        """
        Add a mapping to the attribute
        """
        if isinstance(mapping, dict):
            if "ConstantValue" in mapping.keys():
                mapping = Constant(mapping)
            elif "Timeseries" in mapping.keys():
                mapping = Timeseries(mapping)
            else:
                raise ValueError(
                    "Mapping provided as dict must be a Constant or Timeseries"
                )

        if not isinstance(mapping, Mapping):
            raise ValueError(
                "Input mapping must be a Mapping or a dict that can construct a Mapping."
            )

        if mapping.mode not in [x.mode for x in self.mapping]:
            self.mapping.append(mapping)
        else:
            raise ValueError(
                f"Mapping for mode {mapping.mode} already exists in attribute {self.name}"
            )

    def print_report(self):
        """
        Print a report of the attribute
        """
        print("Attribute Report")
        print(f"Name: {self.name}")
        print(f"Identifier: {self.identifier}")
        print(f"Description: {self.description}")
        print(f"Alias: {self.alias}")
        print(f"Type: {self.type}")
        print("Mappings:")
        for mapping in self.mapping:
            print(f"  {mapping}")

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Attribute):
            return NotImplemented

        return (
            self.name == value.name
            and self.identifier == value.identifier
            and self.description == value.description
            and self.alias == value.alias
            and self.type == value.type
            and len(self.mapping) == len(value.mapping)
            and all(self.mapping[i] in value.mapping for i in range(len(self.mapping)))
        )

    def __str__(self):
        alias = self.alias if self.alias else "''"
        description = self.description if self.description else "''"
        return f"Attribute: {self.name} - ({self.identifier}) - {alias} - {self.type} - {description}"


class ModelTemplate:
    """
    Class defining model templates, i.e., models with a set of attributes.

    An instantiated model with mappings to a specific object is called a Model.
    """

    def __init__(self, yaml: Union[dict, str]):
        if isinstance(yaml, dict):
            data = yaml
        else:
            if not isinstance(yaml, str):
                raise ValueError("Input yaml must be a dict or a yaml string")
            if os.path.isfile(yaml):
                with open(yaml, "r") as f:
                    data = pyyaml.safe_load(f)
            else:
                data = pyyaml.safe_load(yaml)

        if "model" in data.keys():
            data = data["model"]

        if "owner" not in data.keys():
            raise ValueError("Model data must contain an 'owner' key")
        self.owner = str(data.get("owner"))
        if "name" not in data.keys():
            raise ValueError("Model data must contain a 'name' key")
        self.name = str(data.get("name"))
        self.description = str(data.get("description", ""))
        self.version = data.get("version", -1)

        self.attribute = []
        if "attribute" in data.keys():
            attributes = data["attribute"]
            if isinstance(attributes, list):
                self.attribute = attributes.copy()
            elif isinstance(attributes, dict):
                for attkey in attributes.keys():
                    self.attribute.append(Attribute(attkey, attributes[attkey]))
            else:
                raise ValueError("Attribute data must be a list or a dict")

    def get_attribute(self, name: str) -> Attribute:
        """
        Get an attribute by name
        """
        for attribute in self.attribute:
            if attribute.name == name:
                return attribute

        for attribute in self.attribute:
            if attribute.alias == name:
                return attribute

        for attribute in self.attribute:
            if attribute.identifier == name:
                return attribute
        raise ValueError(f"Attribute {name} not found in model {self.name}")

    def get_yaml_file(self, filename: str = ""):
        if filename is None or len(filename):
            filename = f"{self.owner}_{self.name}.yaml"

        if not filename.endswith(".yaml"):
            filename += ".yaml"

        with open(filename, "w") as f:
            pyyaml.dump(self.__dict__, f, default_flow_style=False)

    def get_yaml(self):
        """
        Get the YAML file for the model
        """
        yaml_dict = self.__dict__.copy()
        yaml_dict["attribute"] = {}
        for att in self.attribute:
            if isinstance(att, Attribute):
                yaml_dict["attribute"][att.name] = att.__dict__.copy()
                yaml_dict["attribute"][att.name].pop("mapping", None)
        d = {"model": yaml_dict}
        return pyyaml.dump(d, sort_keys=False, default_flow_style=False)

    def print_report(self):
        """
        Print a report of the model template
        """
        print("Generic Model Template Report")
        print(f"Model Owner: {self.owner}")
        print(f"Model Name: {self.name}")
        print(f"Model Description: {self.description}")
        print(f"Model Version: {self.version}")
        print("Attributes:")
        for attribute in self.attribute:
            print(f"  {attribute}")

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ModelTemplate):
            return NotImplemented

        return (
            self.owner == value.owner
            and self.name == value.name
            and self.description == value.description
            and self.version == value.version
            and len(self.attribute) == len(value.attribute)
            and all(
                self.attribute[i] in value.attribute for i in range(len(self.attribute))
            )
        )

    def __str__(self):
        return f"Generic Model Template: {self.owner} - {self.name} - {self.description} - {self.version}"
