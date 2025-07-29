from dataclasses import dataclass

from context_configuration.context_configuration import ContextConfigurationBuilder, Property
from context_configuration.converter.dataclass_converter import DataclassConverter
from context_configuration.property_source.env_vars_property_source import EnvVarsPropertySource


@dataclass
class Policy:
    name: str
    description: str


dataclass_converter = DataclassConverter(Policy)

conf = (ContextConfigurationBuilder()
        .with_property_source(EnvVarsPropertySource())
        .with_converter((dataclass_converter.for_type(), dataclass_converter.convert))
        .build())


@conf.properties(properties=[
    Property("name", "name", str),
    Property("description", "description", str),
], is_singleton=False)
def get_policy(name, description):
    return Policy(name, description)


@conf.properties(properties=[
    Property("name", "a", str),
    Property("description", "b", str),
], is_singleton=True)
def get_new_policy(name, description):
    return Policy(name, description)


def main():
    print(get_policy())
    print(get_policy())
    print(get_new_policy())
    print(get_new_policy())


if __name__ == '__main__':
    main()
