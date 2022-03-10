"""Object definitions for the presentable transformation of the settings."""

from dataclasses import dataclass
from typing import ClassVar
from typing import Dict
from typing import List
from typing import NewType
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from .definitions import CliParameters
from .definitions import Constants as C
from .definitions import SettingsEntry
from .navigator_configuration import Internals
from .utils import create_settings_file_sample


PresentableSettingsEntryValue = Union[bool, Dict, str, List]

TCli = TypeVar("TCli", bound="PresentableCliParameters")
TEnt = TypeVar("TEnt", bound="PresentableSettingsEntry")


@dataclass(frozen=True)
class PresentableCliParameters:
    """A settings entry's cli parameters in a presentable structure."""

    NO_LONG_MSG: ClassVar[str] = "No long CLI parameter"
    NO_SHORT_MSG: ClassVar[str] = "No short CLI parameter"

    long: str = NO_LONG_MSG
    """The long cli parameter value"""
    short: str = NO_SHORT_MSG
    """The short cli parameter value"""

    @classmethod
    def from_cli_params(
        cls: Type[TCli],
        cli_parameters: Optional[CliParameters],
        name_dashed: str,
    ) -> TCli:
        """Create an ``_HRCliParameters`` based on an entry's cli parameters.

        :param cli_parameters: The entry's cli parameters
        :param name_dashed: The dashed name of the parent settings entry
        :returns: The instance of self based on an entry's cli parameters
        """
        if isinstance(cli_parameters, CliParameters):
            short = cli_parameters.short or cls.NO_SHORT_MSG
            long = cli_parameters.long(name_dashed)
            return cls(long=long, short=short)
        return cls()


@dataclass(frozen=True)
class PresentableSettingsEntry:
    # pylint: disable=too-many-instance-attributes
    """A settings entry in a presentable structure."""

    choices: List
    """The possible values"""
    current_settings_file: str
    """The path to the current settings file"""
    current_value: PresentableSettingsEntryValue
    """The current, effective value"""
    default_value: PresentableSettingsEntryValue
    """The default value"""
    default: bool
    """Indicates if the current value == the default"""
    description: str
    """A short description"""
    env_var: str
    """The environment variable"""
    name: str
    """The name"""
    settings_file_sample: Union[str, Dict]
    """A sample settings file snippet"""
    source: str
    """The source of the current value"""
    subcommands: List
    """A list of subcommands where this entry is available"""
    cli_parameters: PresentableCliParameters = PresentableCliParameters()
    """The CLI parameters, long and short"""

    @property
    def current(self) -> str:
        """Convert the current value into a string.

        :returns: The current value as a string
        """
        return str(self.current_value)

    def get(self, attribute: str):
        """Allow this dataclass to be treated like a dictionary.

        This is a work around until the UI fully supports dataclasses
        at which time this can be removed.

        Default is intentionally not implemented as a safeguard to enure
        this is not more work than necessary to remove in the future
        and will only return attributes in existence.

        :param attribute: The attribute to get
        :returns: The gotten attribute
        """
        return getattr(self, attribute)

    def __lt__(self, other):
        """Compare based on name, called by sort, sorted.

        :param other: The entry to compare this to
        :returns: Indication of less than the other
        """
        return self.name < other.name

    @classmethod
    def for_settings_file(
        cls: Type[TEnt],
        all_subcommands: List,
        application_name: str,
        internals: Internals,
    ) -> TEnt:
        """Create an ``PresentableSettingsEntry`` containing the details for the settings file.

        :param all_subcommands: All application subcommands
        :param application_name: The application name
        :param internals: The internal storage for settings information
        :returns: The settings file entry
        """
        description = (
            "The path to the current settings file. Possible locations are"
            " {CWD}/ansible-navigator.{ext} or {HOME}/.ansible-navigator.{ext}"
            " where ext is yml, yaml or json."
        )
        return cls(
            choices=[],
            current_settings_file=internals.settings_file_path or C.NONE.value,
            current_value=internals.settings_file_path or C.NONE.value,
            default=internals.settings_source is C.NONE,
            default_value=C.NONE.value,
            description=description,
            name="Current settings file",
            env_var=f"{application_name.upper()}_CONFIG",
            settings_file_sample="Not applicable",
            source=internals.settings_source.value,
            subcommands=all_subcommands,
        )

    @classmethod
    def from_settings_entry(
        cls: Type[TEnt],
        all_subcommands: List,
        application_name_dashed: str,
        entry: SettingsEntry,
        settings_file_path: str,
    ) -> TEnt:
        """Create an ``PresentableSettingsEntry`` containing the details for one settings entry.

        :param application_name_dashed: The application name, dashed
        :param all_subcommands: All application subcommands
        :param entry: A settings entry
        :param settings_file_path: The path to the settings file

        :returns: The settings file entry
        """
        cli_parameters = PresentableCliParameters.from_cli_params(
            cli_parameters=entry.cli_parameters,
            name_dashed=entry.name_dashed,
        )

        env_var = entry.environment_variable(application_name_dashed)
        entry_value_resolved = entry.value.resolved

        path = entry.settings_file_path(application_name_dashed)
        settings_file_sample = create_settings_file_sample(path, placeholder="<------")

        if isinstance(entry.subcommands, C):
            if entry.subcommands is C.ALL:
                subcommands = all_subcommands
            else:
                subcommands = [entry.subcommands.value]
        else:
            subcommands = entry.subcommands

        result = cls(
            choices=list(entry.choices),  # May be a tuple e.g. PLUGIN_TYPES
            cli_parameters=cli_parameters,
            current_settings_file=str(settings_file_path),
            current_value=entry_value_resolved.current,
            default=entry_value_resolved.is_default,
            default_value=entry_value_resolved.default,
            description=entry.short_description,
            env_var=env_var,
            name=entry.name.replace("_", " ").capitalize(),
            settings_file_sample=settings_file_sample,
            source=entry.value.source.value,
            subcommands=subcommands,
        )
        return result


PresentableSettingsEntries = NewType(
    "PresentableSettingsEntries",
    Tuple[PresentableSettingsEntry, ...],
)