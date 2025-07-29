"""
This module contains tests for the main functionality of the tomldantic library.
It tests the conversion of Pydantic models to TOML strings and vice versa.
It also checks the handling of various Pydantic features such as default values,
required fields, nested models, and descriptions.

"""

# pylint: disable=disallowed-name

import pytest
import toml
from pydantic import BaseModel, Field
from toml import TomlDecodeError

import tomldantic as tomldantic


def test_basic_types_with_defaults() -> None:
    """This is the most basic use case with the types string, float and integer."""

    class TestModel(BaseModel):
        """This is the documentation for the TestModel."""

        s: str = "hello"
        i: int = 42
        f: float = 3.14

    expected = "\n".join(
        [
            "",
            "# This is the documentation for the TestModel.",
            "",
            's = "hello"',
            "i = 42",
            "f = 3.14",
        ]
    )

    # create schema and toml template
    result = tomldantic.dumps(TestModel)
    assert result.strip() == expected.strip()


def test_basic_types_with_required_arguments() -> None:
    """This is the most basic use case with the types string, float and integer
    but without default values."""

    # pylint: disable=missing-class-docstring
    class TestModel(BaseModel):
        s: str
        i: int
        f: float

    expected = "\n".join(
        [
            "s = <string>",
            "i = <integer>",
            "f = <number>",
        ]
    )

    # create template and assert
    result = tomldantic.dumps(TestModel)
    assert result.strip() == expected.strip()

    # the model should not be valid because the fields are required
    with pytest.raises(TomlDecodeError):
        TestModel.model_validate(toml.loads(result))


def test_basic_types_with_description() -> None:
    """This is the most basic use case with the types string, float and integer
    but with descriptions."""

    # pylint: disable=missing-class-docstring
    class TestModel(BaseModel):
        s: str = Field(default="hello", description="This is a string field.")
        i: int = Field(default=42, description="This is an integer.")
        f: float = Field(default=3.14, description="This is a float number.")

    expected = "\n".join(
        [
            's = "hello"  # This is a string field.',
            "i = 42  # This is an integer.",
            "f = 3.14  # This is a float number.",
        ]
    )

    result = tomldantic.dumps(TestModel)
    assert result.strip() == expected.strip()


def test_nested_object_with_defaults() -> None:
    """Simple test for a nested model with default values."""

    # pylint: disable=missing-class-docstring
    class Inner(BaseModel):
        foo: str = "hello world"
        bar: int = 42

    class TestModel(BaseModel):
        inner: Inner = Inner()

    expected = "\n".join(
        [
            "[inner]",
            'foo = "hello world"',
            "bar = 42",
        ]
    )

    # check if the template is created correctly
    result = tomldantic.dumps(TestModel)
    assert result.strip() == expected.strip()

    # check if the model can be validated from the toml string and the values are
    # correct
    obj = TestModel.model_validate(toml.loads(result))
    assert obj.inner.foo == "hello world"
    assert obj.inner.bar == 42


def test_nested_object_with_required_arguments() -> None:
    """Simple test for a nested model with default values and required arguments."""

    # pylint: disable=missing-class-docstring
    class Inner(BaseModel):
        foo: str
        bar: int

    class TestModel(BaseModel):
        inner: Inner

    expected = "\n".join(
        [
            "[inner]",
            "foo = <string>",
            "bar = <integer>",
        ]
    )
    # check if the template is created correctly
    result = tomldantic.dumps(TestModel)
    assert result.strip() == expected.strip()

    # the model should not be valid because the inner object is required
    with pytest.raises(TomlDecodeError):
        TestModel.model_validate(toml.loads(result))


def test_object_descriptions() -> None:
    """Test for object descriptions in the TOML template."""

    class Inner(BaseModel):
        """This is the inner config."""

        foo: str = Field(description="The foo parameter.")

    class TestModel(BaseModel):
        """This is the main config."""

        inner: Inner

    expected = "\n".join(
        [
            "# This is the main config.",
            "",
            "[inner]",
            "",
            "# This is the inner config.",
            "",
            "foo = <string>  # The foo parameter.",
        ]
    )

    result = tomldantic.dumps(TestModel)
    assert result.strip() == expected.strip()


def test_simple_array() -> None:
    """Test for a simple array of strings in the TOML template."""

    # pylint: disable=missing-class-docstring
    class TestModel(BaseModel):
        foo: list[str]
        bar: list[str] = Field(default=["hello", "world"])

    expected = "\n".join(
        [
            "foo = <array>",
            'bar = ["hello", "world"]',
        ]
    )

    result = tomldantic.dumps(TestModel)
    assert result.strip() == expected.strip()


def test_object_list() -> None:
    """Test for a list of objects in the TOML template."""

    # pylint: disable=missing-class-docstring
    class Inner(BaseModel):
        """This is the inner config."""

        foo: str = Field(default="hello", description="The foo parameter.")

    class TestModel(BaseModel):
        """This is the main config."""

        inner: list[Inner] = Field(default=[Inner()])

    expected = "\n".join(
        [
            "",
            "# This is the main config.",
            "",
            "[[inner]]",
            "",
            "# This is the inner config.",
            "",
            'foo = "hello"  # The foo parameter.',
        ]
    )
    result = tomldantic.dumps(TestModel)
    assert result.strip() == expected.strip()
