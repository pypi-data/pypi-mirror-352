""" main module of git_repo_manager. """
import ast
import datetime
import glob
import os
import pprint
import re
import shutil
import sys
import tempfile
import time

from collections import OrderedDict
from contextlib import contextmanager
from difflib import context_diff, diff_bytes, ndiff, unified_diff
from functools import wraps
from traceback import format_exc
from typing import (
    Any, Callable, Collection, Iterable, Iterator, Optional, OrderedDict as OrderedDictType,
    Sequence, TYPE_CHECKING, Union, cast)

from github import Github, Auth, GithubException
from github.AuthenticatedUser import AuthenticatedUser
from github.Repository import Repository

from gitlab import Gitlab, GitlabCreateError, GitlabError, GitlabHttpError
from gitlab.const import MAINTAINER_ACCESS
from gitlab.v4.objects import Group, Project, User

from packaging.version import Version
from PIL import Image

import requests

import ae.base                                                                          # type: ignore # for patching
from ae.base import (
    PY_EXT, PY_INIT, TEMPLATES_FOLDER, UNSET, UnsetType,
    camel_to_snake, duplicates, in_wd, load_dotenvs, module_attr, norm_name, norm_path,
    os_path_abspath, os_path_basename, os_path_dirname, os_path_isdir, os_path_isfile, os_path_join,
    os_path_relpath, os_path_sep, os_path_splitext,
    project_main_file, read_file, stack_var, write_file)
from ae.files import FileObject                                                         # type: ignore
from ae.paths import (                                                                  # type: ignore
    Collector, FilesRegister, coll_folders, copy_file, move_file, path_files, path_items, paths_match,
    skip_py_cache_files)
from ae.dynamicod import try_eval                                                       # type: ignore
from ae.literal import Literal                                                          # type: ignore
from ae.updater import MOVES_SRC_FOLDER_NAME, UPDATER_ARGS_SEP, UPDATER_ARG_OS_PLATFORM  # type: ignore
from ae.core import DEBUG_LEVEL_DISABLED                                                # type: ignore
from ae.console import STDERR_BEG_MARKER, sh_exec, ConsoleApp                           # type: ignore

from aedev.pythonanywhere import PythonanywhereApi                                      # type: ignore
from aedev.setup_project import (                                                       # type: ignore
    APP_PRJ, DJANGO_PRJ, MODULE_PRJ, NO_PRJ, PACKAGE_PRJ, PARENT_PRJ, PLAYGROUND_PRJ, ROOT_PRJ,
    VERSION_PREFIX, VERSION_QUOTE,
    pev_str, pev_val, project_env_vars)

# --------------- global constants ------------------------------------------------------------------------------------

ANY_PRJ_TYPE = (APP_PRJ, DJANGO_PRJ, MODULE_PRJ, PACKAGE_PRJ, PLAYGROUND_PRJ, ROOT_PRJ)
""" tuple of real project types (not including the pseudo-project-types: no-/incomplete-project and parent-folder) """
ALL_PRJ_TYPES = ANY_PRJ_TYPE + (NO_PRJ, PARENT_PRJ)         #: all projec types (including no/parent project)

ARG_MULTIPLES = ' ...'                                      #: mark multiple args in the :func:`_action` arg_names kwarg
ARG_ALL = 'all'                                             #: `all` argument, for lists, e.g., of namespace portions
ARGS_CHILDREN_DEFAULT = ((ARG_ALL, ), ('children-sets-expr', ), ('children-names' + ARG_MULTIPLES, ))
""" default arguments for children actions. """

_CG_ERR_PREFIX = "_cl() returned error "                    #: used by _cg() to return _cl() err code in the first line

CMD_PIP = "python -m pip"                                   #: pip command using python venvs, especially on Windows
CMD_INSTALL = f"{CMD_PIP} install"                          #: pip install command

COMMIT_MSG_FILE_NAME = '.commit_msg.txt'                    #: name of the file containing the commit message

DJANGO_EXCLUDED_FROM_CLEANUP = {'db.sqlite', 'project.db', '**/django.mo', 'media/**/*', 'static/**/*'}
""" set of file path masks/pattern to exclude essential files from to be cleaned-up on the server. """

GIT_FOLDER_NAME = '.git'                                    #: git subfolder in project path root of local repository

NULL_VERSION = '0.0.0'                                      #: initial package version number for a new project

LOCK_EXT = '.locked'                                        #: additional file extension to block updates from templates

MAIN_BRANCH = 'develop'                                     #: main/develop/default branch name

MOVE_TPL_TO_PKG_PATH_NAME_PREFIX = 'de_mtp_'
""" template file/folder name prefix, to move the templates to the package path (instead of the project path);
has to be specified after :data:`SKIP_IF_PORTION_DST_NAME_PREFIX` (if both prefixes are needed).
"""

OUTSOURCED_MARKER = 'THIS FILE IS EXCLUSIVELY MAINTAINED'   #: to mark an outsourced project file, maintained externally
OUTSOURCED_FILE_NAME_PREFIX = 'de_otf_'                     #: name prefix of an outsourced/externally maintained file

PROJECT_VERSION_SEP = '=='                                  #: separates package name and version in pip req files

PPF = pprint.PrettyPrinter(indent=6, width=189, depth=12).pformat   #: formatter for console printouts

SKIP_IF_PORTION_DST_NAME_PREFIX = 'de_sfp_'                 #: skip portion prj template dst root folder/file nam prefix
SKIP_PRJ_TYPE_FILE_NAME_PREFIX = 'de_spt_'                  #: file name prefix of skipped template if dst != prj type

# these TEMPLATE_* constants get added by :func:`project_dev_vars` to be used/recognized by :func:`refresh_templates`
TEMPLATE_PLACEHOLDER_ID_PREFIX = "# "                       #: template id prefix marker
TEMPLATE_PLACEHOLDER_ID_SUFFIX = "#("                       #: template id suffix marker
TEMPLATE_PLACEHOLDER_ARGS_SUFFIX = ")#"                     #: template args suffix marker
TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID = "IncludeFile"        #: placeholder (func:`replace_with_file_content_or_default`)

TPL_FILE_NAME_PREFIX = 'de_tpl_'                            #: file name prefix if template contains f-strings
TPL_IMPORT_NAME_PREFIX = 'aedev.tpl_'                       #: package/import name prefix of template projects
TPL_STOP_CNV_PREFIX = '_z_'                                 #: file name prefix to support template of template

TPL_PACKAGES = [TPL_IMPORT_NAME_PREFIX + norm_name(_) for _ in ANY_PRJ_TYPE] + [TPL_IMPORT_NAME_PREFIX + 'project']
""" import names of all possible template projects """

TEMPLATES_FILE_NAME_PREFIXES = (
    SKIP_IF_PORTION_DST_NAME_PREFIX, SKIP_PRJ_TYPE_FILE_NAME_PREFIX, OUTSOURCED_FILE_NAME_PREFIX, TPL_FILE_NAME_PREFIX,
    TPL_STOP_CNV_PREFIX)
""" supported template file name prefixes (in the order they have to specified, apart from :data:`TPL_STOP_CNV_PREFIX`
which can be specified anywhere, to deploy template files to other template projects).

.. hint::
    :data:`SKIP_IF_PORTION_DST_NAME_PREFIX` can also be path name prefix, like :data:`MOVE_TPL_TO_PKG_PATH_NAME_PREFIX`.
"""

VERSION_MATCHER = re.compile("^" + VERSION_PREFIX + r"(\d+)[.](\d+)[.](\d+)[a-z\d]*" + VERSION_QUOTE, re.MULTILINE)
""" pre-compiled regular expression to detect and bump the app/portion file version numbers of a version string.

The version number format has to be :pep:`conform to PEP396 <396>` and the sub-part to `Pythons distutils
<https://docs.python.org/3/distutils/setupscript.html#additional-meta-data>`__ (trailing version information indicating
sub-releases, are either “a1,a2,…,aN” (for alpha releases), “b1,b2,…,bN” (for beta releases) or “pr1,pr2,…,prN” (for
pre-releases). Note that distutils got deprecated in Python 3.12 (see package :mod:`packaging.version` as replacement)).
"""


ActionArgs = list[str]                                      #: action arguments specified on grm command line
ActionArgNames = tuple[tuple[str, ...], ...]
# ActionFunArgs = tuple[PdvType, str, ...]                  # silly mypy does not support tuple with dict, str, ...
# silly mypy: ugly casts needed for ActionSpecification = dict[str, Union[str, ActionArgNames, bool]]
ActionFlags = dict[str, Any]                                #: action flags/kwargs specified on grm command line
Replacer = Callable[[str], str]

# RegisteredActionValues = Union[bool, str, ActionArgNames, Sequence[str], Callable]
ActionSpec = dict[str, Any]                                 # mypy errors if Any get replaced by RegisteredActionValues
RegisteredActions = dict[str, ActionSpec]

RegisteredTemplateProject = dict[str, str]                  #: registered template project info (tpl_projects item)
RegisteredTemplates = dict[str, RegisteredTemplateProject]

# PdvVarType = list[RegisteredTemplateProject]; mypy does not recognize PevType: Union[PevType, dict[str, PdvVarType]]
PdvType = dict[str, Any]                                    #: project development variables type
ChildrenType = OrderedDictType[str, PdvType]                #: children pdv of a project parent or a namespace root

RepoType = Union[Repository, Project]                       #: repo host libs repo object (PyGithub, python-gitlab)


# --------------- global variables - most of them are constant after app initialization/startup -----------------------


REGISTERED_ACTIONS: RegisteredActions = {}                  #: implemented actions registered via :func:`_action` deco

_RCS: dict[str, Callable] = {}
""" registered recordable callees, for check* actions, using other actions with temporary redirected callees. """

REGISTERED_HOSTS_CLASS_NAMES: dict[str, str] = {}           #: class names of all supported remote host domains

REGISTERED_TPL_PROJECTS: RegisteredTemplates = {}           #: projects providing templates and outsourced files

TEMP_CONTEXT: Optional[tempfile.TemporaryDirectory] = None  #: temp patch folder context (optional/lazy/late created)
TEMP_PARENT_FOLDER: str                                     #: temporary parent folder for to clone git repos into

# because ae.core determines the app version with stack_var('__version__') it doesn't find it, alternatively to pass
# it via the app_version kwarg to ConsoleApp() the next line could be uncommented:
# __version__ = module_attr('aedev.git_repo_manager', '__version__'))
cae = ConsoleApp(app_name="grm", app_version=module_attr('aedev.git_repo_manager', '__version__'),
                 debug_level=DEBUG_LEVEL_DISABLED)          # DEBUG_LEVEL_VERBOSE is now default in ae.core/ae.console
""" main app instance of this grm tool, initialized out of __name__ == '__main__' to be used for unit tests """


# --------------- dev helper functions, decorators and context managers -----------------------------------------------


def _action(*project_types: str, **deco_kwargs) -> Callable:     # Callable[[Callable], Callable]:
    """ parametrized decorator to declare functions and :class:`RemoteHost` methods as `grm` actions. """
    if not project_types:
        project_types = ALL_PRJ_TYPES

    def _deco(fun):
        # global REGISTERED_ACTIONS
        method_of = stack_var('__qualname__')
        if 'local_action' not in deco_kwargs:
            deco_kwargs['local_action'] = not method_of
        if project_types == (PARENT_PRJ, ROOT_PRJ) and 'arg_names' not in deco_kwargs:
            deco_kwargs['arg_names'] = ARGS_CHILDREN_DEFAULT
        doc_str = os.linesep.join(_ for _ in fun.__doc__.split(os.linesep)
                                  if ':param ini_pdv:' not in _ and ':return:' not in _)
        REGISTERED_ACTIONS[(method_of + "." if method_of else "") + fun.__name__] = {
            'annotations': fun.__annotations__, 'docstring': doc_str, 'project_types': project_types, **deco_kwargs}

        @wraps(fun)
        def _wrapped(*fun_args, **fun_kwargs):  # fun_args==(self, ) for remote action methods and ==() for functions
            return fun(*fun_args, **fun_kwargs)
        return _wrapped

    return _deco


def _recordable_function(callee: Callable) -> Callable:
    """ decorator to register function as recordable (to be replaced/redirected in protocol mode). """
    _RCS[callee.__name__] = callee
    return callee


def _rc_id(instance: Any, method_name: str) -> str:
    """ compile recordable callee id of object method or module instance attribute/function. """
    return f'{getattr(instance, "__class__", instance).__name__}.{method_name}'


_RCS[_rc_id(ae.base, 'write_file')] = ae.base.write_file
_RCS[_rc_id(os, 'makedirs')] = os.makedirs


@contextmanager
def _record_calls(*recordable_methods: Any, **recordable_functions: Callable) -> Iterator[None]:
    assert len(recordable_methods) % 3 == 0, "expecting (object-or-module, method_name, callee) argument triple(s)"

    ori_callees = {}

    try:
        for obj_idx in range(0, len(recordable_methods), 3):
            instance, method_name, callee = recordable_methods[obj_idx: obj_idx + 3]
            obj_method = _rc_id(instance, method_name)
            ori_callees[obj_method] = _RCS[obj_method]
            _RCS[obj_method] = callee

        for callee_name, callee in recordable_functions.items():
            ori_callees[callee_name] = _RCS[callee_name]
            _RCS[callee_name] = callee

        yield

    finally:
        for callee_name, ori_call in ori_callees.items():
            _RCS[callee_name] = ori_call


# --------------- global helpers --------------------------------------------------------------------------------------


def activate_venv(name: str = "") -> str:
    """ ensure to activate a virtual environment if it is different to the current one (the one on Python/app start).

    :param name:                the name of the venv to activate. if this arg is empty or not specified, then the venv
                                of the project in the current working directory tree will be activated.
    :return:                    the name of the previously active venv
                                or an empty string if the requested or no venv was active, or if venv is not supported.
    """
    old_name = active_venv()
    bin_path = venv_bin_path(name)
    if not old_name or not bin_path:
        if name and old_name:
            cae.dpo(f"    * the venv '{name}' does not exists - skipping switch from current venv '{old_name}'")
        else:
            cae.vpo("    # venv {name=} activation skipped {os.getcwd()=} {old_name=} {bin_path=}")
        return ""

    activate_script_path = os_path_join(bin_path, 'activate')
    if not os_path_isfile(activate_script_path):
        cae.po(f"    * skipping venv activation, because the activate script '{activate_script_path}' does not exist")
        return ""

    new_name = bin_path.split(os_path_sep)[-2]
    if old_name == new_name:
        cae.vpo(f"    # skipped activation of venv '{new_name}' because it is already activated")
        return ""

    cae.dpo(f"    - activating venv: switching from current venv '{old_name}' to '{new_name}'")
    out: list[str] = []    # venv activation command line inspired by https://stackoverflow.com/questions/7040592
    _cl(123, f"env -i bash -c 'set -a && source {activate_script_path} && env -0'", lines_output=out, shell=True)
    if out and "\0" in out[0]:      # fix error for APP_PRJ (e.g. kivy_lisz)
        os.environ.update(line.split("=", maxsplit=1) for line in out[0].split("\0"))   # type: ignore

    return old_name


def active_venv() -> str:
    """ determine the virtual environment that is currently active.

    .. note:: the current venv gets set via `data:`os.environ` on start of this Python app or by :func:`activate_venv`.

    :return:                    the name of the currently active venv.
    """
    return os.getenv('VIRTUAL_ENV', "").split(os_path_sep)[-1]


def bump_file_version(file_name: str, increment_part: int = 3) -> str:
    """ increment part of a version number of a module/script file, also removing any pre/alpha version subpart/suffix.

    :param file_name:           module/script file name to be patched/version-bumped.
    :param increment_part:      version number part to increment: 1=mayor, 2=minor, 3=build/revision (default=3).
    :return:                    empty string on success, else error string.
    """
    return replace_file_version(file_name, increment_part=increment_part)


def bytes_file_diff(file_content: bytes, file_path: str, line_sep: str = os.linesep) -> str:
    """ return the differences between the content of a file against the specified file content buffer.

    :param file_content:        older file bytes to be compared against the file content of the file specified by the
                                :paramref:`~bytes_file_diff.file_path` argument.
    :param file_path:           path to the file of which newer content gets compared against the file bytes specified
                                by the :paramref:`~bytes_file_diff.file_content` argument.
    :param line_sep:            string used to prefix, separate and indent the lines in the returned output string.
    :return:                    differences between the two file contents, compiled with the `git diff` command.
    """
    with tempfile.NamedTemporaryFile('w+b', delete=False) as tfp:  # delete_on_close kwarg available in Python 3.12+
        tfp.write(file_content)
        tfp.close()
        output = _cg(72, "git diff", extra_args=("--no-index", tfp.name, file_path), exit_on_err=False)
        os.remove(tfp.name)

    if output and line_sep != os.linesep:
        output[0] = line_sep + output[0]

    return line_sep.join(output)


def deploy_template(tpl_file_path: str, dst_path: str, patcher: str, pdv: PdvType,
                    logger: Callable = print,
                    replacer: Optional[dict[str, Replacer]] = None,
                    dst_files: Optional[set[str]] = None) -> bool:
    """ create/update outsourced project file content from a template.

    :param tpl_file_path:       template file path/name.ext (absolute or relative to the current working directory).
    :param dst_path:            absolute or relative destination path without the destination file name. relative paths
                                are relative to the project root path (the `project_path` item in the
                                :paramref:`~deploy_template.pdv` argument).
    :param patcher:             patching template project or function (to be added into the outsourced project file).
    :param pdv:                 project env/dev variables dict of the destination project to patch/refresh.
                                providing values for (1) f-string template replacements, and (2) to specify the project
                                type, and root or package data folder (in the `project_type`, and `project_path` or
                                `package_path` items).
    :param logger:              print()-like callable for logging.
    :param replacer:            optional dict with multiple replacer: key=placeholder-id and value=replacer callable.
    :param dst_files:           optional set of project file paths to be excluded from to be created/updated. if the
                                project file got created/updated by this function, then the destination file path will
                                be added to this set.
    :return:                    boolean True if template got deployed/written to the destination, else False.

    .. note::
         the project file will be kept unchanged if either:

         * the absolute file path is in the set specified by the :paramref:`~deploy_template.dst_files` argument,
         * there exists a lock-file with the additional :data:`LOCK_EXT` file extension, or
         * the outsourced project text does not contain the :data:`OUTSOURCED_MARKER` string.

    """
    if replacer is None:
        replacer = {}
    if dst_files is None:
        dst_files = set()

    dst_file = os_path_basename(tpl_file_path)

    if dst_file.startswith(SKIP_IF_PORTION_DST_NAME_PREFIX):
        dst_file = dst_file[len(SKIP_IF_PORTION_DST_NAME_PREFIX):]

    if dst_file.startswith(SKIP_PRJ_TYPE_FILE_NAME_PREFIX):
        project_type, dst_file = dst_file[len(SKIP_PRJ_TYPE_FILE_NAME_PREFIX):].split('_', maxsplit=1)
        if project_type == pdv['project_type']:
            logger(f"    - destination-project-type-skip ({project_type=}) of template {tpl_file_path}")
            return False

    outsourced = dst_file.startswith(OUTSOURCED_FILE_NAME_PREFIX)
    formatting = dst_file.startswith(TPL_FILE_NAME_PREFIX)
    mode = "" if outsourced or formatting else "b"

    new_content = read_file(tpl_file_path, extra_mode=mode)

    if outsourced:
        new_content = _patch_outsourced(dst_file, new_content, patcher)
        dst_file = dst_file[len(OUTSOURCED_FILE_NAME_PREFIX):]
        formatting = dst_file.startswith(TPL_FILE_NAME_PREFIX)
    if formatting:
        new_content = patch_string(new_content, pdv, **replacer)
        dst_file = dst_file[len(TPL_FILE_NAME_PREFIX):]
    if dst_file.startswith(TPL_STOP_CNV_PREFIX):    # needed only for de_otf__z_de_tpl_*.* or _z_*.* template files
        dst_file = dst_file[len(TPL_STOP_CNV_PREFIX):]

    deployed = False
    dst_path = os_path_join(pdv.get('project_path', ""), dst_path)   # project_path ignored on absolute dst_path
    dst_file = norm_path(os_path_join(dst_path, patch_string(dst_file, pdv)))
    if dst_file in dst_files:
        deploy_state = "lower-priority-skip"
    else:
        dst_files.add(dst_file)
        if os_path_isfile(dst_file + LOCK_EXT):
            deploy_state = "lock-extension-skip"
        else:
            old_content = read_file(dst_file, extra_mode=mode) if os_path_isfile(dst_file) else b"" if mode else ""
            if old_content and mode:
                deploy_state = "binary-exists-skip"
            elif new_content == old_content:
                deploy_state = "unchanged-skip"
            elif not mode and old_content and OUTSOURCED_MARKER not in old_content:
                deploy_state = "missing-outsourced-marker-skip"
            else:
                if not os_path_isdir(dst_path):
                    _RCS[_rc_id(os, 'makedirs')](dst_path)
                _RCS[_rc_id(ae.base, 'write_file')](dst_file, new_content, extra_mode=mode)
                deploy_state = "refresh"
                deployed = True

    logger(f"    - {deploy_state} of template {tpl_file_path}")
    return deployed


def editable_project_path(project_name: str) -> str:
    """ determine the project path of a project package installed as editable.

    :param project_name:        project package name to search for.
    :return:                    project source root path of an editable installed package
                                or empty string, if an editable installed package could not be found.
    """
    for install_path in sys.path:
        egg_link_file = os_path_join(install_path, project_name + '.egg-link')
        if os_path_isfile(egg_link_file):
            return read_file(egg_link_file).split(os.linesep)[0]
    return ""


def find_extra_modules(project_path: str, namespace_name: str = "", portion_name: str = "") -> list[str]:
    """ determine additional modules of a local (namespace portion) project.

    :param project_path:        file path of the local namespace project root directory/folder. passing an empty string
                                will search in the current working directory.
    :param namespace_name:      namespace name or pass an empty string for non-namespace-portion projects.
    :param portion_name:        name of the portion (folder). pass an empty string for non-namespace-portion projects.
    :return:                    list of module import name strings (without file extension and path separators as dots).
                                modules in :data:`TEMPLATES_FOLDER` as well as :data:`PY_INIT` modules are excluded.
    """
    pkg_path = norm_path(os_path_join(project_path, namespace_name, portion_name))
    if not os_path_isdir(pkg_path):
        return []

    base = os_path_basename
    rel_path = os_path_relpath
    path_sep = os_path_sep

    def _select_file(file_path: str) -> bool:
        return not rel_path(file_path, pkg_path).startswith(TEMPLATES_FOLDER + path_sep) and base(file_path) != PY_INIT

    def _create_file(file_path: str) -> str:
        return rel_path(file_path, pkg_path).replace(path_sep, '.')[:-len(PY_EXT)]

    return path_items(os_path_join(pkg_path, "**", '*' + PY_EXT), selector=_select_file, creator=_create_file)


def find_git_branch_files(project_path: str, branch_or_tag: str = MAIN_BRANCH, untracked: bool = False,
                          skip_file_path: Callable[[str], bool] = lambda _: False) -> set[str]:
    """ find all added/changed/deleted/renamed/unstaged worktree files that are not merged into the main branch.

    :param project_path:        path of the project root folder. pass empty string to use the current working directory.
    :param branch_or_tag:       branch(es)/tag(s)/commit(s) passed to `git diff <https://git-scm.com/docs/git-diff>`__
                                to specify the changed files between version(s).
    :param skip_file_path:      called for each found file passing the file path relative to the project root folder
                                (specified by the :paramref:`~find_git_branch_files.project_path` argument), returning
                                True to exclude/skip the file with passed file path.
    :param untracked:           pass True to include untracked files from the returned result set.
    :return:                    set of file paths relative to worktree root specified by the project root path
                                specified by the :paramref:`~find_git_branch_files.project_path` argument.
    """
    file_paths = set()

    def _call(_cmd: str, _args: tuple[str, ...], _dedent: int = 0):
        _output = _cg(18, _cmd, extra_args=_args)
        for _fil_path in _output:
            _fil_path = _fil_path[_dedent:]
            if not skip_file_path(_fil_path):
                file_paths.add(_fil_path)

    with _in_prj_dir_venv(project_path):
        if untracked:
            _call("git ls-files", ("--cached", "--others"))
            _call("git status", ("--find-renames", "--porcelain",  "--untracked-files", "-v"), _dedent=3)
        # --compact-summary is alternative to --name-only
        _call("git diff", ("--find-renames", "--full-index", "--name-only", "--no-color", branch_or_tag))

    return file_paths


def find_project_files(project_path: str, root_path_masks: list[str],
                       skip_file_path: Callable[[str], bool] = lambda _: False
                       ) -> set[str]:
    """ find all files of a python package including the .py modules.

    :param project_path:        path of the project root folder. pass empty string to use the current working directory.
    :param root_path_masks:     list of folder or subpackage path masks with wildcards, relative to the project root.
    :param skip_file_path:      called for each found file with their file path (relative to project root folder in
                                :paramref:`~find_project_files.project_path`) as argument, returning True to
                                exclude/skip the specified file.
    :return:                    set of file paths relative to the project root folder specified by the argument
                                :paramref:`~find_project_files.project_path`.
    """
    file_paths = set()
    for root_pkg_path in sorted(root_path_masks):
        for file_path in glob.glob(os_path_join(project_path, root_pkg_path), recursive=True):
            if os_path_isfile(file_path) and not skip_file_path(file_path):
                file_paths.add(os_path_relpath(file_path, project_path))

    return file_paths


def increment_version(version: Union[str, Iterable[str]], increment_part: int = 3) -> str:
    """ increment version number.

    :param version:             version number string or an iterable of version string parts.
    :param increment_part:      part of the version number to increment (1=mayor, 2=minor, 3=patch).
    :return:                    incremented version number.
    """
    if isinstance(version, str):
        version = version.split(".")

    return ".".join(str(int(part_str) + 1) if part_idx + 1 == increment_part else part_str
                    for part_idx, part_str in enumerate(version))


def install_requirements(req_file: str, project_path: str = ""):
    """ install requirements from requirements*.txt file with pip

    :param req_file:            pip requirements.txt file path.
    :param project_path:        project root folder path.
    :return:                    0/zero on installation without errors, else pip error return code.
    """
    project_path = norm_path(project_path)
    with _in_prj_dir_venv(project_path):
        sh_err = _cl(12, f"{CMD_INSTALL} -r {req_file}", exit_on_err=False)

    return sh_err


@contextmanager
def in_venv(name: str = "") -> Iterator[None]:
    """ ensure the virtual environment gets activated within the context.

    :param name:                the name of the venv to activate. if not specified, then the venv of the project in the
                                current working directory tree will be activated.
    """
    old_venv = activate_venv(name)
    yield
    if old_venv:
        activate_venv(old_venv)


def main_file_path(project_path: str, project_type: str, namespace_name: str) -> str:
    """ return the file path of the main/version type for the specified project type.

    :param project_path:        project path, including the package name as basename.
    :param project_type:        project type to determine the main/version file path for.
    :param namespace_name:      namespace name if for namespace portion or root projects, else pass empty string.
    :return:                    main file path and name.
    """
    main_path = project_path

    main_stem = os_path_basename(project_path)
    if namespace_name:
        main_path = os_path_join(main_path, namespace_name)
        main_stem = main_stem[len(namespace_name) + 1:]

    if project_type in (DJANGO_PRJ, PACKAGE_PRJ, ROOT_PRJ):
        main_path = os_path_join(main_path, namespace_name if project_type == ROOT_PRJ else main_stem)
        main_name = PY_INIT
    elif project_type == APP_PRJ:
        main_name = 'main' + PY_EXT
    else:
        main_name = main_stem + PY_EXT

    return os_path_join(main_path, main_name)


def on_ci_host() -> bool:
    """ check and return True if this tool is running on the GitLab/GitHub CI host/server.

    :return:                    True if running on CI host, else False
    """
    return 'CI' in os.environ or 'CI_PROJECT_ID' in os.environ


def project_version(imp_or_pkg_name: str, packages_versions: list[str]) -> Sequence[str]:
    """ determine package name and version in the specified list of package/version strings.

    :param imp_or_pkg_name:     import or package name to search.
    :param packages_versions:   project package versions string: <project_name>[<PROJECT_VERSION_SEP><project_version>].
    :return:                    sequence of package name and version number. the package name is an empty string if it
                                is not in :paramref:`~project_version.packages_versions`. the version number is an
                                empty string if no package version is specified in
                                :paramref:`~project_version.packages_versions`.
    """
    project_name = norm_name(imp_or_pkg_name)
    for imp_or_pkg_name_and_ver in packages_versions:
        imp_or_pkg_name, *ver = imp_or_pkg_name_and_ver.split(PROJECT_VERSION_SEP)
        prj_name = norm_name(imp_or_pkg_name)
        if prj_name == project_name:
            return project_name, ver[0] if ver else ""
    return "", ""


def patch_string(content: str, pdv: PdvType, **replacer: Replacer) -> str:
    """ replace f-string / dynamic placeholders in content with variable values / return values of replacer callables.

    :param content:             f-string to patch (e.g., a template file's content).
    :param pdv:                 project env/dev vars dict with variables used as globals for f-string replacements.
    :param replacer:            optional kwargs dict with key/name=placeholder-id and value=replacer-callable. if not
                                 passed, then the replacer with id TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID will be searched
                                and if found the callable :func:`replace_with_file_content_or_default` will be executed.
    :return:                    string extended with include snippets found in the same directory.
    :raises Exception:          if evaluation of :paramref;`~patch_string.content` f-string failed (because of
                                missing-globals-NameError/SyntaxError/ValueError/...).
    """
    glo_vars = globals().copy()     # provide globals of this module, e.g., COMMIT_MSG_FILE_NAME for .gitignore template
    glo_vars.update(pdv)
    glo_vars['_add_base_globals'] = ""
    content = try_eval('f"""' + content.replace('"""', r'\"\"\"') + '"""', glo_vars=glo_vars)
    if content:
        content = content.replace(r'\"\"\"', '"""')     # recover docstring delimiters

    for key, fun in replacer.items() or ((TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID, replace_with_file_content_or_default),):
        beg = 0
        pre = TEMPLATE_PLACEHOLDER_ID_PREFIX + key + TEMPLATE_PLACEHOLDER_ID_SUFFIX
        len_pre = len(pre)
        suf = TEMPLATE_PLACEHOLDER_ARGS_SUFFIX
        len_suf = len(suf)

        while True:
            beg = content.find(pre, beg)
            if beg == -1:
                break
            end = content.find(suf, beg)
            assert end != -1, f"patch_string() placeholder {key} is missing args suffix marker ({suf})"
            content = content[:beg] + fun(content[beg + len_pre: end]) + content[end + len_suf:]

    return content


def pdv_str(pdv: PdvType, var_name: str) -> str:
    """ string value of project development variable :paramref:`~pdv_str.var_name` of :paramref:`~pdv_str.pdv`.

    :param pdv:                 project development variables dict.
    :param var_name:            name of variable.
    :return:                    variable value or if not exists in pdv then the constant/default value of the module
                                :mod:`aedev_setup_project`, or any empty string if no constant with this name exists.
    :raises AssertionError:     if the specified variable value is not of type `str`. in this case, use the function
                                :func:`pdv_val` instead.
    """
    value = pev_str(pdv, var_name)
    if not value and var_name not in pdv and _debug_or_verbose():
        cae.po(f"    # project dev variable {var_name} does not exist" + (f" in: {PPF(pdv)}" if cae.verbose else ""))
    return value


def pdv_val(pdv: PdvType, var_name: str) -> Any:        # silly mypy does not allow PdvVarType
    """ determine the project development variable value from the specified pdv argument.

    :param pdv:                 project environment variables dict.
    :param var_name:            name of the variable to determine the value of.
    :return:                    project env var or module constant value. empty string if variable is not defined.
    """
    value = pev_val(pdv, var_name)
    if not value and var_name not in pdv and _debug_or_verbose():
        cae.po(f"     # project dev var value {var_name} does not exist" + (f" in: {PPF(pdv)}" if cae.verbose else ""))
    return value


def project_dev_vars(project_path: str = "") -> PdvType:
    """ analyze and map an extended project development environment, including template/root projects and git status.

    :param project_path:        optional rel/abs package/app/project root directory path of a new and existing
                                project (defaults to the current working directory if empty or not passed).
    :return:                    dict/mapping with the determined project development variable values.
    """
    abs_prj_path = os_path_abspath(project_path)
    if os_path_isdir(abs_prj_path):
        with in_wd(abs_prj_path):   # load .env file from project path folder (or above from projects folder)
            load_dotenvs()

    pdv = cast(PdvType, project_env_vars(project_path=project_path))
    project_path = pdv_str(pdv, 'project_path')     # re-read as an absolute path
    project_type = pdv_str(pdv, 'project_type')
    sep = os.linesep
    ins = sep + " " * 4

    pdv['editable_project_path'] = editable_project_path(pdv_str(pdv, 'project_name'))
    pdv['namespace_name'] = namespace_name = _get_namespace(pdv, project_type)  # pdv_str(pdv, 'namespace_name')
    pdv['prj_id'] = '_'.join(pdv_str(pdv, _) for _ in ('repo_domain', 'repo_group', 'project_name', 'project_version'))
    pdv['project_desc'] = " ".join(pdv_str(pdv, _) for _ in ('project_name', 'project_type', 'project_version'))
    pdv['repo_group'] = _get_host_group(pdv, pdv_str(pdv, 'repo_domain'))
    if not on_ci_host():
        pdv['tpl_projects'] = _template_projects(pdv)

    pdv.update({k: v for k, v in globals().items() if k.startswith('TEMPLATE_')})

    if project_type == ROOT_PRJ:
        namespace_len = len(namespace_name)
        pypi_host = pdv_str(pdv, 'PYPI_PROJECT_ROOT')

        imp_names = []
        por_vars: ChildrenType = OrderedDict()
        pypi_refs_rst = []
        pypi_refs_md = []
        for project_name_version in cast(list[str], pdv_val(pdv, 'portions_packages')):
            p_name = project_name_version.split(PROJECT_VERSION_SEP)[0]
            portion_path = os_path_join(os_path_dirname(project_path), p_name)
            portion_name = p_name[namespace_len + 1:]
            import_name = p_name[:namespace_len] + '.' + portion_name

            pypi_refs_rst.append(f'* `{p_name} <{pypi_host}/{p_name}>`_')
            pypi_refs_md.append(f'* [{p_name}]({pypi_host}/{p_name} "{namespace_name} namespace portion {p_name}")')

            por_vars[p_name] = project_dev_vars(project_path=portion_path)

            imp_names.append(import_name)
            for e_mod in find_extra_modules(portion_path, namespace_name=namespace_name, portion_name=portion_name):
                imp_names.append(import_name + '.' + e_mod)

        pdv['children_project_vars'] = por_vars

        pdv['portions_pypi_refs'] = sep.join(pypi_refs_rst)                 # templates/..._README.rst
        pdv['portions_pypi_refs_md'] = sep.join(pypi_refs_md)               # templates/..._README.md
        pdv['portions_import_names'] = ins.join(imp_names)                  # templates/docs/..._index.rst

    elif project_type == PARENT_PRJ:
        coll = Collector(item_collector=coll_folders)
        coll.collect(project_path, select="*")
        pdv['children_project_vars'] = {os_path_basename(chi_prj_path): project_dev_vars(project_path=chi_prj_path)
                                        for chi_prj_path in coll.paths}

    docs_dir = os_path_join(pdv_str(pdv, 'project_path'), pdv_str(pdv, 'DOCS_FOLDER'))
    extra_docs = path_files(os_path_join(docs_dir, "man", "**", "*.rst"))
    pdv['manuals_include'] = ""
    if extra_docs:
        pdv['manuals_include'] = f"manuals and tutorials{sep}" \
                                 f"*********************{sep}{sep}" \
                                 f".. toctree::{sep}{sep}" \
                                 f"    {ins.join(os_path_relpath(_, docs_dir) for _ in extra_docs)}"

    return pdv


def pypi_versions(pip_name: str) -> list[str]:
    """ determine all the available release versions of a package hosted at the PyPI 'Cheese Shop'.

    :param pip_name:            pip/package name to get release versions from.
    :return:                    list of released versions (the latest last) or
                                on error a list with a single empty string item.
    """
    try:
        response = requests.get(f"https://pypi.org/pypi/{pip_name}/json")   # pylint: disable=missing-timeout
        response.raise_for_status()             # raise HTTPError
        data = response.json()
        versions = list(data['releases'].keys())
        versions.sort(key=Version)
        return versions
    except (KeyError, ValueError, Exception):   # pylint: disable=broad-exception-caught
        # catching too: requests.exceptions.HTTPError/.JSONDecodeError
        return [""]         # ignore error on invalid pip_name/page-not-found/never released to PyPi


def refresh_templates(pdv: PdvType, logger: Callable = print, **replacer: Replacer) -> set[str]:
    """ convert ae namespace package templates found in the cwd or underneath (except excluded) to the final files.

    :param pdv:                 project env/dev variables dict of the destination project to patch/refresh,
                                providing values for (1) f-string template replacements, and (2) to control the template
                                registering, patching, and deployment via the variables:

                                * `namespace_name`: namespace of the destination project.
                                * `package_path`: path to package data root of the destination project.
                                * `project_path`: path to working tree root of the destination project.
                                * 'project_name': pypi name of the package/portion/app/... project.
                                * `project_type`: type of the destination project.
                                * `repo_url`: remote/upstream repository url of the destination project.
                                * `tpl_projects`: template projects data (import name, project path and version).

                                .. hint:: use the function :func:`project_dev_vars` to create this dict.

    :param logger:              print()-like callable for logging.

    :param replacer:            dict of optional replacer with key=placeholder-id and value=callable.
                                if not passed, then only the replacer with id TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID and
                                its callable/func :func:`replace_with_file_content_or_default` will be executed.

    :return:                    set of patched destination file names.
    """
    pdv['pypi_versions'] = pypi_versions(pdv_str(pdv, 'pip_name'))
    is_portion = pdv_str(pdv, 'namespace_name') and pdv_str(pdv, 'project_type') != ROOT_PRJ

    joi, isf, bna, dna, rpa = os_path_join, os_path_isfile, os_path_basename, os_path_dirname, os_path_relpath
    glb = path_items
    dst_files: set[str] = set()
    for tpl_prj in cast(list[RegisteredTemplateProject], pdv_val(pdv, 'tpl_projects')):
        tpl_path = tpl_prj['tpl_path']
        patcher = f"{tpl_prj['import_name']} V{tpl_prj['version']}"
        for tpl_file_path in [file for file in glb(joi(tpl_path, "**/.*")) + glb(joi(tpl_path, "**/*")) if isf(file)]:
            dst_path = rpa(dna(tpl_file_path), tpl_path)
            if ((no_por_p := dst_path.startswith(SKIP_IF_PORTION_DST_NAME_PREFIX))
                    or bna(tpl_file_path).startswith(SKIP_IF_PORTION_DST_NAME_PREFIX)) and is_portion:
                continue
            if no_por_p:
                dst_path = dst_path[len(SKIP_IF_PORTION_DST_NAME_PREFIX):]
            if dst_path.startswith(MOVE_TPL_TO_PKG_PATH_NAME_PREFIX):
                dst_path = joi(pdv_str(pdv, 'package_path'), dst_path[len(MOVE_TPL_TO_PKG_PATH_NAME_PREFIX):])

            deploy_template(tpl_file_path, dst_path, patcher, pdv,
                            logger=logger, replacer=replacer, dst_files=dst_files)

    return dst_files


def replace_file_version(file_name: str, increment_part: int = 0, new_version: str = "") -> str:
    """ replace version number of a module/script file.

    :param file_name:           module/script file name to be patched/version-bumped.
    :param increment_part:      version number part to increment: 1=mayor, 2=minor, 3=build/revision, default 0=nothing.
    :param new_version:         if passed, replace the original version in the file.
    :return:                    empty string on success, else error string.
    """
    msg = f"replace_file_version({file_name}) expects "
    if not os_path_isfile(file_name):
        return msg + f"existing code file path reachable from current working directory {os.getcwd()}"

    content = read_file(file_name)
    if not content:
        return msg + f"non-empty code file in {os_path_abspath(file_name)}"

    if new_version:
        _replacement = VERSION_PREFIX + increment_version(new_version, increment_part=increment_part) + VERSION_QUOTE
    else:
        def _replacement(_m):
            return VERSION_PREFIX + increment_version((_m.group(p) for p in range(1, 4)),
                                                      increment_part=increment_part) + VERSION_QUOTE
    content, replaced = VERSION_MATCHER.subn(_replacement, content)

    if replaced != 1:
        return msg + f"single occurrence of module variable {VERSION_PREFIX}{VERSION_QUOTE}, but found {replaced} times"

    _RCS[_rc_id(ae.base, 'write_file')](file_name, content)

    return ""


def replace_with_file_content_or_default(args_str: str) -> str:
    """ return file content if the file specified in first string arg exists, else return empty string or 2nd arg str.

    :param args_str:            pass either file name, or file name and default literal separated by a comma character.
                                spaces, tabs, and newline characters get removed from the start/end of the file name.
                                a default literal gets parsed like a config variable, the literal value gets return.
    :return:                    file content or default literal value or empty string (if the file does not exist and
                                there is no comma char in :paramref:`~replace_with_file_content_or_default.args_str`).
    """
    file_name, *default = args_str.split(",", maxsplit=1)
    if file_name:
        file_name = file_name.split()[0]    # strip spaces, tabs, and newlines
    return read_file(file_name) if os_path_isfile(file_name) else Literal(default[0]).value if default else ""


def root_packages_masks(pdv: PdvType) -> list[str]:
    """ determine root sub packages from the passed project packages and add them glob path wildcards.

    :param pdv:                 project environment variables dict.
    :return:                    list of project root packages extended with glob path wildcards.
    """
    project_packages = pdv_val(pdv, 'project_packages')
    root_packages = []
    root_paths = []
    for app_import_name in sorted(project_packages):
        pkg_name_parts = app_import_name.split('.')
        if pkg_name_parts[0] not in root_packages:
            root_packages.append(pkg_name_parts[0])
            root_paths.append(os_path_join(pkg_name_parts[0], '**', '*'))
    return root_paths


def skip_files_migrations(file_path: str) -> bool:
    """ file exclusion callback for the files under the django migrations folders.

    :param file_path:       path to file to check for exclusion, relative to the project root folder.
    :return:                boolean True, if the file specified in :paramref:`~skip_files_migrations.file_path`
                            has to be excluded, else False.
    """
    return 'migrations' in file_path.split('/')


def skip_files_lean_web(file_path: str) -> bool:
    """ file exclusion callback to reduce the deployed files on the web server to the minimum.

    :param file_path:       path to file to check for exclusion, relative to the project root folder.
    :return:                boolean True, if the file specified in :paramref:`~skip_files_lean_web.file_path`
                            has to be excluded, else False.
    """
    return (skip_py_cache_files(file_path)
            or skip_files_migrations(file_path)
            or '/static/' in file_path
            or os_path_splitext(file_path)[1] == '.po'
            )


def venv_bin_path(name: str = "") -> str:
    """ determine the absolute bin/executables folder path of a virtual pyenv environment.

    :param name:                the name of the venv. if not specified, then the venv name will be determined from the
                                first found ``.python-version`` file, starting in the current working directory (cwd)
                                and up to 3 parent directories above.
    :return:                    absolute bin folder path of the projects local pyenv virtual environment
    """
    venv_root = os.getenv('PYENV_ROOT')
    if not venv_root:   # pyenv is not installed
        return ""

    if not name:
        loc_env_file = '.python-version'
        for _ in range(3):
            if os_path_isfile(loc_env_file):
                name = read_file(loc_env_file).split(os.linesep)[0]
                break
            loc_env_file = ".." + os_path_sep + loc_env_file
        else:
            return ""

    return os_path_join(venv_root, 'versions', name, 'bin')

# --------------- module helpers --------------------------------------------------------------------------------------


def _act_callable(ini_pdv: PdvType, act_name: str) -> Optional[Callable]:
    return globals().get(act_name) or getattr(pdv_val(ini_pdv, 'host_api'), act_name, None)


def _act_spec(pdv: PdvType, act_name: str) -> tuple[dict[str, Any], str]:   # ActionSpecification
    for reg_name, reg_spec in REGISTERED_ACTIONS.items():
        if reg_name == act_name:
            return reg_spec, 'repo'
        if reg_name.endswith(f'.{act_name}'):
            for name_prefix in ('repo', 'web'):
                host_domain = _get_host_domain(pdv, name_prefix=name_prefix)
                cls_name = _get_host_class_name(host_domain)
                if name_prefix == getattr(globals().get(cls_name, None), 'name_prefix', ""):
                    key_name = f"{cls_name}.{act_name}"
                    if key_name == reg_name:
                        return reg_spec, name_prefix

    return {'local_action': True}, 'repo'  # action isn't found; return pseudo action spec to display an error later


def _available_actions(project_type: Union[UnsetType, str] = UNSET) -> set[str]:
    return set(name.split(".")[-1] for name, data in REGISTERED_ACTIONS.items()
               if project_type is UNSET or project_type in data['project_types'])


def _check_commit_msg_file(pdv: PdvType) -> str:
    commit_msg_file = os_path_join(pdv_str(pdv, 'project_path'), COMMIT_MSG_FILE_NAME)
    if not os_path_isfile(commit_msg_file) or not read_file(commit_msg_file):
        _exit_error(81, f"missing commit message in {commit_msg_file}{_hint(prepare_commit)}")
    return commit_msg_file


def _check_folders_files_completeness(pdv: PdvType):
    changes: list[tuple] = []

    with _record_calls(ae.base, 'write_file', lambda _dst_fn, *_, **__: changes.append(('wf', _dst_fn, _, __)),
                       os, 'makedirs', lambda _dir: changes.append(('md', _dir))):
        _renew_prj_dir(pdv)

    if changes:
        cae.po(f"  --  missing {len(changes)} basic project folders/files:")
        if cae.verbose:
            cae.po(PPF(changes))
            cae.po(f"   -- use the 'new_{pdv_str(pdv, 'project_type')}' action to re-new/complete/update this project")
        else:
            project_path = pdv_str(pdv, 'project_path')
            for change in changes:
                cae.po(f"    - {change[0] == 'md' and 'folder' or 'file  '} {os_path_relpath(change[1], project_path)}")
    elif _debug_or_verbose():
        cae.po("    = project folders and files are complete and up-to-date")


def _check_children_not_exist(parent_or_root_pdv: PdvType, *project_versions: str):
    for pkg_and_ver in project_versions:
        parent_path, pkg_and_ver = _get_parent_packageversion(parent_or_root_pdv, pkg_and_ver)
        project_path = os_path_join(parent_path, pkg_and_ver.split(PROJECT_VERSION_SEP)[0])
        _chk_if(12, not os_path_isdir(project_path), f"project path {project_path} does already exist")


def _check_resources_img(pdv: PdvType) -> list[str]:
    """ check images, message texts and sounds of the specified project. """
    local_images = FilesRegister(os_path_join(pdv_str(pdv, 'project_path'), "img", "**"))
    for name, files in local_images.items():
        dup_files = duplicates(norm_path(str(file)) for file in files)
        _chk_if(69, not dup_files, f"duplicate image file paths for '{name}': {dup_files}")

    file_names: list[str] = []
    for name, files in local_images.items():
        file_names.extend(norm_path(str(file)) for file in files)
    dup_files = duplicates(file_names)
    _chk_if(69, not dup_files, f"image resources file paths duplicates: {dup_files}")

    for name, files in local_images.items():
        for file_name in (norm_path(str(file)) for file in files):
            _chk_if(69, bool(read_file(file_name, extra_mode='b')), f"empty image resource in {file_name}")
            # noinspection PyBroadException
            try:
                img = Image.open(file_name)
                img.verify()
            except Exception as ex:                                 # pylint: disable=broad-exception-caught
                _chk_if(69, False, f"Pillow/PIL detected corrupt image {file_name=} {ex=}")

    if _debug_or_verbose():
        cae.po(f"    = passed checks of {len(local_images)} image resources ({len(file_names)} files: {file_names})")

    return list(local_images.values())


def _check_resources_i18n_ae(file_name: str, content: str):
    """ check a translation text file with ae_i18n portion message texts.

    :param file_name:           message texts file name.
    :param content:             message texts file content.
    """
    eval_texts = try_eval(content, ignored_exceptions=(Exception, ))
    texts = ast.literal_eval(content)
    _chk_if(69, eval_texts == texts, f"eval and literal_eval results differ in {file_name}")
    _chk_if(69, isinstance(texts, dict), f"no dict literal in {file_name}, got {type(texts)}")
    for key, text in texts.items():
        _chk_if(69, isinstance(key, str), f"file content dict keys must be strings, but got {type(key)}")
        _chk_if(69, isinstance(text, (str, dict)), f"dict values must be str|dict, got {type(text)}")
        if isinstance(text, dict):
            for sub_key, sub_txt in text.items():
                _chk_if(69, isinstance(sub_key, str), f"sub-dict-keys must be strings, got {type(sub_key)}")
                typ = float if sub_key in ('app_flow_delay', 'fade_out_app', 'next_page_delay',
                                           'page_update_delay', 'tour_start_delay', 'tour_exit_delay') else str
                _chk_if(69, isinstance(sub_txt, typ), f"sub-dict-values of {sub_key} must be {typ}")


def _check_resources_i18n_po(file_name: str, content: str):
    """ check a translation text file with GNU gettext message texts.

    :param file_name:           message texts file name (.po file).
    :param content:             message texts file content.
    """
    native = '/en/' in file_name
    mo_file_name = os_path_splitext(file_name)[0] + '.mo'
    _chk_if(69, os_path_isfile(mo_file_name), f"missing compiled message file {mo_file_name}")
    if not on_ci_host():    # skip this check on CI host because the unpacked/installed mo/po file dates are not correct
        po_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_name))
        mo_date = datetime.datetime.fromtimestamp(os.path.getmtime(mo_file_name))
        _chk_if(69, native or po_date <= mo_date, f"{file_name} ({po_date}) not compiled into .mo ({mo_date})")

    id_marker = "msgid"
    str_marker = "msgstr"
    in_txt = msg_id = msg_str = ""
    in_header = True
    for lno, text in enumerate(content.split(os.linesep), start=1):
        in_id = in_txt.startswith(id_marker)
        if text.startswith(id_marker):
            _chk_if(69, not in_txt, f"new {id_marker} in uncompleted {in_txt} in {file_name}:{lno}")
            _chk_if(69, not msg_id, f"duplicate {id_marker} in {file_name}:{lno}")
            _chk_if(69, text[len(id_marker) + 1] == text[-1] == '"', f"missing \" in {text} in {file_name}:{lno}")
            msg_id = text[len(id_marker) + 2:-1]
            _chk_if(69, in_header or msg_id != "", f"missing header or empty {id_marker} text in {file_name}:{lno}")
            in_txt = text
        elif text.startswith(str_marker):
            _chk_if(69, text[len(str_marker) + 1] == text[-1] == '"', f"missing \" in {text} in {file_name}:{lno}")
            _chk_if(69, in_header or bool(msg_id and in_id), f"{str_marker} w/o {id_marker} in {file_name}:{lno}")
            msg_str = text[len(str_marker) + 2:-1]
            in_txt = text
        elif in_txt:
            if text:
                _chk_if(69, text[0] == text[-1] == '"', f"misplaced \" in multiline text {in_txt} in {file_name}:{lno}")
                if in_id:
                    msg_id += text[1:-1]
                else:       # in_txt.startswith(str_marker)
                    msg_str += text[1:-1]
                in_txt += ".."
            else:
                _chk_if(69, in_header or msg_id != "", f"empty id text in {file_name}:{lno}")
                if _debug_or_verbose() and not native and not msg_str:
                    cae.po(f"    # ignoring empty translation of \"{msg_id}\" in {file_name}:{lno}")
                in_txt = msg_id = msg_str = ""
                in_header = False
        else:
            _chk_if(69, not text or text[0] == "#", f"expected comment/empty-line, got {text} in {file_name}:{lno}")


def _check_resources_i18n_texts(pdv: PdvType) -> list[str]:
    def _chk_files(chk_func: Callable[[str, str], None], *path_parts: str) -> list[FileObject]:
        stem_mask = path_parts[-1]
        regs = FilesRegister(os_path_join(pdv_str(pdv, 'project_path'), *path_parts))
        file_names: list[str] = []
        for stem_name, files in regs.items():
            for file_name in (norm_path(str(file)) for file in files):
                content = read_file(file_name)
                _chk_if(69, bool(content), f"stem {stem_name} has empty translation message file {file_name}")
                chk_func(file_name, content)
                file_names.append(file_name)

        dup_files = duplicates(file_names)
        _chk_if(69, not dup_files, f"file paths duplicates of {stem_mask} translations: {dup_files}")

        if _debug_or_verbose():
            cae.po(f"    = passed checks of {len(regs)} {stem_mask} (with {len(file_names)} files: {file_names})")

        return list(regs.values())

    return (_chk_files(_check_resources_i18n_ae, "loc", "**", "**Msg.txt") +
            _chk_files(_check_resources_i18n_po, "**", "locale", "**", "django.po"))


def _check_resources_snd(pdv: PdvType) -> list[str]:
    local_sounds = FilesRegister(os_path_join(pdv_str(pdv, 'project_path'), "snd", "**"))

    for name, files in local_sounds.items():
        dup_files = duplicates(norm_path(str(file)) for file in files)
        _chk_if(69, not dup_files, f"duplicate sound file paths for '{name}': {dup_files}")

    file_names: list[str] = []
    for name, files in local_sounds.items():
        file_names.extend(norm_path(str(file)) for file in files)
    dup_files = duplicates(file_names)
    _chk_if(69, not dup_files, f"sound resources file paths duplicates: {dup_files}")

    for name, files in local_sounds.items():
        for file_name in (norm_path(str(file)) for file in files):
            _chk_if(69, bool(read_file(file_name, extra_mode='b')), f"empty sound resource in {file_name}")

    if _debug_or_verbose():
        cae.po(f"    = passed checks of {len(local_sounds)} sound resources ({len(file_names)} files: {file_names})")

    return list(local_sounds.values())


def _check_resources(pdv: PdvType):
    """ check images, message texts and sounds of the specified project. """
    resources = _check_resources_img(pdv) + _check_resources_i18n_texts(pdv) + _check_resources_snd(pdv)
    if resources:
        cae.po(f"  === {len(resources)} image/message-text/sound resources checks passed")
        if _debug_or_verbose():
            cae.po(_pp(str(_) for _ in resources)[1:])


def _check_templates(pdv: PdvType):
    verbose = _debug_or_verbose()
    project_path = pdv_str(pdv, 'project_path')
    rel_path = os_path_relpath

    missing: list[tuple] = []
    outdated: list[tuple] = []

    def _block_and_log_file_writes(dst_fn: str, content: Union[str, bytes], extra_mode: str = ""):
        wf_args = (dst_fn, content, extra_mode)
        if os_path_isfile(dst_fn):
            old = read_file(dst_fn, extra_mode=extra_mode)
            if old != content:
                outdated.append(wf_args + (old,))
        else:
            missing.append(wf_args)

    with _in_prj_dir_venv(project_path), _record_calls(ae.base, 'write_file', _block_and_log_file_writes,
                                                       os, 'makedirs', lambda _dir: None):
        checked = refresh_templates(pdv, logger=cae.po if verbose else cae.vpo)

    tpl_projects: list[RegisteredTemplateProject] = pdv_val(pdv, 'tpl_projects')
    tpl_cnt = len(tpl_projects)
    cae.dpo(f"   -- checking {tpl_cnt} of {len(REGISTERED_TPL_PROJECTS)} registered template projects: "
            + (PPF(tpl_projects) if cae.verbose else " ".join(_['import_name'] for _ in tpl_projects)))

    if missing or outdated:
        if missing:
            cae.po(f"   -- {len(missing)} outsourced files missing: "
                   + (PPF(missing) if cae.debug else " ".join(rel_path(fn, project_path) for fn, *_ in missing)))
        if outdated:
            cae.po(f"   -- {len(outdated)} outsourced files outdated: "
                   + (PPF(outdated) if cae.debug else " ".join(rel_path(fn, project_path) for fn, *_ in outdated)))
        for file_name, new_content, binary, old_content in outdated:
            cae.po(f"   -  {rel_path(file_name, project_path)}  ---")
            if verbose:
                if binary:
                    diff = cast(Iterator[str], [str(lin) for lin in diff_bytes(unified_diff, old_content, new_content)])
                elif cae.verbose:
                    diff = ndiff(old_content.splitlines(keepends=True), new_content.splitlines(keepends=True))
                else:
                    diff = context_diff(old_content.splitlines(keepends=True), new_content.splitlines(keepends=True))
            else:
                old_lines, new_lines = old_content.splitlines(keepends=True), new_content.splitlines(keepends=True)
                if cae.debug:
                    diff = unified_diff(old_lines, new_lines, n=cae.debug_level)
                else:
                    diff = cast(Iterator[str], [line for line in ndiff(old_lines, new_lines) if line[0:1].strip()])
            cae.po("      " + "      ".join(diff), end="")

        cae.po()
        _chk_if(40, False, "integrity check failed. update outsourced files via the actions 'refresh' or 'renew'")

    elif checked:
        cae.po(f"  === {len(checked)} outsourced files from {tpl_cnt} template projects are up-to-date"
               + (": " + (_pp(checked) if cae.verbose else " ".join(rel_path(_, project_path) for _ in checked))
                  if verbose else ""))

    elif verbose:
        cae.po(f"   == no outsourced files found from {tpl_cnt} associated template projects")


def _check_types_linting_tests(pdv: PdvType):
    mll = 120   # maximal length of code lines
    namespace_name = pdv_str(pdv, 'namespace_name')
    project_name = pdv_str(pdv, 'project_name')
    project_path = pdv_str(pdv, 'project_path')
    project_type = pdv_str(pdv, 'project_type')
    project_packages = pdv_val(pdv, 'project_packages')
    root_packages = [_ for _ in project_packages if '.' not in _]

    excludes = ['migrations' if project_type == DJANGO_PRJ else 'templates']    # folder names to exclude from checks
    args = namespace_name and [namespace_name] or root_packages or [pdv_str(pdv, 'version_file')]

    options = []
    if _debug_or_verbose():
        options.append("-v")
        if cae.verbose:
            options.append("-v")
        cae.po(f"    - project packages: {_pp(project_packages)}")
        cae.po(f"    - project root packages: {_pp(root_packages)}")
        cae.po(f"    - command line options: {_pp(options)}")
        cae.po(f"    - command line arguments: {_pp(args)}")

    with _in_prj_dir_venv(project_path):
        extra_args = [f"--max-line-length={mll}"] + ["--exclude=" + _ for _ in excludes] + options + args
        _cl(60, "flake8", extra_args=extra_args)

        os.makedirs("mypy_report", exist_ok=True)                               # _cl(61, "mkdir -p ./mypy_report")
        extra_args = ["--exclude=" + _ for _ in excludes] + [
            "--lineprecision-report=mypy_report", "--pretty", "--show-absolute-path", "--show-error-codes",
            "--show-error-context", "--show-column-numbers", "--warn-redundant-casts", "--warn-unused-ignores"
        ] + (["--namespace-packages", "--explicit-package-bases"] if namespace_name else []) + options + args
        # refactor/extend to the --strict option/level, equivalent to the following:  ( [*] == already used )
        # check-untyped-defs, disallow-any-generics, disallow-incomplete-defs, disallow-subclassing-any,
        # disallow-untyped-calls, disallow-untyped-decorators, disallow-untyped-defs, no-implicit-optional,
        # no-implicit-reexport, strict-equality, warn-redundant-casts [*], warn-return-any, warn-unused-configs,
        # warn-unused-ignores [*], """
        _cl(61, "mypy", extra_args=extra_args)
        _cl(61, "anybadge", extra_args=("--label=MyPy", "--value=passed", "--file=mypy_report/mypy.svg", "-o"))

        os.makedirs(".pylint", exist_ok=True)
        out: list[str] = []
        # disabling false-positive pylint errors E0401(unable to import) and E0611(no name in module) caused by name
        # clash for packages kivy and ae.kivy (see https://github.com/PyCQA/pylint/issues/5226 of user hmc-cs-mdrissi).
        extra_args = [f"--max-line-length={mll}", "--output-format=text", "--recursive=y", "--disable=E0401,E0611"] \
            + ["--ignore=" + _ for _ in excludes] + options + args
        # alternatively to exit_on_err=False: using pylint option --exit-zero
        _cl(62, 'pylint', extra_args=extra_args, exit_on_err=False, lines_output=out)
        if cae.get_option('verbose') and not cae.debug:
            cae.po(_pp(out))
        matcher = re.search(r"Your code has been rated at ([-\d.]*)", os.linesep.join(out))
        _chk_if(62, bool(matcher), f"pylint score search failed in string {os.linesep.join(out)}")
        write_file(os_path_join(".pylint", "pylint.log"), os.linesep.join(out))
        score = matcher.group(1) if matcher else "<undetermined>"
        _cl(62, "anybadge", extra_args=("-o", "--label=Pylint", "--file=.pylint/pylint.svg", f"--value={score}",
            "2=red", "4=orange", "8=yellow", "10=green"))
        cae.po(f"  === pylint score: {score}")

        sub_dir = ".pytest_cache"
        cov_db = ".coverage"
        extra_args = [f"--ignore-glob=**/{_}/*" for _ in excludes] \
            + [f"--cov={_}" for _ in namespace_name and [namespace_name] or root_packages or ["."]] \
            + ["--cov-report=html"] + options + [pdv_str(pdv, 'TESTS_FOLDER') + "/"]
        if not namespace_name or project_type != PACKAGE_PRJ:
            # --doctest-glob="...*.py" does not work for .py files (only collectable via --doctest-modules).
            # doctest fails on namespace packages even with --doctest-ignore-import-errors (modules are ok).
            # actually, pytest doesn't raise an error on namespace-package, but without collecting doctests and only if
            # --doctest-ignore-import-errors get specified and if args (==namespace) got specified after TESTS_FOLDER
            extra_args = ["--doctest-modules"] + extra_args + args
        _cl(63, "python -m pytest", extra_args=extra_args)
        db_ok = os_path_isfile(cov_db)
        _chk_if(63, db_ok, f"coverage db file ({cov_db}) not created for tests or doctests in {args}")
        os.makedirs(sub_dir, exist_ok=True)
        if db_ok:           # prevent FileNotFoundError exception to allow ignorable fail on forced check run
            os.rename(cov_db, os_path_join(sub_dir, cov_db))

        os.chdir(sub_dir)   # KIS: move .coverage and create coverage.txt/coverage.svg in the .pytest_cache sub-dir
        out = []            # IO fixed: .coverage/COV_CORE_DATAFILE in cwd, txt->stdout
        _cl(63, "coverage report --omit=" + ",".join("*/" + _ + "/*" for _ in excludes), lines_output=out)
        write_file("coverage.txt", os.linesep.join(out))
        _cl(63, "coverage-badge -o coverage.svg -f")
        cov_rep_file = f"{project_path}/htmlcov/{project_name}_py.html"
        if not os_path_isfile(cov_rep_file):
            cov_rep_file = f"{project_path}/htmlcov/index.html"
        cae.po(f"  === pytest coverage: {out[-1][-4:]} - check detailed report in file:///{cov_rep_file}")
        os.chdir("..")


def _check_version_tag(pdv: PdvType) -> str:
    increment_part = cae.get_option('versionIncrementPart')
    first_ver = increment_version(NULL_VERSION, increment_part=increment_part)
    pkg_ver = _git_project_version(pdv, increment_part=increment_part)
    file_ver = pdv_str(pdv, 'project_version')

    _chk_if(77, pkg_ver in (first_ver, file_ver), f"version mismatch: local={file_ver} remote={pkg_ver}")

    if Version(pkg_ver) > Version(file_ver):  # and cae.get_option('force')
        replace_file_version(pdv_str(pdv, 'version_file'), new_version=pkg_ver)
        _write_commit_message(pdv, pkg_version=pkg_ver,
                              title=f"late commit of forced push version correction {file_ver}->{pkg_ver}")
        _git_add(pdv)
        _git_commit(pdv)
        pdv['project_version'] = pkg_ver
    else:
        pkg_ver = file_ver

    tag = f"v{pkg_ver}"
    _git_tag_add(pdv, tag)

    return tag


def _children_desc(pdv: PdvType, children_pdv: Collection[PdvType] = ()) -> str:
    namespace_name = pdv_str(pdv, 'namespace_name')

    ret = f"{len(children_pdv)} " if children_pdv else ""
    ret += f"{namespace_name} portions" if pdv_str(pdv, 'project_type') == ROOT_PRJ else "children"

    if children_pdv:
        ns_len = len(namespace_name)
        if ns_len:
            ns_len += 1
        ret += ": " + ", ".join(pdv_str(chi_pdv, 'project_name')[ns_len:] for chi_pdv in children_pdv)

    return ret


def _children_project_names(ini_pdv: PdvType, names: Iterable[str], chi_vars: ChildrenType) -> list[str]:
    if pdv_str(ini_pdv, 'project_type') == ROOT_PRJ:
        assert pdv_str(ini_pdv, 'namespace_name'), "namespace is not set for ROOT_PRJ"
        pkg_prefix = pdv_str(ini_pdv, 'namespace_name') + '_'
        names = [("" if por_name.startswith(pkg_prefix) else pkg_prefix) + por_name for por_name in names]

    if chi_vars:    # return children package names in the same order as in the OrderedDict 'children_project_vars' var
        ori_names = list(names)
        names = [pdv_str(chi, 'project_name') for chi in chi_vars.values() if pdv_str(chi, 'project_name') in names]
        assert len(names) == len(ori_names)

    return list(names)


def _children_path_package_option_reset():
    if cae.get_option('project'):
        cae.set_option('project', "", save_to_config=False)
    if cae.get_option('path'):
        cae.set_option('path', "", save_to_config=False)


def _chk_if(error_code: int, check_result: bool, error_message: str):
    """ exit/quit this console app if the `check_result` argument is False and the `force` app option is False. """
    if not check_result:
        if cae.get_option('force'):
            cae.po(f"    # forced to ignore/skip error {error_code}: {error_message}")
        else:
            _exit_error(error_code,
                        error_message=error_message + os.linesep + "      (specify --force to ignore/skip this error)")


def _cg(err_code: int, command_line: str, extra_args: Sequence = (), lines_output: Optional[list[str]] = None,
        exit_on_err: bool = True) -> list[str]:
    """ execute git command with optional git trace output, returning the stdout lines cleaned from any trace messages.

    :param err_code:            error code to pass to the console as exit code if :paramref:`~_cl.exit_on_err` is True.
    :param command_line:        command line string to execute on the console/shell. could contain command line args
                                separated by whitespace characters (alternatively use :paramref:`~sh_exec.extra_args`).
    :param extra_args:          optional sequence of extra command line arguments.
    :param lines_output:        optional list to return the lines printed to stdout/stderr on execution.
                                by passing an empty list, the stdout and stderr streams/pipes will be separated,
                                resulting in having the stderr output lines at the end of the list. specify at
                                least on list item to merge-in the stderr output (into the stdout output and return).
    :param exit_on_err:         pass False to **not** exit the app on error (:paramref:`~_cl.exit_msg` has then to be
                                empty).
    :return:                    output lines of git command - cleaned from GIT_TRACE messages
    """
    if lines_output is None:
        lines_output = []

    git_debug = cae.verbose
    env_vars = {}
    if verbose := git_debug or cae.get_option('verbose'):
        env_vars['GIT_CURL_VERBOSE'] = "1"
        env_vars['GIT_MERGE_VERBOSITY'] = "5"
    git_trace_vars = ('GIT_TRACE', 'GIT_TRACE_PACK_ACCESS', 'GIT_TRACE_PACKET', 'GIT_TRACE_SETUP')
    if git_debug:
        for var in git_trace_vars:
            env_vars[var] = "1"

    cl_err = _cl(err_code, command_line, extra_args=extra_args, lines_output=lines_output, exit_on_err=exit_on_err,
                 env_vars={**os.environ.copy(), **env_vars} if env_vars else None)
    if cl_err:      # if cl_err and exit_on_err then _cl() would have exit grm (so never would run to here)
        cae.vpo(f"    * ignored error {cl_err} of {command_line=} with {extra_args=} and git trace {env_vars=}")
        lines_output.insert(0, _CG_ERR_PREFIX + str(cl_err))

    if STDERR_BEG_MARKER in lines_output and (  # output marker only if stderr not got merged/called w/ lines_output==[]
            git_debug or any(os.environ.get(_, "0") in ("true", "1", "2") for _ in git_trace_vars)):
        start = lines_output.index(STDERR_BEG_MARKER)
        if verbose and not ((cl_err and exit_on_err) or cae.debug):     # if not already printed by _cl()
            sep = " " * 6
            cae.po(sep + "git trace output:")
            for line_no in range(start + 1, len(lines_output) - 1):
                cae.po(sep + lines_output[line_no])
        lines_output[:] = lines_output[:start]      # del output[start:]

    return lines_output


def _cl(err_code: int, command_line: str, extra_args: Sequence = (), lines_output: Optional[list[str]] = None,
        exit_on_err: bool = True, exit_msg: str = "", shell: bool = False, env_vars: Optional[dict[str, str]] = None
        ) -> int:
    """ execute command in the current working directory of the OS console/shell, dump error, and exit app if needed.

    :param err_code:            error code to pass to the console as exit code if :paramref:`~_cl.exit_on_err` is True.
    :param command_line:        command line string to execute on the console/shell. could contain command line args
                                separated by whitespace characters (alternatively use :paramref:`~sh_exec.extra_args`).
    :param extra_args:          optional sequence of extra command line arguments.
    :param lines_output:        optional list to return the lines printed to stdout/stderr on execution.
                                by passing an empty list, the stdout and stderr streams/pipes will be separated,
                                resulting in having the stderr output lines at the end of the list. specify at
                                least on list item to merge-in the stderr output (into the stdout output and return).
    :param exit_on_err:         pass False to **not** exit the app on error (:paramref:`~_cl.exit_msg` has then to be
                                empty).
    :param exit_msg:            additional text to print on stdout/console if the app debug level is greater or equal
                                to 1 or if an error occurred and :paramref:`~_cl.exit_on_err` is True.
    :param shell:               pass True to execute command in the default OS shell (see :meth:`subprocess.run`).
    :param env_vars:            OS shell environment variables to be used instead of the console/bash defaults.
    :return:                    0 on success or the error number if an error occurred.
    """
    assert exit_on_err or not exit_msg, "specified exit message will never be shown because exit_on_err is False"
    if lines_output is None:
        lines_output = []

    sh_err = sh_exec(command_line, extra_args=extra_args,
                     lines_output=lines_output, cae=cae, shell=shell, env_vars=env_vars)

    if (sh_err and exit_on_err) or cae.debug:
        for line in lines_output:
            if cae.verbose or not line.startswith("LOG:  "):    # hiding mypy's end/useless (stderr) log entries
                cae.po(" " * 6 + line)
        msg = f"command: {command_line} " + " ".join('"' + arg + '"' if " " in arg else arg for arg in extra_args)
        if not sh_err:
            cae.dpo(f"    = successfully executed {msg}")
        else:
            if exit_msg:
                cae.po(f"      {exit_msg}")
            _chk_if(err_code, not exit_on_err, f"_cl error {sh_err} in {msg}")        # app exit

    return sh_err


def _clone_template_project(import_name: str, version: str) -> str:
    namespace_name, portion_name = import_name.split('.')

    # partial clone tpl-prj into tmp dir, --depth 1 extra-arg is redundant if branch_or_tag/--single-branch is specified
    path = _git_clone(f"https://gitlab.com/{namespace_name}-group", norm_name(import_name), branch_or_tag=f"v{version}",
                      extra_args=("--filter=blob:none", "--sparse"))
    if path:
        with _in_prj_dir_venv(path):
            tpl_dir = '/'.join((namespace_name, portion_name, TEMPLATES_FOLDER))  # *nix-path-separator also on MsWin
            if _cl(40, "git sparse-checkout", extra_args=("add", tpl_dir), exit_on_err=False):
                path = ""
            else:
                path = os_path_join(path, namespace_name, portion_name, TEMPLATES_FOLDER)

    return path


def _debug_or_verbose() -> bool:
    """ determine if a verbose or debug option got specified (preventing an app init early cae.get_option() call). """
    # noinspection PyProtectedMember
    return cae.debug or not cae._parsed_arguments or cae.get_option('verbose')  # pylint: disable=protected-access


def _exit_error(error_code: int, error_message: str = ""):
    """ quit this shell script, optionally displaying an error message. """
    if error_code <= 9:
        cae.show_help()
    if error_message:
        cae.po("***** " + error_message)
    global TEMP_CONTEXT                                 # pylint: disable=global-statement
    if TEMP_CONTEXT is not None and not cae.debug:
        TEMP_CONTEXT.cleanup()
        TEMP_CONTEXT = None
    cae.shutdown(error_code)


def _expected_args(act_spec: ActionSpec) -> str:
    arg_names: ActionArgNames = act_spec.get('arg_names', ())
    msg = " -or- ".join(" ".join(_) for _ in arg_names)

    arg_flags = act_spec.get('flags', {})
    if arg_flags:
        if msg:
            msg += ", followed by "
        msg += "optional flags; default: " + " ".join(_n + '=' + repr(_v) for _n, _v in arg_flags.items())

    return msg


def _get_branch(pdv: PdvType) -> str:
    return cae.get_option('branch') or _git_current_branch(pdv)


def _get_host_class_name(host_domain: str) -> str:
    if host_domain in REGISTERED_HOSTS_CLASS_NAMES:
        return REGISTERED_HOSTS_CLASS_NAMES[host_domain]

    host_domain = '.'.join(host_domain.split('.')[-2:])  # to associate eu.pythonanywhere.com with PythonanywhereCom
    if host_domain in REGISTERED_HOSTS_CLASS_NAMES:
        return REGISTERED_HOSTS_CLASS_NAMES[host_domain]

    return ""


def _get_host_config_val(host_domain: str, option_name: str, host_user: str = "", name_prefix: str = "repo"
                         ) -> Optional[str]:
    """ determine host domain, group, user and credential values.

    :param host_domain:         domain name of the host. pass empty string to skip search for host-specific variable.
    :param option_name:         host option name and config variable name part ('domain', 'group', 'user', 'token'),
                                resulting in e.g., user, repo_user, repo_user_at_xxx, web_user, web_user_at...
    :param host_user:           username at the host. if not passed or :paramref:`~_get_host_config_val.host_domain` is
                                 empty, then skip the search for a user-specific variable value.
    :param name_prefix:         config variable name prefix. pass 'web' to get web server host config values.
    :return:                    config variable value or None if not found.
    """
    val = cae.get_option(option_name)
    if val is None:
        var_name = f'{name_prefix}_{option_name}'
        if host_domain:
            if host_user:
                val = cae.get_variable(f'{var_name}_at_{norm_name(host_domain)}_{norm_name(host_user)}')
            if val is None:
                val = cae.get_variable(f'{var_name}_at_{norm_name(host_domain)}')
        if val is None:
            val = cae.get_variable(var_name)
    return val


def _get_host_domain(pdv: PdvType, name_prefix: str = 'repo') -> str:
    """ determine domain name of repository|web host from --domain option, repo_domain or web_domain config variable.

    :param name_prefix:         config variable name prefix. pass 'web' to get web server host config values.
    :return:                    domain name of repository|web host.
    """
    host_domain = _get_host_config_val("", 'domain', name_prefix=name_prefix)
    if host_domain is None:
        host_domain = pdv_str(pdv, f'{name_prefix}_domain') or pdv_str(pdv, 'REPO_CODE_DOMAIN')     # repo_|web_domain

    if not _get_host_class_name(host_domain):
        _exit_error(9, f"unknown --domain {host_domain}, pass {' or [xx.]'.join(REGISTERED_HOSTS_CLASS_NAMES)}")

    return host_domain


def _get_host_group(pdv: PdvType, host_domain: str) -> str:
    """ determine the user group name from the `group` option or repo_group config variable.

    :param host_domain:         domain to get user token for.
    :return:                    user group name or, if not found, then the default username STK_AUTHOR.
    """
    user_group = _get_host_config_val(host_domain, 'group')
    if user_group is None:
        user_group = pdv_str(pdv, 'repo_group') or pdv_str(pdv, 'STK_AUTHOR')
    return user_group


def _get_host_user_name(pdv: PdvType, host_domain: str, name_prefix: str = 'repo') -> str:
    """ determine username from --user option, repo_user or web_user config variable.

    :param host_domain:         domain to get user token for.
    :param name_prefix:         config variable name prefix. pass 'web' to get web server host config values.
    :return:                    username or if not found the user group name.
    """
    user_name = _get_host_config_val(host_domain, 'user', name_prefix=name_prefix)
    if user_name is None:
        user_name = pdv_str(pdv, f'{name_prefix}_user')     # if specified in the pev.defaults config file
        if not user_name:
            user_name = _get_host_group(pdv, host_domain)
    return user_name


def _get_host_user_token(host_domain: str, host_user: str = "", name_prefix: str = 'repo') -> str:
    """ determine token or password of user from --token option, repo_token or web_token config variable.

    :param host_domain:         domain to get user token for.
    :param host_user:           host user to get token for.
    :param name_prefix:         config variable name prefix. pass 'web' to get web server host config values.
    :return:                    token string for domain and user on repository|web host.
    """
    return _get_host_config_val(host_domain, 'token', host_user=host_user, name_prefix=name_prefix) or ""


def _get_namespace(pdv: PdvType, project_type: str) -> str:
    namespace_name = cae.get_option('namespace') or pdv_str(pdv, 'namespace_name')
    if project_type == ROOT_PRJ and not namespace_name:
        _exit_error(9, "namespace root project expects the --namespace command line option")
    return namespace_name


def _get_parent_path(pdv) -> str:
    parent_path = pdv_str(pdv, 'project_path')
    if pdv_str(pdv, 'project_type') != PARENT_PRJ:
        parent_path = os_path_dirname(parent_path)
    return parent_path


def _get_parent_packageversion(pdv, package_or_portion: str) -> tuple[str, str]:
    if package_or_portion:
        pkg_and_ver = package_or_portion
        parent_path = _get_parent_path(pdv)
    else:
        parent_path, _project_path, pkg_and_ver = _get_path_package(pdv)

    return parent_path, pkg_and_ver


def _get_path_package(pdv: PdvType, project_type: str = NO_PRJ) -> tuple[str, str, str]:
    parent_folders = pdv_val(pdv, 'PARENT_FOLDERS')
    if project_type == NO_PRJ:
        project_type = pdv_str(pdv, 'project_type')

    project_path = cae.get_option('path')       # if specified then value of cae.get_option('project') will be ignored
    if project_path:
        project_path = norm_path(project_path)
        parent_path = project_path if project_type == PARENT_PRJ else os_path_dirname(project_path)
        project_name = '' if project_type == PARENT_PRJ else os_path_basename(project_path)
    else:
        project_name = _get_prj_name(pdv, project_type=project_type)
        parent_path = _get_parent_path(pdv)
        project_path = os_path_join(parent_path, project_name)

    if os_path_basename(parent_path) not in parent_folders:     # or not parent_path
        _exit_error(9, f"{os_path_basename(parent_path)} is not a registered parent folder ({parent_folders})")

    cae.dpo(f"    = initialized project path ({project_path}) and package ({project_name}) from command line args")

    return parent_path, project_path, project_name


def _get_prj_name(pdv: PdvType, project_type: str = NO_PRJ) -> str:
    project_name = cae.get_option('project') or pdv_str(pdv, 'project_name')
    if not project_name:
        _exit_error(9, "missing package name (specify via the --project or --path option)")

    project_type = project_type or pdv_str(pdv, 'project_type')
    namespace_name = _get_namespace(pdv, project_type)
    if namespace_name and not project_name.startswith(namespace_name + '_'):
        project_name = namespace_name + '_' + project_name

    project_path = pdv_str(pdv, 'project_path')
    _chk_if(9, project_name == os_path_basename(project_path),
            f"project path '{project_path}' does not end with project name '{project_name}'")

    return project_name


def _get_renamed_path_package(pdv: PdvType, namespace_name: str, project_type: str) -> tuple[str, str]:
    _parent_path, project_path, project_name = _get_path_package(pdv, project_type=project_type)
    import_name = namespace_name + '.' + project_name[len(namespace_name) + 1:] if namespace_name else project_name
    old_ns_name = pdv_str(pdv, 'namespace_name')
    old_prj_type = pdv_str(pdv, 'project_type')

    old_prj_path = project_path
    if old_prj_type != project_type and ROOT_PRJ in (old_prj_type, project_type):
        project_name = _get_prj_name(pdv) if old_prj_type == ROOT_PRJ else namespace_name + '_' + namespace_name
        project_path = os_path_join(os_path_dirname(project_path), project_name)
        _chk_if(6, not os_path_isdir(project_path), f"{project_type} root folder {project_path} exists already")

    if old_ns_name != namespace_name:
        if not old_ns_name or not namespace_name:
            _exit_error(6, f"conversion from/to namespace {old_ns_name}{namespace_name} is not implemented.")
        if not cae.get_option('path'):
            _exit_error(7, f"specify --path option to rename namespace from {old_ns_name} to {namespace_name}")

        new_ns_path = os_path_join(project_path, namespace_name)
        if not os_path_isdir(new_ns_path):
            os.makedirs(new_ns_path)

            if project_path == old_prj_path:
                _old = os_path_join(project_path, old_ns_name)
                if os_path_isdir(_old):
                    os.renames(_old, os_path_join(os_path_dirname(_old), "_old_" + os_path_basename(_old)))

    if old_prj_type in ANY_PRJ_TYPE and old_prj_type != project_type:
        if not cae.get_option('path'):
            _exit_error(7, f"specify --path option to change project type from {old_prj_type} to {project_type}")

        _old = project_main_file(import_name, project_path=old_prj_path)
        if os_path_isfile(_old):
            _new = main_file_path(project_path, project_type, namespace_name)
            write_file(_new, read_file(_old), make_dirs=True)

            if project_path == old_prj_path:
                os.renames(_old, os_path_join(os_path_dirname(_old), "_old_" + os_path_basename(_old)))

    return project_path, project_name


@_recordable_function
def _git_add(pdv: PdvType):
    args = ["-A"]
    if _debug_or_verbose():
        args.append("-v")

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        if not _git_init_if_needed(pdv):
            _cl(31, "git add", extra_args=args)


def _git_branches(pdv: PdvType) -> list[str]:
    project_path = pdv_str(pdv, 'project_path')
    if not os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        return []

    with _in_prj_dir_venv(project_path):
        all_branches = _cg(27, "git branch", extra_args=("-a", "--no-color"))
    return [branch_name[2:] for branch_name in all_branches if cae.debug or branch_name[1] == " "]


def _git_checkout(pdv: PdvType, *extra_args: str, branch: str = "", from_branch: str = ""):
    files_uncommitted = _git_uncommitted(pdv)
    is_clean = files_uncommitted == [] or branch not in _git_branches(pdv)
    _chk_if(57, is_clean, f"branch {branch} exists already and current branch {_git_current_branch(pdv)}"
                          f" has uncommitted files: {files_uncommitted}")

    args = list(extra_args)
    if branch:
        args.extend(["-B", branch])
    if from_branch:
        args.append(from_branch)

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        _cl(57, "git checkout", extra_args=args)


def _git_clone(repo_root: str, project_name: str, branch_or_tag: str = "", parent_path: str = "",
               extra_args: Sequence = ()) -> str:
    global TEMP_CONTEXT, TEMP_PARENT_FOLDER                     # pylint: disable=global-statement

    if not parent_path:
        if not TEMP_CONTEXT:
            TEMP_CONTEXT = tempfile.TemporaryDirectory()        # pylint: disable=consider-using-with
            TEMP_PARENT_FOLDER = os_path_join(TEMP_CONTEXT.name, pdv_val({}, 'PARENT_FOLDERS')[-1])
            _RCS[_rc_id(os, 'makedirs')](TEMP_PARENT_FOLDER)
        parent_path = TEMP_PARENT_FOLDER

    args = []
    if _debug_or_verbose():
        args.append("-v")
    if branch_or_tag:
        # https://stackoverflow.com/questions/791959/download-a-specific-tag-with-git says:
        # add -b <tag> to specify a release tag/branch to clone, adding --single-branch will speed up the download
        args.append("--branch")
        args.append(branch_or_tag)
        args.append("--single-branch")
    if extra_args:
        args.extend(extra_args)
    args.append(f"{repo_root}/{project_name}.git")

    with _in_prj_dir_venv(parent_path):
        output = _cg(40, "git clone", extra_args=args, exit_on_err=False)   # usr/pwd prompt if repo is private/invalid!

    if output and output[0].startswith(_CG_ERR_PREFIX):
        return ""
    return norm_path(os_path_join(parent_path, project_name))


def _git_commit(pdv: PdvType, extra_options: Iterable[str] = ()):
    """ execute the command 'git commit' for the specified project.

    :param pdv:                 providing project-name and -path in which this git command gets executed.
    :param extra_options:       additional options passed to the `git commit` command line,
                                e.g., ["--patch", "--dry-run"].

    .. note:: ensure the commit message in the file :data:`COMMIT_MSG_FILE_NAME` is uptodate.
    """
    file_name = _check_commit_msg_file(pdv)
    commit_msg = read_file(file_name).replace('{apk_ext}', '{{apk_ext}}')
    write_file(file_name, patch_string(commit_msg, pdv))
    args = [f"--file={file_name}"]
    if _debug_or_verbose():
        args.append("-v")
    args.extend(extra_options)

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        _cl(82, "git commit", extra_args=args)


def _git_current_branch(pdv: PdvType) -> str:
    project_path = pdv_str(pdv, 'project_path')
    if not os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        return ""

    with _in_prj_dir_venv(project_path):
        cur_branch = _cg(27, "git branch --show-current")
    return cur_branch[0] if cur_branch else ""


def _git_diff(pdv: PdvType, *extra_opt_and_ref_specs: str) -> list[str]:
    args = ["--no-color", "--find-copies-harder", "--find-renames", "--full-index"]
    if not _debug_or_verbose():
        args.append("--compact-summary")        # alt: --name-only
    args.extend(extra_opt_and_ref_specs)

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        output = _cg(70, "git diff", extra_args=args, exit_on_err=False)

    return output


def _git_fetch(pdv: PdvType, *extra_args: str) -> list[str]:
    if pdv_str(pdv, 'project_version') == NULL_VERSION:
        return []   # skip fetch preventing input of user/pw if origin remote is set but the project still not pushed

    project_path = pdv_str(pdv, 'project_path')
    if not os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        return [f"missing {GIT_FOLDER_NAME} folder in '{pdv_str(pdv, 'project_name')} project root dir: {project_path}"]

    args = []
    if _debug_or_verbose():
        args.append("-v")
    args.extend(extra_args or ("--all", "--prune", "--prune-tags", "--set-upstream", "--tags"))
    # if "--all" not in args and 'origin' not in args and MAIN_BRANCH not in args:
    #    args.extend(('origin', MAIN_BRANCH))

    with _in_prj_dir_venv(project_path):
        output = _cg(75, "git fetch", extra_args=args, exit_on_err=False)

    return [_ for _ in output if _[0] == "!"]


def _git_init_if_needed(pdv: PdvType) -> bool:
    project_path = pdv_str(pdv, 'project_path')

    if os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        return False

    args = ("-v", ) if _debug_or_verbose() else ()
    with _in_prj_dir_venv(project_path):
        # the next two config commands prevent error in test systems/containers
        _cl(51, "git init")
        _cl(52, "git config", extra_args=("user.email", pdv_str(pdv, 'STK_AUTHOR_EMAIL') or "CI@test.tst"))
        _cl(52, "git config", extra_args=("user.name", pdv_str(pdv, 'STK_AUTHOR') or "CiUserName"))
        _cl(55, "git checkout", extra_args=("-b", MAIN_BRANCH))
        _cl(56, "git commit", extra_args=args + ("--allow-empty", "-m", "grm repository initialization"))

    return True


def _git_merge(pdv: PdvType, from_branch: str) -> bool:
    args = [f"--file={_check_commit_msg_file(pdv)}", "--log", "--no-stat"]
    if _debug_or_verbose():
        args.append("-v")
    args.append(from_branch)

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        output = _cg(75, "git merge", extra_args=args)

    return "=======" not in "".join(output)


def _git_project_version(pdv: PdvType, increment_part: int = 3) -> str:
    """ determine the latest or the next free package git repository version of the specified project.

    :param pdv:                 project dev vars to identify the package.
    :param increment_part:      part of the version number to be incremented (1=mayor, 2=minor/namespace, 3=patch).
                                pass zero/0 to return the latest published package version.
    :return:                    the latest published repository package version as a string
                                or the first version (increment_version(NULL_VERSION, increment_part) or "0.0.1")
                                if the project never published a version tag to `remotes/origin`
                                or an empty string on error.
    """
    if _git_fetch(pdv):
        return ""

    version_tags = _git_tag_list(pdv)
    return increment_version(version_tags[-1][1:] if version_tags[-1] else NULL_VERSION, increment_part=increment_part)


def _git_push(pdv: PdvType, *branches_and_tags: str, exit_on_error: bool = True, extra_args: Iterable[str] = ()) -> int:
    """ push the portion in the current working directory to the specified branch. """
    protocol = pdv_str(pdv, 'REPO_HOST_PROTOCOL')
    domain = _get_host_domain(pdv)
    project_name = _get_prj_name(pdv)
    usr = _get_host_user_name(pdv, domain)
    group_or_user_name = usr if 'upstream' in _git_remotes(pdv) else _get_host_group(pdv, domain)
    pwd = _get_host_user_token(domain)

    args = list(extra_args)
    if cae.get_option('verbose'):
        args.append("-v")
    args.append(f"{protocol}{usr}:{pwd}@{domain}/{group_or_user_name}/{project_name}.git")
    args.extend(branches_and_tags)

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        sh_err = _cl(80, "git push", extra_args=args, exit_on_err=exit_on_error)

    return sh_err


def _git_remotes(pdv: PdvType) -> dict[str, str]:
    project_path = pdv_str(pdv, 'project_path')
    remotes = {}
    if os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        with _in_prj_dir_venv(project_path):
            remote_ids = _cg(21, "git remote")
            for remote_id in remote_ids:
                remote_url = _cg(22, "git remote", extra_args=("get-url", "--push", remote_id))
                remotes[remote_id] = remote_url[0]
    return remotes


def _git_renew_remotes(pdv: PdvType):
    git_remotes: dict[str, str] = _git_remotes(pdv)
    forked = 'upstream' in git_remotes
    domain = _get_host_domain(pdv)
    user_or_group = _get_host_user_name(pdv, domain) if forked else _get_host_group(pdv, domain)
    origin_url = f"{pdv_str(pdv, 'REPO_HOST_PROTOCOL')}{domain}/{user_or_group}/{_get_prj_name(pdv)}.git"

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        if forked:
            upstream_url = pdv_str(pdv, 'repo_url') + ".git"  # adding .git prevents 'git fetch --all' redirect warning
            if git_remotes['upstream'] != upstream_url:
                _cl(41, "git remote", extra_args=("set-url", 'upstream', upstream_url))

        if 'origin' not in git_remotes:
            _cl(42, "git remote", extra_args=("add", 'origin', origin_url))
        elif git_remotes['origin'] != origin_url:
            _cl(43, "git remote", extra_args=("set-url", 'origin', origin_url))


def _git_status(pdv: PdvType) -> list[str]:
    args = ["--find-renames",  "--untracked-files"]  # --untracked-files=normal is missing a full subdir-rel-file-path
    if cae.get_option('verbose'):
        args.append("--branch")
        args.append("-vv")
        args.append("--porcelain=2")
    else:
        args.append("-v")
        args.append("--porcelain")

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        output = _cg(75, "git status", extra_args=args)

    return output


def _git_tag_add(pdv: PdvType, tag: str):
    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        _cl(87, "git tag --annotate", extra_args=("--file", _check_commit_msg_file(pdv), tag))


def _git_tag_in_branch(pdv: PdvType, tag: str, branch: str = f'origin/{MAIN_BRANCH}') -> bool:
    """ check if tag/ref is in the specified or in the remote origin main branch.

    :param pdv:                 project vars.
    :param tag:                 any ref like a tag or another branch, to be searched within
                                :paramref:`~_git_tag_in_branch.branch`.
    :param branch:              branch to be searched in for :paramref:`~_git_tag_in_branch.tag`.
    :return:                    boolean True if the ref got found in the branch, else False.
    """
    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        extra_args = ("--all", "--contains", tag, "--format=%(refname:short)")
        output = _cg(88, "git branch", extra_args=extra_args, exit_on_err=False)
    return bool(output) and not output[0].startswith(_CG_ERR_PREFIX) and branch in output


def _git_tag_list(pdv: PdvType, tag_pattern: str = "v*") -> list[str]:
    project_path = pdv_str(pdv, 'project_path')
    output = []
    if os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        with _in_prj_dir_venv(project_path):
            output = _cg(89, "git tag", extra_args=("--list", "--sort=version:refname", tag_pattern), exit_on_err=False)
    return output or [""]


def _git_uncommitted(pdv: PdvType) -> list[str]:
    project_path = pdv_str(pdv, 'project_path')
    if not os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        return []
    with _in_prj_dir_venv(project_path):
        output = _cg(79, "git status", extra_args=("--find-renames",  "--untracked-files=normal", "--porcelain"))
    return [_[3:] for _ in output]


def _hint(act_fun: Callable, run_grm_message_suffix: str = "") -> str:
    return f"{os.linesep}      (run: grm {act_fun.__name__}{run_grm_message_suffix})" if _debug_or_verbose() else ""


@contextmanager
def _in_prj_dir_venv(project_path: str, venv_name: str = "") -> Iterator[None]:
    with in_wd(project_path), in_venv(name=venv_name):
        yield


def _init_act_args_check(ini_pdv: PdvType, act_spec: Any, act_name: str, act_args: ActionArgs, act_flags: ActionFlags):
    """ check and possibly complete the command line arguments and split optional action flags from action args.

    called after _init_act_exec_args/INI_PDV-initialization.
    """
    cae.dpo(f"   -- args check of action {act_name} ({act_spec.get('docstring', '').split(os.linesep)[0].strip('. ')})")
    cae.vpo(f"    - {act_name} action arguments and flags: {act_args}")

    optional_flags = act_spec.get('flags', {})
    for flag_name, flag_def in optional_flags.items():
        val_pos, flag_type = len(flag_name) + 1, type(flag_def)
        for act_arg in act_args[:]:
            if (bool_flag := act_arg == flag_name) or act_arg.startswith(flag_name + '='):
                flag_val = True if bool_flag else Literal(act_arg[val_pos:]).value
                _chk_if(9, isinstance(flag_val, flag_type),
                        f"command line flag {flag_name} has invalid type '{type(flag_val)}', expected '{flag_type}'")
                act_flags[flag_name] = flag_val
                act_args.remove(act_arg)
                break
        else:
            act_flags[flag_name] = flag_def

    alt_arg_names = act_spec.get('arg_names', ())
    arg_count = len(act_args)
    if alt_arg_names:
        for arg_names in alt_arg_names:
            pos_names = []
            opt_names = []
            for arg_name in arg_names:
                if arg_name.startswith("--"):
                    opt_names.append(arg_name[2:])
                else:
                    pos_names.append(arg_name)
            pos_cnt = len(pos_names)
            pos_ok = pos_cnt and pos_names[-1].endswith(ARG_MULTIPLES) and pos_cnt <= arg_count or pos_cnt == arg_count
            if pos_ok and all(cae.get_option(opt_name) for opt_name in opt_names):
                break
        else:
            _exit_error(9, f"expected arguments/flags: {_expected_args(act_spec)}")
    elif arg_count:
        _exit_error(9, f"no arguments expected, but got {act_args}")

    project_type = pdv_str(ini_pdv, 'project_type')
    cae.vpo(f"    - detected project type '{project_type}' for project in {pdv_str(ini_pdv, 'project_path')}")
    if project_type not in act_spec['project_types']:
        _exit_error(9, f"action '{act_name}' only available for: {act_spec['project_types']}")

    cae.dpo("    = passed checks of basic command line options and arguments")


def _init_act_args_shortcut(ini_pdv: PdvType, ini_act_name: str) -> str:
    project_type = pdv_str(ini_pdv, 'project_type')
    found_actions = []
    for act_name, act_spec in REGISTERED_ACTIONS.items():
        if project_type in act_spec['project_types'] and act_spec.get('shortcut') == ini_act_name:
            found_actions.append(act_name.split(".")[-1])
    count = len(found_actions)
    if not count:
        return ""

    assert count in (1, 2), f"duplicate shortcut declaration for {found_actions}; correct _action() shortcut kwargs"
    if count > 1:   # happens for a namespace-root project type, where action is available for a project and children
        found_actions = sorted(found_actions, key=len)      # 'project'/7 is shorter than 'children'/8
    return found_actions[0]


def _init_act_exec_args() -> tuple[PdvType, str, tuple, dict[str, Any]]:
    """ prepare execution of an action requested via command line arguments and options.

    * init project dev vars
    * checks if action is implemented
    * check action arguments
    * run optional pre_action.

    :return:                    tuple of project pdv, action name to execute, a tuple with additional action args
                                and a dict of optional action flag arguments.
    """
    ini_pdv = project_dev_vars(project_path=cae.get_option('path'))

    act_name = initial_action = norm_name(cae.get_argument('action'))
    act_args = cae.get_argument('arguments').copy()
    initial_args = act_args.copy()
    project_type = pdv_str(ini_pdv, 'project_type')
    actions = _available_actions(project_type=project_type)
    while act_name not in actions:
        if not act_args:
            found_act_name = _init_act_args_shortcut(ini_pdv, initial_action)
            if found_act_name:
                act_name = found_act_name
                act_args[:] = initial_args
                break
            msg = "undefined/new projects" if project_type is NO_PRJ else f"projects of type '{project_type}'"
            _exit_error(36, f"invalid action '{act_name}' for {msg}. valid actions: {actions}")
        act_name += '_' + norm_name(act_args[0])
        act_args[:] = act_args[1:]

    act_spec, var_prefix = _act_spec(ini_pdv, act_name)
    if not act_spec['local_action']:    # prepare cfg var names: repo_group, repo_token, web_token, repo_user, web_user
        ini_pdv[f'{var_prefix}_domain'] = host_domain = _get_host_domain(ini_pdv, name_prefix=var_prefix)
        ini_pdv['host_api'] = host_api = globals()[_get_host_class_name(host_domain)]()
        ini_pdv[f'{var_prefix}_group'] = _get_host_group(ini_pdv, host_domain)     # only repo hosts having user groups
        ini_pdv[f'{var_prefix}_user'] = host_user = _get_host_user_name(ini_pdv, host_domain, name_prefix=var_prefix)
        ini_pdv[f'{var_prefix}_token'] = _get_host_user_token(host_domain, host_user=host_user, name_prefix=var_prefix)
        _chk_if(38, bool(_act_callable(ini_pdv, act_name)), f"action {act_name} not implemented for {host_domain}")
        _chk_if(39, host_api.connect(ini_pdv), f"connection to {host_domain} remote host server failed")

    act_flags: ActionFlags = {}
    _init_act_args_check(ini_pdv, act_spec, act_name, act_args, act_flags)

    extra_children_args = ""
    extra_msg = ""
    if 'children_pdv' in act_spec['annotations']:           # and '_children' in act_name
        arg_count = len(act_spec['annotations']) - (2       # ini_pdv
                                                    + (1 if 'return' in act_spec['annotations'] else 0)
                                                    + (1 if 'optional_flags' in act_spec['annotations'] else 0))
        if arg_count:
            extra_children_args = " <" + " ".join(_ for _ in act_args[:arg_count]) + ">"
        act_args[arg_count:] = _init_children_pdv_args(ini_pdv, act_args[arg_count:])
        extra_msg += f" :: {_children_desc(ini_pdv, children_pdv=act_args[arg_count:])}"

    pre_action = act_spec.get('pre_action')
    if pre_action:
        cae.po(f" ---- executing pre-action {pre_action.__name__}")
        pre_action(ini_pdv, *act_args)

    cae.po(f"----- {act_name}{extra_children_args} on {pdv_str(ini_pdv, 'project_desc')}{extra_msg}")

    return ini_pdv, act_name, act_args, act_flags


def _init_children_pdv_args(ini_pdv: PdvType, act_args: ActionArgs) -> list[PdvType]:
    """ get package names of the portions specified as command line args, optionally filtered by --branch option. """
    chi_vars: ChildrenType = pdv_val(ini_pdv, 'children_project_vars')

    if act_args == [ARG_ALL]:
        pkg_names = list(chi_vars)
    else:
        chi_presets = _init_children_presets(chi_vars).copy()
        pkg_names = try_eval(" ".join(act_args), (Exception, ), glo_vars=chi_presets)
        if pkg_names is UNSET:
            pkg_names = _children_project_names(ini_pdv, act_args, OrderedDict())
            cae.vpo(f"    # action arguments {act_args} are not evaluable with vars={PPF(chi_presets)}")
        else:
            pkg_names = _children_project_names(ini_pdv, pkg_names, chi_vars)

    for preset in ('filterExpression', 'filterBranch'):
        _chk_if(23, bool(cae.get_option(preset)) == any((preset in _) for _ in act_args),   # == (preset in presets)
                f"mismatch of option '{preset}' and its usage in children-sets-expression {' '.join(act_args)}")
    _chk_if(23, bool(pkg_names) and isinstance(pkg_names, (list, set, tuple)),
            f"empty or invalid children/portion arguments: '{act_args}' resulting in: {pkg_names}")
    _chk_if(23, len(pkg_names) == len(set(pkg_names)),
            f"{len(pkg_names) - len(set(pkg_names))} duplicate children specified: {duplicates(pkg_names)}")

    return [chi_vars.get(p_name, {'project_name': p_name}) for p_name in pkg_names]


def _init_children_presets(chi_vars: ChildrenType) -> dict[str, set[str]]:
    branch = cae.get_option('filterBranch')
    expr = cae.get_option('filterExpression')

    chi_ps: dict[str, set[str]] = {}
    ps_all = chi_ps[ARG_ALL] = set()
    ps_edi = chi_ps['editable'] = set()
    ps_mod = chi_ps['modified'] = set()
    ps_dev = chi_ps['develop'] = set()
    if branch:
        chi_ps['filterBranch'] = set()
    if expr:
        chi_ps['filterExpression'] = set()

    for chi_pdv in chi_vars.values():
        project_name = pdv_str(chi_pdv, 'project_name')
        current_branch = _git_current_branch(chi_pdv)

        ps_all.add(project_name)
        if pdv_str(chi_pdv, 'editable_project_path'):
            ps_edi.add(project_name)
        if _git_uncommitted(chi_pdv):
            ps_mod.add(project_name)
        if current_branch == MAIN_BRANCH:
            ps_dev.add(project_name)
        if branch and current_branch == branch:
            chi_ps['filterBranch'].add(project_name)
        if expr:
            glo_vars = globals().copy()
            glo_vars.update(chi_pdv)
            glo_vars['chi_pdv'] = chi_pdv
            with _in_prj_dir_venv(pdv_str(chi_pdv, 'project_path')):
                result = try_eval(expr, ignored_exceptions=(Exception, ), glo_vars=glo_vars)
            if result:
                chi_ps['filterExpression'].add(project_name)
            elif result == UNSET:
                cae.vpo(f"    # filter expression {expr} not evaluable; glo_vars={PPF(glo_vars)}")

    return chi_ps


def _patch_outsourced(file_name: str, content: str, patcher: str) -> str:
    ext = os_path_splitext(file_name)[1]
    sep = os.linesep
    if ext == '.md':
        beg, end = "<!-- ", " -->"
    elif ext == '.rst':
        beg, end = f"{sep}..{sep}    ", sep
    else:
        beg, end = "# ", ""
    return f"{beg}{OUTSOURCED_MARKER} by the project {patcher}{end}{sep}{content}"


def _pp(output: Iterable[str]) -> str:
    sep = os.linesep + "      "
    return sep + sep.join(output)


def _print_pdv(pdv: PdvType):
    if not cae.get_option('verbose'):
        pdv = pdv.copy()
        pdv['setup_kwargs'] = skw = (pdv_val(pdv, 'setup_kwargs') or {}).copy()

        nsp_len = len(pdv_str(pdv, 'namespace_name')) + 1
        if pdv_str(pdv, 'project_type') in (PARENT_PRJ, ROOT_PRJ):
            pdv['children_project_vars'] = ", ".join(pdv_val(pdv, 'children_project_vars'))
        pdv['dev_require'] = ", ".join(pdv_val(pdv, 'dev_require'))
        pdv['docs_require'] = ", ".join(pdv_val(pdv, 'docs_require'))
        pdv['install_require'] = ", ".join(pdv_val(pdv, 'install_require'))
        if 'long_desc_content' in pdv:
            pdv['long_desc_content'] = skw['long_description'] = pdv_str(pdv, 'long_desc_content')[:33] + "..."
        pdv['package_data'] = ", ".join(pdv_val(pdv, 'package_data'))
        pdv['portions_packages'] = ", ".join(pkg[nsp_len:] for pkg in sorted(pdv_val(pdv, 'portions_packages')))
        pdv['project_packages'] = ", ".join(pdv_val(pdv, 'project_packages'))
        pdv['setup_require'] = ", ".join(pdv_val(pdv, 'setup_require'))
        pdv['tests_require'] = ", ".join(pdv_val(pdv, 'tests_require'))

    if not cae.verbose:
        pdv = pdv.copy()
        for name, val in list(pdv.items()):
            if not val or name in (
                    name.upper(), 'children_project_vars', 'dev_require', 'docs_require', 'import_name',
                    'install_require', 'long_desc_content', 'long_desc_type', 'namespace_name',
                    'pip_name', 'portion_name', 'portions_packages', 'portions_import_names',
                    'portions_pypi_refs', 'portions_pypi_refs_md', 'portions_project_vars',
                    'project_desc', 'project_name', 'project_packages', 'project_version', 'prj_id', 'pypi_url',
                    'repo_domain', 'repo_group', 'repo_pages', 'repo_root', 'repo_url',
                    'setup_kwargs', 'setup_require', 'tests_require', 'tpl_projects', 'version_file', 'web_domain'):
                pdv.pop(name, None)

    cae.po(f"      {PPF(pdv)}")


def _register_template(import_name: str, dev_require: list[str], add_req: bool, tpl_projects: list
                       ) -> RegisteredTemplateProject:
    project_name = norm_name(import_name)
    dev_req_pkg, dev_req_ver = project_version(project_name, dev_require)

    version = cae.get_option(_template_version_option(import_name))
    if not version:
        if dev_req_ver:
            version = dev_req_ver
        else:
            reg_pkg, version = project_version(project_name, list(REGISTERED_TPL_PROJECTS.keys()))
            if not reg_pkg:
                version = pypi_versions(project_name)[-1]

    key = import_name + PROJECT_VERSION_SEP + version
    if key not in REGISTERED_TPL_PROJECTS:
        path = _clone_template_project(import_name, version) if version else ""
        REGISTERED_TPL_PROJECTS[key] = {'import_name': import_name, 'tpl_path': path, 'version': version}
        if path and version:
            cae.vpo(f"    - {import_name} package v{version} in {path} registered as template id '{key}'")
        else:
            cae.dpo(f"    # template project {import_name} not found/registered ({version=} {path=})")

    if add_req and version:
        dev_require.append(project_name + PROJECT_VERSION_SEP + version)

    tpl_prj = REGISTERED_TPL_PROJECTS[key]
    if (add_req or dev_req_pkg) and version:
        tpl_projects.append(tpl_prj)

    return tpl_prj


def _renew_prj_dir(new_pdv: PdvType):
    namespace_name = pdv_str(new_pdv, 'namespace_name')
    project_name = pdv_str(new_pdv, 'project_name')
    project_path = pdv_str(new_pdv, 'project_path')
    project_type = pdv_str(new_pdv, 'project_type')

    is_root = project_type == ROOT_PRJ
    import_name = namespace_name + '.' + project_name[len(namespace_name) + 1:] if namespace_name else project_name

    is_file = os_path_isfile
    is_dir = os_path_isdir
    join = os_path_join
    sep = os.linesep

    if not is_dir(project_path):
        _RCS[_rc_id(os, 'makedirs')](project_path)

    file_name = join(project_path, pdv_str(new_pdv, 'REQ_FILE_NAME'))
    if not is_file(file_name):
        _RCS[_rc_id(ae.base, 'write_file')](file_name, f"# runtime dependencies of the {import_name} project")

    main_file = project_main_file(import_name, project_path=project_path)
    if not main_file:
        main_file = main_file_path(project_path, project_type, namespace_name)
        main_path = os_path_dirname(main_file)
        if not is_dir(main_path):
            _RCS[_rc_id(os, 'makedirs')](main_path)
    if not is_file(main_file):
        _RCS[_rc_id(ae.base, 'write_file')](main_file, f"\"\"\" {project_name} {project_type} main module \"\"\"{sep}"
                                                       f"{sep}"
                                                       f"{VERSION_PREFIX}{NULL_VERSION}{VERSION_QUOTE}{sep}")

    if project_type == PLAYGROUND_PRJ:
        return

    sub_dir = join(project_path, pdv_str(new_pdv, 'DOCS_FOLDER'))
    if (not namespace_name or is_root) and not is_dir(sub_dir):
        _RCS[_rc_id(os, 'makedirs')](sub_dir)

    sub_dir = join(pdv_str(new_pdv, 'package_path'), pdv_str(new_pdv, 'TEMPLATES_FOLDER'))
    if is_root and not is_dir(sub_dir):
        _RCS[_rc_id(os, 'makedirs')](sub_dir)

    sub_dir = join(project_path, pdv_str(new_pdv, 'TESTS_FOLDER'))
    if not is_dir(sub_dir):
        _RCS[_rc_id(os, 'makedirs')](sub_dir)

    file_name = join(project_path, pdv_str(new_pdv, 'BUILD_CONFIG_FILE'))
    if project_type == APP_PRJ and not is_file(file_name):
        _RCS[_rc_id(ae.base, 'write_file')](file_name, f"# {OUTSOURCED_MARKER}{sep}[app]{sep}")

    file_name = join(project_path, 'manage.py')
    if project_type == DJANGO_PRJ and not is_file(file_name):
        _RCS[_rc_id(ae.base, 'write_file')](file_name, f"# {OUTSOURCED_MARKER}{sep}")


def _renew_project(ini_pdv: PdvType, project_type: str) -> PdvType:
    namespace_name = _get_namespace(ini_pdv, project_type)

    project_path, project_name = _get_renamed_path_package(ini_pdv, namespace_name, project_type)

    if not os_path_isdir(project_path):
        os.makedirs(project_path)

    new_pdv = {  # pre-init new prj-vars for the first creation/upd of prj dir; reinit. after _renew_prj_dir() call
        'namespace_name': namespace_name, 'project_name': project_name,
        'project_path': project_path, 'project_type': project_type,
        'package_path': os_path_join(project_path, *namespace_name.split("."), project_name[len(namespace_name) + 1:])
        if namespace_name else project_path,    # sync to aedev.setup_project._init_pev()
        'project_version': pdv_str(ini_pdv, 'project_version')
        if project_name == pdv_str(ini_pdv, 'project_name') else NULL_VERSION,
    }
    new_pdv.update([(var, pdv_str(ini_pdv, var)) for var in (   # add vars needed by _renew_prj_dir() from ini_pdv
        'BUILD_CONFIG_FILE', 'DOCS_FOLDER', 'TEMPLATES_FOLDER', 'TESTS_FOLDER', 'REQ_FILE_NAME',
        'STK_AUTHOR', 'STK_AUTHOR_EMAIL', 'project_desc')])

    new_repo = _git_init_if_needed(new_pdv)
    action = "new" if new_repo else "renew"
    errors = update_project(new_pdv)
    _chk_if(15, not bool(errors), f"git fetch errors:{_pp(errors)}")

    req_branch = cae.get_option('branch')
    if req_branch or _git_current_branch(new_pdv) == MAIN_BRANCH:
        renew_branch = req_branch if req_branch and req_branch != MAIN_BRANCH else \
            f"{action}_{project_type}_{project_name}"
        co_args = ("--merge", "--track") if f"remotes/origin/{renew_branch}" in _git_branches(new_pdv) else ()
        _git_checkout(new_pdv, *co_args, branch=renew_branch)

    _renew_prj_dir(new_pdv)
    new_pdv.update(project_dev_vars(project_path=project_path))

    bump_version(new_pdv)

    with _in_prj_dir_venv(project_path):
        dst_files = refresh_templates(new_pdv, logger=cae.po if cae.get_option('verbose') else cae.vpo)
    dbg_msg = ": " + " ".join(os_path_relpath(_, project_path) for _ in dst_files) if _debug_or_verbose() else ""
    cae.po(f"    - renewed {len(dst_files)} outsourced files{dbg_msg}")

    if new_repo:
        # install test-requirement on the first new-action (install new root dev_requirements after first publishing)
        install_requirements(os_path_join(pdv_str(new_pdv, 'TESTS_FOLDER'), pdv_str(new_pdv, 'REQ_FILE_NAME')),
                             project_path)

    new_pdv.update(project_dev_vars(project_path=project_path))

    _git_add(new_pdv)
    _git_renew_remotes(new_pdv)

    if namespace_name and project_type != ROOT_PRJ:     # is namespace portion
        _renew_local_root_req_file(new_pdv)

    cae.po(f" ==== {action} {pdv_str(new_pdv, 'project_desc')}")
    return new_pdv


def _renew_local_root_req_file(pdv: PdvType):
    namespace_name = pdv_str(pdv, 'namespace_name')
    project_name = pdv_str(pdv, 'project_name')
    req_dev_file_name = pdv_str(pdv, 'REQ_DEV_FILE_NAME')
    root_imp_name = namespace_name + '.' + namespace_name
    root_pkg_name = norm_name(root_imp_name)

    root_prj_path = os_path_join(os_path_dirname(pdv_str(pdv, 'project_path')), root_pkg_name)
    if not os_path_isdir(root_prj_path):
        cae.dpo(f"    # {namespace_name} namespace root project not found locally in {root_prj_path}")
        cae.po(f"  ### ensure to manually add {project_name} to {req_dev_file_name} of {namespace_name} namespace root")
        return

    root_req = os_path_join(root_prj_path, req_dev_file_name)
    if os_path_isfile(root_req):
        req_content = read_file(root_req)
    else:
        cae.po(f"   ## {root_req} not found in {root_imp_name} namespace root project path: creating ...")
        req_content = ""

    sep = os.linesep
    if not _required_package(project_name, req_content.split(sep)):
        if req_content and not req_content.endswith(sep):
            req_content += sep
        write_file(root_req, req_content + project_name + sep)


def _required_package(import_or_package_name: str, packages_versions: list[str]) -> bool:
    project_name, _ = project_version(import_or_package_name, packages_versions)
    return bool(project_name)


def _template_projects(pdv: PdvType) -> list[RegisteredTemplateProject]:
    """ determine template projects of namespace, project type, and generic project (the highest priority first). """
    namespace_name = pdv_str(pdv, 'namespace_name')
    project_type = pdv_str(pdv, 'project_type')
    dev_require = pdv_val(pdv, 'dev_require')
    dev_req_path = os_path_join(pdv_str(pdv, 'project_path'), pdv_str(pdv, 'REQ_DEV_FILE_NAME'))
    add_req = not dev_require and not os_path_isfile(dev_req_path) and not os_path_isfile(dev_req_path + LOCK_EXT)

    tpl_projects: list[RegisteredTemplateProject] = []
    if namespace_name:
        _register_template(namespace_name + '.' + namespace_name, dev_require, add_req, tpl_projects)

    if project_type not in (PARENT_PRJ, NO_PRJ):
        _register_template(TPL_IMPORT_NAME_PREFIX + norm_name(project_type), dev_require, add_req, tpl_projects)

    _register_template(TPL_IMPORT_NAME_PREFIX + 'project', dev_require, add_req, tpl_projects)

    if _debug_or_verbose():
        if tpl_projects:
            msg = f"  --- {pdv_str(pdv, 'project_desc')} uses {len(tpl_projects)} template project(s):"
            if cae.debug:
                cae.po(msg)
                cae.po(f"      {PPF(tpl_projects)}")
            else:
                cae.po(msg + " " + " ".join(_['import_name'] for _ in tpl_projects))
        cae.vpo(f"   -- all {len(REGISTERED_TPL_PROJECTS)} registered template projects:")
        cae.vpo(f"      {PPF(REGISTERED_TPL_PROJECTS)}")
        if add_req:
            cae.vpo(f"   -- added {len(dev_require)} template projects to {dev_req_path}: {PPF(dev_require)}")
        else:
            drt = [_ for _ in dev_require
                   if _.startswith(norm_name(TPL_IMPORT_NAME_PREFIX))
                   or _.startswith(namespace_name + '_' + namespace_name)]
            cae.vpo(f"   -- {dev_req_path} activating {len(drt)} template projects: {PPF(drt)}")

    return tpl_projects


def _template_version_option(import_name: str) -> str:
    return norm_name(import_name.split('.')[-1]) + '_version'


def _update_frozen_req_files(pdv):
    req_file_name = pdv_str(pdv, 'REQ_FILE_NAME')
    req_file_paths = (
        req_file_name,
        pdv_str(pdv, 'REQ_DEV_FILE_NAME'),
        os_path_join(pdv_str(pdv, 'DOCS_FOLDER'), req_file_name),
        os_path_join(pdv_str(pdv, 'TESTS_FOLDER'), req_file_name),
    )
    pip_freeze_comment = "## The following requirements were added by pip freeze:"

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        for req_file_path in req_file_paths:
            frozen_file_stub, frozen_file_ext = os_path_splitext(req_file_path)
            frozen_file_path = f'{frozen_file_stub}_frozen{frozen_file_ext}'
            if os_path_isfile(frozen_file_path):
                line_count = len(read_file(req_file_path).split(os.linesep))
                out_lines = []
                _cl(48, f"{CMD_PIP} freeze -r {req_file_path}", lines_output=out_lines)
                write_file(frozen_file_path, os.linesep.join(out_lines[:line_count]).replace(pip_freeze_comment, ""))


def _wait():
    wait_seconds = cae.get_option('delay')
    cae.po(f"..... waiting {wait_seconds} seconds")
    time.sleep(wait_seconds)


def _write_commit_message(pdv: PdvType, pkg_version: str = "{project_version}", title: str = ""):
    sep = os.linesep
    file_name = os_path_join(pdv_str(pdv, 'project_path'), COMMIT_MSG_FILE_NAME)
    if not title:
        title = _git_current_branch(pdv).replace("_", " ")
    write_file(file_name, f"V{pkg_version}: {title}{sep}{sep}{os.linesep.join(_git_status(pdv))}{sep}")


# --------------- git remote repo connection --------------------------------------------------------------------------

class RemoteHost:
    """ base class registering subclasses as remote host repo class in :data:`REGISTERED_HOSTS_CLASS_NAMES`. """
    name_prefix: str = 'repo'       # config variable name prefix

    create_branch: Callable
    release_project: Callable
    repo_obj: Callable
    request_merge: Callable

    def __init_subclass__(cls, **kwargs):
        """ register a remote host class name; called on declaration of a subclass of :class:`RemoteHost`. """
        # global REGISTERED_HOSTS_CLASS_NAMES
        REGISTERED_HOSTS_CLASS_NAMES[camel_to_snake(cls.__name__)[1:].replace('_', '.').lower()] = cls.__name__
        super().__init_subclass__(**kwargs)

    def _repo_merge_src_dst_fork_branch(self, ini_pdv: PdvType) -> tuple[RepoType, RepoType, bool, str]:
        branch = _get_branch(ini_pdv)
        domain = _get_host_domain(ini_pdv)
        group_name = _get_host_group(ini_pdv, domain)
        project_name = _get_prj_name(ini_pdv)

        remotes = _git_remotes(ini_pdv)
        forked = 'upstream' in remotes
        if forked:
            owner_name = remotes['upstream'].split('/')[-2]
            _chk_if(64, owner_name == group_name, f"upstream/owner-group mismatch: '{owner_name}' != '{group_name}'")
            user_name = _get_host_user_name(ini_pdv, domain)
        else:
            user_name = group_name
        origin_user = remotes.get('origin', "/").split('/')[-2]
        _chk_if(64, origin_user == user_name, f"origin/user mismatch: '{origin_user}' != '{user_name}'")

        # target_project_id/project_id is the upstream and source_project_id is the origin/fork
        msg = "repository '{name}' not found on remote host server " + self.__class__.__name__
        src = self.repo_obj(65, f"source/origin/fork {msg}", f"{user_name}/{project_name}")
        tgt = self.repo_obj(66, f"target/upstream/forked {msg}", f"{group_name}/{project_name}")

        return src, tgt, forked, branch

    def _release_project(self, ini_pdv: PdvType, version_tag: str):
        errors = _git_fetch(ini_pdv)
        _chk_if(84, not bool(errors), f"git fetch errors:{_pp(errors)}" + _hint(
            self.release_project, " later to retry if server is currently unavailable, or check remote configuration"))

        # switch back to local MAIN_BRANCH and then merge-in the release-branch&-tag from remotes/origin/MAIN_BRANCH
        _git_checkout(ini_pdv, branch=MAIN_BRANCH)
        _git_merge(ini_pdv, f"origin/{MAIN_BRANCH}")

        if version_tag == 'LATEST':
            pkg_version = _git_project_version(ini_pdv, increment_part=0)
            version_tag = f"v{pkg_version}"
        else:
            _chk_if(85, version_tag[0] == "v" and version_tag.count(".") == 2, f"version '{version_tag}' format error")
            pkg_version = version_tag[1:]
        _chk_if(85, _git_tag_in_branch(ini_pdv, version_tag),
                f"push version tag {version_tag} has first to be merged into origin/{MAIN_BRANCH}" + _hint(
                    self.request_merge, " to request to merge your branch."))

        msg = f"updated local {MAIN_BRANCH} branch"
        if pdv_str(ini_pdv, 'pip_name'):  # create release*ver branch only for projects available in PyPi via pip
            release_branch = f"release{pkg_version}"
            _chk_if(85, not _git_tag_in_branch(ini_pdv, release_branch),
                    f"release branch {release_branch} already exists in origin/{MAIN_BRANCH}")
            cae.dpo(f"   -- creating branch '{release_branch}' for tag '{version_tag}' at remotes/origin")
            prj_id = f"{_get_host_group(ini_pdv, _get_host_domain(ini_pdv))}/{pdv_str(ini_pdv, 'project_name')}"
            self.create_branch(prj_id, release_branch, version_tag)
            msg += f" and released {pkg_version} onto new protected release branch {release_branch}"

        cae.po(f" ==== {msg} of {pdv_str(ini_pdv, 'project_desc')}")


class GithubCom(RemoteHost):
    """ remote connection and actions on remote repo in gitHub.com. """
    connection: Github                  #: connection to GitHub host

    def connect(self, ini_pdv: PdvType) -> bool:
        """ connect to gitHub.com remote host.

        :param ini_pdv:         project dev vars (host_token).
        :return:                boolean True on successful authentication else False.
        """
        try:
            self.connection = Github(auth=Auth.Token(pdv_val(ini_pdv, 'repo_token')))
        except (Exception, ) as ex:                                 # pylint: disable=broad-exception-caught
            cae.po(f"****  Github authentication exception: {ex}")
            return False
        return True

    def create_branch(self, group_repo: str, branch_name: str, tag_name: str):
        """ create a new remote branch onto/from the tag name.

        :param group_repo:      string with owner-user-name/repo-name of the repository, e.g. "UserName/RepositoryName".
        :param branch_name:     name of the branch to create.
        :param tag_name:        name of the tag/ref to create the branch from.
        """
        prj = self.repo_obj(95, "project {name} not found", group_repo)
        try:
            git_tag = prj.get_git_tag(tag_name)     # https://gist.github.com/ursulacj/36ade01fa6bd5011ea31f3f6b572834e
            prj.create_git_ref(f'refs/heads/{branch_name}', git_tag.sha)
        except (GithubException, Exception):        # pylint: disable=broad-exception-caught
            _exit_error(86, f"error creating branch '{branch_name}' for tag '{tag_name}': {format_exc()}")

        # protect the branch until GitHub Api supports wildcards in the initial push (see self.init_new_repo())
        self._protect_branches(prj, [branch_name])

    def init_new_repo(self, group_repo: str, project_desc: str):
        """ config new project repo.

        :param group_repo:      project owner user and repository names in the format "user-name/repo-name".
        :param project_desc:    project description.
        """
        project_repo = self.repo_obj(78, "repository '{name}' to initialize not found", group_repo)
        cae.vpo(f"    - setting remote project properties of new repository '{group_repo}'")
        project_repo.edit(default_branch=MAIN_BRANCH, description=project_desc, visibility='public')

        branch_masks = [MAIN_BRANCH]      # , 'release*']
        self._protect_branches(project_repo, branch_masks)
        # the GitHub REST api does still not allow creating branch protection with a wildcard (for release*)
        # .. see https://github.com/orgs/community/discussions/24703
        # current workaround is to protect individual release branch in the release_project action

        cae.po(f"   == initialized project and created {len(branch_masks)} protected branch(es): {branch_masks}")

    def repo_obj(self, err_code: int, err_msg: str, group_repo: str) -> Repository:
        """ convert user repo names to a repository instance of the remote api.

        :param err_code:        error code, pass 0 to not quit if a project is not found.
        :param err_msg:         error message to display on error with optional {name} to be automatically substituted
                                with the project name from the :paramref:`~repo_obj.group_repo_names` argument.
        :param group_repo:      string with owner-user-name/repo-name of the repository, e.g. "UserName/RepositoryName".
        :return:                GitHub repository if found, else return None if err_code is zero else quit.
        """
        try:
            # search for repo projects: repos = list(self.connection.search_repositories(query="user:AndiEcker"))
            return self.connection.get_repo(group_repo)
        except (GithubException, Exception) as gh_ex:           # pylint: disable=broad-exception-caught
            if err_code:
                _exit_error(err_code, err_msg.format(name=group_repo))
            elif _debug_or_verbose():
                cae.po(f"   * repository '{group_repo}' not found on connected remote server (exception: {gh_ex})")
            return cast(Repository, None)

    @staticmethod
    def _protect_branches(project_repo: Repository, branch_masks: list[str]):
        for branch_mask in branch_masks:
            # see also GitHub WebUI docs: https://docs.github.com/de/rest/branches/branch-protection and
            # https://docs.github.com/de/repositories/configuring-branches-and-merges-in-your-repository/...
            # ...managing-protected-branches/managing-a-branch-protection-rule
            # example: https://github.com/txqueuelen/reposettings/blob/master/reposettings.py
            # .. done with powerscript: https://medium.com/objectsharp/...
            # ...adding-branch-protection-to-your-repo-with-the-github-rest-api-and-powershell-67ee19425e40
            branch_obj = project_repo.get_branch(branch_mask)
            cae.vpo(f"    - protecting branch {branch_mask}")
            branch_obj.edit_protection(strict=True)

    # ----------- remote action methods ----------------------------------------------------------------------------

    @_action(PARENT_PRJ, *ANY_PRJ_TYPE, arg_names=(('forked-user-slash-repo', ), ), shortcut='fork')
    def fork_project(self, ini_pdv: PdvType, forked_usr_repo: str):
        """ create/renew a fork of a remote repo specified via the 1st argument, into our user/group namespace. """
        domain = _get_host_domain(ini_pdv)
        _chk_if(20, domain == 'github.com', f"invalid repo host domain '{domain}'! add option --domain=github.com")

        prj = self.repo_obj(20, "repository {name} to fork not found", forked_usr_repo)
        cast(AuthenticatedUser, self.connection.get_user()).create_fork(prj)

        cae.po(f" ==== forked {pdv_str(ini_pdv, 'project_desc')} on {domain}")

    @_action(*ANY_PRJ_TYPE, arg_names=((), ('branch-name', ), ), shortcut='push')
    def push_project(self, ini_pdv: PdvType, branch_name: str = ''):
        """ push the current/specified branch of project/package version-tagged to the remote repository host.

        :param ini_pdv:             project dev vars.
        :param branch_name:         optional branch name to push (alternatively specified by the ``branch`` command line
                                    option).
        """
        group_name = _get_host_group(ini_pdv, _get_host_domain(ini_pdv))
        project_name = _get_prj_name(ini_pdv)

        changed = _git_uncommitted(ini_pdv)
        _chk_if(76, not changed, f"{project_name} has {len(changed)} uncommitted files: {changed}")

        new_repo = False
        push_refs = []
        if not self.repo_obj(0, "", f"{group_name}/{project_name}"):
            usr_obj = cast(AuthenticatedUser, self.connection.get_user())
            usr_obj.create_repo(project_name)   # if not, then git push throws the error "Repository not found"
            new_repo = True
            push_refs.append(MAIN_BRANCH)

        branch_name = branch_name or _get_branch(ini_pdv)
        if branch_name and branch_name not in push_refs:
            push_refs.append(branch_name)

        tag = _check_version_tag(ini_pdv)
        push_refs.append(tag)

        _git_push(ini_pdv, *push_refs, extra_args=("--set-upstream", ))

        if new_repo:    # branch protection rules have to be created after branch creation done by git push
            self.init_new_repo(f"{group_name}/{project_name}", pdv_str(ini_pdv, 'project_desc'))

        cae.po(f" ==== pushed {' '.join(push_refs)} branches/tags to remote project {project_name}")

    @_action(*ANY_PRJ_TYPE, arg_names=(("version-tag", ), ('LATEST', )), shortcut='release')
    def release_project(self, ini_pdv: PdvType, version_tag: str):
        """ update local MAIN_BRANCH from origin, and if pip_name is set, then release the latest/specified version too.

        :param ini_pdv:         project dev vars.
        :param version_tag:     push version tag in the format ``v<version-number>`` to release or ``LATEST`` to use
                                the version tag of the latest git repository version.
        """
        self._release_project(ini_pdv, version_tag)

    @_action(*ANY_PRJ_TYPE, shortcut='request')
    def request_merge(self, ini_pdv: PdvType):
        """ request merge of the origin=fork repository into the main branch at remote/upstream=forked. """
        # see https://docs.github.com/de/rest/pulls/pulls?apiVersion=2022-11-28#create-a-pull-request
        src_prj, tgt_prj, forked, branch = self._repo_merge_src_dst_fork_branch(ini_pdv)
        if TYPE_CHECKING:
            assert isinstance(src_prj, Repository)
            assert isinstance(tgt_prj, Repository)

        commit_msg_title, commit_msg_body = read_file(_check_commit_msg_file(ini_pdv)).split(os.linesep, maxsplit=1)
        merge_req = tgt_prj.create_pull(base=MAIN_BRANCH, head=branch, title=commit_msg_title, body=commit_msg_body)
        if _debug_or_verbose():
            diff_url = merge_req.diff_url
            cae.po(f"    . merge request diffs available at: {diff_url}")

        action = "requested merge"
        if not forked:
            _wait()  # wait for the created un-forked/direct maintainer merge request
            tgt_prj.merge(base=MAIN_BRANCH, head=branch, commit_message=commit_msg_title + os.linesep + commit_msg_body)
            action = "auto-merged un-forked merge request"

        cae.po(f" ==== {action} of branch {branch} from fork/origin ({src_prj.id}) into upstream ({tgt_prj.id})")


class GitlabCom(RemoteHost):
    """ remote connection and actions on gitlab.com. """
    connection: Gitlab                  #: connection to Gitlab host

    def connect(self, ini_pdv: PdvType) -> bool:
        """ connect to gitlab.com remote host.

        :param ini_pdv:         project dev vars (REPO_HOST_PROTOCOL, host_domain, host_token).
        :return:                boolean True on successful authentication else False.
        """
        try:
            self.connection = Gitlab(pdv_str(ini_pdv, 'REPO_HOST_PROTOCOL') + pdv_str(ini_pdv, 'repo_domain'),
                                     private_token=pdv_val(ini_pdv, 'repo_token'))
            if cae.debug:
                self.connection.enable_debug()
            self.connection.auth()          # authenticate and create user attribute
        except (Exception, ) as ex:         # pylint: disable=broad-exception-caught
            cae.po(f"****  Gitlab connection exception: {ex}")
            return False
        return True

    def create_branch(self, group_repo: str, branch_name: str, tag_name: str):
        """ create a new remote branch onto/from the tag name.

        :param group_repo:      string with owner-user-name/repo-name of the repository, e.g. "UserName/RepositoryName".
        :param branch_name:     name of the branch to create.
        :param tag_name:        name of the tag/ref to create the branch from.
        """
        cae.dpo(f"   -- creating branch '{branch_name}' for tag '{tag_name}' at remotes/origin")
        prj = self.repo_obj(95, "group/project {name} not found", group_repo)
        try:
            prj.branches.create({'branch': branch_name, 'ref': tag_name})
        except (GitlabHttpError, GitlabCreateError, GitlabError, Exception):    # pylint: disable=broad-exception-caught
            _exit_error(86, f"error '{format_exc()}' creating branch '{branch_name}' for tag '{tag_name}'")

    def init_new_repo(self, ini_pdv: PdvType):
        """ create a group/user project specified in ini_pdv or quit with error if group/user not found.

        :param ini_pdv:         project dev vars.
        """
        owner_obj = self.project_owner(ini_pdv)
        project_name = _get_prj_name(ini_pdv)
        project_properties = {
            'name': project_name,
            'description': pdv_str(ini_pdv, 'project_desc'),
            'default_branch': MAIN_BRANCH,
            'visibility': 'public',
        }
        if isinstance(owner_obj, User):
            project_properties['user_id'] = owner_obj.id
        else:
            project_properties['namespace_id'] = owner_obj.id
        cae.vpo(f"    - remote project properties of new package {project_name}: {PPF(project_properties)}")

        # using UserProtectManager|owner_obj.projects.create() for user projects results in 403 Forbidden error
        project = cast(Project, self.connection.projects.create(project_properties))
        cae.po(f"   == created new project for user/group '{owner_obj.name}'; attributes: {PPF(project.attributes)}")

        _wait()

        for branch_mask in (MAIN_BRANCH, 'release*'):
            protected_branch_properties = {'name': branch_mask,
                                           'merge_access_level': MAINTAINER_ACCESS,
                                           'push_access_level': MAINTAINER_ACCESS}
            cae.vpo(f"    - {branch_mask} protected branch properties: {protected_branch_properties}")
            project.protectedbranches.create(protected_branch_properties)
        cae.po(f"   == created 2 protected branches: '{MAIN_BRANCH}', 'release*'")

    def repo_obj(self, err_code: int, err_msg: str, group_repo: str) -> Project:
        """ convert group/project_name or an endswith-fragment of it to a Project instance of the remote repo api.

        :param err_code:        error code, pass 0 to not quit if the project is not found.
        :param err_msg:         error message to display on error with optional {name} to be automatically substituted
                                with the project name from the :paramref:`~repo_obj.group_repo` argument.
        :param group_repo:      group/project-name to search for.
        :return:                python-gitlab project instance if found, else return None if err_code is zero else quit.
        """
        try:
            # Projects.get() raises GitLabError (404 project not found) on an exact project name if there are other
            # project names starting with the same string. Projects.list() then returns the project as the last item.
            return self.connection.projects.get(group_repo)
        except GitlabError:     # e.g., GitlabGetError: 404: 404 Project Not Found
            if err_code:
                _exit_error(err_code, err_msg.format(name=group_repo))
            elif _debug_or_verbose():
                cae.po(f"   * group/project {group_repo} not found on connected remote server")
            return cast(Project, None)

    def project_owner(self, ini_pdv: PdvType) -> Union[Group, User]:
        """ get the owner (group|user) of the project specified by ini_pdv or quit with error if group/user not found.

        :param ini_pdv:         project dev vars.
        :return:                instance of Group or User, determined via the user-/group-names specified by ini_pdv.
        """
        domain = _get_host_domain(ini_pdv)
        group_name = _get_host_group(ini_pdv, domain)
        user_name = _get_host_user_name(ini_pdv, domain)

        owner_obj: Optional[Union[Group, User]] = None
        try:
            owner_obj = self.connection.groups.get(group_name)
        except GitlabError:
            groups = self.connection.groups.list(search=group_name)
            if groups:
                owner_obj = groups[0]                               # type: ignore

        if owner_obj is None:
            try:
                owner_obj = self.connection.users.get(user_name)
            except GitlabError:
                users = self.connection.users.list(username=user_name)
                if users:
                    owner_obj = users[0]                            # type: ignore

        if owner_obj is None:
            _exit_error(37, f"neither group '{group_name}' nor user '{user_name}' found on repo host '{domain}'")
            raise  # never executed; needed by mypy for owner_obj type checking # pylint: disable=misplaced-bare-raise
        return owner_obj

    # ----------- remote action methods ----------------------------------------------------------------------------

    @_action(*ANY_PRJ_TYPE)
    def clean_releases(self, ini_pdv: PdvType) -> list[str]:
        """ delete local+remote release tags and branches of the specified project that got not published to PYPI. """
        pip_name = pdv_str(ini_pdv, 'pip_name')
        if not pip_name:
            cae.po(" ==== this project has no PyPi release tags/branches to clean")
            return []

        project_path = pdv_str(ini_pdv, 'project_path')
        group_repo = f"{_get_host_group(ini_pdv, _get_host_domain(ini_pdv))}/{_get_prj_name(ini_pdv)}"

        all_branches = _git_branches(ini_pdv)
        cae.po(f"    - found {len(all_branches)} branches to check for to be deleted: {all_branches}")

        pypi_releases = pypi_versions(pip_name)
        _chk_if(34, bool(pypi_releases), "no PyPI releases found (check installation of pip)")
        cae.po(f"    - found {len(pypi_releases)} PyPI release versions protected from to be deleted: {pypi_releases}")

        deleted = []
        for branch_name in all_branches:
            chk, *ver = branch_name.split('release')
            if len(ver) != 1 or ver[0] in pypi_releases:
                continue
            version = ver[0]
            if chk == 'remotes/origin/':        # un-deployed remote release branch found
                # _git_push(ini_pdv, branch_name, extra_args=("--delete",)) protected 'release*' branch raises error
                project = self.repo_obj(33, "{name} not found at origin", group_repo)
                try:
                    project.protectedbranches.delete(branch_name)
                except GitlabError as ex:  # GitlabDeleteError on failed release upload
                    cae.po(f"    # try other method to delete protected branch {branch_name} on remote after err: {ex}")
                    try:
                        branch_obj = project.protectedbranches.get(branch_name)
                        branch_obj.delete()
                    except GitlabError as ex2:
                        cae.po(f"   ## ignoring error deleting release branch {branch_name} on remote origin: {ex2}")

                sh_err = _git_push(ini_pdv, f"v{version}", extra_args=("--delete", ), exit_on_error=False)
                if sh_err:
                    cae.po(f"   ## ignoring error {sh_err} deleting tag v{version} via push to remote")

                deleted.append(branch_name)

            elif not chk:                       # un-deployed local release branch found
                with _in_prj_dir_venv(project_path):
                    sh_err = _cl(33, f"git branch --delete {branch_name}", exit_on_err=False)
                    if sh_err:
                        cae.po(f"   ## ignoring error {sh_err} deleting branch {branch_name} via 'git branch --delete'")

                    sh_err = _cl(33, f"git tag --delete v{version}", exit_on_err=False)
                    if sh_err:
                        cae.po(f"   ## ignoring error {sh_err} deleting local tag v{version} via 'git tag --delete'")

                deleted.append(branch_name)

        cae.po(f" ==== cleaned {len(deleted)} release branches and tags: {deleted}")

        return deleted

    @_action(PARENT_PRJ, ROOT_PRJ)
    def fork_children(self, ini_pdv: PdvType, *children_pdv: PdvType):
        """ fork children of a namespace root project or of a parent folder. """
        _children_path_package_option_reset()
        for chi_pdv in children_pdv:
            self.fork_project(chi_pdv)
        cae.po(f"===== forked {_children_desc(ini_pdv, children_pdv)}")

    @_action(PARENT_PRJ, *ANY_PRJ_TYPE, shortcut='fork')
    def fork_project(self, ini_pdv: PdvType):
        """ create/renew a fork of a remote repo specified via the `package` option, into our user/group namespace. """
        domain = _get_host_domain(ini_pdv)
        _chk_if(20, domain == 'gitlab.com', f"invalid repo host domain '{domain}'! add option --domain=gitlab.com")

        if 'upstream' in _git_remotes(ini_pdv):    # renew origin from upstream if already forked
            with _in_prj_dir_venv(pdv_str(ini_pdv, 'project_path')):
                _cl(20, f"git checkout {MAIN_BRANCH}")
                _cl(20, "git fetch upstream")
                _cl(20, f"git pull upstream {MAIN_BRANCH}")
                _cl(20, f"git push origin {MAIN_BRANCH}")
        else:
            group_name = _get_host_group(ini_pdv, domain)
            parent_path, _project_path, project_name = _get_path_package(ini_pdv)
            prj_instance = self.repo_obj(20, "project {name} not found on remote", f"{group_name}/{project_name}")

            prj_instance.forks.create({})        # {'namespace': usr_name}

            usr_name = self.connection.user.name                # type: ignore # silly mypy
            host_url = f"{pdv_str(ini_pdv, 'REPO_HOST_PROTOCOL')}{domain}"
            with _in_prj_dir_venv(parent_path):
                _cl(21, "git clone", extra_args=(f"{host_url}/{usr_name}/{project_name}.git", ))
                _cl(21, "git remote", extra_args=("add", 'upstream', f"{host_url}/{group_name}/{project_name}.git"))
                _git_renew_remotes(ini_pdv)     # add/renew git remote origin

        _git_checkout(ini_pdv, branch=_get_branch(ini_pdv))
        cae.po(f" ==== forked {pdv_str(ini_pdv, 'project_desc')}")

    @_action(PARENT_PRJ, ROOT_PRJ)
    def push_children(self, ini_pdv: PdvType, *children_pdv: PdvType):
        """ push specified children projects to remotes/origin. """
        for chi_pdv in children_pdv:
            self.push_project(chi_pdv)
            if chi_pdv != children_pdv[-1]:
                _wait()
        cae.po(f"===== pushed {_children_desc(ini_pdv, children_pdv)}")

    @_action(*ANY_PRJ_TYPE, arg_names=((), ('branch-name', ), ), shortcut='push')
    def push_project(self, ini_pdv: PdvType, branch_name: str = ''):
        """ push current/specified branch of project/package version-tagged to the remote host domain.

        :param ini_pdv:             project dev vars.
        :param branch_name:         optional branch name to push (alternatively specified by the ``branch`` command line
                                    option).
        """
        group_repo = f"{_get_host_group(ini_pdv, _get_host_domain(ini_pdv))}/{_get_prj_name(ini_pdv)}"

        changed = _git_uncommitted(ini_pdv)
        _chk_if(76, not changed, f"{group_repo} has {len(changed)} uncommitted files: {changed}")

        push_refs = []
        if not self.repo_obj(0, "", group_repo):
            self.init_new_repo(ini_pdv)
            push_refs.append(MAIN_BRANCH)

        branch_name = branch_name or _get_branch(ini_pdv)
        if branch_name and branch_name not in push_refs:
            push_refs.append(branch_name)

        tag = _check_version_tag(ini_pdv)
        push_refs.append(tag)

        _git_push(ini_pdv, *push_refs, extra_args=("--set-upstream", ))

        cae.po(f" ==== pushed {' '.join(push_refs)} branches/tags to remote project {group_repo}")

    @_action(PARENT_PRJ, ROOT_PRJ)
    def release_children(self, ini_pdv: PdvType, *children_pdv: PdvType):
        """ release the latest versions of the specified parent/root children projects to remotes/origin. """
        for chi_pdv in children_pdv:
            cae.po(f" ---  {pdv_str(chi_pdv, 'project_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
            self.release_project(chi_pdv, 'LATEST')
            if chi_pdv != children_pdv[-1]:
                _wait()
        cae.po(f"===== released {_children_desc(ini_pdv, children_pdv)}")

    @_action(*ANY_PRJ_TYPE, arg_names=(("version-tag", ), ('LATEST', )), shortcut='release')
    def release_project(self, ini_pdv: PdvType, version_tag: str):
        """ update local MAIN_BRANCH from origin, and if pip_name is set, then release the latest/specified version too.

        :param ini_pdv:         project dev vars.
        :param version_tag:     push version tag in the format ``v<version-number>`` to release or ``LATEST`` to use
                                the version tag of the latest git repository version.
        """
        self._release_project(ini_pdv, version_tag)

    @_action(PARENT_PRJ, ROOT_PRJ)
    def request_children_merge(self, ini_pdv: PdvType, *children_pdv: PdvType):
        """ request specified children merge of a parent/namespace on remote/upstream. """
        for chi_pdv in children_pdv:
            cae.po(f" ---  {pdv_str(chi_pdv, 'project_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
            self.request_merge(chi_pdv)
            if chi_pdv != children_pdv[-1]:
                _wait()
        cae.po(f"===== requested merge of {_children_desc(ini_pdv, children_pdv)}")

    @_action(*ANY_PRJ_TYPE, shortcut='request')
    def request_merge(self, ini_pdv: PdvType):
        """ request merge of the origin=fork repository into the main branch at remote/upstream=forked. """
        # https://docs.gitlab.com/ee/api/merge_requests.html#create-mr and https://stackoverflow.com/questions/51104622
        src_prj, tgt_prj, forked, branch = self._repo_merge_src_dst_fork_branch(ini_pdv)
        if TYPE_CHECKING:
            assert isinstance(src_prj, Project)
            assert isinstance(tgt_prj, Project)
        commit_msg = read_file(_check_commit_msg_file(ini_pdv))
        merge_req = tgt_prj.mergerequests.create({
            'project_id': tgt_prj.id,
            'source_project_id': src_prj.id,
            'source_branch': branch,
            'target_project_id': tgt_prj.id,
            'target_branch': MAIN_BRANCH,
            'title': commit_msg.split(os.linesep)[0],
            # 'remove_source_branch': False,
            # 'force_remove_source_branch': False,
            # 'allow_collaboration': True,
            # 'subscribed': True,
        })
        if _debug_or_verbose():
            cae.po(f"    . merge request diffs: {PPF([_.attributes for _ in merge_req.diffs.list()])}")

        action = "requested merge"
        if not forked:
            _wait()  # wait for the created un-forked/direct maintainer merge request
            merge_req.merge(merge_commit_message=commit_msg)
            action = "auto-merged un-forked merge request"

        cae.po(f" ==== {action} of branch {branch} from fork/origin ({src_prj.id}) into upstream ({tgt_prj.id})")

    @_action(*ANY_PRJ_TYPE, arg_names=((), ('fragment', ), ))
    def search_repos(self, ini_pdv: PdvType, fragment: str = ""):
        """ search remote repositories via a text fragment in its project name/description. """
        fragment = fragment or _get_prj_name(ini_pdv)
        repos = self.connection.projects.list(search=fragment, get_all=True)
        cae.po(f"----  found {len(repos)} repos containing '{fragment}' in its name project name or description:")
        for repo in repos:
            cae.po(f"    - {PPF(repo)}")
        cae.po(f" ==== searched all repos at {_get_host_domain(ini_pdv)} for '{fragment}'")

    @_action(PARENT_PRJ, ROOT_PRJ)
    def show_children_repos(self, ini_pdv: PdvType, *children_pdv: PdvType):
        """ display remote properties of parent/root children repos. """
        for chi_pdv in children_pdv:
            self.show_repo(chi_pdv)
        cae.po(f"===== dumped info of {_children_desc(ini_pdv, children_pdv)}")

    @_action(*ANY_PRJ_TYPE)
    def show_repo(self, ini_pdv: PdvType):
        """ display properties of the remote repository. """
        group_repo = f"{_get_host_group(ini_pdv, _get_host_domain(ini_pdv))}/{_get_prj_name(ini_pdv)}"
        repo_api = self.repo_obj(0, "", group_repo)
        if isinstance(repo_api, Project):
            cae.po(f"   -- {group_repo} remote repository attributes:")
            for attr in sorted(repo_api.attributes) if _debug_or_verbose() else \
                    ('created_at', 'default_branch', 'description', 'id', 'path_with_namespace', 'visibility'):
                cae.po(f"    - {attr} = {getattr(repo_api, attr, None)}")

            cae.po(f"   -- protected branches = {PPF(repo_api.protectedbranches.list())}")
            cae.po(f"   -- protected tags = {PPF(repo_api.protectedtags.list())}")
        else:
            cae.po(f"    * project {group_repo} not found on remote server")
        cae.po(f" ==== dumped repo info of {pdv_str(ini_pdv, 'project_desc')}")


class PythonanywhereCom(RemoteHost):
    """ remote actions on remote web host pythonanywhere.com (to be specified by --domain option). """
    connection: PythonanywhereApi               #: requests http connection
    name_prefix: str = 'web'                    #: config variable name prefix

    def connect(self, ini_pdv: PdvType) -> bool:
        """ connect to www. and eu.pythonanywhere.com web host.

        :param ini_pdv:         parent/root project dev vars.
        :return:                boolean True on successful authentication else False.
        """
        self.connection = PythonanywhereApi(pdv_str(ini_pdv, 'web_domain'),
                                            pdv_str(ini_pdv, 'web_user'),
                                            pdv_val(ini_pdv, 'web_token'),
                                            pdv_val(ini_pdv, 'project_name'))
        return not self.connection.error_message

    deploy_flags = {'ALL': False, 'CLEANUP': False, 'LEAN': False, 'MASKS': []}
    """ optional flag names and default values for the actions :meth:`check_deploy` and :meth:`deploy_project` """

    def deploy_differences(self, ini_pdv: PdvType, action: str, version_tag: str, **optional_flags
                           ) -> tuple[str, str, set[str], set[str]]:
        """ determine differences between the specified repository and web host/server (deployable and deletable files).

        :param ini_pdv:         project dev vars.
        :param action:          pass 'check' to only check the differences between the specified repository and
                                the web server/host, or 'deploy' to prepare the deployment of these differences.
        :param version_tag:     project package version to deploy. pass ``LATEST`` to use the version tag
                                of the latest repository version (PyPI release), or ``WORKTREE`` to deploy
                                the actual working tree package version (including unstaged/untracked files).
        :param optional_flags:  optional command line arguments, documented in detail in the declaration of
                                the action method parameter :paramref:`check_deploy.optional_flags`.
        :return:                tuple of 2 strings and 2 sets. the first string contains a description of the project
                                and the server to check/deploy-to, and the second the path to the project root folder.
                                the two sets containing project file paths, relative to the
                                local/temporary project root folder, the first one with the deployable files,
                                and the 2nd one with the removable files.
        """
        prj_desc = f"{pdv_str(ini_pdv, 'web_user')}@{pdv_str(ini_pdv, 'web_domain')}/{pdv_str(ini_pdv, 'project_desc')}"
        func = self.check_deploy if action == 'check' else self.deploy_project
        lean_msg = ' lean' if optional_flags['LEAN'] else ''
        verbose = _debug_or_verbose()
        deployed_ver = self.connection.deployed_version()
        cae.po(f" ---- {action} {version_tag}{lean_msg} against host/project {prj_desc} {deployed_ver}")

        if version_tag == 'WORKTREE':
            include_untracked = True
            branch_or_tag = f"v{deployed_ver}" if deployed_ver else MAIN_BRANCH     # from this to HEAD
            prj_root_path = pdv_str(ini_pdv, 'project_path')
            version_tag = f"v{_git_project_version(ini_pdv, increment_part=0)}w"    # w suffix only visible in logs
        else:
            include_untracked = False
            if version_tag == 'LATEST':
                version_tag = f"v{_git_project_version(ini_pdv, increment_part=0)}"
            else:
                _chk_if(85, version_tag[0] == "v" and version_tag.count(".") == 2,
                        f"expected 'LATEST', 'WORKTREE' or a project version tag (e.g. 'v0.1.2'), got '{version_tag}'")
                _chk_if(85, not deployed_ver or version_tag[1:] in (deployed_ver, increment_version(deployed_ver)),
                        f"too big increment between old|deployed ({deployed_ver}) and new version ({version_tag[1:]})"
                        + _hint(func, " with the current/next version or the --force option to skip the version check"))
            prj_root_path = _git_clone(pdv_str(ini_pdv, 'repo_root'), pdv_str(ini_pdv, 'project_name'),
                                       branch_or_tag=version_tag, extra_args=("--filter=blob:none", ))
            _chk_if(85, bool(prj_root_path), "git clone tmp cleanup error, to check run again with the -D 1 option")
            branch_or_tag = f"v{deployed_ver}...{version_tag}"

        path_masks = optional_flags['MASKS'] + ['manage.py'] + root_packages_masks(ini_pdv)
        cae.vpo(f"  --- {len(path_masks)} deploy file path masks found: {_pp(sorted(path_masks))}")

        skip_func = skip_files_lean_web if lean_msg else skip_py_cache_files
        skipped = set()

        def _track_skipped(file_path: str) -> bool:
            if skip_func(file_path):
                if skip_py_cache_files(file_path):
                    return True
                skipped.add(file_path)
            return False
        deployable = find_project_files(prj_root_path, path_masks, skip_file_path=_track_skipped)
        cae.vpo(f"  --- {len(deployable)} deployable project files found: {_pp(sorted(deployable))}")
        cae.vpo(f"  --- {len(skipped)}{lean_msg} project files got skipped: {_pp(sorted(skipped))}")

        to_deploy = deployable - skipped
        to_delete = set()
        which_files = "deployable"
        if deployed_ver and not optional_flags['ALL']:
            which_files = "new|changed|deleted"
            changed = find_git_branch_files(prj_root_path, branch_or_tag=branch_or_tag, untracked=include_untracked,
                                            skip_file_path=skip_func)
            cae.vpo(f"  --- {len(changed)} changed project files found in {branch_or_tag}: {_pp(sorted(changed))}")
            to_deploy &= changed
            to_delete = set(paths_match(changed, path_masks)) - deployable

        for pkg_file_path in sorted(to_deploy):
            src_path = os_path_join(prj_root_path, pkg_file_path)
            src_content = read_file(src_path, extra_mode='b') if os_path_isfile(src_path) else None
            dst_content = self.connection.deployed_file_content(pkg_file_path)
            if src_content == dst_content:
                dif = "is missing on both, repository and server" if src_content is None else "is identical on server"
                to_deploy.remove(pkg_file_path)
            elif src_content is None:                   # should never happen
                dif = f"need to be deleted on server (size={len(dst_content)})"
                to_delete.add(pkg_file_path)
                to_deploy.remove(pkg_file_path)
            elif dst_content is None:
                dif = f"is missing on server(size={len(src_content)})"
            else:
                dif = f"need to be upgraded on server (file size repo={len(src_content)} server={len(dst_content)})"
                if verbose:
                    dif += ":" + bytes_file_diff(dst_content, src_path, line_sep=os.linesep + " " * 6) + os.linesep
            cae.po(f"  --= {pkg_file_path: <45} {dif}")

        to_cleanup = set()
        if optional_flags['CLEANUP']:
            def _cleanup_speedup_skipper(file_path: str) -> bool:
                return skip_func(file_path) or bool(set(paths_match([file_path], DJANGO_EXCLUDED_FROM_CLEANUP)))
            to_cleanup = self.connection.deployed_code_files(['**/*'] if optional_flags['ALL'] else path_masks,
                                                             skip_file_path=_cleanup_speedup_skipper)
            cae.vpo(f"  --- {len(to_cleanup)} removable files found on {self.connection.project_name} project server:"
                    f" {_pp(sorted(to_cleanup))}")
            to_cleanup -= (deployable - skipped)
            if not to_cleanup:
                cae.po("  --- no extra files to clean up found on server")
            else:
                cae.po(f"  --- {len(to_cleanup)} deletable{lean_msg} files: {_pp(sorted(to_cleanup))}" +
                       (_hint(self.deploy_project, " to remove them from the server") if action == 'check' else ""))

        _chk_if(85, bool(to_deploy | to_delete | to_cleanup), f"no {which_files}|cleanup files found in {version_tag}"
                + _hint(func, f" specifying ALL as extra argument to {action} all deployable project files"))

        verbose = action == 'check' or verbose
        cae.po(f" ===  {len(to_deploy)} {which_files} files found to migrate server to {version_tag} version"
               f"{'; from v' + deployed_ver if deployed_ver else ''}{':' + _pp(sorted(to_deploy)) if verbose else ''}")
        cae.po(f" ===  {len(to_delete) + len(to_cleanup)} deletable (repo={len(to_delete)} cleanup={len(to_cleanup)})"
               f" files found{':' + _pp(sorted(to_delete | to_cleanup)) if verbose else ''}")

        return prj_desc, prj_root_path, to_deploy, to_delete | to_cleanup

    # ----------- remote action methods ----------------------------------------------------------------------------

    @_action(APP_PRJ, DJANGO_PRJ, arg_names=(("version-tag", ), ('LATEST', ), ('WORKTREE', ), ), flags=deploy_flags)
    def check_deploy(self, ini_pdv: PdvType, version_tag: str, **optional_flags):
        """ check all project package files at the app/web server against the specified package version.

        :param ini_pdv:         project dev vars.

        :param version_tag:     version tag in the format ``v<version-number>`` to check or ``LATEST`` to check against
                                the latest repository version or ``WORKTREE`` to check directly against
                                the local work tree (with the locally added, unstaged and changed files).

        :param optional_flags:  additional/optionally supported command line arguments:

                                * ``ALL`` is including all deployable package files, instead of only the new, changed or
                                  deleted files in the specified repository.
                                * ``CLEANUP`` is checking for deletable files on the web server/host, e.g., after
                                  they got removed from the specified repository or work tree.
                                * ``LEAN`` is reducing the deployable files sets to the minimum (using e.g., the
                                  function :func:`skip_files_lean_web`), like e.g., the gettext ``.po`` files,
                                  the ``media_ini`` root folder and the ``static`` subfolder with the initial static
                                  files of the web project.
                                * ``MASKS`` specifies a list of file paths masks/pattern to be included in the
                                  repository files to check/deploy. to include e.g., the files of the static root folder
                                  specify this argument as ``MASKS="['static/**/*']"``. single files can be included
                                  too, by adding their possible file names to the list - only the found ones will be
                                  included. for example, to include the django database, you could add some possible DB
                                  file names to the list like in ``"MASKS=['static/**/*', 'db.sqlite', 'project.db']"``

        """
        prj_desc, _, to_deploy, to_delete = self.deploy_differences(ini_pdv, 'check', version_tag, **optional_flags)

        cae.po(f" ==== found {len(to_deploy)} outdated and {len(to_delete)} deletable files on host/project {prj_desc}")

    @_action(APP_PRJ, DJANGO_PRJ, arg_names=(("version-tag", ), ('LATEST', ), ('WORKTREE', ), ), flags=deploy_flags,
             shortcut='deploy')
    def deploy_project(self, ini_pdv: PdvType, version_tag: str, **optional_flags):
        """ deploy code files of a django/app project version to the web-/app-server.

        :param ini_pdv:         project dev vars.
        :param version_tag:     version tag in the format ``v<version-number>`` to deploy or ``LATEST`` to use
                                the tag of the latest repository version or ``WORKTREE`` to deploy directly
                                from the local work tree (including locally added, unstaged and changed files).
        :param optional_flags:  optional command line arguments, documented in the :meth:`.check_deploy` action.
        """
        prj_desc, root, to_deploy, to_delete = self.deploy_differences(ini_pdv, 'deploy', version_tag, **optional_flags)

        for upg_fil in to_deploy:
            err_str = self.connection.deploy_file(upg_fil, read_file(os_path_join(root, upg_fil), extra_mode='b'))
            _chk_if(96, not err_str, err_str)

        for del_fil in to_delete:
            err_str = self.connection.delete_file_or_folder(del_fil)
            _chk_if(96, not err_str, err_str)

        if to_deploy:
            cae.po(f"  === {len(to_deploy)} files deployed: {_pp(sorted(to_deploy))}")
        if to_delete:
            cae.po(f"  === {len(to_delete)} files removed: {_pp(sorted(to_delete))}")
        if to_deploy or to_delete:
            cae.po("  === check server if Django manage migration command(s) have to be run and if a restart is needed")
        cae.po(f" ==== successfully deployed {version_tag} to host/project {prj_desc}")


# --------------- local actions ---------------------------------------------------------------------------------------


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=tuple(tuple(('source-name', 'rel-path', ) + _) for _ in ARGS_CHILDREN_DEFAULT))
def add_children_file(ini_pdv: PdvType, file_name: str, rel_path: str, *children_pdv: PdvType) -> bool:
    """ add any file to the working trees of parent/root and children/portions.

    :param ini_pdv:             parent/root project dev vars.
    :param file_name:           source (template) file name (optional with a path).
    :param rel_path:            relative destination path within the working tree.
    :param children_pdv:        project dev vars of the children to process.
    :return:                    boolean True if the file got added to the parent/root and to all children, else False.
    """
    added = []
    is_root = pdv_str(ini_pdv, 'project_type') == ROOT_PRJ
    if is_root and add_file(ini_pdv, file_name, rel_path):
        added.append(pdv_str(ini_pdv, 'project_name'))

    for chi_pdv in children_pdv:
        if add_file(chi_pdv, file_name, rel_path):
            added.append(pdv_str(chi_pdv, 'project_name'))

    cae.po(f"===== added {len(added)}/{len(children_pdv)} times {file_name} into {rel_path} for: {added}")
    return len(added) == (1 if is_root else 0) + len(children_pdv)


@_action(*ANY_PRJ_TYPE, arg_names=(('source-name', 'rel-path', ), ))
def add_file(ini_pdv: PdvType, file_name: str, rel_path: str) -> bool:
    """ add any file into the project working tree.

    :param ini_pdv:             project dev vars.
    :param file_name:           file name to add (optional with an abs. path, else relative to the working tree root).
    :param rel_path:            relative path in the destination project working tree.
    :return:                    boolean True if the file got added to the specified project, else False.
    """
    project_path = pdv_str(ini_pdv, 'project_path')
    file_name = os_path_join(project_path, file_name)
    dst_dir = os_path_join(project_path, rel_path)
    if not os_path_isfile(file_name) or not os_path_isdir(dst_dir):
        cae.dpo(f"  ### either source file {file_name} or destination folder {dst_dir} does not exist")
        return False

    if any(os_path_basename(file_name).startswith(_) for _ in TEMPLATES_FILE_NAME_PREFIXES):
        dst_files: set[str] = set()
        ret = deploy_template(file_name, rel_path, "grm.add_file", ini_pdv, dst_files=dst_files)
        if not ret or not dst_files:
            cae.dpo(f"  ### template {file_name} could not be added to {rel_path}")
            return False
        dst_file_name = dst_files.pop()

    else:
        dst_file_name = os_path_join(dst_dir, os_path_basename(file_name))
        if os_path_isfile(dst_file_name):
            cae.dpo(f"  ### destination file {dst_file_name} already exists")
            return False
        if os_path_isdir(dst_file_name):
            cae.dpo(f"  ### folder {dst_file_name} already exists, preventing writing file with same name")
            return False
        write_file(dst_file_name, read_file(file_name))

    if not os_path_isfile(dst_file_name):                   # pragma: no cover
        cae.dpo(f"  *** failure in adding the file {dst_file_name} to project {pdv_str(ini_pdv, 'project_desc')}")
        return False

    cae.po(f" ==== added {file_name} to {rel_path} in {pdv_str(ini_pdv, 'project_desc')}")
    return True


@_action(APP_PRJ, shortcut='build', flags={'LIBS': False, 'EMBED': False})
def build_gui_app(ini_pdv: PdvType, **build_flags):
    """ build gui app with buildozer, add LIBS to make a clean/full build and EMBED to include APK to share. """
    extra_args = []
    apk_ext = ".{apk_ext}"  # mask/camouflage APK extension for buildozer/P4A to embed APK

    verbose_debug = cae.verbose
    if verbose_debug or cae.get_option('verbose'):
        extra_args.append('-v')

    extra_args += ['android', 'debug']
    output: list[str] = [f" ---  buildozer arguments: {extra_args}"]    # non-empty list to keep stderr/stdout merged
    with _in_prj_dir_venv(pdv_str(ini_pdv, 'project_path')):
        if build_flags['LIBS'] and os_path_isdir('.buildozer'):
            cae.po("  --- removing local .buildozer folder")
            shutil.rmtree('.buildozer', ignore_errors=True)

        for old_apk in reversed(glob.glob(os_path_join(MOVES_SRC_FOLDER_NAME + "*", "*" + apk_ext))):
            cae.po(f"   -- removing {old_apk=} from the previous build")
            os.remove(old_apk)
            apk_dir = os_path_dirname(old_apk)
            break
        else:
            apk_dir = MOVES_SRC_FOLDER_NAME + UPDATER_ARGS_SEP + UPDATER_ARG_OS_PLATFORM + 'android'

        _cg(120, "buildozer", extra_args=extra_args, lines_output=output, exit_on_err=False)

        in_filters = ('% Loading', '% Fetch', '% Computing', '% Installing', '% Downloading', '% Unzipping',
                      'Compressing objects:', 'Counting objects:', 'Enumerating objects:', 'Finding sources:',
                      'Receiving objects:', 'Resolving deltas:')
        start_filters = ('     |', '   ━', '   ╸', '- Download ')
        strip_esc = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')  # https://stackoverflow.com/questions/75904146
        log_lines = []
        for lines in output:
            for line in lines.split('\r'):              # split %-progress lines (separated only with CR)
                sl = strip_esc.sub('', line)            # remove coloring/formatting ANSI escape sequences
                if sl and not (any(_ in sl for _ in in_filters) or any(sl.startswith(_) for _ in start_filters)):
                    log_lines.append(sl)

        log_file = 'build_log.txt'
        write_file(log_file, os.linesep.join(log_lines))

        success = log_lines[-1].endswith("available in the bin directory")
        for line_no in range(-2 if success else -201, 0):
            cae.po(" " * 6 + log_lines[line_no])

        if success and build_flags['EMBED']:
            new_apk = log_lines[-1].split(" ")[2]   # == "# APK <app_name-version>.apk available in the bin directory"
            file_name = os_path_splitext(new_apk)[0]

            os.makedirs(apk_dir, exist_ok=True)
            copy_file(os_path_join("bin", new_apk), os_path_join(apk_dir, file_name + apk_ext))
            slim_apk = os_path_join("bin", file_name + "_slim.apk")
            if os_path_isfile(slim_apk):
                os.remove(slim_apk)     # without this move_file() would fail on MSWin if slim_apk already exists
            move_file(os_path_join("bin", new_apk), slim_apk)

            cae.po(f"   == compile apk embedding APK at {datetime.datetime.now()}")

            _cg(123, "buildozer", extra_args=extra_args, exit_on_err=False)

            cae.po(f"  === embedded {slim_apk=} into APK in {apk_dir}/ at {datetime.datetime.now()}")

    cae.po(f" ==== {pdv_str(ini_pdv, 'project_desc')} {'successfully' if success else 'NOT'} built;"
           f" see {log_file} ({len(log_lines)} lines) for details{chr(7)}")


@_action(*ANY_PRJ_TYPE)
def bump_version(ini_pdv: PdvType):
    """ increment project version. """
    inc_part = cae.get_option('versionIncrementPart')
    if inc_part not in range(1, 4):
        cae.dpo(f"    = skipped bump of version (because versionIncrementPart=={inc_part})")
        return

    old_version = pdv_str(ini_pdv, 'project_version')
    new_version = increment_version(old_version, increment_part=inc_part)
    nxt_version = _git_project_version(ini_pdv, increment_part=inc_part)
    _chk_if(59, new_version == nxt_version,
            f"next/incremented package versions out of sync: new-local={new_version} next-remote={nxt_version}")

    bump_file_version(pdv_str(ini_pdv, 'version_file'), increment_part=inc_part)

    ini_pdv.update(project_dev_vars(pdv_str(ini_pdv, 'project_path')))

    cae.po(f" ==== bumped package from version {old_version} to {pdv_str(ini_pdv, 'project_version')}")


@_action(PARENT_PRJ, ROOT_PRJ)
def check_children_integrity(parent_pdv: PdvType, *children_pdv: PdvType):
    """ run integrity checks for the specified children of a parent or portions of a namespace. """
    for chi_pdv in children_pdv:
        cae.po(f"  --- {pdv_str(chi_pdv, 'project_name')} ---   {pdv_str(chi_pdv, 'project_desc')}")
        check_integrity(chi_pdv)

    cae.po(f"===== passed integrity checks of {_children_desc(parent_pdv, children_pdv)}")


@_action(*ANY_PRJ_TYPE, shortcut='check')
def check_integrity(ini_pdv: PdvType):
    """ integrity check of files/folders completeness, outsourced/template files update-state, and CI tests. """
    project_type = pdv_str(ini_pdv, 'project_type')
    if project_type in (NO_PRJ, PARENT_PRJ):
        cae.po(f" ==== no checks for {project_type or 'undefined'} project at {pdv_str(ini_pdv, 'project_path')}")
        return

    _check_folders_files_completeness(ini_pdv)
    if not on_ci_host():            # template checks don't work on GitLab/GitHub CI for aedev portions and for ROOT_PRJ
        _check_templates(ini_pdv)   # packages (because find_extra_modules() can't find e.g. enaml_app.functions)
    _check_resources(ini_pdv)
    _check_types_linting_tests(ini_pdv)
    cae.po(f" ==== passed integrity checks for {pdv_str(ini_pdv, 'project_desc')}")


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=(('package-versions' + ARG_MULTIPLES,),), pre_action=_check_children_not_exist)
def clone_children(parent_or_root_pdv: PdvType, *project_versions: str) -> list[str]:
    """ clone specified namespace-portion/parent-child repos to the local machine.

    :param parent_or_root_pdv:  vars of the parent/namespace-root project.
    :param project_versions:    package/project names with an optional version of the children to be cloned.
    :return:                    project paths list of the cloned children projects (for unit testing).
    """
    # _chk_if(15, not cae.get_option('project') and not cae.get_option('path'),
    #         "--project and --path options cannot be used with the 'clone_children' action")
    _children_path_package_option_reset()

    project_paths = []
    for pkg_version in project_versions:
        project_paths.append(clone_project(parent_or_root_pdv, pkg_version))

    cae.po(f"===== {len(project_versions)} projects cloned: {project_versions}")
    return project_paths


@_action(ROOT_PRJ, PARENT_PRJ, arg_names=(("--project", ), ("--path", ), ("package-name", ), ("portion-name", )),
         pre_action=_check_children_not_exist, shortcut='clone')
def clone_project(ini_pdv: PdvType, package_or_portion: str = "") -> str:
    """ clone remote repo to the local machine.

    :param ini_pdv:             vars of the project to clone.
    :param package_or_portion:  name of the package/portion to clone, optionally with a version number.
    :return:                    project path of the cloned project (used for unit tests).
    """
    parent_path, pkg_and_ver = _get_parent_packageversion(ini_pdv, package_or_portion)

    domain = _get_host_domain(ini_pdv)
    repo_root = f"{pdv_str(ini_pdv, 'REPO_HOST_PROTOCOL')}{domain}/{_get_host_group(ini_pdv, domain)}"
    project_name, *ver = pkg_and_ver.split(PROJECT_VERSION_SEP)
    req_branch = cae.get_option('branch')
    branch_or_version = f'v{ver[0]}' if ver else req_branch
    project_path = _git_clone(repo_root, project_name, branch_or_tag=branch_or_version, parent_path=parent_path)
    if project_path and ver and req_branch:
        _git_checkout(project_dev_vars(project_path=project_path), branch=req_branch)
        pkg_and_ver += f" (branch: {req_branch})"

    cae.po(f" ==== cloned project {pkg_and_ver} from {repo_root} into project path {project_path}")

    return project_path


@_action(PARENT_PRJ, ROOT_PRJ, pre_action=check_children_integrity)
def commit_children(ini_pdv: PdvType, *children_pdv: PdvType):
    """ commit changes to children of a namespace/parent using the individually prepared commit message files. """
    for chi_pdv in children_pdv:
        cae.po(f" ---  {pdv_str(chi_pdv, 'project_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
        commit_project(chi_pdv)
    cae.po(f"===== committed {_children_desc(ini_pdv, children_pdv)}")


@_action(*ANY_PRJ_TYPE, pre_action=check_integrity, shortcut='commit')
def commit_project(ini_pdv: PdvType):
    """ commit changes of a single project to the local repo using the prepared commit message file. """
    _update_frozen_req_files(ini_pdv)
    _git_add(ini_pdv)
    _git_commit(ini_pdv)

    cae.po(f" ==== committed {pdv_str(ini_pdv, 'project_name')}")


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=tuple(tuple(('file-or-folder-name', ) + _) for _ in ARGS_CHILDREN_DEFAULT))
def delete_children_file(ini_pdv: PdvType, file_name: str, *children_pdv: PdvType) -> bool:
    """ delete a file or an empty folder from parent/root and children/portions working trees.

    :param ini_pdv:             parent/root project dev vars.
    :param file_name:           file/folder name to delete (optional with a path, relative to the working tree root).
    :param children_pdv:        tuple of children project dev vars.
    :return:                    boolean True if the file got found and deleted from the parent and all the children
                                projects, else False.
    """
    c_del = []
    is_root = pdv_str(ini_pdv, 'project_type') == ROOT_PRJ
    if is_root and delete_file(ini_pdv, file_name):
        c_del.append(ini_pdv)

    for chi_pdv in children_pdv:
        if delete_file(chi_pdv, file_name):
            c_del.append(chi_pdv)

    cae.po(f"===== deleted {file_name} in {_children_desc(ini_pdv, children_pdv=c_del)}")
    return len(c_del) == (1 if is_root else 0) + len(children_pdv)


@_action(*ANY_PRJ_TYPE, arg_names=(('file-or-folder-name', ), ))
def delete_file(ini_pdv: PdvType, file_or_dir: str) -> bool:
    """ delete a file or an empty folder from the project working tree.

    :param ini_pdv:             project dev vars.
    :param file_or_dir:         file/folder name to delete (optional with a path, relative to the working tree root).
    :return:                    boolean True if the file got found and deleted from the specified project, else False.
    """
    # git is too picky - does not allow deleting unstaged/changed files
    # project_path = pdv_str(ini_pdv, 'project_path')
    # with _in_prj_dir_venv(project_path):
    #     return _cl(89, f"git rm -f {os_path_relpath(file_or_dir, project_path)}", exit_on_err=False) == 0
    file_or_dir = os_path_join(pdv_str(ini_pdv, 'project_path'), file_or_dir)   # prj path ignored if file_or_dir is abs
    is_dir = os_path_isdir(file_or_dir)
    if not is_dir and not os_path_isfile(file_or_dir):
        cae.po(f"  *** {file_or_dir} to delete does not exist in {pdv_str(ini_pdv, 'project_desc')}")
        return False

    if is_dir:
        os.rmdir(file_or_dir)
    else:
        os.remove(file_or_dir)

    if os_path_isdir(file_or_dir) if is_dir else os_path_isfile(file_or_dir):               # pragma: no cover
        cae.po(f"  *** error deleting {file_or_dir} from {pdv_str(ini_pdv, 'project_desc')}")
        return False

    cae.po(f" ==== deleted {'folder' if is_dir else 'file'} {file_or_dir} in {pdv_str(ini_pdv, 'project_desc')}")
    return True


@_action(PARENT_PRJ, ROOT_PRJ)
def install_children_editable(ini_pdv: PdvType, *children_pdv: PdvType):
    """ install parent children or namespace portions as editable on the local machine. """
    for chi_pdv in children_pdv:
        install_editable(chi_pdv)
    cae.po(f"===== installed as editable {_children_desc(ini_pdv, children_pdv)}")


@_action(*ANY_PRJ_TYPE, shortcut='editable')
def install_editable(ini_pdv: PdvType):
    """ install a project as editable from the source/project root folder. """
    project_path = pdv_str(ini_pdv, 'project_path')
    _cl(90, f"{CMD_INSTALL} -e {project_path}", exit_msg=f"installation from local portions path {project_path} failed")
    cae.po(f" ==== installed as editable: {pdv_str(ini_pdv, 'project_desc')}")


@_action()
def new_app(ini_pdv: PdvType) -> PdvType:
    """ create or complete/renew a gui app project. """
    return _renew_project(ini_pdv, APP_PRJ)


@_action(PARENT_PRJ, ROOT_PRJ)
def new_children(ini_pdv: PdvType, *children_pdv: PdvType) -> list[PdvType]:
    """ initialize or renew parent folder children or namespace portions. """
    _children_path_package_option_reset()
    new_vars = []
    for chi_pdv in children_pdv:
        cae.po(f" ---  {pdv_str(chi_pdv, 'project_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
        new_vars.append(new_project(chi_pdv))
    cae.po(f"===== renewed {_children_desc(ini_pdv, children_pdv=new_vars)}")
    return new_vars


@_action()
def new_django(ini_pdv: PdvType) -> PdvType:
    """ create or complete/renew a django project. """
    return _renew_project(ini_pdv, DJANGO_PRJ)


@_action()
def new_module(ini_pdv: PdvType) -> PdvType:
    """ create or complete/renew a module project. """
    return _renew_project(ini_pdv, MODULE_PRJ)


@_action()
def new_namespace_root(ini_pdv: PdvType) -> PdvType:
    """ create or complete/renew a namespace root package. """
    return _renew_project(ini_pdv, ROOT_PRJ)


@_action()
def new_package(ini_pdv: PdvType) -> PdvType:
    """ create or complete/renew a package project. """
    return _renew_project(ini_pdv, PACKAGE_PRJ)


@_action()
def new_playground(ini_pdv: PdvType) -> PdvType:
    """ create or complete/renew a playground project. """
    return _renew_project(ini_pdv, PLAYGROUND_PRJ)


@_action(shortcut='renew')
def new_project(ini_pdv: PdvType) -> PdvType:
    """ complete/renew an existing project. """
    return _renew_project(ini_pdv, pdv_str(ini_pdv, 'project_type'))


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=tuple(tuple(('commit-message-title', ) + _) for _ in ARGS_CHILDREN_DEFAULT))
def prepare_children_commit(ini_pdv: PdvType, title: str, *children_pdv: PdvType):
    """ run code checks and prepare/overwrite the commit message file for a bulk-commit of children projects.

    :param ini_pdv:             parent/root project dev vars.
    :param title:               optional commit message title.
    :param children_pdv:        project dev var args tuple of the children to process.
    """
    for chi_pdv in children_pdv:
        cae.po(f" ---  {pdv_str(chi_pdv, 'project_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
        prepare_commit(chi_pdv, title=title)
    cae.po(f"===== prepared commit of {_children_desc(ini_pdv, children_pdv)}")


@_action(*ANY_PRJ_TYPE, arg_names=((), ('commit-message-title', ), ), shortcut='prepare')
def prepare_commit(ini_pdv: PdvType, title: str = ""):
    """ run code checks and prepare/overwrite the commit message file for the commit of a single project/package.

    :param ini_pdv:             project dev vars.
    :param title:               optional commit message title.
    """
    _update_frozen_req_files(ini_pdv)
    _git_add(ini_pdv)
    _write_commit_message(ini_pdv, title=title)
    cae.po(f" ==== prepared commit of {pdv_str(ini_pdv, 'project_desc')}")


@_action(PARENT_PRJ, ROOT_PRJ)
def refresh_children_outsourced(ini_pdv: PdvType, *children_pdv: PdvType):
    """ refresh outsourced files from templates in namespace/project-parent children projects. """
    for chi_pdv in children_pdv:
        cae.po(f" ---  {pdv_str(chi_pdv, 'project_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
        refresh_outsourced(chi_pdv)
    cae.po(f"===== refreshed {_children_desc(ini_pdv, children_pdv)}")


@_action(*ANY_PRJ_TYPE, shortcut='refresh')
def refresh_outsourced(ini_pdv: PdvType):
    """ refresh/renew all the outsourced files in the specified project. """
    project_path = pdv_str(ini_pdv, 'project_path')

    with _in_prj_dir_venv(project_path):
        dst_files = refresh_templates(ini_pdv, logger=cae.po if cae.get_option('verbose') else cae.vpo)

    dbg_msg = ": " + " ".join(os_path_relpath(_, project_path) for _ in dst_files) if _debug_or_verbose() else ""
    cae.po(f" ==== refreshed {len(dst_files)} outsourced files in {pdv_str(ini_pdv, 'project_desc')}{dbg_msg}")


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=tuple(tuple(('old-name', 'new-name', ) + _) for _ in ARGS_CHILDREN_DEFAULT))
def rename_children_file(ini_pdv: PdvType, old_file_name: str, new_file_name: str, *children_pdv: PdvType) -> bool:
    """ rename a file or folder in parent/root and children/portions working trees.

    :param ini_pdv:             parent/root project dev vars.
    :param old_file_name:       file/folder name to rename (optional with a path, relative to the working tree root).
    :param new_file_name:       new name of file/folder (optional with a path, relative to the working tree root).
    :param children_pdv:        project dev vars tuple of the children to process.
    :return:                    boolean True if the file got renamed in the parent and all the children projects,
                                else False.
    """
    ren = []
    if pdv_str(ini_pdv, 'project_type') == ROOT_PRJ and rename_file(ini_pdv, old_file_name, new_file_name):
        ren.append(pdv_str(ini_pdv, 'project_name'))

    for chi_pdv in children_pdv:
        if rename_file(chi_pdv, old_file_name, new_file_name):
            ren.append(pdv_str(chi_pdv, 'project_name'))

    cae.po(f"===== renamed {len(ren)}/{len(children_pdv) + 1} times {old_file_name} to {new_file_name} in: {ren}")
    return len(ren) == 1 + len(children_pdv)


@_action(*ANY_PRJ_TYPE, arg_names=(('old-file-or-folder-name', 'new-file-or-folder-name', ), ))
def rename_file(ini_pdv: PdvType, old_file_name: str, new_file_name: str) -> bool:
    """ rename a file or folder in the project working tree.

    :param ini_pdv:             project dev vars.
    :param old_file_name:       source file/folder (optional with a path, absolute or relative to the working tree).
    :param new_file_name:       destination file/folder (optional path, absolute or relative to the working tree).
    :return:                    boolean True if the file/folder got renamed, else False.
    """
    old_file_name = os_path_join(pdv_str(ini_pdv, 'project_path'), old_file_name)   # prj path ignored if absolute
    new_file_name = os_path_join(pdv_str(ini_pdv, 'project_path'), new_file_name)
    if not os.path.exists(old_file_name) or os.path.exists(new_file_name):
        cae.po(f"  ### either source file {old_file_name} not found or destination {new_file_name} already exists")
        return False

    os.rename(old_file_name, new_file_name)     # using os.remove because git mv is too picky

    if os.path.exists(old_file_name) or not os.path.exists(new_file_name):              # pragma: no cover
        cae.po(f"  *** rename of {old_file_name} to {new_file_name} failed: old-exists={os.path.exists(old_file_name)}")
        return False

    cae.po(f" ==== renamed file {old_file_name} to {new_file_name} in {pdv_str(ini_pdv, 'project_desc')}")
    return True


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=tuple(tuple(('command', ) + _) for _ in ARGS_CHILDREN_DEFAULT), shortcut='run')
def run_children_command(ini_pdv: PdvType, command: str, *children_pdv: PdvType):
    """ run console command for the specified portions/children of a namespace/parent.

    :param ini_pdv:             parent/root project dev vars.
    :param command:             console command string (including all command arguments).
    :param children_pdv:        tuple of children project dev vars.
    """
    for chi_pdv in children_pdv:
        cae.po(f"---   {pdv_str(chi_pdv, 'project_name')}   ---   {pdv_str(chi_pdv, 'project_desc')}")

        output: list[str] = []
        with _in_prj_dir_venv(pdv_str(chi_pdv, 'project_path')):
            _cl(98, command, lines_output=output, exit_on_err=not cae.get_option('force'))
        cae.po(_pp(output)[1:])

        if chi_pdv != children_pdv[-1]:
            _wait()

    cae.po(f"===== run command '{command}' for {_children_desc(ini_pdv, children_pdv)}")


@_action(local_action=False, shortcut='actions')    # local_action=False sets host_api to display remote actions
def show_actions(ini_pdv: PdvType):
    """ get available/registered/implemented actions info of the specified/current project and remote. """
    compact = not cae.get_option('verbose')
    host_domain = _get_host_domain(ini_pdv)
    sep = os.linesep
    ind = " " * 9

    actions = sorted(_available_actions())
    if compact:
        cae.po(f"  --- available actions (locally and on {host_domain}, add --verbose to see other host actions):")
        for act in actions:
            act_fun = _act_callable(ini_pdv, act)
            if callable(act_fun):
                cae.po(f"    - {act_fun.__name__ : <30} {(act_fun.__doc__ or '').split(sep)[0]}")
    else:
        cae.po(f"  --- all registered actions (locally and at {'|'.join(REGISTERED_HOSTS_CLASS_NAMES)}):")

        def _act_print(act_reg_key: str):
            spe = REGISTERED_ACTIONS[act_reg_key]
            cae.po(f"{ind}{act_reg_key}==" + (sep + ind).join(_ for _ in spe['docstring'].split(sep)))
            if 'arg_names' in spe or 'flags' in spe:
                cae.po(f"{ind}args/flags: {_expected_args(spe)}")
            cae.po(f"{ind}project types: {', '.join(spe['project_types'])}")
            if 'shortcut' in spe:
                cae.po(f"{ind}shortcut: {spe['shortcut']}")

        for act in actions:
            cae.po(f"    - {act} -------------------------------------------------------------------")
            for name in [act] + [_ + "." + act for _ in REGISTERED_HOSTS_CLASS_NAMES.values()]:
                if name in REGISTERED_ACTIONS:
                    _act_print(name)

    if other_host_actions := ', '.join(_ for _ in actions if not _act_callable(ini_pdv, _)):
        cae.po(f"  --- actions registered but not available on {host_domain}:")
        cae.po(f"      {other_host_actions}")

    cae.po(f"===== actions available for {pdv_str(ini_pdv, 'project_desc')}")


@_action(PARENT_PRJ, ROOT_PRJ)
def show_children_status(ini_pdv: PdvType, *children_pdv: PdvType):
    """ run integrity checks for the specified portions/children of a namespace/parent. """
    for chi_pdv in children_pdv:
        show_status(chi_pdv)
    cae.po(f"===== status shown of {_children_desc(ini_pdv, children_pdv)}")


@_action(PARENT_PRJ, ROOT_PRJ)
def show_children_versions(ini_pdv: PdvType, *children_pdv: PdvType):
    """ show package versions (local, remote and on pypi) for the specified children of a namespace/parent. """
    for chi_pdv in children_pdv:
        show_versions(chi_pdv)
    cae.po(f"===== versions shown of {_children_desc(ini_pdv, children_pdv)}")


@_action(PARENT_PRJ, *ANY_PRJ_TYPE, shortcut='status')
def show_status(ini_pdv: PdvType):
    """ show git status of the specified/current project and remote. """
    cae.po(f" ---- {pdv_str(ini_pdv, 'project_name')} ---- {pdv_str(ini_pdv, 'project_desc')}")
    verbose = _debug_or_verbose()

    if verbose:
        cae.po("  --- project vars:")
        _print_pdv(ini_pdv)

    project_type = pdv_str(ini_pdv, 'project_type')

    if verbose and project_type in (PARENT_PRJ, ROOT_PRJ):
        presets = _init_children_presets(pdv_val(ini_pdv, 'children_project_vars'))
        cae.po(f"  --- {len(presets)} children presets: ")
        nsp_len = len(pdv_str(ini_pdv, 'namespace_name'))
        if nsp_len:
            nsp_len += 1
        for preset, dep_packages in presets.items():
            cae.po(f"      {preset: <9} == {', '.join(pkg[nsp_len:] for pkg in sorted(dep_packages))}")

    if project_type not in (NO_PRJ, PARENT_PRJ):
        project_path = pdv_str(ini_pdv, 'project_path')

        cur_branch = _git_current_branch(ini_pdv)
        if cur_branch != MAIN_BRANCH:
            cae.po(f"   -- current working branch of project at '{project_path}' is '{cur_branch}'")
            output = _git_diff(ini_pdv, MAIN_BRANCH)
            if output or verbose:
                cae.po(f"  --- git diff {cur_branch} against {MAIN_BRANCH} branch:{_pp(output)}")

        output = _git_diff(ini_pdv)
        if output or verbose:
            cae.po(f"  --- git diff - to be staged/added:{_pp(output)}")

        output = _git_diff(ini_pdv, MAIN_BRANCH, f'origin/{MAIN_BRANCH}')
        if output or verbose:
            cae.po(f"  --- git diff {MAIN_BRANCH} origin/{MAIN_BRANCH} ('grm update' to update branch):{_pp(output)}")

        if verbose:
            cae.po(f"   -- git status:{_pp(_git_status(ini_pdv))}")
            cae.po(f"   -- branches:{_pp(_git_branches(ini_pdv))}")
            cae.po(f"   -- remotes:{_pp(f'{name}={url}' for name, url in _git_remotes(ini_pdv).items())}")

        changed = _git_uncommitted(ini_pdv)
        if changed:
            cae.po(f" ---- '{project_path}' has {len(changed)} uncommitted files: {changed}")
    cae.po(f" ==== status shown of {pdv_str(ini_pdv, 'project_desc')}")


@_action(shortcut='versions')
def show_versions(ini_pdv: PdvType):
    """ display package versions of worktree, remote/origin repo, latest PyPI release and default app/web host. """
    _git_fetch(ini_pdv)
    project_name = pdv_str(ini_pdv, 'project_name')
    msg = f" ==== {project_name: <27}"
    msg += f" local:{pdv_str(ini_pdv, 'project_version'): <9}"
    msg += f" origin:{_git_tag_list(ini_pdv)[-1][1:]: <9}"

    pip_name = pdv_str(ini_pdv, 'pip_name')
    if pip_name:
        msg += f" pypi:{pypi_versions(pip_name)[-1]: <9}"

    if pdv_str(ini_pdv, 'project_type') == DJANGO_PRJ:
        web_domain = pdv_str(ini_pdv, 'web_domain')
        web_user = pdv_str(ini_pdv, 'web_user')
        if 'pythonanywhere.com' in web_domain and web_user:     # only if a default web host is defined in pev.defaults
            web_token = _get_host_user_token(web_domain, host_user=web_user, name_prefix='web')
            connection = PythonanywhereApi(web_domain, web_user, web_token, project_name)
            msg += f" web:{connection.deployed_version(): <9}"

    cae.po(msg)


@_action(PARENT_PRJ, ROOT_PRJ)
def update_children(ini_pdv: PdvType, *children_pdv: PdvType):
    """ fetch and rebase the MAIN_BRANCH to the local children repos of the parent/namespace-root(also updated). """
    for chi_pdv in children_pdv:
        update_project(chi_pdv)
    cae.po(f"===== updated {_children_desc(ini_pdv, children_pdv)}")


@_action(*ANY_PRJ_TYPE, shortcut='update')
def update_project(ini_pdv: PdvType) -> list[str]:
    """ fetch and rebase the MAIN_BRANCH of the specified project in the local repo. """
    with _in_prj_dir_venv(pdv_str(ini_pdv, 'project_path')):
        sh_err = _cl(58, f"git branch --set-upstream-to origin/{MAIN_BRANCH} {MAIN_BRANCH}", exit_on_err=False)
        if sh_err and _debug_or_verbose():
            cae.po(f"    # ignoring error {sh_err} renewing tracking of main branch {MAIN_BRANCH}")

    errors = _git_fetch(ini_pdv)
    if errors and _debug_or_verbose():
        cae.po(f" #### update_project cannot update local branch because of 'git fetch' errors:{_pp(errors)}")
    else:
        _git_fetch(ini_pdv, ".", f"origin/{MAIN_BRANCH}:{MAIN_BRANCH}")

    cae.po(f" ==== updated {pdv_str(ini_pdv, 'project_desc')}")
    return errors


# ----------------------- main ----------------------------------------------------------------------------------------


def prepare_and_run_main():                                                                # pragma: no cover
    """ prepare and run app """
    cae.add_argument('action', help="action to execute (run `grm -v show_actions` to display all available actions)")
    cae.add_argument('arguments',
                     help="additional arguments and optional flags, depending on specified action, e.g. all children"
                          " actions expecting either a list of package/portion names or an expression using one of the"
                          " preset children sets like all|editable|modified|develop|filterBranch|filterExpression",
                     nargs='*')
    cae.add_option('branch', "branch or version-tag to checkout/filter-/work-on", "")
    cae.add_option('delay', "seconds to pause, e.g. between sub-actions of a children-bulk-action", 12, short_opt='w')
    cae.add_option('domain', "web|repository domain (e.g. pythonanywhere.com|github.com|...)", None)
    cae.add_option('force', "force execution of action, ignoring minor errors", UNSET)
    cae.add_option('filterExpression', "Python expression evaluated against each children project, to be used as"
                                       " 'filterExpression' children-set-expression argument", "", short_opt='F')
    cae.add_option('filterBranch', "branch name matching the children current branch, to be used as"
                                   " 'filterBranch' children-set-expression argument", "", short_opt='B')
    cae.add_option('group', "user group name of a project repository at the remote host", None)
    cae.add_option('namespace', "namespace name for new namespace root or portion (module/package) project", "")
    cae.add_option('path', "project directory of a new (namespace) package (default=current working directory)", "")
    cae.add_option('project', "project package or portion name", "", short_opt='P')
    cae.add_option('token', "user credential access token to connect to remote repository|web host", None)
    cae.add_option('user', "remote repository|web host user name (e.g. for web-deploy/repo-fork/...)", None)
    cae.add_option('verbose', "verbose console output", UNSET)
    cae.add_option('versionIncrementPart', "project version number part to increment (0=disable, 1...3=mayor...patch)",
                   3, short_opt='i', choices=range(4))
    for import_name in TPL_PACKAGES:
        cae.add_option(_template_version_option(import_name),
                       f"branch/version-tag of {import_name} template package (default=latest version)",
                       "",
                       short_opt=UNSET)
    cae.run_app()                                           # parse command line arguments

    ini_pdv, act_name, act_args, act_flags = _init_act_exec_args()      # init globals, check action, compile args
    _act_callable(ini_pdv, act_name)(ini_pdv, *act_args, **act_flags)   # execute action

    global TEMP_CONTEXT                                                             # pylint: disable=global-statement
    if TEMP_CONTEXT:
        TEMP_CONTEXT.cleanup()
        TEMP_CONTEXT = None


def main():                                                                                 # pragma: no cover
    """ main app script """
    try:
        prepare_and_run_main()
    except Exception as main_ex:                                    # pylint: disable=broad-exception-caught
        debug_info = f":{os.linesep}{format_exc()}" if _debug_or_verbose() else ""
        _exit_error(99, f"unexpected exception {main_ex} raised{debug_info}")


if __name__ == '__main__':                                                                  # pragma: no cover
    main()
