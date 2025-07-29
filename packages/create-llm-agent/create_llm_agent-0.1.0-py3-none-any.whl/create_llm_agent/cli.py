#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Agent - Enhanced version with auto-setup, and improvements.
Includes logic for vendoring Jinja2/MarkupSafe from embedded base64 strings
(actual base64 data needs to be provided by the user).
Fallback to pip install for Jinja2/MarkupSafe if not embedded or pre-installed.
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
import shutil
import logging
import re
from typing import Optional, List, Dict, Any
import platform
from dataclasses import dataclass, field
import unicodedata
from datetime import datetime
import gzip # Added for embedded wheel decompression

# --- Determine SCRIPT_DIR and Execution Context (Piped or File) ---
_IS_PIPED_EXECUTION = False
_SCRIPT_FILE_PATH_IN_MAIN = getattr(sys.modules.get('__main__'), '__file__', None)

if __name__ == "__main__" and \
   (not _SCRIPT_FILE_PATH_IN_MAIN or \
    Path(_SCRIPT_FILE_PATH_IN_MAIN).name == '<stdin>' or \
    _SCRIPT_FILE_PATH_IN_MAIN == '-'):
    SCRIPT_DIR = Path.cwd()
    _IS_PIPED_EXECUTION = True
else:
    SCRIPT_DIR = Path(_SCRIPT_FILE_PATH_IN_MAIN or __file__).parent.resolve()

# =================== PYTHON VERSION CHECK ======================
if sys.version_info < (3, 9):
    print("ERRO: Este script requer Python versão 3.9 ou superior.", file=sys.stderr)
    print(f"Sua versão: {sys.version.splitlines()[0]}", file=sys.stderr)
    sys.exit(1)

# =================== LOGGING CONFIG ======================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("create_agent")
if _IS_PIPED_EXECUTION:
    logger.debug(f"Execução via pipe (ou similar) detectada. SCRIPT_DIR={SCRIPT_DIR} (cwd)")
else:
    logger.debug(f"Execução via arquivo de script detectada. SCRIPT_DIR={SCRIPT_DIR}")


# =================== VENDORING PREPARATION & JINJA2 LOADER ===================
import base64
import zipfile # Though not directly used in current _load_single_embedded_wheel, good to have if strategy changes
import tempfile
import importlib
# import site # Not strictly needed now
import atexit

# --- Placeholders for Base64 encoded wheels ---
# TODO: PASTE YOUR ACTUAL BASE64 ENCODED (AND GZIPPED) WHEEL CONTENT HERE
# Replace the entire placeholder string including the """..."""
EMBEDDED_OPENAI_WHEEL_B64 = """PLACEHOLDER_FOR_OPENAI_WHEEL_BASE64_CONTENT_FROM_YOUR_FILE"""
EMBEDDED_JINJA2_WHEEL_B64 = """PLACEHOLDER_FOR_JINJA2_WHEEL_BASE64_CONTENT_FROM_YOUR_FILE"""
EMBEDDED_MARKUPSAFE_WHEEL_B64 = """PLACEHOLDER_FOR_MARKUPSAFE_WHEEL_BASE64_CONTENT_FROM_YOUR_FILE"""


_temp_vendored_dir_path: Optional[Path] = None
_temp_sys_path_additions: List[str] = []

def _cleanup_vendored_dependencies():
    global _temp_vendored_dir_path, _temp_sys_path_additions
    for path_entry in list(_temp_sys_path_additions): # Iterate over a copy
        if path_entry in sys.path:
            try:
                sys.path.remove(path_entry)
                logger.debug(f"Removed from sys.path: {path_entry}")
            except ValueError:
                pass # Already removed or not found
    if _temp_vendored_dir_path and _temp_vendored_dir_path.exists():
        try:
            shutil.rmtree(_temp_vendored_dir_path)
            logger.debug(f"Removed temporary vendored directory: {_temp_vendored_dir_path}")
        except Exception as e:
            logger.warning(f"Could not remove temp vendored directory {_temp_vendored_dir_path}: {e}")
    _temp_sys_path_additions.clear()
    _temp_vendored_dir_path = None

atexit.register(_cleanup_vendored_dependencies)

def _is_placeholder(b64_string: str) -> bool:
    return not b64_string or b64_string.startswith("PLACEHOLDER_") or len(b64_string) < 200 # Real B64 strings are long

def _load_single_embedded_wheel(wheel_b64_content: str, wheel_module_name: str, temp_dir_for_wheels: Path) -> bool:
    if _is_placeholder(wheel_b64_content):
        logger.debug(f"No embedded wheel content (placeholder found) for {wheel_module_name}.")
        return False
    try:
        logger.info(f"Attempting to load embedded wheel for {wheel_module_name}...")
        
        # Step 1: Base64 decode
        decoded_gzipped_bytes = base64.b64decode(wheel_b64_content)
        # Step 2: Gzip decompress
        wheel_bytes = gzip.decompress(decoded_gzipped_bytes)
        
        # Use a descriptive name for the temp wheel file
        # Use a random suffix to avoid potential collisions if this function were called multiple times for same module (not current use case)
        temp_wheel_file = temp_dir_for_wheels / f"{wheel_module_name.lower()}_embedded_{os.urandom(4).hex()}.whl"
        temp_wheel_file.write_bytes(wheel_bytes) # Write the original wheel bytes
        
        wheel_path_str = str(temp_wheel_file.resolve())
        if wheel_path_str not in sys.path:
            sys.path.insert(0, wheel_path_str)
            _temp_sys_path_additions.append(wheel_path_str)
        logger.info(f"Embedded wheel for {wheel_module_name} prepared at {temp_wheel_file} and added to sys.path.")
        return True
    except Exception as e:
        logger.error(f"Failed to decode/load embedded wheel for {wheel_module_name}: {e}", exc_info=True) # Log full traceback for this error
        return False

def _ensure_openai_is_available():
    global _temp_vendored_dir_path
    try:
        import openai
        logger.debug("OpenAI already available in current environment.")
        return
    except ModuleNotFoundError:
        logger.info("OpenAI not found. Attempting to load embedded or install.")

    if not _temp_vendored_dir_path:
        try:
            _temp_vendored_dir_path = Path(tempfile.mkdtemp(prefix="createagent_vendor_"))
            logger.debug(f"Created temporary directory for vendored wheels: {_temp_vendored_dir_path}")
        except Exception as e:
            logger.error(f"Could not create temporary directory for vendoring: {e}. Pip fallback will be attempted.")
            _temp_vendored_dir_path = None

    vendored_openai_loaded = False
    if _temp_vendored_dir_path: # Proceed only if temp dir was created
        if vendored_openai_loaded:
            if _load_single_embedded_wheel(EMBEDDED_OPENAI_WHEEL_B64, "Jinja2", _temp_vendored_dir_path):
                try:
                    importlib.invalidate_caches()
                    import openai
                    vendored_openai_loaded = True
                    logger.info("Jinja2 loaded successfully from embedded wheel.")
                except ImportError as e:
                    logger.warning(f"Failed to import OpeanAI after preparing embedded wheel: {e}")
        elif not _is_placeholder(EMBEDDED_OPENAI_WHEEL_B64): # Only log if OpeanAI wheel was actually provided
            logger.debug("Skipping load of embedded OpeanAI was not loaded from embedded.")

    if vendored_openai_loaded:
        logger.debug("Successfully loaded OpeanAI from embedded wheels.")
        return

    if _is_placeholder(EMBEDDED_OPENAI_WHEEL_B64):
        logger.info("Placeholders for embedded OpenAI detected or loading from embed failed.")
    
    logger.info("Attempting to install OpenAI using pip as a fallback...")
    pip_cmd = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--quiet", "openai>=1.0"]
    try:
        _run_subprocess([sys.executable, "-m", "pip", "--version"], description="Pip availability check", capture_output=True, log_output_on_debug=False)
        _run_subprocess(pip_cmd, description="pip install opeanai", log_output_on_debug=True)
        importlib.invalidate_caches()
        import openai
        logger.info("OpenAI successfully installed/found and imported via pip.")
    except (RuntimeError, subprocess.CalledProcessError) as e:
        logger.error(f"Failed to install OpenAI using pip: {e}")
        logger.critical("OpenAI is required. It could not be loaded or installed.\nPlease install it manually (e.g., 'pip install opeanai') and try again.")
        sys.exit(1)
    except ImportError as e:
        logger.error(f"ImportError for OpenAI after pip attempt: {e}")
        logger.critical("Jinja2 was reported as installed by pip, but cannot be imported.\nThere might be an issue with your Python environment or PATH.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred while trying to ensure OpenAI availability: {e}", exc_info=True)
        sys.exit(1)

def _ensure_jinja_is_available():
    global _temp_vendored_dir_path
    try:
        import jinja2
        import markupsafe
        logger.debug("Jinja2 and MarkupSafe already available in current environment.")
        return
    except ModuleNotFoundError:
        logger.info("Jinja2 and/or MarkupSafe not found. Attempting to load embedded or install.")

    if not _temp_vendored_dir_path:
        try:
            _temp_vendored_dir_path = Path(tempfile.mkdtemp(prefix="createagent_vendor_"))
            logger.debug(f"Created temporary directory for vendored wheels: {_temp_vendored_dir_path}")
        except Exception as e:
            logger.error(f"Could not create temporary directory for vendoring: {e}. Pip fallback will be attempted.")
            _temp_vendored_dir_path = None

    vendored_markup_loaded = False
    if _temp_vendored_dir_path: # Proceed only if temp dir was created
        if _load_single_embedded_wheel(EMBEDDED_MARKUPSAFE_WHEEL_B64, "MarkupSafe", _temp_vendored_dir_path):
            try:
                importlib.invalidate_caches()
                import markupsafe
                vendored_markup_loaded = True
                logger.info("MarkupSafe loaded successfully from embedded wheel.")
            except ImportError as e:
                logger.warning(f"Failed to import MarkupSafe after preparing embedded wheel: {e}")

    vendored_jinja_loaded = False
    if _temp_vendored_dir_path: # Proceed only if temp dir was created
        if vendored_markup_loaded:
            if _load_single_embedded_wheel(EMBEDDED_JINJA2_WHEEL_B64, "Jinja2", _temp_vendored_dir_path):
                try:
                    importlib.invalidate_caches()
                    import jinja2
                    vendored_jinja_loaded = True
                    logger.info("Jinja2 loaded successfully from embedded wheel.")
                except ImportError as e:
                    logger.warning(f"Failed to import Jinja2 after preparing embedded wheel: {e}")
        elif not _is_placeholder(EMBEDDED_JINJA2_WHEEL_B64): # Only log if Jinja2 wheel was actually provided
            logger.debug("Skipping load of embedded Jinja2 as its dependency MarkupSafe was not loaded from embedded.")

    if vendored_jinja_loaded and vendored_markup_loaded:
        logger.debug("Successfully loaded Jinja2 and MarkupSafe from embedded wheels.")
        return

    if _is_placeholder(EMBEDDED_JINJA2_WHEEL_B64) or _is_placeholder(EMBEDDED_MARKUPSAFE_WHEEL_B64):
        logger.info("Placeholders for embedded Jinja2/MarkupSafe detected or loading from embed failed.")
    
    logger.info("Attempting to install Jinja2 and MarkupSafe using pip as a fallback...")
    pip_cmd = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--quiet", "jinja2>=3.0", "markupsafe>=2.0"]
    try:
        _run_subprocess([sys.executable, "-m", "pip", "--version"], description="Pip availability check", capture_output=True, log_output_on_debug=False)
        _run_subprocess(pip_cmd, description="pip install Jinja2 & MarkupSafe", log_output_on_debug=True)
        importlib.invalidate_caches()
        import jinja2 
        import markupsafe
        logger.info("Jinja2 and MarkupSafe successfully installed/found and imported via pip.")
    except (RuntimeError, subprocess.CalledProcessError) as e:
        logger.error(f"Failed to install Jinja2/MarkupSafe using pip: {e}")
        logger.critical("Jinja2 is required. It could not be loaded or installed.\nPlease install it manually (e.g., 'pip install jinja2 markupsafe') and try again.")
        sys.exit(1)
    except ImportError as e:
        logger.error(f"ImportError for Jinja2/MarkupSafe after pip attempt: {e}")
        logger.critical("Jinja2 was reported as installed by pip, but cannot be imported.\nThere might be an issue with your Python environment or PATH.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred while trying to ensure Jinja2 availability: {e}", exc_info=True)
        sys.exit(1)

# =================== CONSTANTS (continued) =========================
PROFILES_BASE_DIR = SCRIPT_DIR / "project_profiles"
UTILS_DIR = SCRIPT_DIR / "utils"
CONFIG_FILE = SCRIPT_DIR / "config.json"
CREATE_AGENT_VERSION = "0.1.0" # Version increment for vendoring logic
DEFAULT_PROFILE_MARKER_FILENAME = ".create_agent_default_profile_initialized"

# =================== STATIC CONTENT & JINJA RENDERER INITIALIZATION ===================
class StaticContent:
    JINJA_RENDERER_CODE = """# utils/jinja_renderer.py
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import logging
import re
import unicodedata # N°3: Importação para normalização Unicode
from datetime import datetime

logger = logging.getLogger(__name__)

class JinjaRenderer:
    def __init__(self, templates_dir: Path):
        if not templates_dir.is_dir():
            logger.error(f"Diretório de templates não encontrado: {templates_dir}")
            raise FileNotFoundError(f"Diretório de templates não encontrado: {templates_dir}")

        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml', 'jinja', 'yml', 'md', 'py', 'toml', 'txt', 'sh', 'yaml']),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

        self.env.filters['slugify'] = self._slugify
        self.env.filters['camelcase'] = self._camelcase
        self.env.filters['pascalcase'] = self._pascalcase

        self.env.globals['now'] = datetime.now
        self.env.globals['current_year'] = datetime.now().year

        logger.debug(f"JinjaRenderer inicializado com templates de: {templates_dir}")

    def _slugify(self, text: str) -> str: # N°3: Função _slugify atualizada
        text = str(text) 
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^\\w\\s-]", "", text.lower()).strip() 
        return re.sub(r"[-\\s]+", "-", text) 

    def _camelcase(self, text: str) -> str:
        s = self._slugify(text).replace('-', ' ').replace('_', ' ') 
        components = s.split()
        if not components: return ""
        return components[0].lower() + "".join(x.title() for x in components[1:])

    def _pascalcase(self, text: str) -> str:
        s = self._slugify(text).replace('-', ' ').replace('_', ' ') 
        components = s.split()
        if not components: return ""
        return "".join(x.title() for x in components)

    def render(self, template_name: str, context: dict) -> str:
        try:
            template = self.env.get_template(template_name)
            logger.debug(f"Renderizando template: {template_name}")
            return template.render(context)
        except Exception as e:
            logger.error(f"Erro ao renderizar template '{template_name}': {e}")
            raise
"""
    DEFAULT_PROFILE_TEMPLATES = {
        "README.md.jinja": """# {{ project_name }}

Bem-vindo ao seu novo projeto de Agente LLM: "{{ project_name }}"!

Gerado com o perfil '{{ profile_name }}' (create-agent v{{ create_agent_version }}).
Autor: {{ author_name }} <{{ author_email }}>
Licença: {{ license_type }}

## Próximos Passos
1.  Ative o ambiente virtual:
    ```bash
{%- if with_poetry %}
    poetry shell
{%- else %}
    source venv/bin/activate  # Linux/macOS
    # .\\venv\\Scripts\\activate  # Windows
{%- endif %}
    ```
2.  Instale dependências (se não usar Poetry e houver `requirements.txt`):
    ```bash
{%- if not with_poetry %}
    pip install -r requirements.txt
    # pip install -r requirements-dev.txt # Se existir
{%- endif %}
    ```
3.  Configure suas chaves de API: copie `.env.example` para `.env` e edite-o.
4.  Inicialize o pre-commit (se habilitado):
    ```bash
{%- if with_pre_commit %}
    pre-commit install
{%- endif %}
    ```
5.  Explore `main.py` e comece a desenvolver!
""",
"main.py.jinja": """# main.py para {{ project_name }}
import os
import sys
from dotenv import load_dotenv
import logging

from collections.abc import Callable
from typing import Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REGISTRY: dict[str, Callable[..., Any]] = {}
def tool(fn):
    REGISTRY[fn.__name__] = fn
    return fn

def dispatch_tool_call(call):
    import json, inspect
    fn   = REGISTRY[call.function.name]
    data = json.loads(call.function.arguments or "{}")
    return fn(**data) if inspect.signature(fn).parameters else fn()

from datetime import datetime

@tool
def hora_atual():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")

# Carrega as variáveis de ambiente do arquivo .env
def load_env():
    logger.info(f"Agente 'meu_primeiro_agent' iniciado.")
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    api_model = os.getenv("OPENAI_API_MODEL")

    if not api_key or api_key == "your_openai_api_key_here":
        logger.warning("OPENAI_API_KEY não configurada ou com valor padrão em .env.")
        logger.info("Edite o arquivo .env com sua chave para usar a API da OpenAI.")
        raise ValueError("Chave da API da OpenAI não configurada corretamente.")
    
    if not base_url:
        logger.warning("OPENAI_URL_BASE não configurada ou com valor padrão em .env.")
        logger.info("Edite o arquivo .env com a URL base da API da OpenAI.")
        raise ValueError("URL base da API da OpenAI não configurada corretamente.")
    
    if not api_model:
        logger.warning("OPENAI_API_MODEL não configurada ou com valor padrão em .env.")
        logger.info("Edite o arquivo .env com o modelo da OpenAI que deseja usar.")
        raise ValueError("Modelo da API da OpenAI não configurado corretamente.")

    logger.info("Chave OpenAI API carregada.")

    return api_key, base_url, api_model

def run_agent(client, api_model, user_input):

    messages = [
        {"role": "system", "content": "você é o cronos, um agente que informa a hora atual quando solicitado."},
        {"role": "user", "content": user_input}
    ]

    tools = [{
        "type": "function",
        "function": {
            "name": "hora_atual",
            "description": "obtem a hora atual no formato YYYY-MM-DDTHH:MI:SSZ",
            "parameters": {"type": "object", "properties": {}}
        }
    }]

    completion = client.chat.completions.create(
        model=api_model,
        messages=messages,
        tools=tools,
        temperature=0.1,
        top_p=1.0, 
        tool_choice="auto"
    )

    if not completion.choices[0].message.tool_calls:
        logger.info("Nenhuma chamada de ferramenta foi feita.")
        return completion.choices[0].message.content
    
    call = completion.choices[0].message.tool_calls[0]
    result = dispatch_tool_call(call)

    messages.extend([
        completion.choices[0].message,
        {
            "role": "tool",
            "tool_call_id": call.id,
            "content": result
        }
    ])

    answer = client.chat.completions.create(
        model=api_model,
        messages=messages
    )
     
    return answer.choices[0].message.content

def main():
    try:
        load_dotenv()
        load_env()

        api_key, base_url, api_model = load_env()

        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)

        print("Digite 'sair' para encerrar o cronos ou faça uma pergunta: ")
        user_input = ''
        while True:
            user_input = input("cronos> ")
            if user_input.lower() == 'sair':
                print("Encerrando o cronos.")
                break
            
            response = run_agent(client, api_model, user_input)
            print(f"cronos: {response}")
        
        return 0
    except Exception as e:
        logger.critical(f"Erro fatal no cronos: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())

""",
        "requirements.txt.jinja": """# Dependências principais para {{ project_name }}
# Este arquivo é usado se --poetry NÃO for especificado.
python-dotenv>=1.0.0
# openai>=1.0.0
# langchain>=0.1.0
""",
        "requirements-dev.txt.jinja": """# Dependências de desenvolvimento para {{ project_name }} (sem Poetry)
# pytest>=7.0.0
# black
# flake8
# mypy
{% if with_pre_commit %}pre-commit>=3.0.0{% endif %}
""",
        "pyproject.toml.jinja": """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{{ project_slug }}"
version = "0.1.0"
description = "Projeto LLM '{{ project_name }}' gerado por create-agent."
authors = [
    {name = "{{ author_name }}", email = "{{ author_email }}"},
]
readme = "README.md"
requires-python = ">={{ python_version }}"
license = {text = "{{ license_type }}"}
keywords = ["llm", "agent", "ai"]

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "{{ license_classifier }}",
    "Programming Language :: Python :: {{ python_version }}",
    "Programming Language :: Python :: 3 :: Only",
]
dependencies = [
    # "python-dotenv>=1.0.0",
]

[project.scripts]
# {{ project_slug }}_cli = "{{ project_slug }}.cli:main"

[project.urls]
Homepage = "https://github.com/example_user/{{ project_slug }}"

# --- Configurações de Ferramentas ---
[tool.black]
line-length = 88
target-version = ['py{{ python_version.replace('.', '') }}']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "{{ python_version }}"
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --cov={{ project_slug }} --cov-report=html --cov-report=term"
testpaths = [ "tests",]
python_files = "test_*.py"

{% if with_poetry %}
# --- Configurações Específicas do Poetry ---
[tool.poetry]
name = "{{ project_slug }}"
version = "0.1.0"
description = "Projeto LLM '{{ project_name }}' gerado por create-agent (Poetry)."
authors = ["{{ author_name }} <{{ author_email }}>"]
license = "{{ license_type }}"
readme = "README.md"
packages = [{include = "{{ project_slug }}"}]

[tool.poetry.dependencies]
python = ">={{ python_version }}"
python-dotenv = ">=1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = ">=7.0.0"
pytest-cov = ">=3.0.0"
black = {extras = ["jupyter"], version = ">=23.0.0"}
flake8 = ">=6.0.0"
mypy = ">=1.0.0"
isort = ">=5.0.0"
{% if with_pre_commit %}pre-commit = ">=3.0.0"{% endif %}
ipykernel = ">=6.0.0"
{% endif %}
""",
        ".env.example.jinja": """# Variáveis de Ambiente para {{ project_name }}
OPENAI_API_KEY="your_openai_api_key_here"
OPENAI_BASE_URL="https://api.groq.com/openai/v1"
OPENAI_API_MODEL="meta-llama/llama-4-scout-17b-16e-instruct"
# LANGCHAIN_TRACING_V2="true"
# LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
# LANGCHAIN_API_KEY="your_langsmith_api_key_here"
# LANGCHAIN_PROJECT="{{ project_slug }}"
""",
        ".gitignore.jinja": """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
*.manifest
*.spec
pip-log.txt
pip-delete-this-directory.txt
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/
pytestdebug.log
*.mo
*.pot
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
instance/
.webassets-cache
.scrapy
docs/_build/
target/
.ipynb_checkpoints
profile_default/
ipython_config.py
__pypackages__/
celerybeat-schedule
celerybeat.pid
.sage/
.env
.env.local
.env.*.local
!.env.example
.venv
venv/
ENV/
env/
virtualenv/
venv.bak/
.direnv/
env.bak/
poetry.lock
.vscode/
!.vscode/settings.json
!.vscode/extensions.json
!.vscode/launch.json
.idea/
*.project
*.pydevproject
*.tmproj
*.sublime-workspace
*.sublime-project
nbproject/
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
desktop.ini
logs/
*.sql
*.sqlite
*.sqlite3
*.db
*.bak
*.swp
*~
*.tmp
.mypy_cache/
""",
        "poetry.toml.jinja": """# poetry.toml para {{ project_name }}
[virtualenvs]
in-project = true # Cria .venv na raiz do projeto
# prefer-active-python = true # Opcional
""",
        ".vscode/settings.json.jinja": """{
    // Configurações VSCode para {{ project_name }}
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true,
    "files.eol": "\\n",
    "editor.rulers": [88, 100]
}
"""
    }

JinjaRenderer = None # Global placeholder

@dataclass
class ProjectConfig:
    # ... (ProjectConfig definition remains the same) ...
    project_name: str
    profile_name: str
    author_name: str = "Your Name"
    author_email: str = "your.email@example.com"
    python_version: str = field(default_factory=lambda: f"{sys.version_info.major}.{sys.version_info.minor}")
    with_docker: bool = False
    with_compose: bool = False
    with_ci: bool = False
    with_poetry: bool = False
    with_pre_commit: bool = True
    license_type: str = "MIT"
    skip_install: bool = False

    def _get_project_slug(self) -> str:
        text = str(self.project_name)
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^a-zA-Z0-9\s_.-]", "", text.lower()).strip()
        text = re.sub(r"[\s._-]+", "_", text) 
        return text.strip("_")

    def to_jinja_context(self) -> Dict[str, Any]:
        license_classifiers = {
            "MIT": "License :: OSI Approved :: MIT License",
            "Apache-2.0": "License :: OSI Approved :: Apache Software License",
            "GPL-3.0": "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "BSD-3-Clause": "License :: OSI Approved :: BSD License",
            "UNLICENSED": "License :: Other/Proprietary License",
        }
        return {
            "project_name": self.project_name,
            "project_slug": self._get_project_slug(),
            "author_name": self.author_name,
            "author_email": self.author_email,
            "python_version": self.python_version,
            "create_agent_version": CREATE_AGENT_VERSION,
            "with_docker": self.with_docker,
            "with_compose": self.with_compose,
            "with_ci": self.with_ci,
            "with_poetry": self.with_poetry,
            "with_pre_commit": self.with_pre_commit,
            "license_type": self.license_type,
            "license_classifier": license_classifiers.get(self.license_type, "License :: Other/Proprietary License"),
            "platform": platform.system().lower(),
        }

# =================== UTILITY FUNCTIONS ... =======================
# ... (_run_subprocess, _ensure_utils_structure_and_renderer, _create_minimal_default_profile, etc.
#      load_user_config, save_user_config, detect_git_config, is_valid_project_name,
#      check_system_dependencies, get_available_profiles are the same as in the previous version with this structure)
def _run_subprocess(command: List[str], cwd: Optional[Path] = None, description: Optional[str] = None,
                    check: bool = True, capture_output: bool = True,
                    log_output_on_debug: bool = True) -> subprocess.CompletedProcess:
    log_msg_prefix = description or f"Comando '{command[0]}'"
    cmd_str = ' '.join(command)
    logger.debug(f"Executando: {cmd_str}{f' em {cwd}' if cwd else ''}")
    try:
        process = subprocess.run(
            command, cwd=cwd, capture_output=capture_output, text=True,
            check=check, encoding='utf-8', errors='surrogateescape'
        )
        if log_output_on_debug and capture_output:
            if process.stdout and logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Saída de {log_msg_prefix}: {process.stdout.strip()}")
            if process.stderr and logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Saída de erro (debug) de {log_msg_prefix}: {process.stderr.strip()}")
        return process
    except FileNotFoundError:
        logger.error(f"{log_msg_prefix} falhou: Executável '{command[0]}' não encontrado.")
        raise RuntimeError(f"Executável '{command[0]}' não encontrado. Verifique sua instalação e PATH.")
    except subprocess.CalledProcessError as e:
        err_msg = ""
        if capture_output:
            err_msg = e.stderr.strip() if e.stderr else ""
            if not err_msg and e.stdout:
                err_msg = e.stdout.strip()
        if not err_msg:
             err_msg = str(e)
        logger.error(f"{log_msg_prefix} falhou: {err_msg}")
        raise RuntimeError(f"{log_msg_prefix} falhou.")


def _ensure_utils_structure_and_renderer():
    global JinjaRenderer 
    if not UTILS_DIR.exists():
        logger.info(f"Criando diretório '{UTILS_DIR.name}' em '{SCRIPT_DIR}'...")
        try: UTILS_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e: logger.critical(f"Falha ao criar '{UTILS_DIR}': {e}", exc_info=True); sys.exit(1)
    init_py_path = UTILS_DIR / "__init__.py"
    if not init_py_path.exists():
        logger.info(f"Criando '{init_py_path.relative_to(SCRIPT_DIR)}'...")
        try: init_py_path.write_text("# Pacote Utils\nfrom .jinja_renderer import JinjaRenderer\n__all__=[\"JinjaRenderer\"]\n", encoding="utf-8")
        except Exception as e: logger.critical(f"Falha ao criar '{init_py_path.name}': {e}", exc_info=True); sys.exit(1)
    jinja_renderer_path = UTILS_DIR / "jinja_renderer.py"
    if not jinja_renderer_path.exists():
        logger.info(f"Criando '{jinja_renderer_path.relative_to(SCRIPT_DIR)}' (StaticContent)...")
        try: jinja_renderer_path.write_text(StaticContent.JINJA_RENDERER_CODE, encoding="utf-8")
        except Exception as e: logger.critical(f"Falha ao criar '{jinja_renderer_path.name}': {e}", exc_info=True); sys.exit(1)
    if JinjaRenderer is None:
        try:
            utils_parent_dir = str(UTILS_DIR.parent.resolve())
            if utils_parent_dir not in sys.path: sys.path.insert(0, utils_parent_dir)
            from utils.jinja_renderer import JinjaRenderer as ImportedRenderer
            JinjaRenderer = ImportedRenderer
            logger.debug("JinjaRenderer (classe) carregado de utils.")
        except ImportError as e: logger.critical(f"Falha ao importar JinjaRenderer de '{UTILS_DIR}': {e}", exc_info=True); sys.exit(1)
        except Exception as e: logger.critical(f"Erro inesperado ao carregar JinjaRenderer: {e}", exc_info=True); sys.exit(1)

def _create_minimal_default_profile(force_regeneration: bool = False):
    profile_dir = PROFILES_BASE_DIR / "default_profile"
    marker_file = profile_dir / DEFAULT_PROFILE_MARKER_FILENAME
    if force_regeneration and profile_dir.exists():
        logger.info(f"--force... ativo. Removendo '{profile_dir}' para recriação.")
        try: shutil.rmtree(profile_dir)
        except Exception as e: logger.error(f"Falha ao remover '{profile_dir}': {e}")
    if marker_file.exists() and not force_regeneration:
        logger.debug(f"'{profile_dir.name}' já marcado como inicializado. Pulando.")
        if not profile_dir.exists(): # Marker exists but dir doesn't
            logger.warning(f"Marcador '{marker_file.name}' encontrado mas '{profile_dir}' não existe. Tentando recriar.")
            try: marker_file.unlink(missing_ok=True) # Remove orphaned marker
            except Exception: pass
        else: return
    if not profile_dir.exists():
        logger.info(f"Criando/Recriando '{profile_dir.name}' em '{profile_dir.relative_to(SCRIPT_DIR)}' (templates estáticos)...")
        try: profile_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e: raise RuntimeError(f"Não foi possível criar '{profile_dir.name}': {e}")
    for rel_path_str, content in StaticContent.DEFAULT_PROFILE_TEMPLATES.items():
        file_path = profile_dir / rel_path_str
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
        except Exception as e: raise RuntimeError(f"Falha ao criar template '{file_path.name}': {e}")
    try:
        marker_file.write_text(f"v{CREATE_AGENT_VERSION} @ {datetime.now().isoformat()}", encoding="utf-8")
        logger.info(f"'{profile_dir.name}' criado/recriado e marcado.")
    except Exception as e: logger.warning(f"Falha ao escrever marcador para '{profile_dir.name}': {e}")


def ensure_project_profiles_structure(force_default_profile_regeneration: bool = False):
    if not PROFILES_BASE_DIR.exists():
        logger.info(f"'{PROFILES_BASE_DIR.name}' não encontrado em '{SCRIPT_DIR}'. Criando...")
        try: PROFILES_BASE_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e: logger.critical(f"Falha ao criar '{PROFILES_BASE_DIR}': {e}", exc_info=True); sys.exit(1)
    try: _create_minimal_default_profile(force_regeneration=force_default_profile_regeneration)
    except RuntimeError as e: logger.error(f"Não foi possível criar/garantir perfil padrão: {e}", exc_info=True)

def load_user_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        try: return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception as e: logger.warning(f"Erro ao carregar {CONFIG_FILE.relative_to(SCRIPT_DIR)}: {e}. Usando defaults.")
    return {}

def save_user_config(config_data: Dict[str, Any]):
    try:
        CONFIG_FILE.write_text(json.dumps(config_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        logger.info(f"Configuração salva em {CONFIG_FILE.relative_to(SCRIPT_DIR)}")
    except Exception as e: logger.warning(f"Erro ao salvar {CONFIG_FILE.relative_to(SCRIPT_DIR)}: {e}")

def detect_git_config() -> tuple[Optional[str], Optional[str]]:
    try:
        name_proc = _run_subprocess(["git", "config", "user.name"], capture_output=True, check=False, log_output_on_debug=False)
        email_proc = _run_subprocess(["git", "config", "user.email"], capture_output=True, check=False, log_output_on_debug=False)
        git_name = name_proc.stdout.strip() if name_proc.returncode == 0 else None
        git_email = email_proc.stdout.strip() if email_proc.returncode == 0 else None
        return git_name, git_email
    except RuntimeError: logger.debug("Git não encontrado. Nomes de autor não preenchidos via git.")
    except Exception as e: logger.warning(f"Erro não esperado ao detectar config Git: {e}")
    return None, None

def is_valid_project_name(name: str) -> bool:
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9._-]*$", name)) and name not in (".", "..")

def check_system_dependencies(config: ProjectConfig):
    logger.info("Verificando dependências do sistema...")
    deps_to_check = {"Python": [sys.executable, "--version"], "Pip": [sys.executable, "-m", "pip", "--version"], "Git": ["git", "--version"]}
    if config.with_docker or config.with_compose: deps_to_check["Docker"] = ["docker", "--version"]
    if config.with_poetry: deps_to_check["Poetry"] = ["poetry", "--version"]
    all_ok = True
    for tool, cmd in deps_to_check.items():
        try:
            proc = _run_subprocess(cmd, description=f"Verificação de {tool}", log_output_on_debug=False)
            output_lines = (proc.stdout or proc.stderr or "").strip().splitlines()
            version_info = output_lines[0] if output_lines else "(sem saída)"
            logger.debug(f"{tool} OK: {version_info}")
        except RuntimeError: logger.error(f"Falha na verificação: {tool}"); all_ok = False
        except Exception as e: logger.error(f"Erro ao verificar '{tool}': {e}"); all_ok = False
    if config.with_compose and all_ok:
        compose_ok = False
        try: _run_subprocess(["docker", "compose", "version"], description="Verificação Docker Compose (v2)", log_output_on_debug=False); compose_ok = True; logger.debug("Docker Compose (v2) OK.")
        except RuntimeError:
            logger.debug("Docker Compose (v2) não encontrado. Tentando v1.")
            try: _run_subprocess(["docker-compose", "--version"], description="Verificação Docker Compose (v1)", log_output_on_debug=False); compose_ok = True; logger.debug("Docker Compose (v1) OK.")
            except RuntimeError: logger.error("Docker Compose NÃO encontrado (nem v2 nem v1)."); all_ok = False
        if not compose_ok: all_ok = False
    if not all_ok: raise RuntimeError("Dependências críticas faltando ou com erro. Verifique os logs.")
    logger.info("✅ Dependências do sistema verificadas.")

def get_available_profiles(profiles_dir: Path = PROFILES_BASE_DIR) -> List[str]:
    if not profiles_dir.is_dir(): logger.warning(f"Diretório de perfis '{profiles_dir}' não encontrado."); return []
    return sorted([p.name for p in profiles_dir.iterdir() if p.is_dir() and not p.name.startswith((".", "__"))])

# ... (EnhancedAgentProjectCreator class definition from previous version) ...
class EnhancedAgentProjectCreator:
    def __init__(self, config: ProjectConfig):
        self.config = config
        self.project_path = Path.cwd() / config.project_name 
        self.profile_templates_path = PROFILES_BASE_DIR / config.profile_name
        if not self.profile_templates_path.is_dir():
            logger.error(f"Diretório de templates do perfil '{config.profile_name}' não encontrado em {self.profile_templates_path.relative_to(SCRIPT_DIR)}")
            raise ValueError(f"Perfil '{config.profile_name}' não encontrado.")
        if JinjaRenderer is None: 
            logger.critical("JinjaRenderer (classe) não disponível."); sys.exit("Falha crítica: JinjaRenderer não carregado.")
        try: self.jinja_renderer = JinjaRenderer(self.profile_templates_path)
        except Exception as e: logger.critical(f"Falha ao instanciar JinjaRenderer com '{self.profile_templates_path}': {e}", exc_info=True); sys.exit(1)
        logger.info(f"Criador inicializado para '{config.project_name}' (perfil: '{config.profile_name}')")
    def run(self):
        try:
            logger.info(f"🚀 Criando projeto '{self.config.project_name}' (perfil: '{self.config.profile_name}')")
            self._validate_project_target()
            check_system_dependencies(self.config)
            self._create_base_project_directory()
            self._render_all_profile_templates()
            if not self.config.skip_install:
                if self.config.with_poetry: self._setup_poetry_project()
                else: self._setup_pip_project()
            else:
                logger.info("Pulando instalação (--skip-install).")
                if not self.config.with_poetry: self._ensure_empty_venv_for_skip_install()
            self._setup_vscode_settings_if_needed()
            self._initialize_git_repository()
            if self.config.with_pre_commit:
                if not self.config.skip_install: self._setup_pre_commit_hooks()
                else: logger.info("Pulando setup pre-commit (--skip-install).")
            self._print_final_guidance()
            logger.info(f"✅ Projeto '{self.config.project_name}' criado em '{self.project_path.resolve()}'!")
        except (ValueError, FileExistsError, RuntimeError) as e: logger.critical(f"❌ Criação falhou: {e}"); sys.exit(1)
        except Exception as e: logger.critical(f"❌ Erro inesperado na criação: {e}", exc_info=True); sys.exit(1)
    def _validate_project_target(self):
        if not is_valid_project_name(self.config.project_name): raise ValueError(f"Nome inválido: '{self.config.project_name}'")
        if self.project_path.exists() and any(self.project_path.iterdir()): raise FileExistsError(f"'{self.project_path}' já existe e não está vazio.")
    def _create_base_project_directory(self):
        try: self.project_path.mkdir(parents=True, exist_ok=True); logger.info(f"📁 Diretório base '{self.project_path}' criado.")
        except OSError as e: raise RuntimeError(f"Falha ao criar {self.project_path}: {e}")
    def _should_skip_template_rendering(self, target_name: str) -> bool:
        if target_name == "poetry.toml" and not self.config.with_poetry: return True
        if not self.config.with_docker and ("dockerfile" in target_name.lower() or "dockerignore" in target_name.lower()): return True
        if not self.config.with_compose and "docker-compose" in target_name.lower(): return True
        if not self.config.with_ci and any(p == ".github" for p in Path(target_name).parts): return True
        return False
    def _render_single_template(self, template_file: Path, context: Dict[str, Any]) -> bool:
        relative_path = template_file.relative_to(self.profile_templates_path)
        target_filename_str = str(relative_path).replace(".jinja", "")
        if self._should_skip_template_rendering(target_filename_str):
            logger.debug(f"Pulando (condicional): {target_filename_str}"); return False
        target_file_path = self.project_path / target_filename_str
        target_file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            rendered_content = self.jinja_renderer.render(str(relative_path), context)
            target_file_path.write_text(rendered_content, encoding="utf-8")
            logger.debug(f"Renderizado: {relative_path} -> {target_filename_str}"); return True
        except Exception as e: logger.error(f"Erro em '{template_file.name}': {e}"); raise RuntimeError(f"Falha renderizar/escrever {template_file.name}.")
    def _render_all_profile_templates(self):
        logger.info(f"🎨 Renderizando templates do perfil '{self.config.profile_name}'...")
        jinja_context = self.config.to_jinja_context(); rendered_count = 0
        for template_file in self.profile_templates_path.rglob("*.jinja"):
            if self._render_single_template(template_file, jinja_context): rendered_count += 1
        if rendered_count == 0: logger.warning(f"Nenhum template renderizado para '{self.config.profile_name}'.")
        else: logger.info(f"✨ {rendered_count} templates renderizados.")
    def _setup_poetry_project(self):
        logger.info("📦 Configurando com Poetry...")
        try: _run_subprocess(["poetry", "install"], cwd=self.project_path, description="Poetry install", log_output_on_debug=True); logger.info("Dependências Poetry instaladas.")
        except RuntimeError: raise RuntimeError("Falha ao configurar com Poetry.")
    def _init_pip_venv(self) -> Path:
        venv_path = self.project_path / "venv"
        if venv_path.exists(): logger.info(f"Venv '{venv_path.name}' já existe."); return venv_path
        logger.info(f"🐍 Criando venv Pip em '{venv_path}'...")
        try: _run_subprocess([sys.executable, "-m", "venv", str(venv_path)], cwd=self.project_path, description="Criação venv Pip"); logger.info(f"Venv Pip '{venv_path.name}' criado."); return venv_path
        except RuntimeError: raise RuntimeError(f"Falha ao criar venv Pip em '{venv_path}'.")
    def _install_dependencies_in_pip_venv(self, venv_path: Path):
        logger.info("📦 Instalando dependências (Pip)...")
        pip_exe = venv_path / ("Scripts" if os.name == 'nt' else "bin") / "pip"
        if not pip_exe.exists(): raise RuntimeError(f"Pip não achado em {pip_exe}.")
        try:
            _run_subprocess([str(pip_exe), "install", "--upgrade", "pip", "setuptools", "wheel"], cwd=self.project_path, description="Upgrade Pip tools")
            req_file = self.project_path / "requirements.txt"
            if req_file.exists() and req_file.read_text().strip(): _run_subprocess([str(pip_exe), "install", "-r", str(req_file)], cwd=self.project_path, description=f"Install {req_file.name}")
            dev_req_file = self.project_path / "requirements-dev.txt"
            if dev_req_file.exists() and dev_req_file.read_text().strip(): _run_subprocess([str(pip_exe), "install", "-r", str(dev_req_file)], cwd=self.project_path, description=f"Install {dev_req_file.name}")
            elif self.config.with_pre_commit: _run_subprocess([str(pip_exe), "install", "pre-commit"], cwd=self.project_path, description="Install pre-commit (Pip)")
            logger.info("Dependências Pip instaladas.")
        except RuntimeError: raise RuntimeError("Falha ao instalar com Pip.")
    def _setup_pip_project(self): venv_path = self._init_pip_venv(); self._install_dependencies_in_pip_venv(venv_path)
    def _ensure_empty_venv_for_skip_install(self):
        venv_path = self.project_path / "venv"
        if venv_path.exists(): logger.info(f"Venv '{venv_path.name}' já existe (skip-install)."); return
        logger.info(f"🐍 Tentando criar venv (vazio) em {venv_path} (skip-install)...")
        try: _run_subprocess([sys.executable, "-m", "venv", str(venv_path)], cwd=self.project_path, description="Criação venv vazio (skip-install)"); logger.info("Venv (vazio) criado.")
        except RuntimeError: logger.warning("Falha ao criar venv vazio (skip-install). Crie manualmente.")
    def _setup_vscode_settings_if_needed(self):
        settings_file = self.project_path / ".vscode" / "settings.json"
        if not settings_file.exists(): logger.debug(f"'{settings_file.name}' não gerado. Pulando VSCode."); return
        try:
            with open(settings_file, 'r+', encoding='utf-8') as f:
                try: settings = json.load(f)
                except json.JSONDecodeError: settings = {}
                py_env_dir = ".venv" if self.config.with_poetry else "venv"; py_exe = "python.exe" if os.name == 'nt' else "python"; sb = "Scripts" if os.name == 'nt' else "bin"
                interpreter_vscode = f"${{workspaceFolder}}/{Path(py_env_dir, sb, py_exe).as_posix()}"; updated = False
                if settings.get("python.defaultInterpreterPath") != interpreter_vscode: settings["python.defaultInterpreterPath"] = interpreter_vscode; updated = True
                if updated: f.seek(0); json.dump(settings, f, indent=4); f.truncate(); f.write("\n"); logger.info(f"VSCode settings '{settings_file.name}' atualizado.")
                else: logger.debug(f"VSCode settings '{settings_file.name}' já correto.")
        except (IOError,json.JSONDecodeError) as e: logger.error(f"Erro R/W '{settings_file.name}': {e}")
        except Exception as e: logger.warning(f"Erro inesperado VSCode: {e}", exc_info=True)
    def _setup_pre_commit_hooks(self):
        logger.info("🔧 Configurando pre-commit hooks...")
        if not (self.project_path / ".pre-commit-config.yaml").exists(): logger.warning("'.pre-commit-config.yaml' não encontrado. Pulando."); return
        cmd_base = ["poetry", "run", "pre-commit"] if self.config.with_poetry else [str(self.project_path/"venv"/("Scripts" if os.name=='nt' else "bin")/"pre-commit")]
        if not self.config.with_poetry and not (self.project_path/"venv"/("Scripts" if os.name=='nt' else "bin")/"pre-commit").exists():
            pip_exe = self.project_path/"venv"/("Scripts" if os.name=='nt' else "bin")/"pip"
            if pip_exe.exists():
                logger.info(f"pre-commit não achado. Tentando instalar via {pip_exe}...")
                try: _run_subprocess([str(pip_exe), "install", "pre-commit"], cwd=self.project_path, description="Install pre-commit (Pip emergency)")
                except RuntimeError: logger.error("Falha ao instalar 'pre-commit'. Configure manualmente."); return
            else: logger.error(f"'pip' não encontrado para instalar 'pre-commit'. Configure manualmente."); return
        try: _run_subprocess(cmd_base + ["install"], cwd=self.project_path, description="Install pre-commit hooks"); logger.info("Pre-commit hooks instalados.")
        except RuntimeError: logger.warning("Falha ao instalar pre-commit hooks.")
    def _initialize_git_repository(self):
        if (self.project_path / ".git").exists(): logger.info("Git já inicializado."); return
        logger.info("📝 Inicializando Git...")
        try:
            _run_subprocess(["git", "init"], cwd=self.project_path, description="Git init")
            (self.project_path / ".gitattributes").write_text("* text=auto eol=lf\n", encoding="utf-8")
            _run_subprocess(["git", "add", ".gitattributes"], cwd=self.project_path, description="Git add .gitattributes")
            _run_subprocess(["git", "add", "."], cwd=self.project_path, description="Git add all")
            commit_msg = f"Initial commit: {self.config.project_name} (profile: {self.config.profile_name})"
            _run_subprocess(["git", "commit", "-m", commit_msg], cwd=self.project_path, description="Git initial commit")
            logger.info("✅ Git inicializado e commit feito.")
        except RuntimeError: logger.warning("Inicialização Git falhou. Verifique se Git está instalado.")
    def _print_final_guidance(self):
        logger.info("🎯 Próximos passos:"); steps = [f"1. Navegue: cd \"{self.config.project_name}\""]
        if not self.config.skip_install:
            act_cmd = "poetry shell" if self.config.with_poetry else (".\\venv\\Scripts\\activate" if os.name == 'nt' else "source venv/bin/activate")
            steps.extend([f"2. Ambiente virtual ({'Poetry' if self.config.with_poetry else 'venv'}) pronto.", f"   Reativar com: {act_cmd}"])
        else:
            steps.append("2. (--skip-install usado) Configure e ative ambiente virtual manualmente.")
            if self.config.with_poetry: steps.append("   Poetry: `poetry install` e `poetry shell`")
            else: steps.append(f"   venv: crie, ative, e instale dependências.")
        idx = 3
        if (self.project_path / ".env.example").exists(): steps.extend([f"{idx}. Configure .env:", "   Copie .env.example para .env e edite."]); idx+=1
        if self.config.with_pre_commit and (self.project_path / ".pre-commit-config.yaml").exists() and self.config.skip_install:
            pc_cmd = f"{'poetry run ' if self.config.with_poetry else ''}pre-commit install"; steps.append(f"{idx}. (--skip-install) Instale pre-commit hooks: `{pc_cmd}`"); idx+=1
        steps.extend([f"{idx}. Abra no VS Code: code .", f"{idx+1}. Consulte README.md e desenvolva!"]); print("\n" + "\n".join(steps) + "\n"); logger.info(f"Local: {self.project_path.resolve()}")

# =================== CLI & MAIN FUNCTION =========================
def create_cli_parser(user_prefs: Dict[str, Any], available_profiles: List[str]) -> tuple[argparse.ArgumentParser, Optional[str]]:
    git_name, git_email = detect_git_config()
    defaults = {"author_name": user_prefs.get("author_name", git_name or "Your Name"),"author_email": user_prefs.get("author_email", git_email or "your.email@example.com"), "profile": user_prefs.get("default_profile"),"license": user_prefs.get("default_license", "MIT"), "docker": user_prefs.get("with_docker", False),"compose": user_prefs.get("with_compose", False), "ci": user_prefs.get("with_ci", False),"poetry": user_prefs.get("with_poetry", False), "pre_commit": user_prefs.get("with_pre_commit", True),"skip_install": user_prefs.get("skip_install", False), "force_default_profile_regeneration": False,}
    det_def_prof = defaults["profile"]; Z = available_profiles
    if det_def_prof not in Z: det_def_prof = "default_profile" if "default_profile" in Z else (Z[0] if Z else None)
    parser = argparse.ArgumentParser(description=f"Create Agent (v{CREATE_AGENT_VERSION})", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("project_name", help="Nome do projeto.")
    prof_help = "Perfil." + ("\nDisponíveis:\n"+" ".join([f" - {p}"for p in Z])if Z else "\nERRO:Nenhum.")+(f"\n(Padrão:{det_def_prof})"if det_def_prof else "")
    parser.add_argument("--profile","-p",choices=Z if Z else None,default=argparse.SUPPRESS,help=prof_help)
    ag=parser.add_argument_group("Autoria");ag.add_argument("--author-name",default=defaults["author_name"],help=f"Autor (padrão:{defaults['author_name']}).");ag.add_argument("--author-email",default=defaults["author_email"],help=f"Email (padrão:{defaults['author_email']}).");ag.add_argument("--license",choices=["MIT","Apache-2.0","GPL-3.0","BSD-3-Clause","UNLICENSED"],default=defaults["license"],help=f"Licença (padrão:{defaults['license']}).")
    fg=parser.add_argument_group("Funcionalidades");fg.add_argument("--docker",action=argparse.BooleanOptionalAction,default=defaults["docker"],help="Docker.");fg.add_argument("--compose",action=argparse.BooleanOptionalAction,default=defaults["compose"],help="Compose.");fg.add_argument("--ci",action=argparse.BooleanOptionalAction,default=defaults["ci"],help="CI/CD.");fg.add_argument("--poetry",action=argparse.BooleanOptionalAction,default=defaults["poetry"],help="Poetry.");fg.add_argument("--pre-commit",action=argparse.BooleanOptionalAction,default=defaults["pre_commit"],help="Pre-commit.")
    ig=parser.add_argument_group("Instalação");ig.add_argument("--skip-install",action=argparse.BooleanOptionalAction,default=defaults["skip_install"],help="Pular install.");ig.add_argument("--force-default-profile-regeneration",action="store_true",default=defaults["force_default_profile_regeneration"],help="Força recriação do perfil 'default_profile'.")
    cg=parser.add_argument_group("Config Script");cg.add_argument("--save-prefs",action="store_true",help="Salvar opções.");cg.add_argument("--verbose","-v",action="store_true",help="DEBUG log.");cg.add_argument('--version',action='version',version=f'%(prog)s {CREATE_AGENT_VERSION}')
    return parser, det_def_prof

def main():
    _ensure_openai_is_available()
    _ensure_jinja_is_available()
    _ensure_utils_structure_and_renderer()
    user_prefs = load_user_config(); available_profiles = get_available_profiles(PROFILES_BASE_DIR)
    parser, determined_default_profile_for_cli = create_cli_parser(user_prefs, available_profiles)
    args = parser.parse_args()
    if args.verbose: logging.getLogger().setLevel(logging.DEBUG); logger.debug("Verbose mode.")
    logger.debug(f"CLI args: {vars(args)}")
    ensure_project_profiles_structure(force_default_profile_regeneration=args.force_default_profile_regeneration)
    if "default_profile" not in available_profiles and (PROFILES_BASE_DIR/"default_profile").exists(): available_profiles=get_available_profiles(PROFILES_BASE_DIR)
    if JinjaRenderer is None: logger.critical("JinjaRenderer não carregado."); sys.exit(1)
    if not available_profiles: logger.error(f"❌ Nenhum perfil em '{PROFILES_BASE_DIR}'."); sys.exit(1)
    selected_profile = getattr(args,'profile',None) or user_prefs.get('default_profile')
    if selected_profile not in available_profiles: selected_profile = determined_default_profile_for_cli
    if not selected_profile and len(available_profiles)>1 and sys.stdin.isatty():
        print("\nPerfis disponíveis:"); [print(f"  {i+1}. {p}")for i,p in enumerate(available_profiles)]
        while True:
            try: choice=input(f"Escolha (1-{len(available_profiles)}): ");selected_profile=available_profiles[int(choice)-1];break
            except (ValueError,IndexError): print("Inválido.")
            except KeyboardInterrupt: sys.exit("\nSeleção cancelada.")
    elif not selected_profile: selected_profile = available_profiles[0] if available_profiles else None
    if not selected_profile or not (PROFILES_BASE_DIR/selected_profile).exists(): sys.exit(f"Perfil '{selected_profile}' inválido.")
    logger.info(f"Usando perfil: '{selected_profile}'")
    if args.compose and not args.docker: logger.info("--compose implica --docker."); args.docker=True
    project_cfg=ProjectConfig(project_name=args.project_name,profile_name=selected_profile,author_name=args.author_name,author_email=args.author_email,with_docker=args.docker,with_compose=args.compose,with_ci=args.ci,with_poetry=args.poetry,with_pre_commit=args.pre_commit,license_type=args.license,skip_install=args.skip_install)
    logger.debug(f"ProjectConfig: {project_cfg}")
    if args.save_prefs:
        prefs_to_save={k:getattr(project_cfg,k)for k in["author_name","author_email","profile_name","license_type","with_docker","with_compose","with_ci","with_poetry","with_pre_commit","skip_install"]if hasattr(project_cfg,k)}
        if "profile_name" in prefs_to_save: prefs_to_save["default_profile"]=prefs_to_save.pop("profile_name")
        save_user_config(prefs_to_save)
    EnhancedAgentProjectCreator(project_cfg).run()

if __name__ == "__main__":
    try: main()
    except Exception as e: logger.critical(f"Erro fatal não tratado: {e}", exc_info=True); sys.exit(1)
    finally: _cleanup_vendored_dependencies()