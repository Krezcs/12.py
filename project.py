import re
import pickle
from datetime import date
from collections import UserDict


def validation_contact(func):
    def wrapper(*args, **kwargs):
        name, phone = args[0], args[1]
        if not re.match("^[A-Za-z ]+$", name):
            return "Invalid input. Name can only contain English letters and spaces."
        if not re.match("^\d+$", phone):
            return "Invalid input. Phone number can only contain digits."
        return func(*args, **kwargs)
    return wrapper


class Field:
    def __init__(self, value=None):
        self._value = value
        self.validate()

    def validate(self):
        raise NotImplementedError("Validation logic must be implemented in the subclass.")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.validate()


class Birthday(Field):
    def validate(self):
        if self.value and not isinstance(self.value, date):
            raise ValueError("Birthday field must be a date object.")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.validate()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state




class Name(Field):
    def validate(self):
        if not self.value:
            raise ValueError("Name field is required.")


class Phone(Field):
    def validate(self):
        if self.value and not isinstance(self.value, str):
            raise ValueError("Phone field must be a string.")


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(phone)

    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        if old_phone in self.phones:
            index = self.phones.index(old_phone)
            self.phones[index] = new_phone

    def days_to_birthday(self):
        if not self.birthday.value:
            return None

        today = date.today()
        next_birthday = date(today.year, self.birthday.value.month, self.birthday.value.day)

        if next_birthday < today:
            next_birthday = date(today.year + 1, self.birthday.value.month, self.birthday.value.day)

        days_until_birthday = (next_birthday - today).days
        return days_until_birthday



class AddressBook(UserDict):
    def __init__(self, data=None, file_path="address_book.pkl"):
        super().__init__(data)
        self.file_path = file_path

    def add_record(self, record):
        self.data[record.name.value] = record
        self.save_to_disk()

    def remove_record(self, record):
        del self.data[record.name.value]
        self.save_to_disk()

    def edit_record_name(self, old_name, new_name):
        record = self.data.pop(old_name)
        record.name.value = new_name
        self.data[new_name] = record
        self.save_to_disk()

    def save_to_disk(self):
        if self.file_path:
            try:
                with open(self.file_path, "wb") as file:
                    pickle.dump(self.data, file)
            except Exception as e:
                print(f"Error occurred while saving to disk: {str(e)}")

    def load_from_disk(self):
        if self.file_path:
            try:
                with open(self.file_path, "rb") as file:
                    self.data = pickle.load(file)
            except FileNotFoundError:
                print("No previous data found. Starting with an empty address book.")
            except Exception as e:
                print(f"Error occurred while loading from disk: {str(e)}")
                self.data = {}


def add_contact(address_book, name, phone):
    record = Record(name)
    record.add_phone(phone)
    address_book.add_record(record)
    return f"Contact {name} with phone number {phone} has been added."


def change_contact(address_book, name, phone):
    if name in address_book:
        record = address_book[name]
        record.phones = []
        record.add_phone(phone)
        address_book.save_to_disk()
        return f"Phone number for contact {name} has been updated to {phone}."
    else:
        return f"Contact {name} does not exist."


def phone_contact(address_book, name):
    if name in address_book:
        record = address_book[name]
        phone_numbers = ", ".join(record.phones)
        return f"Phone number for contact {name}: {phone_numbers}"
    else:
        return f"Contact {name} does not exist."


def show_all_contacts(address_book):
    if not address_book.data:
        return "No contacts found."
    else:
        contact_list = "\n".join([f"{name}: {', '.join(record.phones)}" for name, record in address_book.data.items()])
        return f"Contacts:\n{contact_list}"


def hello():
    return "How can I help you?"


def main():
    address_book = AddressBook()
    address_book.load_from_disk()

    while True:
        command = input("Enter a command: ").lower().split()
        if not command:
            print("Invalid command. Please try again.")
            continue
        if command[0] == "hello":
            print(hello())
        elif command[0] == "add":
            if len(command) != 3:
                print("Invalid command. Please try again.")
                continue
            name, phone = command[1], command[2]
            result = add_contact(address_book, name, phone)
            print(result)
        elif command[0] == "change":
            if len(command) != 3:
                print("Invalid command. Please try again.")
                continue
            name, phone = command[1], command[2]
            result = change_contact(address_book, name, phone)
            print(result)
        elif command[0] == "phone":
            if len(command) != 2:
                print("Invalid command. Please try again.")
                continue
            name = command[1]
            result = phone_contact(address_book, name)
            print(result)
        elif command[0] == "show":
            if len(command) != 2:
                print("Invalid command. Please try again.")
                continue
            if command[1] == "all":
                result = show_all_contacts(address_book)
                print(result)
            else:
                name = command[1]
                result = phone_contact(address_book, name)
                print(result)
        elif command[0] in ["good", "bye", "close", "exit", "."]:
            address_book.save_to_disk()
            print("Goodbye!")
            break
        else:
            print("Invalid command. Please try again.")


if __name__ == "__main__":
    main()
