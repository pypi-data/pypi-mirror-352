import json
from typing import List, Literal, Optional, Union

from tagmapper.connector_api import (
    get_generic_model_mappings,
    post_generic_model_mapping,
)
from tagmapper.generic_model_template import Attribute, ModelTemplate
from tagmapper.mapping import Constant, Timeseries


def post_timeseries_mapping(
    object_name: str,
    model_owner: str,
    model_name: str,
    attribute_name: str,
    time_series_tag_no: str,
    timeseries_source: str,
    mode: Optional[str] = "",
    unit_of_measure: Optional[str] = "",
    comment: Optional[str] = "",
):
    """
    Post a timeseries to the API
    """
    timeseries_dict = make_timeseries_mapping_dict(
        object_name,
        model_owner,
        model_name,
        attribute_name,
        time_series_tag_no,
        timeseries_source,
        mode,
        unit_of_measure,
        comment,
    )

    return post_generic_model_mapping(timeseries_dict)


def make_timeseries_mapping_dict(
    object_name: str,
    model_owner: str,
    model_name: str,
    attribute_name: str,
    time_series_tag_no: str,
    timeseries_source: str,
    mode: Optional[str] = "",
    unit_of_measure: Optional[str] = "",
    comment: Optional[str] = "",
):
    timeseries_dict = {
        "unique_object_identifier": object_name,
        "model_owner": model_owner,
        "model_name": model_name,
        "mode": mode,
        "UnitOfMeasure": unit_of_measure,
        "TimeseriesSource": timeseries_source,
        "comment": comment,
        "AttributeName": attribute_name,
        "TimeSeriesTagNo": time_series_tag_no,
    }

    return timeseries_dict


def post_constant_mapping(
    object_name: str,
    model_owner: str,
    model_name: str,
    attribute_name: str,
    value: str,
    mode: Optional[str] = "",
    unit_of_measure: Optional[str] = "",
    comment: Optional[str] = "",
):
    """
    Post a constant to the API
    """

    return post_generic_model_mapping(
        make_constant_mapping_dict(
            object_name,
            model_owner,
            model_name,
            attribute_name,
            value,
            mode,
            unit_of_measure,
            comment,
        )
    )


def make_constant_mapping_dict(
    object_name: str,
    model_owner: str,
    model_name: str,
    attribute_name: str,
    value: str,
    mode: Optional[str] = "",
    unit_of_measure: Optional[str] = "",
    comment: Optional[str] = "",
):
    constant_dict = {
        "unique_object_identifier": object_name,
        "model_owner": model_owner,
        "model_name": model_name,
        "mode": mode,
        "UnitOfMeasure": unit_of_measure,
        "comment": comment,
        "AttributeName": attribute_name,
        "ConstantValue": value,
    }

    return constant_dict


def get_mappings(
    model_owner: str = "",
    model_name: str = "",
    object_name: str = "",
    attribute_type: Optional[Literal["constant", "timeseries"]] = None,
) -> List[dict[str, str]]:
    """
    Get generic model mappings from the API as List of dicts
    """

    if attribute_type is None:
        const = get_mappings(
            model_owner=model_owner,
            model_name=model_name,
            object_name=object_name,
            attribute_type="constant",
        )

        ts = get_mappings(
            model_owner=model_owner,
            model_name=model_name,
            object_name=object_name,
            attribute_type="timeseries",
        )
        const.extend(ts)
        return const

    model_dict = {
        "Model_Owner": model_owner,
        "Attribute_Type": str(attribute_type),
        "Model_Name": model_name,
        "unique_object_identifier": object_name
    }

    return get_generic_model_mappings(data=model_dict)


class Model(ModelTemplate):
    """
    Generic model class including mappings
    """

    def __init__(self, data: dict[str, str]):
        """Initialize a Model object.

        Args:
            data (dict[str, str]): Input data for the model. The dictionary should contain
                the keys "name", "description", "comment", "owner", and "object_name" to set
                the corresponding attributes.

        Raises:
            ValueError: If the input data is not a dictionary or if required keys are missing.
        """
        super().__init__(data)

        if not isinstance(data, dict):
            raise ValueError("Input data must be a dict")

        # Model object name is the unique identifier for the object the model is associated with
        if "object_name" not in data.keys() or len(data["object_name"]) == 0:
            raise ValueError("Input data must contain a valid 'object_name' key")
        self.object_name = data["object_name"]
        self.comment = data.get("comment", "")

    def add_attribute(
        self,
        type: Literal["constant", "timeseries"],
        name: str,
        identifier: Optional[str] = "",
        description: Optional[str] = "",
        alias: Optional[str] = "",
    ):
        """
        Add an attribute to the model.
        """

        if not identifier or len(identifier) == 0:
            identifier = name.lower().replace(" ", "_")

        if identifier != identifier.lower().replace(" ", "_"):
            raise ValueError(
                "Invalid identifier. Capital letters and whitespace is not allowed."
            )

        if not identifier or not type:
            raise ValueError("Identifier and type are required")

        attr = Attribute(
            name,
            {
                "identifier": identifier,
                "type": type,
                "description": description,
                "alias": alias,
            },
        )

        if attr.name in [a.name for a in self.attribute]:
            raise ValueError(f"Attribute {attr.name} already exists in the model")

        if attr.identifier in [a.identifier for a in self.attribute]:
            raise ValueError(
                f"Identifier {attr.identifier} already exists in the model"
            )

        self.attribute.append(attr)

    def add_constant_attribute(
        self,
        name: str,
        identifier: Optional[str] = "",
        description: Optional[str] = "",
        alias: Optional[str] = "",
    ):
        """
        Add an attribute of type Constant to the model.
        """
        self.add_attribute("constant", name, identifier, description, alias)

    def add_timeseries_attribute(
        self,
        name: str,
        identifier: Optional[str] = "",
        description: Optional[str] = "",
        alias: Optional[str] = "",
    ):
        """
        Add an attribute of type Timeseries to the model.
        """

        self.add_attribute("timeseries", name, identifier, description, alias)

    def add_mapping(self, attribute_name, mapping: Union[Constant, Timeseries, dict]):
        """
        Add an attribute to the model
        """

        if isinstance(mapping, dict):
            if "ConstantValue" in mapping.keys():
                mapping = Constant(mapping)
            elif "Timeseries" in mapping.keys():
                mapping = Timeseries(mapping)
            else:
                raise ValueError("Mapping must be a Constant or Timeseries")

        if not isinstance(mapping, (Constant, Timeseries)):
            raise ValueError("Input data must be a Constant or Timeseries")

        if attribute_name in [a.name for a in self.attribute]:
            # Update existing attribute
            for i, attr in enumerate(self.attribute):
                if attr.name == attribute_name:
                    if attr.type.lower() == mapping.__class__.__name__.lower():
                        self.attribute[i].add_mapping(mapping)
                    else:
                        raise ValueError(
                            f"Attribute {attribute_name} is a {attr.type} while mapping is a {mapping.__class__.__name__}"
                        )
        elif attribute_name in [a.identifier for a in self.attribute]:
            # Update existing attribute
            for i, attr in enumerate(self.attribute):
                if attr.identifier == attribute_name:
                    if attr.type.lower() == mapping.__class__.__name__.lower():
                        self.attribute[i].add_mapping(mapping)
                    else:
                        raise ValueError(
                            f"Attribute {attribute_name} is a {attr.type} while mapping is a {mapping.__class__.__name__}"
                        )
        else:
            raise ValueError(
                f"Attribute {attribute_name} does not exist in the model. Please add it first."
            )

    def add_constant_mapping(
        self,
        attribute_name: str,
        value: str,
        unit_of_measure: Optional[str] = None,
        comment: Optional[str] = None,
        mode: Optional[str] = None,
    ):
        """
        Add an  of type Constant to the model. If the attribute already exists,
        it will be updated.
        """

        self.add_mapping(
            attribute_name,
            Constant.create(
                value=value,
                unit_of_measure=unit_of_measure,
                comment=comment,
                mode=mode,
            ),
        )

    def add_timeseries_mapping(
        self,
        attribute_name: str,
        tagNo: str,
        source: str,
        unit_of_measure: Optional[str] = None,
        comment: Optional[str] = None,
        mode: Optional[str] = None,
    ):
        """
        Add a mapping of type Timeseries to the attribute. If a mapping with the the same mode already exists,
        it will be updated.
        """

        self.add_mapping(
            attribute_name,
            Timeseries.create(
                tag=tagNo,
                source=source,
                unit_of_measure=unit_of_measure,
                comment=comment,
                mode=mode,
            ),
        )

    def post_mappings(self, model_owner: str = "", model_name: str = ""):
        if model_owner is None or len(model_owner) == 0:
            model_owner = self.owner

        if model_name is None or len(model_name) == 0:
            model_name = self.name

        mappings = []
        for att in self.attribute:
            for mapping in att.mapping:
                if isinstance(mapping, Constant):
                    mappings.append(
                        make_constant_mapping_dict(
                            object_name=self.object_name,
                            model_owner=model_owner,
                            model_name=model_name,
                            attribute_name=att.name,
                            value=mapping.value,
                            mode=mapping.mode,
                            unit_of_measure=mapping.unit_of_measure,
                            comment=mapping.comment,
                        )
                    )
                elif isinstance(mapping, Timeseries):
                    mappings.append(
                        make_timeseries_mapping_dict(
                            object_name=self.object_name,
                            model_owner=model_owner,
                            model_name=model_name,
                            attribute_name=att.name,
                            time_series_tag_no=mapping.tag,
                            timeseries_source=mapping.source,
                            mode=mapping.mode,
                            unit_of_measure=mapping.unit_of_measure,
                            comment=mapping.comment,
                        )
                    )
        if len(mappings) > 0:
            post_generic_model_mapping(mappings)

    def get_mappings(self):
        mappings = get_mappings(
            model_owner=self.owner, model_name=self.name, object_name=self.object_name
        )
        for map in mappings:
            if "ConstantValue" in map.keys():
                self.add_constant_mapping(
                    attribute_name=map["AttributeName"],
                    value=map["ConstantValue"],
                    unit_of_measure=map["UnitOfMeasure"],
                    comment=map["comment"],
                    mode=map["mode"],
                )
            else:
                self.add_timeseries_mapping(
                    map["AttributeName"],
                    map["TimeSeriesTagNo"],
                    map["TimeseriesSource"],
                    unit_of_measure=map["UnitOfMeasure"],
                    comment=map["comment"],
                    mode=map["mode"],
                )

    def print_report(self):
        """
        Print a report of the model
        """
        print("Model Report")
        print(f"Model Object Name: {self.object_name}")
        print(f"Model Comment: {self.comment}")
        print(f"Model Owner: {self.owner}")
        print(f"Model Name: {self.name}")
        print(f"Model Description: {self.description}")
        print(f"Model Version: {self.version}")
        print("Attributes:")
        for attribute in self.attribute:
            print(f"  {attribute}")
            for mapping in attribute.mapping:
                print(f"    {mapping}")

    def to_json(self, file_path: Optional[str] = None, indent: int = 0):
        if file_path is None or len(file_path) == 0:
            return json.dumps(self, default=vars, indent=indent)

        with open(file_path, "w") as f:
            json.dump(self, f, default=vars, indent=indent)

    @staticmethod
    def from_ModelTemplate(
        model_template: ModelTemplate, object_name: str = "", comment: str = ""
    ) -> "Model":
        """
        Create a Model from a ModelTemplate.
        This method copies the attributes from the ModelTemplate and adds the object_name and comment.
        Args:
            model_template (ModelTemplate): The ModelTemplate to copy attributes from.
            object_name (str): The unique identifier for the object the model is associated with.
            comment (str): An optional comment for the model.
        Returns:
            Model: A new Model instance with attributes copied from the ModelTemplate.
        """
        if not isinstance(model_template, ModelTemplate):
            raise ValueError("Input data must be a ModelTemplate")

        data = model_template.__dict__.copy()
        data["object_name"] = object_name
        data["comment"] = comment

        return Model(data=data)

    @staticmethod
    def get_model(model_owner: str = "", model_name: str = "", object_name: str = ""):
        """
        Get a model from the API, with no schema.
        """
        mappings = get_mappings(
            model_owner=model_owner, model_name=model_name, object_name=object_name
        )

        if not mappings or len(mappings) == 0:
            raise ValueError("No mappings found for model")

        data = {}
        data["name"] = mappings[0]["model_name"]
        data["description"] = ""
        data["owner"] = mappings[0]["model_owner"]
        data["object_name"] = mappings[0]["unique_object_identifier"]

        mod = Model(data=data)
        for map in mappings:
            if "ConstantValue" in map.keys():
                mod.add_constant_attribute(name=map["AttributeName"])
                mod.add_constant_mapping(
                    attribute_name=map["AttributeName"],
                    value=map["ConstantValue"],
                    unit_of_measure=map["UnitOfMeasure"],
                    comment=map["comment"],
                    mode=map["mode"],
                )
            else:
                mod.add_timeseries_attribute(name=map["AttributeName"])
                mod.add_timeseries_mapping(
                    attribute_name=map["AttributeName"],
                    tagNo=map["TimeSeriesTagNo"],
                    source=map["TimeseriesSource"],
                    unit_of_measure=map["UnitOfMeasure"],
                    comment=map["comment"],
                    mode=map["mode"],
                )

        return mod
