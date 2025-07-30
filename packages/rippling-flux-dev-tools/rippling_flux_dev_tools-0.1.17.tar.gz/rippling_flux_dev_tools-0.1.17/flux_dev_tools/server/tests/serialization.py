import io
import json
import unittest
from decimal import Decimal
from enum import Enum

from flux_dev_tools.server.serialization import FluxJSONDecoder, FluxJSONEncoder


class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"


class Address:
    street: str
    city: str
    state: str
    zip_code: str


class Employee:
    name: str
    age: int
    salary: Decimal
    gender: Gender
    address: Address


class TestCustomJSONEncoderDecoder(unittest.TestCase):
    def assertEmployeeEqual(self, employee, decoded_employee):
        self.assertEqual(employee.name, decoded_employee.name)
        self.assertEqual(employee.age, decoded_employee.age)
        self.assertEqual(employee.salary, decoded_employee.salary)
        self.assertEqual(employee.gender, decoded_employee.gender)
        self.assertEqual(employee.address.street, decoded_employee.address.street)
        self.assertEqual(employee.address.city, decoded_employee.address.city)
        self.assertEqual(employee.address.state, decoded_employee.address.state)
        self.assertEqual(employee.address.zip_code, decoded_employee.address.zip_code)

    def test_simple_types_encoding_and_decoding(self):
        # Test encoding and decoding of simple types
        text = "Hello World"
        encoded_text = json.dumps(text, cls=FluxJSONEncoder)
        decoded_text = json.loads(encoded_text, cls=FluxJSONDecoder, target_type=str)
        self.assertEqual(decoded_text, text)

        number = 123
        encoded_number = json.dumps(number, cls=FluxJSONEncoder)
        decoded_number = json.loads(encoded_number, cls=FluxJSONDecoder, target_type=int)
        self.assertEqual(decoded_number, number)

        decimal = Decimal("123.45")
        encoded_decimal = json.dumps(decimal, cls=FluxJSONEncoder)
        decoded_decimal = json.loads(encoded_decimal, cls=FluxJSONDecoder, target_type=Decimal)
        self.assertEqual(decoded_decimal, decimal)

    def test_custom_class_encoding_and_decoding(self):
        # Test encoding and decoding of custom class instances
        employee = Employee()
        employee.name = "Alice"
        employee.age = 25
        employee.salary = Decimal("60000.75")
        employee.gender = Gender.FEMALE
        address = Address()
        address.street = "123 Main St"
        address.city = "New York"
        address.state = "NY"
        address.zip_code = "10001"
        employee.address = address

        encoded_employee = json.dumps(employee, cls=FluxJSONEncoder)
        decoded_employee = json.loads(encoded_employee, cls=FluxJSONDecoder, target_type=Employee)

        self.assertEmployeeEqual(decoded_employee, employee)

    def test_enum_encoding_and_decoding(self):
        # Test encoding and decoding of Enums
        encoded_data = json.dumps(Gender.FEMALE, cls=FluxJSONEncoder)
        decoded_data = json.loads(encoded_data, cls=FluxJSONDecoder, target_type=Gender)

        self.assertEqual(decoded_data, Gender.FEMALE)

    def test_string_io_encoding_and_decoding(self):
        # Test encoding and decoding of StringIO
        sample_data = "Hello World"
        stream = io.StringIO(sample_data)

        encoded_string_io = json.dumps(stream, cls=FluxJSONEncoder)
        decoded_string_io = json.loads(encoded_string_io, cls=FluxJSONDecoder, target_type=io.IOBase)

        decoded_data = decoded_string_io.read()
        self.assertEqual(decoded_data, sample_data)

    def test_bytes_io_encoding_and_decoding(self):
        # Test encoding and decoding of BytesIO
        sample_data = b"\x01\x02\x03\x04"
        stream = io.BytesIO(sample_data)

        encoded_bytes_io = json.dumps(stream, cls=FluxJSONEncoder)
        decoded_bytes_io = json.loads(encoded_bytes_io, cls=FluxJSONDecoder, target_type=io.IOBase)

        decoded_data = decoded_bytes_io.read()
        self.assertEqual(decoded_data, sample_data)

    def test_list_of_objects_encoding_and_decoding(self):
        # Test encoding and decoding of lists of objects
        employees = [Employee(), Employee(), Employee()]
        employees[0].name = "Employee 1"
        employees[1].name = "Employee 2"
        employees[2].name = "Employee 3"

        encoded_employees = json.dumps(employees, cls=FluxJSONEncoder)
        decoded_employees = json.loads(encoded_employees, cls=FluxJSONDecoder, target_type=list[Employee])

        for decoded_employee, original_employee in zip(decoded_employees, employees):
            self.assertEqual(decoded_employee.name, original_employee.name)

    def test_list_of_simple_types_encoding_and_decoding(self):
        # Test encoding and decoding of lists of simple types
        numbers = [1, 2, 3, 4, 5]
        encoded_numbers = json.dumps(numbers, cls=FluxJSONEncoder)
        decoded_numbers = json.loads(encoded_numbers, cls=FluxJSONDecoder, target_type=list[int])

        self.assertEqual(decoded_numbers, numbers)

    def test_dict_of_simple_types_encoding_and_decoding(self):
        # Test encoding and decoding of dicts of simple types
        data = {"a": 1, "b": 2, "c": 3}
        encoded_data = json.dumps(data, cls=FluxJSONEncoder)
        decoded_data = json.loads(encoded_data, cls=FluxJSONDecoder, target_type=dict[str, int])

        self.assertEqual(decoded_data, data)