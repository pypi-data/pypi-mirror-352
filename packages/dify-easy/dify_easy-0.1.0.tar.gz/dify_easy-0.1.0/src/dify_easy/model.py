import datetime
import inspect
import os
from enum import Enum
from pathlib import Path
from typing import Callable, get_args

import structlog
import yaml
from pydantic import BaseModel, Field

logger = structlog.get_logger()


PROVIDER_MARKER_ATTR = "_provider_function"
TOOL_MARKER_ATTR = "_tool_function"


def short_name_field():
    return Field(
        pattern=r"^[a-z0-9_-]{1,64}$",
        description="Alphanumeric characters and underscores only.",
    )


def provider(func):
    setattr(func, PROVIDER_MARKER_ATTR, True)
    return func


class Tool(BaseModel):
    name: str = short_name_field()
    label: str = name
    description: str = ""  # Automatically generated llm_description
    required: bool = True


def tool(_func=None, *, name=None, label=None, description=None):
    def decorator(func):
        setattr(func, TOOL_MARKER_ATTR, True)
        if name:
            setattr(func, "tool_name", name)
        if label:
            setattr(func, "tool_label", label)
        if description:
            setattr(func, "tool_description", description)
        return func

    if _func is None:
        return decorator
    else:
        return decorator(_func)


class ParamType(str, Enum):
    string: str = "string"
    number: str = "number"


class FormType(str, Enum):
    llm: str = "llm"
    schema: str = "schema"


class Param(BaseModel):
    name: str = short_name_field()
    label: str = str(name)
    description: str = ""
    llm_description: str = description  # TODO: Automatically generated llm_description
    type: ParamType = ParamType.string

    required: bool = True
    form: FormType = FormType.llm


class CredentialType(str, Enum):
    secret_input: str = "secret-input"
    text_input: str = "text-input"


class Credential:
    def __init__(
        self,
        name: str,
        label: str = None,
        placeholder: str = None,
        help: str = "",
        url: str = "",
        type: CredentialType = CredentialType.secret_input,
        required: bool = True,
    ):
        self.name = name
        self.label = label or name
        self.placeholder = placeholder or name
        self.help = help
        self.url = url
        self.type = type
        self.required = required


class MetaInfo(BaseModel):
    name: str = short_name_field()
    author: str = short_name_field()
    version: str = "0.0.1"

    label: str = str(name)
    description: str

    icon: str = "icon.svg"


class BasePlugin(BaseModel):

    meta: MetaInfo = None
    credentials: BaseModel = None

    def find_decorated_methods(self, marker_attr: str) -> list[Callable]:
        decorated_methods: list[Callable] = []

        for name, member in inspect.getmembers(self):
            if callable(member):
                if getattr(member, marker_attr, False):
                    decorated_methods.append(member)

        return decorated_methods

    def generate_manifest(self):
        manifest = {
            "version": self.meta.version,
            "type": "plugin",
            "author": self.meta.author,
            "name": self.meta.name,
            "label": {
                "en_US": self.meta.label,
            },
            "description": {
                "en_US": self.meta.description,
            },
            "icon": self.meta.icon,
            "resource": {"memory": 268435456, "permission": {}},
            "plugins": {"tools": [f"provider/{self.meta.name}.yaml"]},
            "meta": {
                "version": self.meta.version,
                "arch": ["amd64", "arm64"],
                "runner": {
                    "language": "python",
                    "version": "3.12",
                    "entrypoint": "main",
                },
            },
            "created_at": datetime.datetime.now().isoformat("T") + "Z",
            "privacy": "PRIVACY.md",
            "verified": False,
        }

        # First make sure `manifest.yaml` exists
        if os.path.exists("manifest.yaml"):
            with open("manifest.yaml", "w", encoding="utf-8") as f:
                yaml.dump(manifest, f, allow_unicode=True, sort_keys=False)
        else:
            logger.error("Error: manifest.yaml does not exist. Please create it first.")
            return

    def generate_tools(self):

        for func in self.find_decorated_methods(TOOL_MARKER_ATTR):

            sig = inspect.signature(func)
            parameters: list[Param] = []

            for _, param in sig.parameters.items():
                _, _param = get_args(param.annotation)
                assert isinstance(
                    _param, Param
                ), f"Expected Param type, got {type(_param)}"
                parameters.append(_param)

            tool = {
                "identity": {
                    "name": func.tool_name,
                    "author": self.meta.author,
                    "label": {
                        "en_US": func.tool_label,
                    },
                },
                "description": {
                    "human": {
                        "en_US": func.tool_description,
                    },
                    "llm": func.tool_description,
                },
                "parameters": [
                    {
                        "name": param.name,
                        "type": param.type.value,
                        "required": param.required,
                        "label": {"en_US": param.label},
                        "human_description": {
                            "en_US": param.description,
                        },
                        "llm_description": param.llm_description,
                        "form": param.form.value,
                    }
                    for param in parameters
                ],
                "extra": {"python": {"source": f"tools/{func.__name__}.py"}},
            }

            # Generate yaml files
            with open(f"tools/{func.__name__}.yaml", "w", encoding="utf-8") as f:
                yaml.dump(
                    tool,
                    f,
                    allow_unicode=True,
                    sort_keys=False,
                )
                logger.info(f"Generated tool: tools/{func.__name__}.yaml")

            # Generate Python files
            with open(f"tools/{func.__name__}.py", "w", encoding="utf-8") as f:
                import_statement = generate_import_statement(
                    inspect.getfile(func), os.getcwd()
                )
                # read the template from the file
                template_file = (
                    Path(__file__).parent / "dify-plugin-pdm-template-tool.template"
                )
                with open(template_file, "r", encoding="utf-8") as template_f:
                    template = template_f.read()

                plugin_cls = self.__class__.__name__
                credentials_cls = self.credentials.__class__.__name__
                content = template.format(
                    import_statement=import_statement,
                    plugin_cls=plugin_cls,
                    credentials_cls=credentials_cls,
                    func_name=func.__name__,
                )
                f.write(content)

                logger.info(f"Generated tool implementation: tools/{func.__name__}.py")

    def generate_providers(self):

        # Check the existence of the provider function
        provider_funcs = self.find_decorated_methods(PROVIDER_MARKER_ATTR)
        assert (
            len(provider_funcs) == 1
        ), f"Expected exactly one provider function, found {len(provider_funcs)}"

        credentials: list[Credential] = []

        for _, field_info in type(self.credentials).model_fields.items():

            metadata_list = field_info.metadata
            found_credential = None

            for meta_item in metadata_list:
                if isinstance(meta_item, Credential):
                    found_credential = meta_item
                    break

            if found_credential:
                credentials.append(found_credential)

        provider = {
            "identity": {
                "author": self.meta.author,
                "name": self.meta.name,
                "label": {
                    "en_US": self.meta.label,
                },
                "description": {
                    "en_US": self.meta.description,
                },
                "icon": self.meta.icon,
            },
            "credentials_for_provider": {
                credential.name: {
                    "type": credential.type.value,
                    "required": credential.required,
                    "label": {
                        "en_US": credential.label,
                    },
                    "placeholder": {
                        "en_US": credential.placeholder,
                    },
                    "help": {
                        "en_US": credential.help,
                    },
                    "url": credential.url,
                }
                for credential in credentials
            },
            "tools": [
                f"tools/{func.__name__}.yaml"
                for func in self.find_decorated_methods(TOOL_MARKER_ATTR)
                if hasattr(func, TOOL_MARKER_ATTR)
            ],
            "extra": {"python": {"source": f"provider/{self.meta.name}.py"}},
        }

        # Generate yaml files
        with open(f"provider/{self.meta.name}.yaml", "w", encoding="utf-8") as f:
            yaml.dump(
                provider,
                f,
                allow_unicode=True,
                sort_keys=False,
            )
            logger.info(f"Generated provider: providers/{self.meta.name}.yaml")

        # Generate Python files
        with open(f"provider/{self.meta.name}.py", "w", encoding="utf-8") as f:
            import_statement = generate_import_statement(
                inspect.getfile(provider_funcs[0]), os.getcwd()
            )
            # read the template from the file
            template_file = (
                Path(__file__).parent / "dify-plugin-pdm-template-provider.template"
            )
            with open(template_file, "r", encoding="utf-8") as template_f:
                template = template_f.read()

            plugin_cls = self.__class__.__name__
            credentials_cls = self.credentials.__class__.__name__
            content = template.format(
                import_statement=import_statement,
                plugin_cls=plugin_cls,
                credentials_cls=credentials_cls,
                provider_func_name=provider_funcs[0].__name__,
            )
            f.write(content)

            logger.info(
                f"Generated provider implementation: providers/{self.meta.name}.py"
            )


def generate_import_statement(file_path: str, project_root: str) -> str:
    file = Path(file_path).resolve()
    root = Path(project_root).resolve()

    relative = file.relative_to(root).with_suffix("")
    import_path = ".".join(relative.parts)

    return f"from {import_path} import *"
