# ~/gofigure/src/gofigure/core/base.py
"""
Core base implementation for the Gofig configuration system.
"""
from __future__ import annotations
import os, json, enum, yaml, types, warnings
import typing as t, functools as fn
from pathlib import Path

from gofigure.exceptions import (
    GofigError, UnsupportedFormat,
    FormatMismatch, NamespaceConflict
)

class FileFormat(str, enum.Enum):
    """Supported configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    # to be implemented:
    # TOML
    # INI
    # XML

    def __str__(self) -> str:
        return self.value

    @property
    def extensions(self) -> t.List[str]:
        if self == self.JSON:
            return ['.json']
        if self == self.YAML:
            return ['.yaml', '.yml']
        else:
            return []

    @classmethod
    def FromExtension(cls, extension: str) -> 'FileFormat':
        ext = extension.lower().lstrip('.')
        match ext:
            case 'json':
                return cls.JSON
            case 'yaml' | 'yml':
                return cls.YAML
            case _:
                supported = [f.value for f in cls]
                raise UnsupportedFormat(ext, supported)

    @classmethod
    def FromPath(cls, path: t.Union[str, Path]) -> 'FileFormat':
        path = Path(path)
        return cls.FromExtension(path.suffix)

def savecheck(func: t.Callable) -> t.Callable:
    """Decorator to trigger autosave after state-changing operations."""
    @fn.wraps(func)
    def wrapper(self: 'Gofig', *args, **kwargs):
        print(f"(savecheck) calling: {func.__name__}")
        result = func(self, *args, **kwargs)
        saveable = all((
            hasattr(self, '_autosave'),
            self._autosave,
            hasattr(self, '_filepath'),
            self._filepath
        ))
        print(f"(savecheck) saveable: {saveable}")
        if saveable:
            print(f"(savecheck): triggering save")
            self.__save()
        return result
    return wrapper


class Gofig(dict):
    """
    Dynamic configuration container with dual access patterns.

    Supports both dict-like access (obj['key']) and attribute-like access (obj.key)
    with automatic nesting and optional file persistence.
    """
    _SAVENAMES: t.List[str] = ['save', 'Save', 'SAVE', 'persist', 'write']
    _RELOADNAMES: t.List[str] = ['reload', 'Reload', 'RELOAD', 'refresh', 'reread']

    def __init__(
        self,
        data: t.Optional[t.Dict[str, t.Any]] = None,
        filepath: t.Optional[t.Union[str, Path]] = None,
        autosave: bool = False,
        autovivify: bool = True,
        nullaccess: t.Union[t.Type[Exception], None, t.Type[type]] = None,
        manglenamespace: bool = False,
        root: t.Optional['Gofig'] = None,
        **overrides
    ) -> None:
        """
        Initialize Gofig instance.

        Args:
            data: Initial configuration data
            filepath: Path to config file for persistence
            autosave: Whether to automatically save changes to file
            autovivify: Whether to auto-create nested structures on attribute access
            nullaccess: Behavior for accessing non-existent keys (None=return None, type=create empty, Exception=raise)
            manglenamespace: Allow namespace conflicts without raising NamespaceConflict
            root: Internal parameter for nested objects to reference parent root
            **overrides: Additional key-value pairs to override loaded data
        """
        # set internal attributes first, before calling super().__init__()
        # to avoid attribute errors for @savecheck decorated methods called during initialization
        self._filepath: t.Optional[Path] = Path(filepath) if filepath else None
        self._autosave: bool = autosave
        self._autovivify: bool = autovivify
        self._manglenamespace: bool = manglenamespace
        self._nullaccess: t.Union[t.Type[Exception], None, t.Type[type]] = nullaccess
        self._fileformat: t.Optional[FileFormat] = None # maybe we should make an enum for this? we're gonna expand filetypes supported eventually e.g. TOML
        self._root: t.Optional['Gofig'] = root

        super().__init__() # now safe to call

        if self._filepath:
            self._fileformat = FileFormat.FromPath(self._filepath)

        self._namespaced = {}

        # load hierarchy: file -> data -> overrides
        self._load(data, **overrides) # attributes now exist

        # setup dynamic public API methods
        self.__setupapi()


    def __setupapi(self) -> None:
        """Set up public method names that don't conflict with data keys."""
        # find available save method name
        savename = None
        for name in self._SAVENAMES:
            if name not in self:
                savename = name
                break

        if (savename is None) and (not self._manglenamespace):
            raise NamespaceConflict("save", self._SAVENAMES)

        reloadname = None
        for name in self._RELOADNAMES:
            if name not in self:
                reloadname = name
                break

        if (reloadname is None) and (not self._manglenamespace):
            raise NamespaceConflict("reload", self._RELOADNAMES)

        # only assign if both are available, otherwise rely on operators
        if (savename and reloadname):
            # use object.__setattr__ to avoid adding to dict storage
            object.__setattr__(self, savename, self.__save)
            object.__setattr__(self, reloadname, self.__reload)
            self._namespaced['save'] = savename
            self._namespaced['reload'] = reloadname
        else:
            warnings.warn("No reserved namespace keys for save/reload methods available -- must use operator overloads (>>/<<)", category=RuntimeWarning)
            # no methods available -- must use operators
            self._namespaced = {}

    def __serialize(self) -> t.Dict[str, t.Any]:
        """Convert to plain dictionary for serialization."""
        result = {}
        for k, v in self.items():
            if isinstance(v, Gofig):
                result[k] = v.__serialize()
            elif not callable(v): # skip methods/callables
                result[k] = v
        return result

    def __save(self) -> None:
        """Actual save method implementation."""
        if not self._filepath:
            raise ValueError(f"No filepath configured for saving")

        # ensure directory
        self._filepath.parent.mkdir(parents=True, exist_ok=True)

        # serialize
        data = self.__serialize()

        match self._fileformat:
            case FileFormat.JSON:
                with open(self._filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"(Gofig.__save[JSON]) saved to: {self._filepath}")
            case FileFormat.YAML:
                with open(self._filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                print(f"(Gofig.__save[YAML]) saved to: {self._filepath}")
            case _:
                raise UnsupportedFormat(str(self._fileformat))

    def __reload(self) -> None:
        """Actual reload method implementation."""
        if (not self._filepath) or (not self._filepath.exists()):
            raise ValueError(f"No filepath configured or file doesn't exist")

        match self._fileformat:
            case FileFormat.JSON:
                with open(self._filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            case FileFormat.YAML:
                with open(self._filepath, 'r', encoding='utf-8') as f:
                    data = (yaml.safe_load(f) or {})
            case _:
                raise UnsupportedFormat(str(self._fileformat))

        # clear and relaod
        self.clear()
        self._dataload(data)
        self.__setupapi()

    def __autosave(self) -> None:
        """Trigger autosave on the appropriate object (root if nested)."""
        def should():
            """Check if this Gofig instance should autosave (mainly for use by bound methods)"""
            target = self._root if self._root is not None else self
            conditions = (
                hasattr(target, '_autosave'),
                target._autosave,
                hasattr(target, '_filepath'),
                target._filepath
            )
            return all(conditions)

        if should():
            root = self._root if self._root is not None else self
            root.__save()

    def _dataload(self, data: t.Dict[str, t.Any]) -> None:
        """Load data into the configuration, handling nested structures."""
        for k, v in data.items():
            if isinstance(v, dict):
                if (k in self) and isinstance(self[k], Gofig):
                    # merge with existing nested
                    self[k]._dataload(v)
                else:
                    # create new
                    getroot = lambda obj: obj._root if hasattr(obj, '_root') else obj
                    root = self._root if self._root is not None else self
                    self[k] = Gofig(
                        v,
                        autovivify=self._autovivify,
                        nullaccess=self._nullaccess,
                        root=self
                    ) # recursive wrap nested
            else:
                self[k] = v

    def _load(self, data: t.Optional[t.Dict[str, t.Any]] = None, **overrides) -> None:
        # 1. load from file if available
        if self._filepath and self._filepath.exists():
            self.__reload()

        # 2. override with provided data
        if data:
            self._dataload(data)

        # 3. apply overrides if available
        if overrides:
            self._dataload(overrides)



    ## dict-like access ##
    def __setitem__(self, key: str, value: t.Any) -> None:
        """Set item with automatic nesting and autosave trigger."""
        if isinstance(value, dict) and not isinstance(value, Gofig):
            value = Gofig(value)
        super().__setitem__(key, value)
        self.__autosave()


    def __getitem__(self, key: str) -> t.Any:
        """Get item with proper KeyError for missing keys."""
        try:
            return super().__getitem__(key)
        except KeyError:
            raise KeyError(key)

    ## attribute-like access ##
    def __getattr__(self, name: str) -> t.Any:
        """Get attribute, falling back to dict lookup."""
        if name in self:
            return self[name]

        if not name.startswith("_"):
            if self._autovivify:
                root = self._root if self._root is not None else self
                self[name] = Gofig(autovivify=self._autovivify, nullaccess=self._nullaccess, autosave=False, filepath=None, root=root)
                return self[name]
            elif self._nullaccess is None:
                return None
            elif self._nullaccess is type:
                return Gofig(autovivify=False, nullaccess=self._nullaccess)
            elif isinstance(self._nullaccess, type) and issubclass(self._nullaccess, Exception):
                raise self._nullaccess(f"({self.__class__.__name__}) object has no attribute: {name}")

        # Default fallback
        raise AttributeError(f"({self.__class__.__name__}) object has no attribute: {name}")


    def __setattr__(self, name: str, value: t.Any) -> None:
        """Set attribute, routing to dict storage for non-internal attributes."""
        # internal attributes (start with _) go to object storage
        if name.startswith('_'):
            # Use dict.__setattr__ directly instead of super().__setattr__ to bypass
            # the @savecheck decorator and avoid infinite recursion during __init__
            # when setting internal attributes like _autosave, _filepath, etc.
            dict.__setattr__(self, name, value)
            return

        # everything else dict stored
        self[name] = value
        self.__autosave()

    def __delattr__(self, name: str) -> None:
        """Delete attribute from dict storage."""
        if name.startswith("_"):
            super().__delattr__(name)
        elif name in self:
            del self[name]
            self.__autosave()
        else:
            raise AttributeError(f"({self.__class__.__name__}) object has no attribute: {name}")

    def get(self, key: str, default: t.Any = None) -> t.Any:
        """Get value with optional default, same as dict.get()."""
        return super().get(key, default)

    ## factory methods ##
    ### these are a bit redundant tbh but whatever
    @classmethod
    def FromJSON(
        cls,
        path: t.Union[str, Path],
        autosave: bool = False,
        autovivify: bool = True,
        nullaccess: t.Union[t.Type[Exception], None, t.Type[type]] = None,
        manglenamespace: bool = False
    ) -> 'Gofig':
        """Create Gofig instance from JSON file."""
        if not Path(path).exists():
            raise FileNotFoundError(f"File Not Found: {path}")
        return cls(filepath=path, autosave=autosave, autovivify=autovivify, nullaccess=nullaccess, manglenamespace=manglenamespace)

    @classmethod
    def FromYAML(
        cls,
        path: t.Union[str, Path],
        autosave: bool = False,
        autovivify: bool = True,
        nullaccess: t.Union[t.Type[Exception], None, t.Type[type]] = None,
        manglenamespace: bool = False
    ) -> 'Gofig':
        """Create Gofig instance from YAML file."""
        if not Path(path).exists():
            raise FileNotFoundError(f"File Not Found: {path}")
        return cls(filepath=path, autosave=autosave, autovivify=autovivify, nullaccess=nullaccess, manglenamespace=manglenamespace)

    ## operator overloads ##
    ### use in case of namespace conflict ###
    def __rshift__(self, other: t.Any) -> 'Gofig':
        """Save operation via >> operator."""
        self.__save()
        return self

    def __lshift__(self, other: t.Any) -> 'Gofig':
        """Reload operation via << operator."""
        self.__reload()
        return self

    # not actually needed
    #def __autosave(self) -> None:
        # method to actually trigger autosave
        #raise NotImplemented

def save(gofig: Gofig) -> None:
    """Standalone save function that works regardless of namespace conflicts."""
    if 'save' not in gofig._namespaced:
        raise RuntimeError("No save method available")
    savefunc = getattr(gofig, gofig._namespaced['save'])
    savefunc()

def reload(gofig: Gofig) -> Gofig:
    """Standalone reload function that works regardless of namespace conflicts."""
    if 'reload' not in gofig._namespaced:
        raise RuntimeError("No reload method available")
    reloadfunc = getattr(gofig, gofig._namespaced['reload'])
    reloadfunc()
    return gofig
