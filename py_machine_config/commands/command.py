"""
Python Machine/Container Configuration
.. author:: Tammy Cravit, tammy@tammymakesthings.com
.. version:: 1.0
"""

from io import BytesIO
from tokenize import tokenize, NUMBER, STRING, NAME, OP
from pathlib import Path
from typing import Optional
import jinja2


class BaseCommand:
    """
    The base class for Command executors.

    The BaseCommand is initialized with an argument string (which can be empty). This
    string is tokenized by the Python :py:class:`tokenize` class, and STRING, NUMBER,
    and OP tokens are converted to strings and captured into the ``args`` property.

    Following tokenization, the kwargs are processed, and handled as follows:

    * For ``if_file_exists`` and ``if_not_file_exists``, the value is a file
      path. The ``enabled`` property is set to ``True`` or ``False`` based on
      whether the specified path exists. (The target can be a file, directory,
      symlink, etc.)

    * For ``if_dir_exists`` and ``if_not_dire_exists``, the value is a directory
      path. The ``enabled`` property is set to ``True`` or ``False`` based on
      whether the specified path exists and is a directory.

    * For ``disabled`` and ``enabled``, the ``enabled`` property is set accordingly.

    * For any other key, the key and its value are added to the ``properties`` dict,
      and are accessible to the command at execution time.

    The BaseCommand class provides one abstract method, ``execute()``, which must be
    overridden to provide the behavior of your command (install a package, configure
    a service, etc). It also provides a few useful helper methods for creating files
    and rendering Jinja2 templates.
    """

    __command_name: str
    __step_name: str
    __args: list[str]
    __enabled: bool
    __properties: dict

    def __init__(
        self, command_name: str, step_name: str = "", arg_string: str = "", **kwargs
    ):
        self.__args = list()
        self.__enabled = True
        self.__properties = dict()
        self.__step_name = step_name
        self.__command_name = command_name

        tokenizer = tokenize(BytesIO(arg_string.encode("utf-8")).readline)

        for toktype, tokval, _, _, _ in tokenizer:
            match toktype:
                case NUMBER:
                    args.append(str(tokval))
                case STRING:
                    args.append(tokval)
                case NAME:
                    args.append(str(tokval))
                case OP:
                    args.append(str(tokval))

        for key, val in kwargs:
            match key:
                case "if_file_exists":
                    if not self._file_exists(val):
                        self.enabled = False
                case "if_directory_exists":
                    if not self._directory_exists(val):
                        self.enabled = False
                case "if_not_file_exists":
                    if self._file_exists(val):
                        self.enabled = False
                case "if_not_directory_exists":
                    if self._directory_exists(val):
                        self.enabled = False
                case "disabled":
                    self.enabled = not bool(val)
                case "enabled":
                    self.enabled = bool(val)
                case _:
                    self.__properties[key] = val

    def file_exists(self, file_path: str) -> bool:
        return Path(file_path).exists()

    def directory_exists(self, directory_path: str) -> bool:
        return Path(file_path).exists() and Path(directory_path).is_dir()

    def read_file(self, file_path: str) -> list[str]:
        if not Path(file_path).exists():
            raise IOError("input file not found", file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()

    def write_file(
        self, file_path: str, contents: list[str], overwrite: bool = False
    ) -> None:
        if Path(file_path).exists() and not overwrite:
            raise IOError("file exists and 'overwrite' was not specified", file_path)
        with open(file_path, "w", encoding="utf-8") as f:
            for line in contents:
                f.writeline(line)

    def process_file_template(
        self,
        file_path: str,
        template_file_path: str = None,
        template_contents: str = None,
        context: dict = dict(),
    ) -> None:
        if not template_file_path and not template_contents:
            raise ValueError("must specify a template path or template contents")
        if template_file_path and template_contents:
            raise ValueError("cannot specify both template path and template contents")

        template = None
        env = jinja2.Environment()

        if template_file_path:
            if not Path(template_file_path).exists():
                raise ValueError("template file not found", template_file_path)
            with open(template_file_path, "r", encoding="utf-8") as f:
                template = env.from_string("\n".join(f.readlines()))
        else:
            template = template_contents

        output_content = env.from_string(template_content).render(context)
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(output_content)

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @property
    def step_name(self) -> str:
        return self.__step_name

    @property
    def command_name(self) -> str:
        return self.__command_name

    @property
    def args(self) -> list:
        return self.__args

    @property
    def enabled(self) -> bool:
        return self.__enabled

    @property
    def properties(self) -> dict:
        return self.__properties

    @enabled.setter
    def enabled(self, new_val: bool) -> None:
        self.__enabled = new_val

    @step_name.setter
    def step_name(self, new_val: str) -> None:
        self.__step_name = new_val

    @command_name.setter
    def command_name(self, new_val: str) -> None:
        self.__command_name = new_val
