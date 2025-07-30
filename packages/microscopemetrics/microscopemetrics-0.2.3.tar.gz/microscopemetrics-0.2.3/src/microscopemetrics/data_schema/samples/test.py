# Auto generated from test.yaml by pythongen.py version: 0.9.0
# Generation date: 2023-08-17T14:01:39
# Schema: microscopemetrics_samples_field_illumination_schema
#
# id: https://github.com/MontpellierRessourcesImagerie/microscope-metrics/blob/main/src/microscopemetrics/data_schema/samples/field_illumination_schema.yaml
# description:
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import re
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Union

from jsonasobj2 import JsonObj, as_dict
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions,
)
from linkml_runtime.linkml_model.types import Float
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.dataclass_extensions_376 import (
    dataclasses_init_fn_with_kwargs,
)
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import camelcase, sfx, underscore
from linkml_runtime.utils.metamodelcore import bnode, empty_dict, empty_list
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str,
)
from rdflib import Namespace, URIRef

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
LINKML = CurieNamespace("linkml", "https://w3id.org/linkml/")
DEFAULT_ = CurieNamespace(
    "",
    "https://github.com/MontpellierRessourcesImagerie/microscope-metrics/blob/main/src/microscopemetrics/data_schema/samples/field_illumination_schema.yaml/",
)


# Types

# Class references


@dataclass
class MyClass(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef(
        "https://github.com/MontpellierRessourcesImagerie/microscope-metrics/blob/main/src/microscopemetrics/data_schema/samples/field_illumination_schema.yaml/MyClass"
    )
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "MyClass"
    class_model_uri: ClassVar[URIRef] = URIRef(
        "https://github.com/MontpellierRessourcesImagerie/microscope-metrics/blob/main/src/microscopemetrics/data_schema/samples/field_illumination_schema.yaml/MyClass"
    )

    my_slot: Optional[Union[float, List[float]]] = 0.3

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.my_slot, list):
            self.my_slot = [self.my_slot] if self.my_slot is not None else []
        self.my_slot = [v if isinstance(v, float) else float(v) for v in self.my_slot]

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass


slots.my_slot = Slot(
    uri=DEFAULT_.my_slot,
    name="my_slot",
    curie=DEFAULT_.curie("my_slot"),
    model_uri=DEFAULT_.my_slot,
    domain=None,
    range=Optional[Union[float, List[float]]],
)
