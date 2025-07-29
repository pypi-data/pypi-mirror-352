from eo4eu_data_utils.config import ConfigSource


def test_source_0():
    source = ConfigSource().use_env().use_files()

    print(source.get("configmaps", "eo4eu", "namespace"))
    print(source.get_or("configmaps", "eo4eu", "ns", default = "unknown"))


def test_source_1():
    source = ConfigSource().use_env().use_files()

    print(source.get("configmaps", "eo4eu", "namspace"))
    print(source.get_or("secrets", "eo4eu", "ns", default = "unknown"))


if __name__ == "__main__":
    test_source_0()
    test_source_1()
