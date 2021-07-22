import sys
import os

from h5_info.logger import Logger

ERROR_CODE = 1
SUCCESS_CODE = 0


class Checker:
    @staticmethod
    def check_input_arguments(actual_args, mandatory_args, optional_args, mandatory_arg_list, optional_arg_list,
                              command_line):
        Logger.debug("Checking input parameters")
        errors = []

        arg_iter = iter(range(1, len(sys.argv)))

        for i in arg_iter:
            arg = sys.argv[i]
            if arg.startswith('-') or arg.startswith('--'):
                optional_args[arg] = sys.argv[i + 1]
                next(arg_iter, None)
            else:
                mandatory_args.append(arg)

        if len(mandatory_args) < len(mandatory_arg_list):
            errors.append(ArgumentError("Missing input arguments! At least " + str(len(mandatory_arg_list)) + " arguments are "
                                                                                                "required:"))
            for arg in mandatory_arg_list:
                errors.append(ArgumentError("- " + arg))

        if len(mandatory_args) > len(mandatory_arg_list):
            errors.append(ArgumentError("Too many input arguments! Only " + str(len(mandatory_arg_list)) + " arguments are "
                                                                                                "required:"))
            for arg in mandatory_arg_list:
                errors.append(ArgumentError("- " + arg))

        for arg in optional_args:
            if arg not in optional_arg_list:
                errors.append(ArgumentError("Not supported input argument: '" + arg + "'!"))
            if optional_args[arg] == '':
                errors.append(ArgumentError("Empty value for input argument: '" + arg + "'!"))

        if len(errors) > 0:
            for error in errors:
                Logger.error(error)
            raise ArgumentError("Command line should be: " + command_line)

    @staticmethod
    def check_file_exists(file):
        Logger.debug('Checking file exists: ' + file)
        if file == "" or not os.path.isfile(file):
            raise ArgumentError('File not found: ' + file)

    @staticmethod
    def check_folder_exists(folder, create=False):
        Logger.debug('Checking folder exists: ' + folder)
        if folder == "" or (not os.path.exists(folder) and not create):
            raise ArgumentError('Folder not found: ' + folder)
        else:
            if not os.path.exists(folder) and create:
                Logger.debug("Creating folder: " + folder)
                os.mkdir(folder)

    @staticmethod
    def check_boolean_param(name, value):
        Logger.debug('Checking boolean value for param ' + name)
        if value not in ["true", "false"]:
            raise ArgumentError("Value '"+value+"' for param '"+name+"' is not valid (must be 'true' or 'false')")

    @staticmethod
    def is_optional_param_true(name, args, default=True):
        return (name not in args and default) or (name in args and args[name] == 'true')

    @staticmethod
    def get_optional_numeric_param(name, args, default=0.0):
        if name in args:
            value = args[name]
            try:
                Checker.check_numerical_param(name, value)
            except ArgumentError as error:
                Logger.warning(str(error))
                Logger.warning("Value for param '"+name+"' has been set to default: " + str(default))
                return default
            else:
                return float(value)
        else:
            return default

    @staticmethod
    def check_numerical_param(name, value):
        Logger.debug('Checking numerical value for param ' + name)
        if not value.replace('.', '', 1).isdigit():
            raise ArgumentError("Value '"+value+"' for param '"+name+"' is not valid (must be a numeric value)")

    @staticmethod
    def get_optional_string_param(name, args, default=None):
        return default if name not in args else args[name]


class ArgumentError(Exception):
    """Exception raised for errors in a arguments."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
