""" unit tests for the aedev.git_repo_manager.__main__ portion. """
import contextlib
import os
import pytest
import shutil
import sys
import tempfile

from collections import OrderedDict
from conftest import skip_gitlab_ci
from unittest.mock import PropertyMock, patch

from ae.base import (
    BUILD_CONFIG_FILE, DOCS_FOLDER, PY_CACHE_FOLDER, PY_EXT, PY_INIT, PY_MAIN, TEMPLATES_FOLDER, TESTS_FOLDER,
    load_dotenvs, norm_name, norm_path, project_main_file, read_file, write_file)
from ae.paths import path_items
from aedev.setup_project import (
    APP_PRJ, DJANGO_PRJ, MODULE_PRJ, NO_PRJ, PACKAGE_PRJ, PARENT_FOLDERS, PARENT_PRJ, PLAYGROUND_PRJ,
    REQ_DEV_FILE_NAME, ROOT_PRJ, code_file_version)

import aedev.git_repo_manager.__main__ as git_repo_manager_main
from aedev.git_repo_manager import __version__ as grm_version
# noinspection PyProtectedMember
from aedev.git_repo_manager.__main__ import (
    ANY_PRJ_TYPE, ARG_ALL, COMMIT_MSG_FILE_NAME, GIT_FOLDER_NAME, NULL_VERSION, LOCK_EXT, MAIN_BRANCH,
    OUTSOURCED_FILE_NAME_PREFIX, OUTSOURCED_MARKER, PROJECT_VERSION_SEP, REGISTERED_ACTIONS,
    REGISTERED_TPL_PROJECTS, REGISTERED_HOSTS_CLASS_NAMES, SKIP_PRJ_TYPE_FILE_NAME_PREFIX,
    TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID, TEMPLATE_PLACEHOLDER_ARGS_SUFFIX, TEMPLATE_PLACEHOLDER_ID_PREFIX,
    TEMPLATE_PLACEHOLDER_ID_SUFFIX, TPL_FILE_NAME_PREFIX, TPL_IMPORT_NAME_PREFIX, TPL_PACKAGES, TPL_STOP_CNV_PREFIX,
    GitlabCom, PdvType, cae,
    _act_callable, _action, _available_actions, _cl, _cg, _debug_or_verbose, _exit_error, _expected_args,
    _get_branch, _get_host_user_name, _get_host_user_token,
    _git_add, _git_checkout, _git_clone, _git_commit, _git_current_branch, _git_diff, _git_init_if_needed,
    _git_project_version, _git_status, _git_uncommitted, _in_prj_dir_venv,
    _init_act_args_check, _init_act_exec_args, _init_children_pdv_args, _init_children_presets,
    _patch_outsourced, _print_pdv, _renew_prj_dir, _renew_project,
    _template_projects, _register_template, _template_version_option, _wait,
    activate_venv, active_venv, bump_file_version, deploy_template, editable_project_path,
    find_extra_modules, find_project_files, find_git_branch_files, increment_version,
    in_venv, main_file_path, project_version, patch_string, pdv_str, project_dev_vars,
    pypi_versions, refresh_templates, replace_file_version, replace_with_file_content_or_default,
    root_packages_masks, skip_files_lean_web, skip_files_migrations, venv_bin_path,
    add_children_file, bump_version, check_children_integrity, check_integrity, clone_children, clone_project,
    commit_children, commit_project, delete_children_file, install_children_editable, install_editable,
    new_app, new_children, new_django, new_module, new_namespace_root, new_package, new_playground, new_project,
    on_ci_host, prepare_children_commit, prepare_commit, refresh_children_outsourced, rename_children_file,
    run_children_command, show_actions, show_children_status, show_children_versions, show_status, update_children,
)


tst_ns_name = 'nsn'
tst_ns_por_name = 'tst_por'
tst_pkg_name = tst_ns_name + '_' + tst_ns_por_name
tst_root_name = tst_ns_name + '_' + tst_ns_name
tst_namespaces_roots = ['aedev.aedev', tst_ns_name + '.' + tst_ns_name]

LOCAL_VENV = 'ae39'     # optional local virtual pyenv to test *venv*-functions completely


@contextlib.contextmanager
def _init_parent():
    with tempfile.TemporaryDirectory() as temp_path:
        yield os.path.join(temp_path, PARENT_FOLDERS[0])


@contextlib.contextmanager
def _init_repo(pkg_name: str = ""):
    with _init_parent() as parent_path:
        project_path = os.path.join(parent_path, pkg_name or tst_pkg_name)
        write_file(os.path.join(project_path, ".gitignore"), read_file(".gitignore"), make_dirs=True)
        with _in_prj_dir_venv(project_path):
            _cl(963, "git init", exit_on_err=False)  # exit_on_err=False needed to prevent get_option call from _chk_if
            _cl(963, "git config", extra_args=("user.email", "test@test.tst"), exit_on_err=False)
            _cl(963, "git config", extra_args=("user.name", "TestUserName"), exit_on_err=False)
            _cl(963, "git checkout", extra_args=("-b", MAIN_BRANCH))
            _cl(963, "git commit", extra_args=("-v", "--allow-empty", "-m", "unit tst repo init"))
        yield project_path


@pytest.fixture
def changed_repo_path():
    """ provide a git repository with uncommitted changes, yielding the project's temporary working tree root path. """
    with _init_repo() as project_path:
        with _in_prj_dir_venv(project_path):
            write_file(os.path.join(project_path, 'delete.txt'), "--will be deleted")
            write_file(os.path.join(project_path, 'changed.py'), "# will be changed")
            _cl(969, "git add", extra_args=["-A"], exit_on_err=False)
            _cl(969, "git commit", extra_args=["-m", "git commit message"], exit_on_err=False)

            write_file(os.path.join(project_path, 'added.cfg'), "# added/staged to repo")
            os.remove(os.path.join(project_path, 'delete.txt'))
            write_file(os.path.join(project_path, 'changed.py'), "# got changed")

        yield project_path


@pytest.fixture
def empty_repo_path():
    """ provide an empty git repository, yielding the path of the project's temporary working tree root. """
    with _init_repo() as project_path:
        yield project_path


@pytest.fixture
def gitlab_remote(mocked_app_options):
    """ provide a connected Gitlab remote repository api. """
    repo_domain = "gitlab.com"
    mocked_app_options['group'] = "aedev-group"
    mocked_app_options['namespace'] = ""
    mocked_app_options['project'] = "aedev_git_repo_manager"
    load_dotenvs()  # pytest resets os.environ in each test run, reverting values set by load_dotenvs in __main__.py
    mocked_app_options['token'] = repo_token = cae.get_variable(f'repo_token_at_{norm_name(repo_domain)}')

    remote_project = GitlabCom()
    # remote_project.connect(project_dev_vars(), cae.get_variable('repo_token'))
    remote_project.connect({'REPO_HOST_PROTOCOL': "https://",
                            'repo_domain': repo_domain,
                            'repo_token': repo_token})

    yield remote_project


@pytest.fixture
def mocked_app_options():
    """ prevent argument parsing, e.g., via cae.get_option('domain') called by _get_host_domain(). """
    ori_get_arg = cae.get_argument
    ori_get_opt = cae.get_option
    ori_set_opt = cae.set_option

    mocked_options = {_template_version_option(import_name): "" for import_name in tst_namespaces_roots + TPL_PACKAGES}

    cae.get_argument = cae.get_option = lambda opt: mocked_options.get(opt, f"{opt}_mocked_app_option_value")
    cae.set_option = lambda opt, val, save_to_config = True: mocked_options.__setitem__(opt, val)

    yield mocked_options

    cae.get_argument = ori_get_arg
    cae.get_option = ori_get_opt
    cae.set_option = ori_set_opt


@pytest.fixture
def module_repo_path():
    """ minimal/empty test namespace module project. """
    with _init_repo() as project_path:
        with _in_prj_dir_venv(project_path):
            write_file(os.path.join(tst_ns_name, tst_ns_por_name + PY_EXT),
                       f"\"\"\" {tst_ns_name} namespace module portion tst docstr \"\"\"{os.linesep}{os.linesep}"
                       f"__version__ = '33.6.969'{os.linesep}", 
                       make_dirs=True)
        yield project_path


@pytest.fixture
def patched_exit_call_wrapper():
    """ count _exit_error() calls and ensure return of function to be tested. """
    exit_called = 0

    class _ExitCaller(Exception):
        """ exception to recognize and simulate app exit for function to be tested. """

    def _exit_(*_args, **_kwargs):
        nonlocal exit_called
        exit_called += 1
        raise _ExitCaller

    def _call_wrapper(fun, *args, **kwargs):
        try:
            ret = fun(*args, **kwargs)
        except _ExitCaller:
            ret = None
        return ret

    # noinspection PyProtectedMember
    ori_fun = git_repo_manager_main._exit_error
    git_repo_manager_main._exit_error = _exit_

    yield _call_wrapper

    # noinspection PyProtectedMember
    git_repo_manager_main._exit_error = ori_fun
    assert exit_called


@pytest.fixture
def root_repo_path():
    """ minimal/empty test namespace root project. """
    with _init_repo(tst_root_name) as project_path:
        with _in_prj_dir_venv(project_path):
            write_file(os.path.join(tst_ns_name, tst_ns_name, PY_INIT),
                       f"\"\"\" {tst_ns_name} namespace root docstr \"\"\"{os.linesep}{os.linesep}"
                       f"__version__ = '333.69.96'{os.linesep}", 
                       make_dirs=True)
        yield project_path


def setup_module():
    """ clone template projects to speedup tests, printing warning messages if the tested module is not set up. """
    print(f"##### setup_module BEG {__file__} - registered template projects={REGISTERED_TPL_PROJECTS}")

    ori_get_opt = cae.get_option
    cae.get_option = lambda _opt: ""
    for import_name in tst_namespaces_roots + TPL_PACKAGES:
        tpl_prj = _register_template(import_name, [], True, [])
        print(f"    ->{tpl_prj}")
    cae.get_option = ori_get_opt

    print(f"##### setup_module END {__file__} - registered template projects={REGISTERED_TPL_PROJECTS}")


def teardown_module():
    """ check if the tested module is still set up correctly at the end of this test module. """
    print(f"##### teardown_module {__file__} - registered template projects={REGISTERED_TPL_PROJECTS}")


def test_module_setup_init_of_constants():
    assert REGISTERED_ACTIONS
    assert REGISTERED_HOSTS_CLASS_NAMES
    assert TPL_PACKAGES
    assert len(tst_namespaces_roots) + len(TPL_PACKAGES) == len(REGISTERED_TPL_PROJECTS)


@skip_gitlab_ci  # skip on gitlab because of a missing remote repository user account token
class TestGitlabActions:
    def test_clean_releases(self, gitlab_remote, mocked_app_options, module_repo_path):
        mocked_app_options['domain'] = 'gitlab.com'
        mocked_app_options['path'] = module_repo_path
        mocked_app_options['token'] = cae.get_variable('token')
        mocked_app_options['verbose'] = True
        gitlab_remote.clean_releases(project_dev_vars(project_path=module_repo_path))

    def test_show_repo(self, capsys, gitlab_remote, mocked_app_options):
        mocked_app_options['domain'] = None
        gitlab_remote.show_repo(project_dev_vars())
        output = capsys.readouterr().out
        assert "default_branch = develop" in output
        assert "name = aedev_git_repo_manager" in output
        assert "visibility = public" in output


class TestLocalActions:
    def test_add_children_file(self, empty_repo_path, mocked_app_options, module_repo_path):
        mocked_app_options['namespace'] = ""
        mocked_app_options['path'] = module_repo_path
        mocked_app_options['verbose'] = True
        mocked_app_options[_template_version_option(tst_ns_name + '.' + tst_ns_name)] = ""
        file_name = "add_tst_file.abc"
        file_content = "file content"
        file_src_path = os.path.join(module_repo_path, file_name)
        write_file(file_src_path, file_content)
        file_dst_path = os.path.join(module_repo_path, tst_ns_name, file_name)
        tpl_name = OUTSOURCED_FILE_NAME_PREFIX + "add_tpl_file.xyz"
        tpl_content = "tpl content"
        tpl_src_path = os.path.join(module_repo_path, tpl_name)
        write_file(tpl_src_path, tpl_content)
        tpl_dst_path = os.path.join(module_repo_path, tst_ns_name, tpl_name[len(OUTSOURCED_FILE_NAME_PREFIX):])
        mod_pdv = project_dev_vars(project_path=module_repo_path)

        assert not add_children_file(mod_pdv, "not_existing_file.xxx", tst_ns_name, mod_pdv)

        new_pdv = project_dev_vars(project_path=empty_repo_path)
        new_dst_path = os.path.join(empty_repo_path, tst_ns_name, file_name)
        assert not add_children_file(new_pdv, file_src_path, tst_ns_name, new_pdv)  # fail because no tst_ns_name dir

        os.makedirs(os.path.join(empty_repo_path, tst_ns_name))
        assert not os.path.exists(new_dst_path)
        mod_pdv['project_type'] = ROOT_PRJ
        assert add_children_file(mod_pdv, file_src_path, tst_ns_name, new_pdv)
        assert os.path.exists(file_dst_path)
        assert file_content == read_file(file_dst_path)
        assert os.path.exists(new_dst_path)
        assert file_content == read_file(new_dst_path)

        os.remove(file_dst_path)

        assert not os.path.exists(file_dst_path)
        assert not add_children_file(mod_pdv, file_src_path, tst_ns_name, mod_pdv)  # False: added to parent and child
        assert os.path.exists(file_dst_path)
        assert file_content == read_file(file_dst_path)

        assert not os.path.exists(tpl_dst_path)
        assert not add_children_file(mod_pdv, tpl_src_path, tst_ns_name, mod_pdv)
        assert os.path.exists(tpl_dst_path)
        assert tpl_content in read_file(tpl_dst_path)
        assert OUTSOURCED_MARKER in read_file(tpl_dst_path)

    def test_bump_version(self, mocked_app_options, module_repo_path):
        mocked_app_options['namespace'] = ""        # or tst_ns_name
        mocked_app_options['path'] = module_repo_path
        mocked_app_options['verbose'] = True
        mocked_app_options['versionIncrementPart'] = 3
        import_name = '.'.join(os.path.basename(module_repo_path).split('_', maxsplit=1))
        mocked_app_options[_template_version_option(import_name)] = ""

        version = code_file_version(project_main_file(import_name, project_path=module_repo_path))

        bump_version(project_dev_vars(project_path=module_repo_path))
        assert code_file_version(project_main_file(import_name, project_path=module_repo_path)) > version

    def test_bump_version_disabled(self, mocked_app_options, module_repo_path):
        mocked_app_options['namespace'] = tst_ns_name   # or ""
        mocked_app_options['path'] = module_repo_path
        mocked_app_options['verbose'] = True
        mocked_app_options['versionIncrementPart'] = 0
        import_name = '.'.join(os.path.basename(module_repo_path).split('_', maxsplit=1))
        mocked_app_options[_template_version_option(import_name)] = ""

        version = code_file_version(project_main_file(import_name, project_path=module_repo_path))

        bump_version(project_dev_vars(project_path=module_repo_path))
        assert code_file_version(project_main_file(import_name, project_path=module_repo_path)) == version

    def test_check_integrity(self, capsys, changed_repo_path, empty_repo_path, mocked_app_options, module_repo_path):
        mocked_app_options['namespace'] = ""
        mocked_app_options['verbose'] = False

        check_integrity({'project_path': changed_repo_path})
        assert capsys.readouterr().out

        check_integrity({'project_path': empty_repo_path})
        assert capsys.readouterr().out

        check_integrity(project_dev_vars(project_path=changed_repo_path))
        assert capsys.readouterr().out

        check_integrity(project_dev_vars(project_path=empty_repo_path))
        assert capsys.readouterr().out

        check_children_integrity(
            {}, *(project_dev_vars(project_path=_) for _ in (changed_repo_path, empty_repo_path, module_repo_path)))
        assert capsys.readouterr().out

        mocked_app_options['verbose'] = True

        check_integrity({'project_path': changed_repo_path})
        assert capsys.readouterr().out

        check_integrity({'project_path': empty_repo_path})
        assert capsys.readouterr().out

        check_integrity(project_dev_vars(project_path=changed_repo_path))
        assert capsys.readouterr().out

        check_integrity(project_dev_vars(project_path=empty_repo_path))
        assert capsys.readouterr().out

        check_children_integrity(
            {}, *(project_dev_vars(project_path=_) for _ in (changed_repo_path, empty_repo_path, module_repo_path)))
        assert capsys.readouterr().out

    def test_clone_children(self, mocked_app_options):
        project_versions = ("aedev_git_repo_manager==0.2.24", "aedev_setup_project==0.3.4")
        # mocked_app_options['arguments'] = project_versions
        mocked_app_options['branch'] = ""
        mocked_app_options['domain'] = None
        mocked_app_options['group'] = "aedev-group"
        mocked_app_options['namespace'] = "aedev"
        mocked_app_options['project'] = ""

        with _init_parent() as parent_dir:
            mocked_app_options['path'] = parent_dir
            os.makedirs(parent_dir)
            project_paths = clone_children({'project_path': parent_dir, 'project_type': PARENT_PRJ}, *project_versions)
            for idx, project_path in enumerate(project_paths):
                assert project_path.startswith(parent_dir)
                assert os.path.isdir(project_path)
                import_name = '.'.join(os.path.basename(project_path).split('_', maxsplit=1))
                version = project_versions[idx].split(PROJECT_VERSION_SEP)[1]
                assert version == code_file_version(project_main_file(import_name, project_path=project_path))

    def test_clone_project(self, mocked_app_options):
        import_name = "aedev.git_repo_manager"
        project_name = norm_name(import_name)
        version = "0.2.24"
        mocked_app_options['branch'] = f"release{version}"
        mocked_app_options['domain'] = None
        mocked_app_options['group'] = "aedev-group"
        mocked_app_options['namespace'] = ""
        mocked_app_options['project'] = ""
        mocked_app_options['path'] = ""

        with _init_parent() as parent_dir:
            os.makedirs(parent_dir)
            project_path = clone_project({'project_path': parent_dir, 'project_type': PARENT_PRJ}, project_name)
            assert project_path.startswith(parent_dir)
            assert project_path == os.path.join(parent_dir, project_name)
            assert os.path.isdir(project_path)
            assert version == code_file_version(project_main_file(import_name, project_path=project_path))

    def test_clone_project_via_package_option(self, mocked_app_options):
        import_name = "aedev.git_repo_manager"
        project_name = norm_name(import_name)
        version = "0.2.24"
        mocked_app_options['branch'] = "develop"
        mocked_app_options['domain'] = None
        mocked_app_options['group'] = "aedev-group"
        mocked_app_options['namespace'] = ""
        mocked_app_options['project'] = project_name + PROJECT_VERSION_SEP + version
        mocked_app_options['path'] = ""
        mocked_app_options['verbose'] = False

        with _init_parent() as parent_dir:
            os.makedirs(parent_dir)
            project_path = clone_project({'project_path': parent_dir, 'project_type': PARENT_PRJ})
            assert project_path.startswith(parent_dir)
            assert project_path == os.path.join(parent_dir, project_name)
            assert os.path.isdir(project_path)
            assert version == code_file_version(project_main_file(import_name, project_path=project_path))

    def test_commit_children(self, mocked_app_options, module_repo_path):
        mocked_app_options['namespace'] = ""        # or tst_ns_name
        mocked_app_options['path'] = os.path.dirname(module_repo_path)
        mocked_app_options['verbose'] = True
        mocked_app_options[_template_version_option(tst_ns_name + '.' + tst_ns_name)] = ""
        write_file(os.path.join(module_repo_path, COMMIT_MSG_FILE_NAME), "commit message testing commit_children")
        commit_children({}, project_dev_vars(project_path=module_repo_path))

    def test_commit_project(self, mocked_app_options, module_repo_path):
        mocked_app_options['verbose'] = True
        write_file(os.path.join(module_repo_path, COMMIT_MSG_FILE_NAME), "commit message testing commit_project action")
        commit_project({'project_path': module_repo_path})

    def test_delete_children_file(self, empty_repo_path, mocked_app_options, module_repo_path):
        mocked_app_options['namespace'] = ""        # or tst_ns_name
        mocked_app_options['path'] = module_repo_path
        mocked_app_options['verbose'] = True
        mocked_app_options[_template_version_option(tst_ns_name + '.' + tst_ns_name)] = ""
        root_pdv = project_dev_vars(project_path=empty_repo_path)
        root_pdv['project_type'] = ROOT_PRJ
        mod_pdv = project_dev_vars(project_path=module_repo_path)

        del_dir = "del_dir"
        os.makedirs(os.path.join(empty_repo_path, del_dir))
        assert os.path.isdir(os.path.join(empty_repo_path, del_dir))
        os.makedirs(os.path.join(module_repo_path, del_dir))
        assert os.path.isdir(os.path.join(module_repo_path, del_dir))
        assert delete_children_file(root_pdv, del_dir, mod_pdv)
        assert not os.path.isdir(os.path.join(empty_repo_path, del_dir))
        assert not os.path.isdir(os.path.join(module_repo_path, del_dir))

        del_file = os.path.join(module_repo_path, tst_ns_name, tst_ns_por_name + PY_EXT)
        assert os.path.exists(del_file)
        assert not delete_children_file(root_pdv, del_file, mod_pdv)
        assert not os.path.exists(del_file)

    def test_install_children_editable(self, mocked_app_options, module_repo_path):
        mocked_app_options['namespace'] = ""        # or tst_ns_name
        mocked_app_options['path'] = os.path.dirname(module_repo_path)
        mocked_app_options['verbose'] = True
        mocked_app_options[_template_version_option(tst_ns_name + '.' + tst_ns_name)] = ""
        install_children_editable({}, project_dev_vars(project_path=module_repo_path))

    def test_install_editable(self, mocked_app_options, module_repo_path):
        mocked_app_options['verbose'] = True
        install_editable({'project_path': module_repo_path})

    def test_new_app(self, mocked_app_options, module_repo_path):
        mocked_app_options['domain'] = None
        mocked_app_options['namespace'] = tst_ns_name
        mocked_app_options['path'] = module_repo_path
        mocked_app_options['verbose'] = False

        pdv = project_dev_vars(project_path=module_repo_path)
        assert os.path.isfile(main_file_path(module_repo_path, MODULE_PRJ, tst_ns_name))
        assert not os.path.isfile(main_file_path(module_repo_path, APP_PRJ, tst_ns_name))

        new_pdv = new_app(pdv)
        assert pdv_str(new_pdv, 'project_type') == APP_PRJ
        assert not os.path.isfile(main_file_path(module_repo_path, MODULE_PRJ, tst_ns_name))
        assert os.path.isfile(main_file_path(module_repo_path, APP_PRJ, tst_ns_name))

    def test_new_children(self, mocked_app_options, module_repo_path):
        mocked_app_options['domain'] = None
        mocked_app_options['namespace'] = tst_ns_name
        mocked_app_options['project'] = ""
        mocked_app_options['path'] = os.path.dirname(module_repo_path)
        mocked_app_options['verbose'] = False
        mocked_app_options[_template_version_option(tst_ns_name + '.' + tst_ns_name)] = ""

        parent_pdv = project_dev_vars(project_path=os.path.dirname(module_repo_path))
        module_pdv = project_dev_vars(project_path=module_repo_path)
        assert os.path.isfile(main_file_path(module_repo_path, MODULE_PRJ, tst_ns_name))
        assert not os.path.isfile(main_file_path(module_repo_path, PACKAGE_PRJ, tst_ns_name))

        new_pdv = new_children(parent_pdv, module_pdv)[0]
        assert pdv_str(new_pdv, 'project_type') == MODULE_PRJ
        assert os.path.isfile(main_file_path(module_repo_path, MODULE_PRJ, tst_ns_name))
        assert not os.path.isfile(main_file_path(module_repo_path, PACKAGE_PRJ, tst_ns_name))

    def test_new_django(self, mocked_app_options, module_repo_path):
        mocked_app_options['domain'] = None
        mocked_app_options['namespace'] = tst_ns_name
        mocked_app_options['path'] = module_repo_path
        mocked_app_options['verbose'] = False

        pdv = project_dev_vars(project_path=module_repo_path)
        assert not os.path.isfile(main_file_path(module_repo_path, DJANGO_PRJ, tst_ns_name))

        new_pdv = new_django(pdv)
        assert pdv_str(new_pdv, 'project_type') == DJANGO_PRJ
        assert os.path.isfile(main_file_path(module_repo_path, DJANGO_PRJ, tst_ns_name))

    def test_new_django_without_namespace(self, mocked_app_options, empty_repo_path):
        mocked_app_options['domain'] = None
        mocked_app_options['namespace'] = ""
        mocked_app_options['path'] = empty_repo_path
        mocked_app_options['verbose'] = False

        pdv = project_dev_vars(project_path=empty_repo_path)
        assert pdv_str(pdv, 'project_type') == NO_PRJ
        assert not os.path.isfile(main_file_path(empty_repo_path, DJANGO_PRJ, ""))

        new_pdv = new_django(pdv)
        assert pdv_str(new_pdv, 'project_type') == DJANGO_PRJ
        assert os.path.isfile(main_file_path(empty_repo_path, DJANGO_PRJ, ""))

    def test_new_module(self, mocked_app_options, module_repo_path):
        mocked_app_options['domain'] = None
        mocked_app_options['namespace'] = tst_ns_name
        mocked_app_options['path'] = module_repo_path

        pdv = project_dev_vars(project_path=module_repo_path)
        assert os.path.isfile(main_file_path(module_repo_path, MODULE_PRJ, tst_ns_name))
        assert not os.path.isfile(main_file_path(module_repo_path, PACKAGE_PRJ, tst_ns_name))

        new_pdv = new_module(pdv)
        assert pdv_str(new_pdv, 'project_type') == MODULE_PRJ
        assert os.path.isfile(main_file_path(module_repo_path, MODULE_PRJ, tst_ns_name))
        assert not os.path.isfile(main_file_path(module_repo_path, PACKAGE_PRJ, tst_ns_name))

    def test_new_module_from_root(self, mocked_app_options, root_repo_path):
        mocked_app_options['domain'] = None
        mocked_app_options['namespace'] = tst_ns_name
        mocked_app_options['path'] = root_repo_path
        mocked_app_options['verbose'] = False

        pdv = project_dev_vars(project_path=root_repo_path)
        assert not os.path.isfile(main_file_path(root_repo_path, MODULE_PRJ, tst_ns_name))
        assert os.path.isfile(main_file_path(root_repo_path, ROOT_PRJ, tst_ns_name))

        new_pdv = new_namespace_root(pdv)
        assert pdv_str(new_pdv, 'project_type') == ROOT_PRJ
        assert not os.path.isfile(main_file_path(root_repo_path, MODULE_PRJ, tst_ns_name))
        assert os.path.isfile(main_file_path(root_repo_path, ROOT_PRJ, tst_ns_name))
        assert os.path.isfile(main_file_path(pdv_str(new_pdv, 'project_path'), ROOT_PRJ, tst_ns_name))

    def test_new_namespace_root(self, mocked_app_options, module_repo_path):
        mocked_app_options['domain'] = None
        mocked_app_options['namespace'] = tst_ns_name
        mocked_app_options['path'] = module_repo_path
        mocked_app_options['verbose'] = False

        pdv = project_dev_vars(project_path=module_repo_path)
        assert os.path.isfile(main_file_path(module_repo_path, MODULE_PRJ, tst_ns_name))
        assert not os.path.isfile(main_file_path(module_repo_path, ROOT_PRJ, tst_ns_name))

        new_pdv = new_namespace_root(pdv)
        assert pdv_str(new_pdv, 'project_type') == ROOT_PRJ
        assert os.path.isfile(main_file_path(module_repo_path, MODULE_PRJ, tst_ns_name))
        assert not os.path.isfile(main_file_path(module_repo_path, ROOT_PRJ, tst_ns_name))
        assert os.path.isfile(main_file_path(pdv_str(new_pdv, 'project_path'), ROOT_PRJ, tst_ns_name))

    def test_new_package(self, mocked_app_options, module_repo_path):
        mocked_app_options['domain'] = None
        mocked_app_options['namespace'] = tst_ns_name
        mocked_app_options['path'] = module_repo_path

        pdv = project_dev_vars(project_path=module_repo_path)
        assert os.path.isfile(main_file_path(module_repo_path, MODULE_PRJ, tst_ns_name))
        assert not os.path.isfile(main_file_path(module_repo_path, PACKAGE_PRJ, tst_ns_name))

        new_pdv = new_package(pdv)
        assert pdv_str(new_pdv, 'project_type') == PACKAGE_PRJ
        assert not os.path.isfile(main_file_path(module_repo_path, MODULE_PRJ, tst_ns_name))
        assert os.path.isfile(main_file_path(module_repo_path, PACKAGE_PRJ, tst_ns_name))

    def test_new_playground(self, mocked_app_options, empty_repo_path):
        mocked_app_options['domain'] = None
        mocked_app_options['namespace'] = ""
        mocked_app_options['path'] = empty_repo_path + '_playground'
        mocked_app_options['verbose'] = False

        pdv = project_dev_vars(project_path=empty_repo_path + '_playground')
        new_pdv = new_playground(pdv)
        assert pdv_str(new_pdv, 'project_type') == PLAYGROUND_PRJ

    def test_new_project(self, mocked_app_options, module_repo_path):
        mocked_app_options['domain'] = None
        mocked_app_options['namespace'] = tst_ns_name
        mocked_app_options['path'] = ""
        mocked_app_options['verbose'] = False

        pdv = project_dev_vars(project_path=module_repo_path)
        files = set(path_items(os.path.join(module_repo_path, "**")))

        new_pdv = new_project(pdv)
        assert pdv_str(new_pdv, 'project_type') == MODULE_PRJ
        assert files == set(path_items(os.path.join(module_repo_path, "**")))

    def test_prepare_commit(self, changed_repo_path, empty_repo_path, mocked_app_options, module_repo_path):
        mocked_app_options['namespace'] = ""        # or tst_ns_name
        mocked_app_options['verbose'] = True
        mocked_app_options[_template_version_option(tst_ns_name + '.' + tst_ns_name)] = ""
        title = "commit msg title"

        assert not os.path.isfile(os.path.join(changed_repo_path, COMMIT_MSG_FILE_NAME))
        changed_uncommitted = set(_git_uncommitted({'project_path': changed_repo_path}))

        prepare_commit({'project_path': changed_repo_path}, title)
        assert os.path.isfile(os.path.join(changed_repo_path, COMMIT_MSG_FILE_NAME))
        assert changed_uncommitted == set(_git_uncommitted({'project_path': changed_repo_path}))
        assert title in read_file(os.path.join(changed_repo_path, COMMIT_MSG_FILE_NAME)).split(os.linesep)[0]

        assert not os.path.isfile(os.path.join(empty_repo_path, COMMIT_MSG_FILE_NAME))
        empty_uncommitted = set(_git_uncommitted({'project_path': empty_repo_path}))

        prepare_commit({'project_path': empty_repo_path}, title=title)
        assert os.path.isfile(os.path.join(empty_repo_path, COMMIT_MSG_FILE_NAME))
        assert empty_uncommitted == set(_git_uncommitted({'project_path': empty_repo_path}))
        assert title in read_file(os.path.join(empty_repo_path, COMMIT_MSG_FILE_NAME)).split(os.linesep)[0]

        added = "added_file3.py"
        write_file(os.path.join(changed_repo_path, added), "# added empty python module")
        write_file(os.path.join(empty_repo_path, added), "# added empty python module")

        prepare_children_commit(
            {}, title,
            *(project_dev_vars(project_path=_) for _ in (changed_repo_path, empty_repo_path, module_repo_path)))
        assert added in read_file(os.path.join(changed_repo_path, COMMIT_MSG_FILE_NAME))
        assert set(_git_uncommitted({'project_path': changed_repo_path})) == changed_uncommitted | {added}
        assert added in read_file(os.path.join(empty_repo_path, COMMIT_MSG_FILE_NAME))
        assert set(_git_uncommitted({'project_path': empty_repo_path})) == empty_uncommitted | {added}
        assert title in read_file(os.path.join(changed_repo_path, COMMIT_MSG_FILE_NAME)).split(os.linesep)[0]
        assert title in read_file(os.path.join(empty_repo_path, COMMIT_MSG_FILE_NAME)).split(os.linesep)[0]

    def test_refresh_children_outsourced(self, mocked_app_options, module_repo_path):
        mocked_app_options['namespace'] = tst_ns_name
        tst_dir = os.path.join(module_repo_path, TESTS_FOLDER)
        assert not os.path.isdir(tst_dir)

        refresh_children_outsourced({}, project_dev_vars(project_path=module_repo_path))
        if on_ci_host():
            assert not os.path.isdir(tst_dir)
        else:
            assert os.path.isdir(tst_dir)  # created via aedev.tpl_project, but not in CI host/server

    def test_rename_children_file(self, empty_repo_path, mocked_app_options, module_repo_path):
        mocked_app_options['namespace'] = ""        # or tst_ns_name
        mocked_app_options[_template_version_option(tst_ns_name + '.' + tst_ns_name)] = ""
        mocked_app_options['path'] = module_repo_path
        mocked_app_options['verbose'] = True
        root_pdv = project_dev_vars(project_path=empty_repo_path)
        root_pdv['project_type'] = ROOT_PRJ
        mod_pdv = project_dev_vars(project_path=module_repo_path)

        src_file = "ren.efg"
        write_file(os.path.join(empty_repo_path, src_file), "file content")
        write_file(os.path.join(module_repo_path, src_file), "file content")
        dst_file = "renamed.hij"
        assert not os.path.exists(os.path.join(empty_repo_path, dst_file))
        assert not os.path.exists(os.path.join(module_repo_path, dst_file))

        assert rename_children_file(root_pdv, src_file, dst_file, mod_pdv)
        assert not os.path.exists(os.path.join(empty_repo_path, src_file))
        assert os.path.exists(os.path.join(empty_repo_path, dst_file))
        assert not os.path.exists(os.path.join(module_repo_path, src_file))
        assert os.path.exists(os.path.join(module_repo_path, dst_file))

        src_file = os.path.join(tst_ns_name, tst_ns_por_name + PY_EXT)      # rel path move within prj
        dst_file = tst_ns_por_name + PY_EXT
        assert os.path.exists(os.path.join(module_repo_path, src_file))
        assert not os.path.exists(os.path.join(module_repo_path, dst_file))
        assert not rename_children_file(root_pdv, src_file, dst_file, mod_pdv, mod_pdv)  # no src in root / 2*mod rename
        assert not os.path.exists(os.path.join(module_repo_path, src_file))
        assert os.path.exists(os.path.join(module_repo_path, dst_file))

    def test_run_children_command(self, capsys, mocked_app_options):
        mocked_app_options['delay'] = 0
        mocked_app_options['force'] = False
        output = "tst_run_chi_cmd"
        run_children_command({}, f"echo {output}", {'project_path': TESTS_FOLDER}, {'project_path': "."})
        assert capsys.readouterr().out.count(output) == 3  # 2 lines with echo output and a final one on action complete

    def test_show_actions(self, capsys, changed_repo_path, empty_repo_path, mocked_app_options):
        mocked_app_options['domain'] = 'gitlab.com'
        pdv = {'host_api': GitlabCom()}

        mocked_app_options['verbose'] = False
        show_actions(pdv)
        assert capsys.readouterr().out

        mocked_app_options['verbose'] = True
        show_actions(pdv)
        assert capsys.readouterr().out

    def test_show_children_versions(self, capsys, mocked_app_options):
        mocked_app_options['branch'] = ""
        mocked_app_options['domain'] = None
        mocked_app_options['group'] = "aedev-group"
        mocked_app_options['namespace'] = ""
        mocked_app_options['project'] = ""
        mocked_app_options['path'] = ""

        with _init_parent() as parent_dir:
            os.makedirs(parent_dir)
            root_path = clone_project({'project_path': parent_dir, 'project_type': PARENT_PRJ}, 'aedev_aedev')
            assert os.path.isdir(root_path)
            show_children_versions(project_dev_vars(project_path=root_path), project_dev_vars())
            output = capsys.readouterr().out
            assert 'aedev_git_repo_manager' in output
            assert f"local:{grm_version}" in output

    def test_show_status(self, capsys, changed_repo_path, empty_repo_path, mocked_app_options, module_repo_path):
        mocked_app_options['namespace'] = ""        # or tst_ns_name
        mocked_app_options[_template_version_option(tst_ns_name + '.' + tst_ns_name)] = ""
        mocked_app_options['verbose'] = False

        show_status({'project_path': changed_repo_path})
        assert capsys.readouterr().out

        show_status({'project_path': empty_repo_path})
        assert capsys.readouterr().out

        show_status(project_dev_vars(project_path=changed_repo_path))
        assert capsys.readouterr().out

        show_status(project_dev_vars(project_path=empty_repo_path))
        assert capsys.readouterr().out

        show_children_status(
            *(project_dev_vars(project_path=_) for _ in (changed_repo_path, empty_repo_path, module_repo_path)))
        assert capsys.readouterr().out

        mocked_app_options['verbose'] = True

        show_status({'project_path': changed_repo_path})
        assert capsys.readouterr().out

        show_status({'project_path': empty_repo_path})
        assert capsys.readouterr().out

        show_status(project_dev_vars(project_path=changed_repo_path))
        assert capsys.readouterr().out

        pdv = project_dev_vars(project_path=empty_repo_path)
        _git_checkout(pdv, branch="tst_branch")
        pdv['children_project_vars'] = {}
        pdv['namespace_name'] = tst_ns_name
        pdv['project_type'] = ROOT_PRJ
        show_status(pdv)
        assert capsys.readouterr().out

        show_children_status(
            {'project_path': empty_repo_path, 'project_type': ROOT_PRJ, 'children_project_vars': {}},
            *(project_dev_vars(project_path=_) for _ in (changed_repo_path, empty_repo_path, module_repo_path)))
        assert capsys.readouterr().out

    def test_update_children(self, empty_repo_path, module_repo_path, mocked_app_options):
        mocked_app_options['verbose'] = False
        update_children({'project_path': empty_repo_path, 'project_type': ROOT_PRJ}, {'project_path': module_repo_path})

        with patch('aedev.git_repo_manager.__main__._git_fetch', return_value=['git fetch error']):
            update_children({}, {'project_path': TESTS_FOLDER})


class TestHelpers:
    """ test public helper functions. """
    def test_activate_venv(self):
        cur_venv = active_venv()
        activate_venv(LOCAL_VENV)
        assert active_venv() == '' if 'CI_PROJECT_ID' in os.environ else LOCAL_VENV
        if cur_venv:
            activate_venv(cur_venv)
            assert active_venv() == cur_venv

    def test_active_venv(self):
        assert not bool(active_venv()) == 'CI_PROJECT_ID' in os.environ      # active_venv()=='' on gitlab CI

    def test_bump_file_version_invalid_file(self):
        err = bump_file_version('::invalid_file_name::')
        assert err

    def test_bump_file_version_empty_file(self):
        tst_file = 'test_bump_version' + PY_EXT
        try:
            write_file(tst_file, "")
            err = bump_file_version(tst_file)
            assert err
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_bump_file_version_multi_version(self):
        tst_file = 'test_bump_version' + PY_EXT
        try:
            write_file(tst_file, f"__version__ = '1.2.3'{os.linesep}__version__ = '2.3.4'")
            err = bump_file_version(tst_file)
            assert err
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_bump_file_version_major(self):
        tst_file = 'test_bump_version' + PY_EXT
        try:
            write_file(tst_file, f"__version__ = '1.2.3'{os.linesep}")

            err = bump_file_version(tst_file, increment_part=1)

            assert not err

            content = read_file(tst_file)
            assert "__version__ = '1.2.3'" not in content
            assert "__version__ = '2.2.3'" in content
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_bump_file_version_minor(self):
        tst_file = 'test_bump_version' + PY_EXT
        try:
            write_file(tst_file, f"__version__ = '1.2.3'{os.linesep}{os.linesep}version = '2.3.4'")

            err = bump_file_version(tst_file, increment_part=2)

            assert not err

            content = read_file(tst_file)
            assert "__version__ = '1.2.3'" not in content
            assert "__version__ = '1.3.3'" in content
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_bump_file_version_build(self):
        tst_file = 'test_bump_version' + PY_EXT
        try:
            write_file(tst_file, f"__version__ = '1.2.3'{os.linesep}version = '2.3.4'")

            err = bump_file_version(tst_file)

            assert not err

            content = read_file(tst_file)
            assert "__version__ = '1.2.3'" not in content
            assert "__version__ = '1.2.4'" in content
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_bump_file_version_remove_suffix(self):
        tst_file = 'test_bump_version' + PY_EXT
        try:
            write_file(tst_file, f"__version__ = '1.2.3pre'{os.linesep}version = '2.3.4'")

            err = bump_file_version(tst_file, increment_part=2)

            assert not err

            content = read_file(tst_file)
            assert "__version__ = '1.2.3'" not in content
            assert "__version__ = '1.3.3'" in content
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_bump_file_version_keeping_comment(self):
        tst_file = 'test_bump_version' + PY_EXT
        comment_str = "  # comment string"
        try:
            write_file(tst_file, f"__version__ = '1.2.3'{comment_str}{os.linesep}version = '2.3.4'")

            err = bump_file_version(tst_file, increment_part=1)

            assert not err

            content = read_file(tst_file)
            assert f"__version__ = '2.2.3'{comment_str}" in content
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_declaration_of_template_vars(self):
        assert OUTSOURCED_FILE_NAME_PREFIX
        assert OUTSOURCED_MARKER
        assert TPL_FILE_NAME_PREFIX
        assert TEMPLATE_PLACEHOLDER_ID_PREFIX
        assert TEMPLATE_PLACEHOLDER_ID_SUFFIX
        assert TEMPLATE_PLACEHOLDER_ARGS_SUFFIX
        assert TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID

    def test_deploy_template_dst_files_not_passed(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        src_dir = join(parent_dir, 'tpl_src_prj_dir')
        tpl_dir = join(src_dir, TEMPLATES_FOLDER)
        file_name = 'template.extension'
        src_file = join(tpl_dir, file_name)
        content = "template file content"
        dst_dir = join(parent_dir, 'dst')
        new_pdv = {'project_path': dst_dir}

        try:
            write_file(src_file, content, make_dirs=True)
            os.makedirs(dst_dir)

            deploy_template(src_file, "", "", new_pdv)

            dst_file = join(dst_dir, file_name)
            assert os.path.isfile(dst_file)
            assert read_file(dst_file) == content

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_deploy_template_logged_state(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        src_dir = join(parent_dir, 'tpl_src_prj_dir')
        tpl_dir = join(src_dir, TEMPLATES_FOLDER)
        content = "logged template file content"
        dst_dir = join(parent_dir, 'dst')
        new_pdv = {'project_path': dst_dir}
        log_prefix = "    - "

        try:
            os.makedirs(tpl_dir)
            os.makedirs(dst_dir)
            logged = []

            file_name = "template_state_log.ext"
            src_file = join(tpl_dir, file_name)
            write_file(src_file, content)

            deploy_template(src_file, "", "", new_pdv, logger=lambda *_: logged.extend(arg for arg in _))
            assert logged[-1].startswith(log_prefix + "refresh")

            deploy_template(src_file, "", "", new_pdv, logger=lambda *_: logged.extend(arg for arg in _))
            assert logged[-1].startswith(log_prefix + "binary-exists-skip")

            lock_file = join(dst_dir, file_name + LOCK_EXT)
            write_file(lock_file, "")
            deploy_template(src_file, "", "", new_pdv, logger=lambda *_: logged.extend(arg for arg in _))
            assert logged[-1].startswith(log_prefix + "lock-extension-skip")
            os.remove(lock_file)

            src_file = join(tpl_dir, TPL_FILE_NAME_PREFIX + "template_state_log.ext")
            write_file(src_file, content)

            deploy_template(src_file, "", "", new_pdv, logger=lambda *_: logged.extend(arg for arg in _))
            assert logged[-1].startswith(log_prefix + "unchanged-skip")

            src_file = join(tpl_dir, TPL_FILE_NAME_PREFIX + "template_state_log.ext")
            write_file(src_file, content + " extended")

            deploy_template(src_file, "", "", new_pdv, logger=lambda *_: logged.extend(arg for arg in _))
            assert logged[-1].startswith(log_prefix + "missing-outsourced-marker-skip")

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_deploy_template_otf_in_sub_dir(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        prj_dir = join(parent_dir, 'prj_with_otf_tpl')
        tpl_dir = join(prj_dir, TEMPLATES_FOLDER)
        sub_dir_folder = 'sub_dir'
        tpl_sub_dir = join(tpl_dir, sub_dir_folder)
        file_name = OUTSOURCED_FILE_NAME_PREFIX + 'changed_template' + PY_EXT
        src_file = join(tpl_sub_dir, file_name)
        content = "# template file content"
        dst_dir = join(parent_dir, 'dst')
        new_pdv = {'project_path': dst_dir}
        patcher = "patching package id to be added to patched destination file"

        dst_files = set()
        try:
            write_file(src_file, content, make_dirs=True)
            os.makedirs(dst_dir)

            deploy_template(src_file, sub_dir_folder, patcher, new_pdv, dst_files=dst_files)

            dst_file = join(dst_dir, sub_dir_folder, file_name[len(OUTSOURCED_FILE_NAME_PREFIX):])
            assert os.path.isfile(dst_file)
            assert OUTSOURCED_MARKER in read_file(dst_file)
            assert patcher in read_file(dst_file)
            assert read_file(dst_file).endswith(content)
            assert norm_path(dst_file) in dst_files

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_deploy_template_tpl_in_sub_dir(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        prj_dir = join(parent_dir, 'tpl_src_root_dir')
        tpl_dir = join(prj_dir, TEMPLATES_FOLDER)
        sub_dir_folder = 'sub_dir'
        tpl_sub_dir = join(tpl_dir, sub_dir_folder)
        file_name = TPL_FILE_NAME_PREFIX + 'changed_template' + PY_EXT
        src_file = join(tpl_sub_dir, file_name)
        content = "# template file content created in {project_path}"
        dst_dir = join(parent_dir, 'dst')
        new_pdv = {'project_path': dst_dir}
        patcher = "patching package id here not added to patched destination file"

        dst_files = set()
        try:
            write_file(src_file, content, make_dirs=True)
            os.makedirs(dst_dir)

            deploy_template(src_file, sub_dir_folder, patcher, new_pdv, dst_files=dst_files)

            dst_file = join(dst_dir, sub_dir_folder, file_name[len(TPL_FILE_NAME_PREFIX):])
            assert os.path.isfile(dst_file)
            assert OUTSOURCED_MARKER not in read_file(dst_file)
            assert patcher not in read_file(dst_file)
            assert read_file(dst_file).endswith(content.format(project_path=dst_dir))
            assert norm_path(dst_file) in dst_files

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_deploy_template_otf_tpl_in_sub_dir(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        prj_dir = join(parent_dir, 'prj_root_dir')
        tpl_dir = join(prj_dir, TEMPLATES_FOLDER)
        sub_dir_folder = 'sub_dir'
        tpl_sub_dir = join(tpl_dir, sub_dir_folder)
        file_name = OUTSOURCED_FILE_NAME_PREFIX + TPL_FILE_NAME_PREFIX + 'changed_template' + PY_EXT
        src_file = join(tpl_sub_dir, file_name)
        content = "# template file content created in {project_path}"
        dst_dir = join(parent_dir, 'dst')
        new_pdv = {'project_path': dst_dir}
        patcher = "patching project name to be added to destination file"

        dst_files = set()
        try:
            write_file(src_file, content, make_dirs=True)
            os.makedirs(dst_dir)

            deploy_template(src_file, sub_dir_folder, patcher, new_pdv, dst_files=dst_files)

            dst_file = join(dst_dir, sub_dir_folder,
                            file_name[len(OUTSOURCED_FILE_NAME_PREFIX) + len(TPL_FILE_NAME_PREFIX):])
            assert os.path.isfile(dst_file)
            assert OUTSOURCED_MARKER in read_file(dst_file)
            assert patcher in read_file(dst_file)
            assert read_file(dst_file).endswith(content.format(project_path=dst_dir))
            assert norm_path(dst_file) in dst_files

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_deploy_template_otf_stop_tpl(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        prj_dir = join(parent_dir, 'prj_root_dir')
        tpl_dir = join(prj_dir, TEMPLATES_FOLDER)
        sub_dir_folder = TEMPLATES_FOLDER
        tpl_sub_dir = join(tpl_dir, sub_dir_folder)
        file_name = OUTSOURCED_FILE_NAME_PREFIX + TPL_STOP_CNV_PREFIX + TPL_FILE_NAME_PREFIX + 'chg_template' + PY_EXT
        src_file = join(tpl_sub_dir, file_name)
        content = "# template file content created in {project_path}"
        dst_dir = join(parent_dir, 'dst', TEMPLATES_FOLDER)
        new_pdv = {'project_path': dst_dir}
        patcher = "patcher"

        dst_files = set()
        try:
            write_file(src_file, content, make_dirs=True)
            os.makedirs(dst_dir)

            deploy_template(src_file, sub_dir_folder, patcher, new_pdv, dst_files=dst_files)

            dst_file = join(dst_dir, sub_dir_folder,
                            file_name[len(OUTSOURCED_FILE_NAME_PREFIX) + len(TPL_STOP_CNV_PREFIX):])
            assert os.path.isfile(dst_file)
            assert OUTSOURCED_MARKER in read_file(dst_file)
            assert patcher in read_file(dst_file)
            assert read_file(dst_file).endswith(content)
            assert norm_path(dst_file) in dst_files

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_deploy_template_otf_existing_unlocked_because_marker(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        prj_dir = join(parent_dir, 'project_dir')
        tpl_dir = join(prj_dir, TEMPLATES_FOLDER)
        file_name = OUTSOURCED_FILE_NAME_PREFIX + 'unlocked_template' + PY_EXT
        src_file = join(tpl_dir, file_name)
        content = f"# template file extra content"
        dst_dir = join(parent_dir, 'dst')
        new_pdv = {'project_path': dst_dir}
        patcher = "patching package id to be added to destination file"

        dst_files = set()
        try:
            write_file(src_file, content, make_dirs=True)
            dst_file = join(dst_dir, file_name[len(OUTSOURCED_FILE_NAME_PREFIX):])
            write_file(dst_file, OUTSOURCED_MARKER, make_dirs=True)

            deploy_template(src_file, "", patcher, new_pdv, dst_files=dst_files)

            assert os.path.isfile(dst_file)
            assert OUTSOURCED_MARKER in read_file(dst_file)
            assert content in read_file(dst_file)
            assert patcher in read_file(dst_file)
            assert norm_path(dst_file) in dst_files

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_deploy_template_otf_existing_locked_without_marker(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        prj_dir = join(parent_dir, 'prj_root')
        tpl_dir = join(prj_dir, TEMPLATES_FOLDER)
        file_name = OUTSOURCED_FILE_NAME_PREFIX + 'locked_template' + PY_EXT
        src_file = join(tpl_dir, file_name)
        content = "# template file content"
        dst_dir = join(parent_dir, 'dst')
        new_pdv = {'project_path': dst_dir}
        patcher = "patcher id or package name"

        dst_files = set()
        try:
            write_file(src_file, content, make_dirs=True)
            dst_file = join(dst_dir, file_name[len(OUTSOURCED_FILE_NAME_PREFIX):])
            dst_content = "locked because not contains marker"
            write_file(dst_file, dst_content, make_dirs=True)

            deploy_template(src_file, "", patcher, new_pdv, dst_files=dst_files)

            assert os.path.isfile(dst_file)
            assert OUTSOURCED_MARKER not in read_file(dst_file)
            assert read_file(dst_file) == dst_content
            assert patcher not in read_file(dst_file)
            assert norm_path(dst_file) in dst_files

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_deploy_template_otf_locked_by_file(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        prj_dir = join(parent_dir, 'prj_dir')
        tpl_dir = join(prj_dir, TEMPLATES_FOLDER)
        file_name = OUTSOURCED_FILE_NAME_PREFIX + 'locked_template' + PY_EXT
        src_file = join(tpl_dir, file_name)
        content = "# template file content"
        dst_dir = join(parent_dir, 'dst')
        new_pdv = {'project_path': dst_dir}

        dst_files = set()
        try:
            write_file(src_file, content, make_dirs=True)
            dst_file = join(dst_dir, file_name[len(OUTSOURCED_FILE_NAME_PREFIX):])
            write_file(dst_file + '.locked', "", make_dirs=True)

            deploy_template(src_file, "", "", new_pdv, dst_files=dst_files)

            assert not os.path.isfile(dst_file)
            assert norm_path(dst_file) in dst_files

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_deploy_template_stp_in_sub_dir(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        src_dir = join(parent_dir, 'tpl_src_prj_dir')
        tpl_dir = join(src_dir, TEMPLATES_FOLDER)
        sub_dir_folder = 'sub_dir'
        tpl_sub_dir = join(tpl_dir, sub_dir_folder)
        file_name = SKIP_PRJ_TYPE_FILE_NAME_PREFIX + ROOT_PRJ + "_template_file_name.eee"
        src_file = join(tpl_sub_dir, file_name)
        content = "template file content"
        dst_dir = join(parent_dir, 'dst')
        new_pdv = {'project_path': dst_dir, 'project_type': ROOT_PRJ}

        dst_files = set()
        try:
            write_file(src_file, content, make_dirs=True)
            os.makedirs(dst_dir)

            deploy_template(src_file, sub_dir_folder, "", new_pdv, dst_files=dst_files)
            assert not dst_files        # skipped deploy

            new_pdv['project_type'] = MODULE_PRJ
            deploy_template(src_file, sub_dir_folder, "", new_pdv, dst_files=dst_files)
            assert dst_files            # not skipped deploy
            dst_file = join(dst_dir, sub_dir_folder,
                            file_name[len(SKIP_PRJ_TYPE_FILE_NAME_PREFIX) + len(ROOT_PRJ) + 1:])
            assert os.path.isfile(dst_file)
            assert read_file(dst_file) == content
            assert norm_path(dst_file) in dst_files

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_deploy_template_tpl_locked_by_priority(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        prj_dir = join(parent_dir, 'prj')
        tpl_dir = join(prj_dir, TEMPLATES_FOLDER)
        file_name = TPL_FILE_NAME_PREFIX + 'template' + PY_EXT
        src_file = join(tpl_dir, file_name)
        content = "# template file content"
        dst_dir = join(parent_dir, 'dst')
        new_pdv = {'project_path': dst_dir}

        dst_files = set()
        try:
            write_file(src_file, content, make_dirs=True)
            os.makedirs(dst_dir)
            dst_file = join(dst_dir, file_name[len(TPL_FILE_NAME_PREFIX):])

            deploy_template(src_file, "", "", new_pdv, dst_files=dst_files)

            assert os.path.isfile(dst_file)
            assert read_file(dst_file) == content
            assert norm_path(dst_file) in dst_files
            dst_files_len = len(dst_files)

            write_file(src_file, 'any OTHER content')

            # second deploy try from tpl prj with lower priority
            deploy_template(src_file, "", "", new_pdv, dst_files=dst_files)

            assert os.path.isfile(dst_file)
            assert read_file(dst_file) == content
            assert dst_files_len == len(dst_files)

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_deploy_template_unchanged_in_sub_dir(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        src_dir = join(parent_dir, 'tpl_src_prj_dir')
        tpl_dir = join(src_dir, TEMPLATES_FOLDER)
        sub_dir_folder = 'sub_dir'
        tpl_sub_dir = join(tpl_dir, sub_dir_folder)
        file_name = 'unchanged_template.ext'
        src_file = join(tpl_sub_dir, file_name)
        content = "template file content"
        dst_dir = join(parent_dir, 'dst')
        new_pdv = {'project_path': dst_dir}

        dst_files = set()
        try:
            write_file(src_file, content, make_dirs=True)
            os.makedirs(dst_dir)

            deploy_template(src_file, sub_dir_folder, "", new_pdv, dst_files=dst_files)

            dst_file = join(dst_dir, sub_dir_folder, file_name)
            assert os.path.isfile(dst_file)
            assert read_file(dst_file) == content
            assert norm_path(dst_file) in dst_files

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_editable_project_path(self):
        pkg_name = "tst_pkg_editable"
        egg_link_file = pkg_name + '.egg-link'

        try:
            sys.path.insert(0, TESTS_FOLDER)
            write_file(egg_link_file, TESTS_FOLDER)

            assert editable_project_path(pkg_name) == TESTS_FOLDER

        finally:
            if sys.path[0] == TESTS_FOLDER:
                sys.path.pop(0)
            if os.path.exists(egg_link_file):
                os.remove(egg_link_file)

    def test_find_extra_modules(self):
        assert 'setup' in find_extra_modules("")
        assert 'setup' in find_extra_modules(os.getcwd())
        assert 'aedev.git_repo_manager.__main__' in find_extra_modules("")
        assert 'tests.test_git_repo_manager' in find_extra_modules("")
        assert 'git_repo_manager.__main__' in find_extra_modules(os.path.join(os.getcwd(), 'aedev'))
        assert find_extra_modules(os.getcwd(), 'aedev') == ['git_repo_manager.__main__']
        assert find_extra_modules(os.getcwd(), 'aedev', 'git_repo_manager') == ['__main__']

        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        tst_mod = "tst_mod"
        try:
            write_file(os.path.join(parent_dir, PY_INIT), "# test __init__.py", make_dirs=True)
            write_file(os.path.join(parent_dir, tst_mod + PY_EXT), "# test module")

            assert 'setup' in find_extra_modules("")
            assert 'aedev.git_repo_manager.__main__' in find_extra_modules("")
            assert find_extra_modules(parent_dir) == [tst_mod]
            assert find_extra_modules(TESTS_FOLDER, PARENT_FOLDERS[0]) == [tst_mod]
            assert find_extra_modules(TESTS_FOLDER, portion_name=PARENT_FOLDERS[0]) == [tst_mod]
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_find_git_branch_files_between_versions(self, mocked_app_options):
        mocked_app_options['verbose'] = False
        exp = last_exp = {
            'README.md',
            'aedev/git_repo_manager.py',
            'tests/test_git_repo_manager.py',
        }
        assert find_git_branch_files("", branch_or_tag="v0.3.59..v0.3.60") == exp

        extra_61 = {'requirements.txt'}
        exp = extra_61 | {
            'README.md',
            'aedev/git_repo_manager.py',
        }
        assert find_git_branch_files("", branch_or_tag="v0.3.60..v0.3.61") == exp
        assert find_git_branch_files("", branch_or_tag="v0.3.59..v0.3.61") == exp | last_exp

        exp = {
           'README.md',
           'aedev/git_repo_manager/__init__.py',
           'aedev/git_repo_manager/__main__.py',
           'tests/test_git_repo_manager.py',
        }
        assert find_git_branch_files("", branch_or_tag="v0.3.65..v0.3.66") == exp
        assert find_git_branch_files("", branch_or_tag="v0.3.65...v0.3.66") == exp
        most = find_git_branch_files("", branch_or_tag="v0.3.65...v0.3.66", untracked=True,
                                     skip_file_path=lambda _: PY_CACHE_FOLDER in _
                                                              or _.startswith(".idea")
                                                              or _.startswith(".mypy_cache")
                                                              or _.startswith(".pylint")
                                                              or _.startswith(".pytest_cache")
                                                              or _.startswith("htmlcov")
                                                              or _.startswith("mypy_report")
                                                              or _.startswith("aedev_git_repo_manager.egg-info")
                                     )
        assert all(_ in most for _ in exp)

        exp = big_exp = {
            '.gitignore',
            '.gitlab-ci.yml',
            'CONTRIBUTING.rst',
            'LICENSE.md',
            'README.md',
            'SECURITY.md',
            'aedev/git_repo_manager/__init__.py',
            'aedev/git_repo_manager/__main__.py',
            'dev_requirements.txt',
            'setup.py',
            'tests/conftest.py',
            'tests/requirements.txt',
        }
        assert find_git_branch_files("", branch_or_tag="v0.3.66..v0.3.67") == exp
        assert find_git_branch_files("", branch_or_tag="v0.3.66...v0.3.67") == exp

        extra_62 = {'pev.updates', 'tests/test_git_repo_manager.py'}
        assert find_git_branch_files("", branch_or_tag="v0.3.61...v0.3.62") == exp | extra_62  # ->pkg __init__/__main__
        assert find_git_branch_files("", branch_or_tag="v0.3.62...v0.3.63") == exp      # changed in v0.3.63

        assert find_git_branch_files("", branch_or_tag="v0.3.66...v0.3.69") == exp      # 3 versions

        exp = {
            'README.md',
            'aedev/git_repo_manager/__init__.py',
            'aedev/git_repo_manager/__main__.py',
        }
        assert find_git_branch_files("", branch_or_tag="v0.3.67..v0.3.68") == exp
        assert find_git_branch_files("", branch_or_tag="v0.3.67..v0.3.68") == exp

        assert find_git_branch_files("", branch_or_tag="v0.3.68..v0.3.69") == exp
        assert find_git_branch_files("", branch_or_tag="v0.3.68...v0.3.69") == exp

        assert find_git_branch_files("", branch_or_tag="v0.3.59...v0.3.69") == extra_61 | extra_62 | big_exp

    def test_find_git_branch_files_excludes(self, changed_repo_path, mocked_app_options):
        mocked_app_options['verbose'] = False
        all_fil = {'.gitignore', 'added.cfg', 'changed.py', 'delete.txt'}
        assert find_git_branch_files(changed_repo_path, untracked=True) == all_fil
        assert find_git_branch_files(changed_repo_path) == all_fil - {'.gitignore', 'added.cfg'}
        assert find_git_branch_files(changed_repo_path, skip_file_path=lambda _: _ != 'delete.txt') == {'delete.txt'}
        assert find_git_branch_files(changed_repo_path, skip_file_path=lambda _: _ == 'delete.txt') == {'changed.py'}

    def test_find_git_branch_files_in_worktree(self, changed_repo_path, mocked_app_options):
        mocked_app_options['force'] = False
        mocked_app_options['verbose'] = False
        pev = {'project_path': changed_repo_path}
        branch = "tst_branch"

        def _git_dif(*_args) -> list:
            return _git_diff(pev, "--name-only", *_args)

        def _git_lsf(*_args) -> list:
            _output = []
            with _in_prj_dir_venv(changed_repo_path):
                _cl(0, "git ls-files", extra_args=_args, lines_output=_output)
            return _output

        def _git_sta() -> list:
            gst = _git_status(pev)          # NOTE: [:3]-output-format differs if cae..get_option('verbose') is True
            return [_[3:] for _ in gst]

        def _always_all_files() -> set:
            return set(_git_lsf("--cached", "--others") + _git_sta() + _git_dif("--diff-filter=ABCDMRTUX", MAIN_BRANCH))

        assert _git_current_branch(pev) == MAIN_BRANCH

        assert (set([os.path.relpath(_, changed_repo_path) for _ in path_items(os.path.join(changed_repo_path, "*"))])
                == {'added.cfg', 'changed.py'})    # plus delete.txt and .gitignore (not seen via "*" wildcard

        all_fil = {'.gitignore', 'added.cfg', 'changed.py', 'delete.txt'}

        assert set(_git_dif()) == {'changed.py', 'delete.txt'}
        assert set(_git_dif("--cached")) == set()
        assert set(_git_dif("--cached", "--diff-filter=ABCDMRTUX", "HEAD")) == set()
        assert set(_git_dif("--diff-filter=ABCDMRTUX")) == {'changed.py', 'delete.txt'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", "HEAD")) == {'changed.py', 'delete.txt'}
        assert set(_git_lsf("--cached")) == {'.gitignore', 'changed.py', 'delete.txt'}
        assert set(_git_lsf("--deleted")) == {'delete.txt'}
        assert set(_git_lsf("--modified")) == {'changed.py', 'delete.txt'}
        assert set(_git_lsf("--others")) == {'added.cfg'}
        assert set(_git_lsf("--unmerged")) == set()
        assert set(_git_sta()) == {'added.cfg', 'changed.py', 'delete.txt'}

        assert set(_git_lsf("--cached", "--others")) == all_fil
        assert set(_git_lsf("--cached", "--others") + _git_sta()) == all_fil
        assert set(_git_dif("--diff-filter=ABCDMRTUX", MAIN_BRANCH)) == all_fil - {'.gitignore', 'added.cfg'}
        assert _always_all_files() == all_fil
        assert find_git_branch_files(changed_repo_path, untracked=True) == all_fil

        add2_subdir = os.path.join("subdir", "sub_subdir")
        add2_path = os.path.join(add2_subdir, "add2.yml")
        os.makedirs(os.path.join(changed_repo_path, add2_subdir))
        write_file(os.path.join(changed_repo_path, add2_path), "# new file content")    # ADD add2.yml in subdir

        _git_checkout(pev, branch=branch)                                               # reNEW branch
        assert _git_current_branch(pev) == branch

        all_fil = {'.gitignore', 'added.cfg', add2_path, 'changed.py', 'delete.txt'}

        assert set(_git_dif()) == {'changed.py', 'delete.txt'}
        assert set(_git_dif("--cached")) == set()
        assert set(_git_dif("--cached", "--diff-filter=ABCDMRTUX", "HEAD")) == set()
        assert set(_git_dif("--diff-filter=ABCDMRTUX")) == {'changed.py', 'delete.txt'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", "HEAD")) == {'changed.py', 'delete.txt'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", branch)) == {'changed.py', 'delete.txt'}
        assert set(_git_lsf("--cached")) == {'.gitignore', 'changed.py', 'delete.txt'}
        assert set(_git_lsf("--deleted")) == {'delete.txt'}
        assert set(_git_lsf("--modified")) == {'changed.py', 'delete.txt'}
        assert set(_git_lsf("--others")) == {'added.cfg', add2_path}
        assert set(_git_lsf("--unmerged")) == set()     # unknown option "--format='%(path)'"
        assert set(_git_sta()) == {'added.cfg', add2_path, 'changed.py', 'delete.txt'}

        assert set(_git_lsf("--cached", "--others")) == all_fil
        assert set(_git_lsf("--cached", "--others") + _git_sta()) == all_fil
        assert set(_git_dif("--diff-filter=ABCDMRTUX", MAIN_BRANCH)) == all_fil - {'.gitignore', 'added.cfg', add2_path}
        assert _always_all_files() == all_fil
        assert find_git_branch_files(changed_repo_path, untracked=True) == all_fil

        _git_add(pev)                                                                   # ADD changes to the branch

        chg_file = os.path.join(changed_repo_path, 'changed.py')
        write_file(chg_file, read_file(chg_file) + os.linesep + "# changed")            # UPDATE changed.py

        nearly_all_fil = {'added.cfg', add2_path, 'changed.py', 'delete.txt'}   # .gitignore missing
        assert set(_git_dif()) == {'changed.py'}
        assert set(_git_dif("--cached")) == nearly_all_fil
        assert set(_git_dif("--cached", "--diff-filter=ABCDMRTUX", "HEAD")) == nearly_all_fil
        assert set(_git_dif("--diff-filter=ABCDMRTUX")) == {'changed.py'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", "HEAD")) == nearly_all_fil
        assert set(_git_dif("--diff-filter=ABCDMRTUX", branch)) == nearly_all_fil
        assert set(_git_lsf("--cached")) == {'.gitignore', 'added.cfg', add2_path, 'changed.py'}
        assert set(_git_lsf("--deleted")) == set()
        assert set(_git_lsf("--modified")) == {'changed.py'}
        assert set(_git_lsf("--others")) == set()
        assert set(_git_lsf("--unmerged")) == set()     # unknown option "--format='%(path)'"
        assert set(_git_sta()) == nearly_all_fil

        assert set(_git_lsf("--cached", "--others") + _git_sta()) == all_fil
        assert set(_git_dif("--diff-filter=ABCDMRTUX", MAIN_BRANCH)) == all_fil - {'.gitignore'}
        assert _always_all_files() == all_fil
        assert find_git_branch_files(changed_repo_path, untracked=True) == all_fil

        write_file(os.path.join(changed_repo_path, COMMIT_MSG_FILE_NAME), "commit tst msg")
        _git_commit(pev)                                                                # COMMIT 1

        all_fil = {'.commit_msg.txt', '.gitignore', 'added.cfg', add2_path, 'changed.py', 'delete.txt'}

        assert set(_git_dif()) == {'changed.py'}
        assert set(_git_dif("--cached")) == set()
        assert set(_git_dif("--cached", "--diff-filter=ABCDMRTUX", "HEAD")) == set()
        assert set(_git_dif("--diff-filter=ABCDMRTUX")) == {'changed.py'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", "HEAD")) == {'changed.py'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", branch)) == {'changed.py'}
        assert set(_git_lsf("--cached")) == {'.gitignore', 'added.cfg', add2_path, 'changed.py'}
        assert set(_git_lsf("--deleted")) == set()
        assert set(_git_lsf("--modified")) == {'changed.py'}
        assert set(_git_lsf("--others")) == {'.commit_msg.txt'}
        assert set(_git_lsf("--unmerged")) == set()     # unknown option "--format='%(path)'"
        assert set(_git_sta()) == {'changed.py'}

        assert set(_git_lsf("--cached", "--others") + _git_sta()) == all_fil - {'delete.txt'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", MAIN_BRANCH)) == all_fil - {'.commit_msg.txt', '.gitignore'}
        assert _always_all_files() == all_fil
        assert find_git_branch_files(changed_repo_path, untracked=True) == all_fil

        chg_file = os.path.join(changed_repo_path, 'changed.py')
        write_file(chg_file, read_file(chg_file) + os.linesep + "# change 2")           # CHANGE 2 of changed.py
        add3_path = os.path.join(add2_subdir, 'module.py')
        write_file(os.path.join(changed_repo_path, add3_path), "# new")                 # ADD module.py in subdir

        all_fil = {'.commit_msg.txt', '.gitignore', 'added.cfg', add2_path, add3_path, 'changed.py', 'delete.txt'}

        assert set(_git_dif()) == {'changed.py'}
        assert set(_git_dif("--cached")) == set()
        assert set(_git_dif("--cached", "--diff-filter=ABCDMRTUX", "HEAD")) == set()
        assert set(_git_dif("--diff-filter=ABCDMRTUX")) == {'changed.py'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", "HEAD")) == {'changed.py'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", branch)) == {'changed.py'}
        assert set(_git_lsf("--cached")) == {'.gitignore', 'added.cfg', add2_path, 'changed.py'}
        assert set(_git_lsf("--deleted")) == set()
        assert set(_git_lsf("--modified")) == {'changed.py'}
        assert set(_git_lsf("--others")) == {'.commit_msg.txt', add3_path}
        assert set(_git_lsf("--unmerged")) == set()     # unknown option "--format='%(path)'"
        assert set(_git_sta()) == {add3_path, 'changed.py'}

        assert set(_git_lsf("--cached", "--others") + _git_sta()) == all_fil - {'delete.txt'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", MAIN_BRANCH)) == all_fil - {'.commit_msg.txt', '.gitignore',
                                                                                   add3_path}
        assert _always_all_files() == all_fil
        assert find_git_branch_files(changed_repo_path, untracked=True) == all_fil

        add2_ren_path = os.path.join(add2_subdir, 'renamed_add2.yml')                   # RENAME add2.yml
        os.rename(os.path.join(changed_repo_path, add2_path), os.path.join(changed_repo_path, add2_ren_path))

        all_fil = {'.commit_msg.txt', '.gitignore', 'added.cfg', add2_path, add2_ren_path, add3_path, 'changed.py',
                   'delete.txt'}

        assert set(_git_dif()) == {add2_path, 'changed.py'}
        assert set(_git_dif("--cached")) == set()
        assert set(_git_dif("--cached", "--diff-filter=ABCDMRTUX", "HEAD")) == set()
        assert set(_git_dif("--diff-filter=ABCDMRTUX")) == {add2_path, 'changed.py'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", "HEAD")) == {add2_path, 'changed.py'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", branch)) == {add2_path, 'changed.py'}
        assert set(_git_lsf("--cached")) == {'.gitignore', 'added.cfg', add2_path, 'changed.py'}
        assert set(_git_lsf("--deleted")) == {add2_path}
        assert set(_git_lsf("--modified")) == {add2_path, 'changed.py'}
        assert set(_git_lsf("--others")) == {'.commit_msg.txt', add2_ren_path, add3_path}
        assert set(_git_lsf("--unmerged")) == set()     # unknown option "--format='%(path)'"
        assert set(_git_sta()) == {add2_path, add2_ren_path, add3_path, 'changed.py'}

        assert set(_git_lsf("--cached", "--others") + _git_sta()) == all_fil - {'delete.txt'}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", MAIN_BRANCH)) == all_fil - {'.commit_msg.txt', '.gitignore',
                                                                                   add2_path, add2_ren_path, add3_path}
        assert _always_all_files() == all_fil
        assert find_git_branch_files(changed_repo_path, untracked=True) == all_fil

        _git_add(pev)
        _git_commit(pev)                                                                # COMMIT 2

        assert set(_git_dif()) == set()
        assert set(_git_dif("--cached")) == set()
        assert set(_git_dif("--cached", "--diff-filter=ABCDMRTUX", "HEAD")) == set()
        assert set(_git_dif("--diff-filter=ABCDMRTUX")) == set()
        assert set(_git_dif("--diff-filter=ABCDMRTUX", "HEAD")) == set()
        assert set(_git_dif("--diff-filter=ABCDMRTUX", branch)) == set()
        assert set(_git_lsf("--cached")) == {'.gitignore', 'added.cfg', add2_ren_path, add3_path, 'changed.py'}
        assert set(_git_lsf("--deleted")) == set()
        assert set(_git_lsf("--modified")) == set()
        assert set(_git_lsf("--others")) == {'.commit_msg.txt'}
        assert set(_git_lsf("--unmerged")) == set()     # unknown option "--format='%(path)'"
        assert set(_git_sta()) == set()

        assert set(_git_lsf("--cached", "--others") + _git_sta()) == all_fil - {'delete.txt', add2_path}
        assert set(_git_dif("--diff-filter=ABCDMRTUX", MAIN_BRANCH)) == all_fil - {'.commit_msg.txt', '.gitignore',
                                                                                   add2_path}
        assert _always_all_files() == all_fil - {add2_path}     # nearly all files, only missing deleted/renamed file
        assert find_git_branch_files(changed_repo_path, untracked=True) == all_fil - {add2_path}

    def test_find_project_files(self):
        assert not find_project_files("", [])
        assert find_project_files("", []) == set()
        assert not find_project_files("", ['NonExistingPackageName'])

        modules = {f'aedev/git_repo_manager/{PY_INIT}', f'aedev/git_repo_manager/{PY_MAIN}'}
        assert find_project_files(os.getcwd(), ['aedev/git_repo_manager/**/*.py']) == modules
        assert find_project_files("", ['aedev/git_repo_manager/*.py']) == modules
        assert find_project_files("", ['aedev/**/*.py']) == modules
        assert (find_project_files("", ['aedev/git_repo_manager/*.py'], skip_file_path=lambda fp: fp.endswith(PY_INIT))
                == {f"aedev/git_repo_manager/{PY_MAIN}"})

    def test_increment_version(self):
        assert increment_version("") == ""
        assert increment_version("0.0.1") == "0.0.2"
        assert increment_version("9999.9999.9999") == "9999.9999.10000"

        assert increment_version(NULL_VERSION, increment_part=0) == NULL_VERSION
        assert increment_version(NULL_VERSION, increment_part=1) == "1.0.0"
        assert increment_version(NULL_VERSION, increment_part=2) == "0.1.0"
        # noinspection PyArgumentEqualDefault
        assert increment_version(NULL_VERSION, increment_part=3) == "0.0.1"

        assert increment_version(("0", "1", "2"), increment_part=0) == "0.1.2"
        assert increment_version(("0", "1", "2"), increment_part=1) == "1.1.2"
        assert increment_version(("0", "1", "2"), increment_part=2) == "0.2.2"
        assert increment_version(("0", "1", "2")) == "0.1.3"

        assert increment_version(NULL_VERSION, increment_part=-1) == NULL_VERSION
        assert increment_version(NULL_VERSION, increment_part=4) == NULL_VERSION

    def test_in_venv(self):
        cur_venv = active_venv()
        with in_venv(LOCAL_VENV):
            assert active_venv() == '' if 'CI_PROJECT_ID' in os.environ else LOCAL_VENV
        assert active_venv() == cur_venv

    @skip_gitlab_ci
    def test_on_ci_host_local(self):
        assert not on_ci_host()

    def test_on_ci_host_on_gitlab(self):
        assert on_ci_host() == ('CI_PROJECT_ID' in os.environ)

    def test_project_version(self):
        pkg, ver = project_version('a.b', ['a_b', 'b_c'])
        assert pkg == 'a_b'
        assert ver == ""

        pkg, ver = project_version('a.b', ['bc', 'c_d', 'a_b==1.2.3'])
        assert pkg == 'a_b'
        assert ver == "1.2.3"

    def test_patch_string_empty_args(self):
        assert patch_string("", {}, invalid_place_holder_id=lambda s: "") == ""

    def test_project_dev_vars_not_exists(self, mocked_app_options):
        mocked_app_options['group'] = None
        mocked_app_options['namespace'] = ""
        new_pkg_name = "new_pkg_nam"
        new_prj_path = os.path.join(os.path.dirname(os.getcwd()), new_pkg_name)

        pdv = project_dev_vars(project_path=new_prj_path)
        assert 'namespace_name' in pdv
        assert pdv['namespace_name'] == ''
        assert 'project_name' in pdv
        assert pdv['project_name'] == new_pkg_name
        assert 'project_path' in pdv
        assert pdv['project_path'] == new_prj_path
        assert 'project_type' in pdv
        assert pdv['project_type'] == NO_PRJ
        assert pdv['repo_group'].startswith(new_pkg_name)

        nsn = 'nsn'
        mocked_app_options['namespace'] = nsn
        new_pkg_name = nsn + '_' + new_pkg_name
        new_prj_path = os.path.join(os.path.dirname(os.getcwd()), new_pkg_name)
        pdv = project_dev_vars(project_path=new_prj_path)
        assert pdv['namespace_name'] == nsn
        assert pdv['project_name'] == new_pkg_name
        assert pdv['project_path'] == new_prj_path
        assert pdv['project_type'] == NO_PRJ
        assert pdv['repo_group'].startswith(new_pkg_name)

        mocked_app_options['group'] = "tst-group"
        pdv = project_dev_vars(project_path=new_prj_path)
        assert pdv['namespace_name'] == nsn
        assert pdv['project_name'] == new_pkg_name
        assert pdv['project_path'] == new_prj_path
        assert pdv['project_type'] == NO_PRJ
        assert pdv['repo_group'] == mocked_app_options['group']

    def test_project_dev_vars_namespace_module(self, mocked_app_options):
        mocked_app_options['group'] = "tst_grp"
        mocked_app_options['namespace'] = ""
        nsn = 'abc'
        mocked_app_options[_template_version_option(nsn + '.' + nsn)] = ""

        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        portion_name = 'tst_ns_mod'
        project_path = os.path.join(parent_dir, nsn + '_' + portion_name)
        module_path = os.path.join(project_path, nsn, portion_name + PY_EXT)

        try:
            os.makedirs(os.path.dirname(module_path))
            write_file(module_path, f"mod_content = ''{os.linesep}__version__ = '3.3.3'{os.linesep}")

            pdv = project_dev_vars(project_path=project_path)
            assert pdv['namespace_name'] == nsn
            assert pdv['project_name'] == nsn + '_' + portion_name
            assert pdv['package_path'] == os.path.join(norm_path(project_path), nsn, portion_name)
            assert pdv['project_path'] == norm_path(project_path)
            assert pdv['project_type'] == MODULE_PRJ
            assert pdv['repo_group'] == mocked_app_options['group']
            assert pdv['version_file'] == norm_path(module_path)

            pdv = project_dev_vars(project_path=parent_dir)
            assert pdv['namespace_name'] == ""
            assert pdv['project_name'] == os.path.basename(parent_dir)
            assert pdv['project_path'] == norm_path(parent_dir)
            assert pdv['project_type'] == PARENT_PRJ
            assert pdv['repo_group'] == mocked_app_options['group']
            assert f"{nsn}_{portion_name}" in pdv['children_project_vars']
            assert 'portions_import_names' not in pdv

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_project_dev_vars_namespace_package(self, mocked_app_options):
        mocked_app_options['group'] = "tst_grp"
        mocked_app_options['namespace'] = ""
        nsn = 'efg'
        mocked_app_options[_template_version_option(nsn + '.' + nsn)] = ""

        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        portion_name = 'tst_ns_pkg'
        project_path = os.path.join(parent_dir, nsn + '_' + portion_name)
        package_path = os.path.join(project_path, nsn, portion_name)

        try:
            os.makedirs(package_path)
            write_file(os.path.join(package_path, PY_INIT),
                       f"pkg_ini_content = ''{os.linesep}__version__ = '6.3.6'{os.linesep}")

            pdv = project_dev_vars(project_path=project_path)
            assert pdv['namespace_name'] == nsn
            assert pdv['project_name'] == nsn + '_' + portion_name
            assert pdv['package_path'] == norm_path(package_path)
            assert pdv['project_path'] == norm_path(project_path)
            assert pdv['project_type'] == PACKAGE_PRJ
            assert pdv['repo_group'] == mocked_app_options['group']
            assert pdv['version_file'] == norm_path(os.path.join(package_path, PY_INIT))

            mocked_app_options['namespace'] = nsn
            pdv = project_dev_vars(project_path=project_path)
            assert pdv['namespace_name'] == nsn
            assert pdv['project_name'] == nsn + '_' + portion_name
            assert pdv['package_path'] == norm_path(package_path)
            assert pdv['project_path'] == norm_path(project_path)
            assert pdv['project_type'] == PACKAGE_PRJ
            assert pdv['repo_group'] == mocked_app_options['group']
            assert pdv['version_file'] == norm_path(os.path.join(package_path, PY_INIT))

            mocked_app_options['namespace'] = ""
            pdv = project_dev_vars(project_path=parent_dir)
            assert pdv['namespace_name'] == ""
            assert pdv['project_name'] == os.path.basename(parent_dir)
            assert pdv['project_path'] == norm_path(parent_dir)
            assert pdv['project_type'] == PARENT_PRJ
            assert pdv['repo_group'] == mocked_app_options['group']
            assert f"{nsn}_{portion_name}" in pdv['children_project_vars']
            assert 'portions_import_names' not in pdv

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_project_dev_vars_namespace_root(self, mocked_app_options):
        mocked_app_options['group'] = "tst_grp"
        mocked_app_options['namespace'] = ""
        nsn = 'hij'
        mocked_app_options[_template_version_option(nsn + '.' + nsn)] = ""

        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_path = os.path.join(parent_dir, nsn + '_' + nsn)
        package_path = os.path.join(project_path, nsn, nsn)

        try:
            os.makedirs(package_path)
            write_file(os.path.join(package_path, PY_INIT),
                       f"root_content = ''{os.linesep}__version__ = '9.9.3'{os.linesep}")

            pdv = project_dev_vars(project_path=project_path)
            assert pdv['namespace_name'] == nsn
            assert pdv['project_name'] == nsn + '_' + nsn
            assert pdv['package_path'] == norm_path(package_path)
            assert pdv['project_path'] == norm_path(project_path)
            assert pdv['project_type'] == ROOT_PRJ
            assert pdv['repo_group'] == mocked_app_options['group']
            assert pdv['version_file'] == norm_path(os.path.join(package_path, PY_INIT))
            assert not pdv['children_project_vars']
            assert not pdv['portions_import_names']

            mocked_app_options['namespace'] = nsn
            pdv = project_dev_vars(project_path=project_path)
            assert pdv['namespace_name'] == nsn
            assert pdv['project_name'] == nsn + '_' + nsn
            assert pdv['package_path'] == norm_path(package_path)
            assert pdv['project_path'] == norm_path(project_path)
            assert pdv['project_type'] == ROOT_PRJ
            assert pdv['repo_group'] == mocked_app_options['group']
            assert pdv['version_file'] == norm_path(os.path.join(package_path, PY_INIT))
            assert not pdv['children_project_vars']
            assert not pdv['portions_import_names']

            mocked_app_options['namespace'] = ""
            pdv = project_dev_vars(project_path=parent_dir)
            assert pdv['namespace_name'] == ""
            assert pdv['project_name'] == os.path.basename(parent_dir)
            assert pdv['project_path'] == norm_path(parent_dir)
            assert pdv['project_type'] == PARENT_PRJ
            assert pdv['repo_group'] == mocked_app_options['group']
            assert f"{nsn}_{nsn}" in pdv['children_project_vars']
            assert 'portions_import_names' not in pdv

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_project_dev_vars_namespace_root_portions(self, mocked_app_options):
        mocked_app_options['group'] = "tst_grp"
        mocked_app_options['namespace'] = ""
        nsn = 'uvw'
        mocked_app_options[_template_version_option(nsn + '.' + nsn)] = ""

        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        root_prj_path = os.path.join(parent_dir, nsn + '_' + nsn)
        root_pkg_path = os.path.join(root_prj_path, nsn, nsn)

        project_name = 'tst_ns_pkg'
        package_prj_path = os.path.join(parent_dir, nsn + '_' + project_name)
        package_pkg_path = os.path.join(package_prj_path, nsn, project_name)
        package_extra_module_name = "extra_module_name"

        module_name = 'tst_ns_module'
        module_prj_path = os.path.join(parent_dir, nsn + '_' + module_name)
        module_path = os.path.join(module_prj_path, nsn, module_name + PY_EXT)

        try:
            os.makedirs(root_pkg_path)
            write_file(os.path.join(root_pkg_path, PY_INIT),
                       f"root_content = ''{os.linesep}__version__ = '111.33.63'{os.linesep}")
            write_file(os.path.join(root_prj_path, REQ_DEV_FILE_NAME),
                       nsn + '_' + project_name + os.linesep + nsn + '_' + module_name)

            write_file(os.path.join(package_pkg_path, PY_INIT),
                       f"pkg_content = ''{os.linesep}__version__ = '999.333.636'{os.linesep}",
                       make_dirs=True)
            write_file(os.path.join(package_pkg_path, package_extra_module_name + PY_EXT), "extra_content = ''")

            os.makedirs(os.path.dirname(module_path))
            write_file(os.path.join(module_prj_path, nsn, module_name),
                       f"mod_content = ''{os.linesep}__version__ = '6.9.699'{os.linesep}")

            pdv = project_dev_vars(project_path=root_prj_path)
            assert pdv['namespace_name'] == nsn
            assert pdv['project_name'] == nsn + '_' + nsn
            assert pdv['package_path'] == norm_path(root_pkg_path)
            assert pdv['project_path'] == norm_path(root_prj_path)
            assert pdv['project_type'] == ROOT_PRJ
            assert pdv['repo_group'] == mocked_app_options['group']
            assert pdv['version_file'] == norm_path(os.path.join(root_pkg_path, PY_INIT))

            assert f"{nsn}_{project_name}" in pdv['children_project_vars']
            assert f"{nsn}_{project_name}.{package_extra_module_name}" not in pdv['children_project_vars']
            assert f"{nsn}_{module_name}" in pdv['children_project_vars']

            assert f"{nsn}.{project_name}" in pdv['portions_import_names']
            assert f"{nsn}.{project_name}.{package_extra_module_name}" in pdv['portions_import_names']
            assert f"{nsn}.{module_name}" in pdv['portions_import_names']

            mocked_app_options['namespace'] = nsn
            pdv = project_dev_vars(project_path=root_prj_path)
            assert pdv['namespace_name'] == nsn
            assert pdv['project_name'] == nsn + '_' + nsn
            assert pdv['package_path'] == os.path.join(norm_path(root_prj_path), nsn, nsn)
            assert pdv['project_path'] == norm_path(root_prj_path)
            assert pdv['project_type'] == ROOT_PRJ
            assert pdv['repo_group'] == mocked_app_options['group']
            assert pdv['version_file'] == norm_path(os.path.join(root_pkg_path, PY_INIT))

            assert f"{nsn}_{project_name}" in pdv['children_project_vars']
            assert f"{nsn}_{project_name}.{package_extra_module_name}" not in pdv['children_project_vars']
            assert f"{nsn}_{module_name}" in pdv['children_project_vars']

            assert f"{nsn}.{project_name}" in pdv['portions_import_names']
            assert f"{nsn}.{project_name}.{package_extra_module_name}" in pdv['portions_import_names']
            assert f"{nsn}.{module_name}" in pdv['portions_import_names']

            mocked_app_options['namespace'] = ""
            pdv = project_dev_vars(project_path=parent_dir)
            assert pdv['namespace_name'] == ""
            assert pdv['project_name'] == os.path.basename(parent_dir)
            assert pdv['project_path'] == norm_path(parent_dir)
            assert pdv['project_type'] == PARENT_PRJ
            assert pdv['repo_group'] == mocked_app_options['group']
            assert f"{nsn}_{project_name}" in pdv['children_project_vars']
            assert f"{nsn}_{project_name}.{package_extra_module_name}" not in pdv['children_project_vars']
            assert f"{nsn}_{module_name}" in pdv['children_project_vars']
            assert 'portions_import_names' not in pdv

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_pypi_versions(self):
        assert pypi_versions("") == [""]
        assert pypi_versions("non_existing_pypi_package") == [""]
        assert "0.3.54" in pypi_versions("ae_base")
        assert "0.3.90" in pypi_versions("aedev_git_repo_manager")

    def test_refresh_templates_empty_args(self):
        assert refresh_templates({}) == set()

    def test_refresh_templates_test_registered(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        namespace = "nsn"
        project_name = f"{namespace}_pkg_name"
        project_path = norm_path(join(parent_dir, project_name))
        tpl_projects = [
            {'import_name': namespace + '.' + namespace,
             'tpl_path': join(parent_dir, namespace + '_' + namespace, namespace, namespace, TEMPLATES_FOLDER),
             'version': '1.1.1'},
            {'import_name': TPL_IMPORT_NAME_PREFIX + 'project',
             'tpl_path': join(parent_dir, 'aedev_tpl_package', 'aedev', 'tpl_package', TEMPLATES_FOLDER),
             'version': '3.3.3'},
            {'import_name': TPL_IMPORT_NAME_PREFIX + 'project',
             'tpl_path': join(parent_dir, 'aedev_tpl_project', 'aedev', 'tpl_project', TEMPLATES_FOLDER),
             'version': '9.9.9'},
        ]

        try:
            pdv = {'namespace_name': namespace, 'project_name': project_name,
                   'project_path': project_path, 'project_type': PACKAGE_PRJ}
            _renew_prj_dir(pdv)

            assert not refresh_templates({'project_path': project_path})   # first test w/o created template folders

            assert os.path.isdir(project_path)
            assert not os.path.isdir(join(project_path, DOCS_FOLDER))
            assert not os.path.isdir(join(project_path, TEMPLATES_FOLDER))
            assert os.path.isdir(join(project_path, TESTS_FOLDER))
            assert os.path.isfile(join(project_path, namespace, project_name[len(namespace) + 1:], PY_INIT))
            assert not os.path.isfile(join(project_path, BUILD_CONFIG_FILE))

            deep_sub_dir = join('deeper', 'even_deeper')
            file_for_all = 'file_for_all.ext'
            tpl_file_for_all = OUTSOURCED_FILE_NAME_PREFIX + TPL_FILE_NAME_PREFIX + file_for_all
            for tpl_reg in tpl_projects:
                tpl_path = join(tpl_reg['tpl_path'], deep_sub_dir)
                write_file(join(tpl_path, tpl_file_for_all), tpl_reg['tpl_path'], make_dirs=True)
            tpl_file = join(project_path, deep_sub_dir, file_for_all)

            # 2nd test with template in all templates (root prj has the highest priority)
            pdv = {'namespace_name': namespace, 'project_path': project_path, 'project_type': PACKAGE_PRJ,
                   'TEMPLATES_FOLDER': TEMPLATES_FOLDER, 'tpl_projects': tpl_projects}
            assert refresh_templates(pdv) == {norm_path(tpl_file)}

            assert os.path.isfile(tpl_file)
            content = read_file(tpl_file)
            assert tpl_projects[0]['tpl_path'] in content
            assert OUTSOURCED_MARKER in content

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_refresh_templates_file_include_content(self):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        tpl_pkg_path = norm_path(join(parent_dir, 'tpl_prj'), TEMPLATES_FOLDER)
        tpl_file_name = "including_content.txt"
        tpl_file_path = join(tpl_pkg_path, OUTSOURCED_FILE_NAME_PREFIX + TPL_FILE_NAME_PREFIX + tpl_file_name)
        ver = '9.6.9999'
        tpl_projects = [{'import_name': TPL_IMPORT_NAME_PREFIX + 'project', 'tpl_path': tpl_pkg_path, 'version': ver}]
        included_file_name = norm_path(join(parent_dir, "inc.tst.file"))
        included_file_content = "replacement string"
        project_name = f"prj_name"
        project_path = join(parent_dir, project_name)
        patched_file_name = join(project_path, tpl_file_name)
        cur_dir = os.getcwd()
        try:
            os.makedirs(project_path)
            os.makedirs(tpl_pkg_path)

            tpl = f"{TEMPLATE_PLACEHOLDER_ID_PREFIX}{TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID}"
            tpl += f"{TEMPLATE_PLACEHOLDER_ID_SUFFIX}{included_file_name}{TEMPLATE_PLACEHOLDER_ARGS_SUFFIX}"
            write_file(tpl_file_path, tpl)
            write_file(included_file_name, included_file_content)

            os.chdir(project_path)
            patched = refresh_templates({'TEMPLATES_FOLDER': "", 'tpl_projects': tpl_projects})
            os.chdir(cur_dir)

            assert patched == {norm_path(patched_file_name)}

            content = read_file(patched_file_name)
            assert included_file_content in content
            assert ver in content
            assert "TEMPLATE_PLACEHOLDER_ID_PREFIX" not in content
            assert TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID not in content
            assert "TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID" not in content
            assert TEMPLATE_PLACEHOLDER_ID_SUFFIX not in content
            assert "TEMPLATE_PLACEHOLDER_ID_SUFFIX" not in content
            assert TEMPLATE_PLACEHOLDER_ARGS_SUFFIX not in content
            assert "TEMPLATE_PLACEHOLDER_ARGS_SUFFIX" not in content
        finally:
            os.chdir(cur_dir)
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_refresh_templates_file_include_default_and_with_pev_vars(self, mocked_app_options):
        join = os.path.join
        parent_dir = join(TESTS_FOLDER, PARENT_FOLDERS[0])
        namespace_name = "tns"
        portion_name = 'destination_portion_name'
        project_path = join(parent_dir, f'{namespace_name}_{portion_name}')
        package_path = join(project_path, namespace_name)
        patched_file = "including_content.txt"
        patched_path = join(project_path, patched_file)

        tpl_imp_name = namespace_name + '.' + namespace_name
        tpl_pkg_path = norm_path(join(parent_dir, norm_name(tpl_imp_name),
                                      namespace_name, namespace_name, TEMPLATES_FOLDER))
        tpl_file_path = join(tpl_pkg_path, OUTSOURCED_FILE_NAME_PREFIX + TPL_FILE_NAME_PREFIX + patched_file)

        default = "include file default string"
        version = '6.699.987'
        tpl_projects = [{'import_name': tpl_imp_name, 'tpl_path': tpl_pkg_path, 'version': version}]
        REGISTERED_TPL_PROJECTS[tpl_imp_name + PROJECT_VERSION_SEP + version] = tpl_projects[0]
        mocked_app_options[_template_version_option(tpl_imp_name)] = version
        mocked_app_options['namespace'] = namespace_name    # or ""
        try:
            os.makedirs(package_path)
            write_file(os.path.join(project_path, REQ_DEV_FILE_NAME), norm_name(tpl_imp_name))
            write_file(os.path.join(package_path, portion_name + PY_EXT), "__version__ = '9.6.3'")

            os.makedirs(os.path.dirname(tpl_file_path))
            tpl = "{TEMPLATE_PLACEHOLDER_ID_PREFIX}{TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID}"
            tpl += "{TEMPLATE_PLACEHOLDER_ID_SUFFIX}"
            tpl += f"not_existing_included_file_name.ext,{default}"
            tpl += "{TEMPLATE_PLACEHOLDER_ARGS_SUFFIX}"
            write_file(tpl_file_path, tpl)

            pdv = project_dev_vars(project_path=project_path)

            if on_ci_host():
                assert 'tpl_projects' not in pdv
                assert refresh_templates(pdv) == set()
                assert not os.path.isfile(patched_path)
            else:
                assert pdv['tpl_projects'] == tpl_projects
                assert refresh_templates(pdv) == {norm_path(patched_path)}
                content = read_file(patched_path)
                assert default in content
                assert tpl_imp_name in content
                assert version in content
                assert "TEMPLATE_PLACEHOLDER_ID_PREFIX" not in content
                assert TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID not in content
                assert "TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID" not in content
                assert TEMPLATE_PLACEHOLDER_ID_SUFFIX not in content
                assert "TEMPLATE_PLACEHOLDER_ID_SUFFIX" not in content
                assert TEMPLATE_PLACEHOLDER_ARGS_SUFFIX not in content
                assert "TEMPLATE_PLACEHOLDER_ARGS_SUFFIX" not in content
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)
            del REGISTERED_TPL_PROJECTS[tpl_imp_name + PROJECT_VERSION_SEP + version]

    def test_replace_file_version(self):
        tst_file = os.path.join(TESTS_FOLDER, 'test_bump_version' + PY_EXT)
        try:
            write_file(tst_file, f"__version__ = '1.2.3'{os.linesep}")

            err = replace_file_version(tst_file, increment_part=3, new_version='1.2.6')

            assert not err

            content = read_file(tst_file)
            assert "__version__ = '1.2.3'" not in content
            assert "__version__ = '1.2.7'" in content
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_replace_with_file_content_or_default(self):
        assert replace_with_file_content_or_default("") == ""

        def_val = "default_value"
        assert replace_with_file_content_or_default(f"_non_file,{def_val}") == def_val
        assert replace_with_file_content_or_default(f"_non_file,{def_val},{def_val}") == def_val + "," + def_val

        assert replace_with_file_content_or_default(f"_non_file,'{def_val[:3]}' + '{def_val[3:]}'") == def_val
        assert replace_with_file_content_or_default(f"_non_file,369") == 369
        with pytest.raises(ValueError):
            assert replace_with_file_content_or_default(f"_non_file,{'a': 111}")
        with pytest.raises(ValueError):
            assert replace_with_file_content_or_default(f"_non_file,{3: '111'}")
        assert replace_with_file_content_or_default(f"_non_file,{111}") == 111
        assert replace_with_file_content_or_default(f"_non_file,[111]") == [111]
        assert replace_with_file_content_or_default(f"_non_file,(1, 2, 3)") == (1, 2, 3)

        syntax_err = "syntax error ' + 1"
        assert replace_with_file_content_or_default("_non_file," + syntax_err) == syntax_err

        file_name = os.path.join(TESTS_FOLDER, "returned_file.txt")
        content = "file_content_to_be_returned"
        try:
            assert replace_with_file_content_or_default(f"{file_name},{def_val}") == def_val
            write_file(file_name, content)
            assert replace_with_file_content_or_default(file_name) == content
            assert replace_with_file_content_or_default(f"{file_name},{def_val}") == content
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def test_root_packages_masks(self):
        pdv = {'project_packages': ['x.y.z']}
        assert root_packages_masks(pdv) == ['x/**/*']

        pdv = {'project_packages': ['x.y.z', 'x.a.b.d']}
        assert root_packages_masks(pdv) == ['x/**/*']

        pdv = {'project_packages': ['x.y.z', 'a.b.d']}
        assert set(root_packages_masks(pdv)) == {'x/**/*', 'a/**/*'}

    def test_skip_files_migrations(self):
        assert skip_files_migrations(os.path.join('migrations', "any filename"))
        assert skip_files_migrations(os.path.join('root_folder', 'migrations', "any filename"))

    def test_skip_files_lean_web(self):
        assert skip_files_lean_web(f'any_pkg/{PY_CACHE_FOLDER}/any_filename')
        assert skip_files_lean_web('any_pkg/migrations/any_filename')
        assert skip_files_lean_web('any_pkg/static/any_filename')
        assert not skip_files_lean_web('static/any_file.ext')
        assert skip_files_lean_web('any_pkg/any_i18n_dir/any_filename.po')

    def test_venv_bin_path(self, mocked_app_options):
        mocked_app_options['force'] = False
        ori_env_root = tst_env_root = os.getenv('PYENV_ROOT')
        tst_env_name = 'my_tst_venv99'
        tst_dir = os.path.join(TESTS_FOLDER, "tst_dir")
        tst_sub_dir = os.path.join(tst_dir, "tst_sub_dir")
        venv_file = os.path.join(tst_dir, '.python-version')
        try:
            os.makedirs(tst_sub_dir)
            write_file(venv_file, tst_env_name)
            if not tst_env_root:
                tst_env_root = os.environ['PYENV_ROOT'] = "/any/venv/tst/path"
            with _in_prj_dir_venv(tst_sub_dir):
                assert venv_bin_path() == os.path.join(tst_env_root, 'versions', tst_env_name, 'bin')

        finally:
            if os.path.isdir(tst_dir):
                shutil.rmtree(tst_dir)
            if ori_env_root:
                os.environ['PYENV_ROOT'] = ori_env_root
            else:
                del os.environ['PYENV_ROOT']


class TestHiddenHelpersLocal:
    """ test private helper functions that don't need any authentication against git remote hosts. """
    def test_action_decorator(self, mocked_app_options):
        def test_fun(*_args):
            """ test fun docstring """
            return _args

        try:
            dec = _action(APP_PRJ, MODULE_PRJ, kwarg1='1', kwarg2=2)
            assert callable(dec)
            assert callable(dec(test_fun))
            assert 'test_fun' in REGISTERED_ACTIONS
            assert APP_PRJ in REGISTERED_ACTIONS['test_fun']['project_types']
            assert MODULE_PRJ in REGISTERED_ACTIONS['test_fun']['project_types']
            assert REGISTERED_ACTIONS['test_fun']['docstring'] == " test fun docstring "

            # cae.get_option = lambda opt: "" # prevent argument parsing via cae
            # git_repo_manager_main.ACTION_NAME = 'test_fun'
            # git_repo_manager_main.INI_PDV['project_type'] = APP_PRJ
            assert dec(test_fun)() == ()

        finally:
            REGISTERED_ACTIONS.pop('test_fun', None)

    def test_act_callable(self, mocked_app_options):
        mocked_app_options['domain'] = None
        pdv = {'host_api': None}
        assert callable(_act_callable(pdv, 'new_app'))
        assert not callable(_act_callable(pdv, 'fork'))
        assert callable(_act_callable({'host_api': GitlabCom()}, 'fork_project'))
        assert _act_callable(pdv, 'xxx_yyy_zzz') is None

    def test_available_actions(self):
        assert _available_actions()
        assert 'show_status' in _available_actions()
        assert 'new_app' in _available_actions()
        assert 'fork_project' in _available_actions()

        assert _available_actions(project_type=NO_PRJ)
        assert 'show_status' not in _available_actions(project_type=NO_PRJ)
        assert 'new_app' in _available_actions(project_type=NO_PRJ)
        assert 'fork_project' not in _available_actions(project_type=NO_PRJ)

    def test_check_arguments(self, mocked_app_options, patched_exit_call_wrapper):
        mocked_app_options['domain'] = None
        ini_pdv = {'project_type': PARENT_PRJ}
        act_spec = {'docstring': "act new_app docstring", 'project_types': ANY_PRJ_TYPE}
        patched_exit_call_wrapper(_init_act_args_check, ini_pdv, act_spec, 'new_app', [], {})

        ini_pdv['project_type'] = MODULE_PRJ
        _init_act_args_check(ini_pdv, act_spec, 'new_app', [], {})

        patched_exit_call_wrapper(_init_act_args_check, ini_pdv, act_spec, 'new_app', ['argument_value'], {})

        _init_act_args_check(ini_pdv, act_spec, 'show_repo', [], {})

        patched_exit_call_wrapper(_init_act_args_check, ini_pdv, act_spec, 'show_repo', [], {})

        ini_pdv['project_type'] = ROOT_PRJ
        patched_exit_call_wrapper(_init_act_args_check, ini_pdv, act_spec, 'install_portions_editable', [], {})

        act_spec['arg_names'] = ((ARG_ALL, ),
                                 ('portions-sets-expr', ),
                                 ('portion-names' + git_repo_manager_main.ARG_MULTIPLES,))
        _init_act_args_check(ini_pdv, act_spec, 'install_portions_editable', [ARG_ALL], {})

        _init_act_args_check(ini_pdv, act_spec, 'install_portions_editable', ['por1', 'por2'], {})

        ini_pdv['project_type'] = APP_PRJ
        patched_exit_call_wrapper(_init_act_args_check, ini_pdv, act_spec, 'show_versions', ['p1', 'por2'], {})

        patched_exit_call_wrapper(_init_act_args_check, ini_pdv, act_spec, 'show_status', ['por1', 'por2'], {})

        with pytest.raises(KeyError):
            _init_act_args_check(ini_pdv, {}, 'invalid_action', [], {})

    def test_check_arguments_except_empty_action(self, mocked_app_options):
        mocked_app_options['domain'] = None
        with pytest.raises(KeyError):
            _init_act_args_check({}, {}, "", [], {})

    def test_cl(self):
        output = []
        _cl(693, "", lines_output=output, exit_on_err=False)
        assert not output

    def test_debug_or_verbose(self, restore_app_env, mocked_app_options):
        assert _debug_or_verbose()
        mocked_app_options['verbose'] = False
        assert _debug_or_verbose()

        old_val = git_repo_manager_main.cae._parsed_arguments
        try:
            git_repo_manager_main.cae._parsed_arguments = True
            assert not _debug_or_verbose()
            mocked_app_options['verbose'] = True
            assert _debug_or_verbose()
        finally:
            git_repo_manager_main.cae._parsed_arguments = old_val

    def test_exit_error(self):
        po, show_help, shutdown = cae.po, cae.show_help, cae.shutdown
        try:
            po_args = None

            def _po(*args):
                nonlocal po_args
                po_args = args

            cae.po = _po

            called = 0

            def _sh():
                nonlocal called
                called += 1

            cae.show_help = _sh

            sd_args = None

            def _sd(*args):
                nonlocal sd_args
                sd_args = args

            cae.po = _po
            cae.shutdown = _sd

            _exit_error(3)
            assert po_args is None
            assert called == 1
            assert sd_args == (3, )

            _exit_error(6, 'err')
            assert po_args == ('***** err', )
            assert called == 2
            assert sd_args == (6, )

            _exit_error(9)
            assert po_args == ('***** err', )
            assert called == 3
            assert sd_args == (9, )

            # noinspection PyArgumentEqualDefault
            _exit_error(12, "")
            assert po_args == ('***** err', )
            assert called == 3
            assert sd_args == (12, )

        finally:
            cae.po, cae.show_help, cae.shutdown = po, show_help, shutdown

    def test_expected_args(self):
        spe = {'arg_names': (('varA_arg1', 'varA_arg2'), ('varB_arg1', 'varB_arg2', 'varB_arg3'))}
        assert _expected_args(spe) == "varA_arg1 varA_arg2 -or- varB_arg1 varB_arg2 varB_arg3"

        spe = {'arg_names': (('a', 'b'), ('c', ), ('d', ))}
        assert _expected_args(spe) == "a b -or- c -or- d"

        spe = {'arg_names': (('a', 'b'), ('c', ), ('d', )), 'flags': {'FLAG': False}}
        assert _expected_args(spe).startswith("a b -or- c -or- d")
        assert "FLAG=False" in _expected_args(spe)

        spe = {'flags': {'FLAG': False}}
        assert "FLAG=False" in _expected_args(spe)

    def test_get_branch(self, mocked_app_options):
        branch = "tst_bra"

        mocked_app_options['branch'] = branch
        assert _get_branch({}) == branch

        mocked_app_options['branch'] = ""
        with patch('aedev.git_repo_manager.__main__._git_current_branch', return_value=branch):
            assert _get_branch({}) == branch

    def test_get_host_user_name(self, mocked_app_options):
        user = "tee_st_usr"

        mocked_app_options['user'] = user
        assert _get_host_user_name({}, "") == user

        with patch('aedev.git_repo_manager.__main__._get_host_group', return_value=user):
            assert _get_host_user_name({}, "") == user

    def test_get_host_user_token(self, mocked_app_options):
        token = "t_usr_token"

        mocked_app_options['token'] = token
        assert _get_host_user_token("") == token
        assert _get_host_user_token("", host_user="not_configured_user_name") == token

        with patch('aedev.git_repo_manager.__main__._get_host_group', return_value=token):
            assert _get_host_user_token("domain.xxx") == token
            assert _get_host_user_token("not_configured_domain", host_user="not_configured_user_name") == token

    def test_git_checkout(self, changed_repo_path, mocked_app_options, patched_exit_call_wrapper):
        old_files = set(path_items(os.path.join(changed_repo_path, "**")))
        mocked_app_options['force'] = False
        mocked_app_options['verbose'] = True
        pev = {'project_path': changed_repo_path}
        main_branch = _git_current_branch(pev)
        new_branch = "new_tst_branch"
        new_file = 'new_branch_file_commit_tst.py'

        assert main_branch == MAIN_BRANCH
        _git_add(pev)
        write_file(os.path.join(changed_repo_path, COMMIT_MSG_FILE_NAME), "commit title of develop branch commit")
        _git_commit(pev)

        patched_exit_call_wrapper(_git_checkout, pev, branch="")
        assert _git_current_branch(pev) == MAIN_BRANCH
        assert old_files == set(path_items(os.path.join(changed_repo_path, "**")))

        write_file(os.path.join(changed_repo_path, new_file), f"# new test file{os.linesep}")
        new_files = set(path_items(os.path.join(changed_repo_path, "**")))

        _git_checkout(pev, branch=new_branch)
        assert _git_current_branch(pev) == new_branch
        assert new_files == set(path_items(os.path.join(changed_repo_path, "**")))

        _git_add(pev)
        write_file(os.path.join(changed_repo_path, COMMIT_MSG_FILE_NAME), "new-branch commit message title")
        _git_commit(pev)

        _git_checkout(pev, branch=MAIN_BRANCH)
        assert _git_current_branch(pev) == MAIN_BRANCH
        assert new_files == set(path_items(os.path.join(changed_repo_path, "**")))  # checkout does not remove new files

        with _in_prj_dir_venv(changed_repo_path):
            os.remove(new_file)
        patched_exit_call_wrapper(_git_checkout, pev, branch=MAIN_BRANCH)
        assert old_files == set(path_items(os.path.join(changed_repo_path, "**")))

        _git_checkout(pev, "HEAD", new_file)
        assert _git_current_branch(pev) == MAIN_BRANCH
        assert new_files == set(path_items(os.path.join(changed_repo_path, "**")))

    def test_git_cl(self):
        output = []
        _cl(0, "git", extra_args=("--version", ), lines_output=output, exit_on_err=False)
        assert output
        # with capsys.disabled():
        #     print(f">>>>>> git --version output: {output}")

    def test_git_cg_with_trace(self, mocked_app_options):
        mocked_app_options['verbose'] = False
        with patch('ae.console.ConsoleApp.verbose', new_callable=PropertyMock, return_value=True):
            # patch because mocked_app_options['debug_level'] = 2 will not update the ConsoleApp.verbose property value
            output = _cg(0, "git", extra_args=("--version", ), exit_on_err=False)
        assert output       # e.g. == ['git version 2.43.0']
        assert len(output) == 1
        assert isinstance(output[0], str)

    def test_git_clone_ae_base(self, mocked_app_options):
        mocked_app_options['verbose'] = False
        cur_dir = os.getcwd()
        project_name = 'ae_base'

        project_path = _git_clone(f"https://gitlab.com/ae-group", project_name)

        assert os.getcwd() == cur_dir
        tmp_dir = git_repo_manager_main.TEMP_PARENT_FOLDER
        assert tmp_dir
        assert project_path.startswith(tmp_dir)
        assert os.path.isdir(os.path.join(tmp_dir, project_name))

    def test_git_clone_ae_files_with_trace(self, mocked_app_options):
        mocked_app_options['verbose'] = True
        cur_dir = os.getcwd()
        # cloning ae_base portion again would raise an error (folder ae_base already exists) because TEMP_CONTEXT not
        # gets reset between test cases runs (see TEMP_CONTEXT.cleanup() in test_temp_context_teardown())
        project_name = 'ae_files'

        with patch('ae.console.ConsoleApp.verbose', new_callable=PropertyMock, return_value=True):
            # patch because mocked_app_options['debug_level'] = 2 will not update the ConsoleApp.verbose property value
            project_path = _git_clone(f"https://gitlab.com/ae-group", project_name)

        assert os.getcwd() == cur_dir
        tmp_dir = git_repo_manager_main.TEMP_PARENT_FOLDER
        assert tmp_dir
        assert project_path.startswith(tmp_dir)
        assert os.path.isdir(os.path.join(tmp_dir, project_name))

    def test_git_clone_aedev_git_repo_manager_release(self, mocked_app_options):
        mocked_app_options['verbose'] = False
        import_name = "aedev.git_repo_manager"
        version = "0.2.24"
        project_name = norm_name(import_name)

        project_path = _git_clone("https://gitlab.com/aedev-group", project_name, branch_or_tag=f"release{version}")

        tmp_dir = git_repo_manager_main.TEMP_PARENT_FOLDER
        assert project_path.startswith(tmp_dir)
        assert os.path.isdir(os.path.join(tmp_dir, project_name))
        assert version == code_file_version(project_main_file(import_name, project_path=project_path))

    def test_git_clone_aedev_setup_project_version_tag_to_test(self, mocked_app_options):
        mocked_app_options['verbose'] = False
        import_name = "aedev.setup_project"
        version = "0.3.3"
        project_name = norm_name(import_name)
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])

        try:
            os.makedirs(parent_dir)

            project_path = _git_clone("https://gitlab.com/aedev-group", project_name, branch_or_tag=f"v{version}",
                                      parent_path=parent_dir)

            assert project_path.startswith(norm_path(parent_dir))
            assert os.path.isdir(os.path.join(parent_dir, project_name))
            assert version == code_file_version(project_main_file(import_name, project_path=project_path))
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_git_clone_fail(self, mocked_app_options):
        cur_dir = os.getcwd()
        mocked_app_options['force'] = False
        mocked_app_options['verbose'] = False

        assert _git_clone("_invalid_repo_", "_invalid_project_name", branch_or_tag="9.99.999") == ""
        assert os.getcwd() == cur_dir

    def test_git_clone_fail_with_trace(self, mocked_app_options):
        cur_dir = os.getcwd()
        mocked_app_options['force'] = False
        mocked_app_options['verbose'] = True

        with patch('ae.console.ConsoleApp.verbose', new_callable=PropertyMock, return_value=True):
            # patch because mocked_app_options['debug_level'] = 2 will not update the ConsoleApp.verbose property value
            assert _git_clone("_invalid_repo_", "_invalid_project_name", branch_or_tag="9.99.999") == ""

        assert os.getcwd() == cur_dir

    def test_git_commit_on_changed_repo(self, changed_repo_path, mocked_app_options, patched_exit_call_wrapper):
        files = set(path_items(os.path.join(changed_repo_path, "**")))
        mocked_app_options['force'] = False
        mocked_app_options['verbose'] = True
        pev = {'project_path': changed_repo_path}

        patched_exit_call_wrapper(_git_commit, pev)
        assert files == set(path_items(os.path.join(changed_repo_path, "**")))

        write_file(os.path.join(changed_repo_path, 'tst.py'), "# new test file")
        files = set(path_items(os.path.join(changed_repo_path, "**")))

        patched_exit_call_wrapper(_git_commit, pev)
        assert files == set(path_items(os.path.join(changed_repo_path, "**")))

        _git_add(pev)
        patched_exit_call_wrapper(_git_commit, pev)
        assert files == set(path_items(os.path.join(changed_repo_path, "**")))

        write_file(os.path.join(changed_repo_path, COMMIT_MSG_FILE_NAME), "commit title")
        _git_commit(pev)

    def test_git_commit_on_empty_repo(self, empty_repo_path, mocked_app_options, patched_exit_call_wrapper):
        files = set(path_items(os.path.join(empty_repo_path, "**")))
        mocked_app_options['force'] = False
        mocked_app_options['verbose'] = True
        pev = {'project_path': empty_repo_path}

        patched_exit_call_wrapper(_git_commit, pev)
        assert files == set(path_items(os.path.join(empty_repo_path, "**")))

        write_file(os.path.join(empty_repo_path, 'tst.py'), "# new test file")
        patched_exit_call_wrapper(_git_commit, pev)

        write_file(os.path.join(empty_repo_path, COMMIT_MSG_FILE_NAME),
                   f"commit message title{os.linesep}{os.linesep}commit message body")
        patched_exit_call_wrapper(_git_commit, pev)

        _git_add(pev)       # adding untracked file tst.py
        _git_commit(pev)

    def test_git_diff_on_changed_repo(self, changed_repo_path, mocked_app_options):
        pev = {'project_path': changed_repo_path}

        git_files = _git_diff(pev, "--name-only")
        assert set(git_files) == {'changed.py', 'delete.txt'}

        pth_files = set(path_items(os.path.join(changed_repo_path, "**")))
        assert (set(os.path.relpath(_, changed_repo_path) for _ in pth_files if os.path.isfile(_))
                == {'added.cfg', 'changed.py'})

        mocked_app_options['force'] = False
        mocked_app_options['verbose'] = False
        old_val = cae._parsed_arguments
        try:
            cae._parsed_arguments = True

            output = _git_diff(pev)
            for file in pth_files:
                if not file.endswith('added.cfg'):
                    assert os.path.basename(file) in "".join(output)
            assert pth_files == set(path_items(os.path.join(changed_repo_path, "**")))

            mocked_app_options['verbose'] = True

            verbose_output = _git_diff(pev)
            assert len("".join(verbose_output)) > len("".join(output))
            for file in pth_files:
                if not file.endswith('added.cfg'):
                    assert os.path.basename(file) in "".join(verbose_output)
        finally:
            cae._parsed_arguments = old_val

    def test_git_diff_on_changed_repo_after_add(self, changed_repo_path, mocked_app_options):
        mocked_app_options['force'] = False
        mocked_app_options['verbose'] = False
        pev = {'project_path': changed_repo_path}

        pth_files = set(path_items(os.path.join(changed_repo_path, "**")))  # 'changed.py', 'added.cfg' with an abs-path
        assert len(_git_diff(pev, "--name-only")) == 2                      # 'changed.py', 'delete.txt'

        _git_add(pev)

        assert pth_files == set(path_items(os.path.join(changed_repo_path, "**")))
        assert _git_diff(pev, "--name-only") == []

    def test_git_diff_on_empty_repo(self, empty_repo_path, mocked_app_options):
        mocked_app_options['verbose'] = False
        pev = {'project_path': empty_repo_path}
        git_files = _git_diff(pev, "--name-only")
        pth_files = set(path_items(os.path.join(empty_repo_path, "**")))

        assert set(git_files) == set()
        assert (set(os.path.relpath(_, empty_repo_path) for _ in pth_files if os.path.isfile(_))
                == set())

        assert not _git_diff(pev)

        assert git_files == _git_diff(pev, "--name-only")
        assert pth_files == set(path_items(os.path.join(empty_repo_path, "**")))

    def test_git_init_if_needed(self, mocked_app_options):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        prj_dir = os.path.join(parent_dir, 'tst_git_init_dir')
        pev = {'project_path': prj_dir}
        mocked_app_options['force'] = False
        mocked_app_options['verbose'] = False
        try:
            os.makedirs(prj_dir)
            assert _git_init_if_needed(pev)
            assert os.path.isdir(os.path.join(prj_dir, GIT_FOLDER_NAME))
            assert not _git_uncommitted(pev)
            assert _git_current_branch(pev) == MAIN_BRANCH
        finally:
            if os.path.isdir(parent_dir):
                shutil.rmtree(parent_dir)

    def test_git_ls_files_vs_git_status(self, empty_repo_path, mocked_app_options):
        mocked_app_options['verbose'] = False
        pev = {'project_path': empty_repo_path}
        ls_uncommitted = []
        with _in_prj_dir_venv(empty_repo_path):
            _cl(0, "git ls-files -m", lines_output=ls_uncommitted)
        assert ls_uncommitted == []

        st_uncommitted = _git_status(pev)
        assert st_uncommitted == ['?? .gitignore']

        git_uncommitted = _git_uncommitted(pev)
        assert git_uncommitted == ['.gitignore']

    def test_git_ls_files_vs_git_status_on_changed_repo(self, changed_repo_path, mocked_app_options):
        mocked_app_options['force'] = False
        mocked_app_options['verbose'] = False
        pev = {'project_path': changed_repo_path}
        ls_uncommitted = []
        with _in_prj_dir_venv(changed_repo_path):
            _cl(0, "git ls-files -m", lines_output=ls_uncommitted)
        st_uncommitted = [_[3:] for _ in _git_status(pev)]

        assert len(ls_uncommitted) >= 2 and 'added.cfg' not in ls_uncommitted
        assert all(lsi in st_uncommitted for lsi in ls_uncommitted)

    def test__git_project_version(self, empty_repo_path, mocked_app_options):
        mocked_app_options['namespace'] = ""
        mocked_app_options['verbose'] = False
        assert _git_project_version({'project_path': TESTS_FOLDER}) == ""
        assert _git_project_version({'project_path': empty_repo_path}) == "0.0.1"

    def test__git_project_version_local(self, empty_repo_path, mocked_app_options):
        mocked_app_options['namespace'] = ""
        assert _git_project_version(project_dev_vars()) > "0.0.1"

    def test_git_status_on_changed_repo(self, changed_repo_path, mocked_app_options):
        mocked_app_options['force'] = False
        mocked_app_options['verbose'] = False
        files = set(path_items(os.path.join(changed_repo_path, "**")))
        pev = {'project_path': changed_repo_path}

        output = _git_status(pev)
        for file in files:
            assert os.path.basename(file) in "".join(output)
        assert files == set(path_items(os.path.join(changed_repo_path, "**")))

        mocked_app_options['verbose'] = True

        verbose_output = _git_status(pev)
        assert len(verbose_output) > len(output)
        for file in files:
            assert os.path.basename(file) in "".join(verbose_output)

    def test_git_status_on_empty_repo(self, empty_repo_path, mocked_app_options):
        mocked_app_options['verbose'] = False
        files = set(path_items(os.path.join(empty_repo_path, "**")))
        pev = {'project_path': empty_repo_path}

        assert _git_status(pev) == ['?? .gitignore']
        assert files == set(path_items(os.path.join(empty_repo_path, "**")))

    def test_init_act_exec_args_check_deploy(self, empty_repo_path, mocked_app_options):
        mocked_app_options['action'] = 'check_deploy'
        mocked_app_options['arguments'] = ['WORKTREE', 'ALL', 'MASKS=["file_mask1", "file_mask2"]']
        mocked_app_options['domain'] = 'eu.pythonanywhere.com'
        mocked_app_options['namespace'] = ""
        mocked_app_options['path'] = empty_repo_path
        write_file(os.path.join(empty_repo_path, 'manage.py'), "content")   # to be recognized as a django project type

        ini_pdv, act_name, act_args, act_flags = _init_act_exec_args()

        assert isinstance(ini_pdv, dict)    # PdvType
        assert 'host_api' in ini_pdv
        assert act_name == 'check_deploy'
        assert act_args == ['WORKTREE']
        assert act_flags['ALL'] is True
        assert act_flags['MASKS'] == ["file_mask1", "file_mask2"]
        assert act_flags['CLEANUP'] is False

    def test_init_act_exec_args_exits(self, mocked_app_options, patched_exit_call_wrapper):
        mocked_app_options['action'] = 'what_ever_not_existing_action'
        mocked_app_options['arguments'] = ['what_ever_invalid_action_arg']
        mocked_app_options['namespace'] = ""        # or tst_ns_name
        mocked_app_options[_template_version_option(tst_ns_name + '.' + tst_ns_name)] = ""
        patched_exit_call_wrapper(_init_act_exec_args)

    def test_init_act_exec_args_new_app(self, mocked_app_options):
        mocked_app_options['action'] = 'new_app'
        mocked_app_options['arguments'] = []
        mocked_app_options['domain'] = 'github.com'
        mocked_app_options['namespace'] = ""
        mocked_app_options['path'] = ""

        ini_pdv, act_name, act_args, act_flags = _init_act_exec_args()

        assert isinstance(ini_pdv, dict)    # PdvType
        assert 'host_api' not in ini_pdv
        assert act_name == 'new_app'
        assert act_args == []
        assert act_flags == {}

    def test_init_act_exec_args_show_status(self, mocked_app_options):
        mocked_app_options['action'] = 'status'
        mocked_app_options['arguments'] = []
        mocked_app_options['domain'] = None
        mocked_app_options['namespace'] = ""
        mocked_app_options['path'] = ""

        ini_pdv, act_name, act_args, act_flags = _init_act_exec_args()

        assert isinstance(ini_pdv, dict)    # PdvType
        assert 'host_api' not in ini_pdv
        assert act_name == 'show_status'
        assert act_args == []
        assert act_flags == {}

    def test_init_children_pdv_args_branch_filter(self, mocked_app_options):
        mocked_app_options['filterExpression'] = ""
        mocked_app_options['filterBranch'] = ""
        mocked_app_options['force'] = False
        filtered_branch = "filter_branch"
        a_pdv = {'project_name': "n_a", 'project_path': TESTS_FOLDER}
        b_pdv = {'project_name': "n_b", 'project_path': TESTS_FOLDER}
        ini_pdv = {'children_project_vars': {'n_a': a_pdv, 'n_b': b_pdv}, 'namespace_name': 'n',
                   'portions_packages': ['n_a', 'n_b']}

        assert _init_children_pdv_args(ini_pdv, [ARG_ALL]) == [a_pdv, b_pdv]

        with patch('aedev.git_repo_manager.__main__._git_current_branch',
                   new=lambda _: filtered_branch if _['project_name'] == "n_b" else MAIN_BRANCH):
            mocked_app_options['filterBranch'] = filtered_branch
            assert _init_children_pdv_args(ini_pdv, ['filterBranch']) == [b_pdv]

    def test_init_children_pdv_args_exit(self, mocked_app_options, patched_exit_call_wrapper):
        mocked_app_options['filterExpression'] = ""
        mocked_app_options['filterBranch'] = ""
        mocked_app_options['force'] = False
        ini_pdv = {'children_project_vars': {}, 'namespace_name': 'n'}
        patched_exit_call_wrapper(_init_children_pdv_args, ini_pdv, [])

        patched_exit_call_wrapper(_init_children_pdv_args, ini_pdv, ["undefined_project_name"])

        patched_exit_call_wrapper(_init_children_pdv_args, ini_pdv, ["filterBranch"])

        mocked_app_options['filterBranch'] = "branch_name_to_filter"
        patched_exit_call_wrapper(_init_children_pdv_args, ini_pdv, [ARG_ALL])

    def test_init_children_pdv_args_expression(self, mocked_app_options):
        mocked_app_options['filterExpression'] = ""
        mocked_app_options['filterBranch'] = ""
        mocked_app_options['force'] = False
        ch1_pdv = {'project_name': "p1", 'project_path': TESTS_FOLDER}
        ch2_pdv = {'project_name': "p2", 'project_path': TESTS_FOLDER}
        chi_vars = {'p1': ch1_pdv, 'p2': ch2_pdv}
        ini_pdv: PdvType = {'children_project_vars': chi_vars, 'project_type': PARENT_PRJ}

        assert _init_children_pdv_args(ini_pdv, ["any_pkg_name"]) == [{'project_name': 'any_pkg_name'}]

        with patch('aedev.git_repo_manager.__main__._init_children_presets',
                   return_value={'ps_a': {'p1'}, 'ps_b': {'p1', 'p2'}}):
            assert _init_children_pdv_args(ini_pdv, ["ps_a"]) == [ch1_pdv]
            assert ch1_pdv in _init_children_pdv_args(ini_pdv, ["ps_b"])
            assert ch2_pdv in _init_children_pdv_args(ini_pdv, ["ps_b"])
            assert _init_children_pdv_args(ini_pdv, ["ps_b - ps_a"]) == [ch2_pdv]

        ini_pdv['namespace_name'] = 'n'
        ch1_pdv = {'project_name': "n_1", 'project_path': TESTS_FOLDER}
        ch2_pdv = {'project_name': "n_por2", 'project_path': TESTS_FOLDER}
        ch3_pdv = {'project_name': "n_b", 'project_path': TESTS_FOLDER}
        ini_pdv['children_project_vars'] = {'n_1': ch1_pdv, 'n_por2': ch2_pdv, 'n_b': ch3_pdv}
        with patch('aedev.git_repo_manager.__main__._init_children_presets',
                   return_value={'ps_a': {'n_1', 'n_b'}, 'ps_b': {'n_1', 'n_por2'}, 'ps_c': {'n_por2'}}):
            assert _init_children_pdv_args(ini_pdv, ["ps_a ^ (ps_b - ps_c)"]) == [ch3_pdv]

            assert ch1_pdv in _init_children_pdv_args(ini_pdv, ["ps_a | (ps_b - ps_c)"])
            assert ch3_pdv in _init_children_pdv_args(ini_pdv, ["ps_a | (ps_b - ps_c)"])

            assert _init_children_pdv_args(ini_pdv, ["ps_a & ps_b"]) == [ch1_pdv]
            assert _init_children_pdv_args(ini_pdv, ["ps_b & ps_c"]) == [ch2_pdv]

            assert _init_children_pdv_args(ini_pdv, ["set(ps_a) & (ps_b - set(['n_por2']))"]) == [ch1_pdv]

            assert _init_children_pdv_args(ini_pdv, ["ps_a&ps_b"]) == [ch1_pdv]
            assert _init_children_pdv_args(ini_pdv, ["ps_a", "&", "ps_b"]) == [ch1_pdv]

    def test_init_children_pdv_args_list(self, mocked_app_options):
        mocked_app_options['filterExpression'] = ""
        mocked_app_options['filterBranch'] = ""
        mocked_app_options['force'] = False
        ch1_pdv = {'project_name': "p1", 'project_path': TESTS_FOLDER}
        ch2_pdv = {'project_name': "p2", 'project_path': TESTS_FOLDER}
        chi_vars = {'p1': ch1_pdv, 'p2': ch2_pdv}
        ini_pdv = {'children_project_vars': chi_vars, 'project_type': PARENT_PRJ}
        assert _init_children_pdv_args(ini_pdv, ["('p1', ) + ('p2', )"]) == [ch1_pdv, ch2_pdv]

        chi_vars = {key: {'project_name': key, 'project_path': TESTS_FOLDER} for key in ['a1', 'b', 'p3']}
        ini_pdv['children_project_vars'] = chi_vars
        assert _init_children_pdv_args(ini_pdv, [ARG_ALL]) == list(chi_vars.values())

        assert _init_children_pdv_args(ini_pdv, ['p3']) == [{'project_name': 'p3', 'project_path': TESTS_FOLDER}]

        mocked_app_options['force'] = True
        assert _init_children_pdv_args(ini_pdv, ['p3', 'p3']) == [{'project_name': 'p3', 'project_path': TESTS_FOLDER},
                                                                  {'project_name': 'p3', 'project_path': TESTS_FOLDER}]

        nsn = 'n'
        ch1_pdv = {'project_name': nsn + "_1", 'project_path': TESTS_FOLDER}
        ch2_pdv = {'project_name': nsn + "_por2", 'project_path': TESTS_FOLDER}
        chi_vars = {nsn + '_1': ch1_pdv, nsn + '_por2': ch2_pdv}
        ini_pdv = {'children_project_vars': chi_vars, 'namespace_name': nsn, 'project_type': ROOT_PRJ}
        assert _init_children_pdv_args(ini_pdv, ["('1', ) + ('n_por2', )"]) == [ch1_pdv, ch2_pdv]

    def test_init_children_presets(self, mocked_app_options):
        pkg_name = "pkg_nam"
        chi = {'editable_project_path': "edi_prj_dir", 'project_name': pkg_name, 'project_path': TESTS_FOLDER}

        mocked_app_options['filterBranch'] = MAIN_BRANCH
        mocked_app_options['filterExpression'] = "True"
        with patch('aedev.git_repo_manager.__main__._git_uncommitted', return_value=["non-empty"]):
            with patch('aedev.git_repo_manager.__main__._git_current_branch', return_value=MAIN_BRANCH):
                presets = _init_children_presets(OrderedDict({pkg_name: chi}))
        assert len(presets) == 6
        assert presets[ARG_ALL] == {pkg_name}
        assert presets['editable'] == {pkg_name}
        assert presets['modified'] == {pkg_name}
        assert presets['develop'] == {pkg_name}
        assert presets['filterBranch'] == {pkg_name}
        assert presets['filterExpression'] == {pkg_name}

        mocked_app_options['filterBranch'] = ""
        mocked_app_options['filterExpression'] = ":invalid:exp+ess+on"
        presets = _init_children_presets(OrderedDict({pkg_name: chi}))
        assert len(presets) == 5
        assert presets[ARG_ALL] == {pkg_name}
        assert presets['editable'] == {pkg_name}
        assert presets['modified'] == set()
        assert presets['develop'] == set()
        assert 'filterBranch' not in presets
        assert presets['filterExpression'] == set()

    def test_patch_outsourced_md(self):
        content = "content"
        patcher = "patcher"
        patched_content = _patch_outsourced("any.md", content, patcher)
        assert patched_content.endswith(content)
        assert patched_content.startswith(f"<!-- {OUTSOURCED_MARKER}")
        assert patcher in patched_content

    def test_patch_outsourced_rst(self):
        content = "content"
        patcher = "patcher"
        sep = os.linesep
        patched_content = _patch_outsourced("any.rst", content, patcher)
        assert patched_content.endswith(content)
        assert patched_content.startswith(f"{sep}..{sep}    {OUTSOURCED_MARKER}")
        assert patcher in patched_content

    def test_patch_outsourced_txt(self):
        content = "content"
        patcher = "patcher"
        patched_content = _patch_outsourced("any.txt", content, patcher)
        assert patched_content.endswith(content)
        assert patched_content.startswith(f"# {OUTSOURCED_MARKER}")
        assert patcher in patched_content

    def test_print_pdv(self, mocked_app_options):
        mocked_app_options['verbose'] = False
        _print_pdv({'project_type': PARENT_PRJ, 'long_desc_content': "long desc content (not that long ;)"})
        # assert capsys.readouterr().out worked in TestHiddenHelpersRemote, but after moving here is always empty string

    def test_register_template_aedev_root(self, mocked_app_options):
        nsn = "aedev"
        tpl_imp_name = nsn + "." + nsn
        pkg_name = norm_name(tpl_imp_name)
        tpl_path = os.path.join(pkg_name, nsn, nsn, TEMPLATES_FOLDER)
        dev_require = []
        tpl_projects = []

        assert mocked_app_options[_template_version_option(tpl_imp_name)] == ""

        _register_template(tpl_imp_name, dev_require, True, tpl_projects)
        assert dev_require
        assert dev_require[0].startswith(pkg_name + PROJECT_VERSION_SEP)
        assert dev_require[0].split(PROJECT_VERSION_SEP)[1]

        assert tpl_projects
        assert tpl_projects[0]['import_name'] == tpl_imp_name
        assert tpl_projects[0]['tpl_path'] != ""
        assert tpl_projects[0]['tpl_path'].endswith(tpl_path)
        assert tpl_projects[0]['version'] != ""

        pkg_name, version = project_version(tpl_imp_name, list(REGISTERED_TPL_PROJECTS.keys()))
        assert tpl_imp_name + PROJECT_VERSION_SEP + version in REGISTERED_TPL_PROJECTS
        assert REGISTERED_TPL_PROJECTS[tpl_imp_name + PROJECT_VERSION_SEP + version]['import_name'] == tpl_imp_name
        assert REGISTERED_TPL_PROJECTS[tpl_imp_name + PROJECT_VERSION_SEP + version]['tpl_path'] != ""
        assert REGISTERED_TPL_PROJECTS[tpl_imp_name + PROJECT_VERSION_SEP + version]['tpl_path'].endswith(tpl_path)
        assert REGISTERED_TPL_PROJECTS[tpl_imp_name + PROJECT_VERSION_SEP + version]['version'] == version

    def test_register_template_not_existing(self, mocked_app_options):
        tpl_imp_name = "not.existing_tpl_package_imp_name"
        dev_require = []
        tpl_projects = []
        mocked_app_options[_template_version_option(tpl_imp_name)] = ""

        _register_template(tpl_imp_name, dev_require, True, tpl_projects)
        assert not dev_require
        assert not tpl_projects
        assert tpl_imp_name + PROJECT_VERSION_SEP in REGISTERED_TPL_PROJECTS
        assert REGISTERED_TPL_PROJECTS[tpl_imp_name + PROJECT_VERSION_SEP]['import_name'] == tpl_imp_name
        assert REGISTERED_TPL_PROJECTS[tpl_imp_name + PROJECT_VERSION_SEP]['tpl_path'] == ""
        assert REGISTERED_TPL_PROJECTS[tpl_imp_name + PROJECT_VERSION_SEP]['version'] == ""

    def test_renew_prj_dir(self, mocked_app_options):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        app_name = 'cpl_prj_dir_app'
        project_path = norm_path(os.path.join(parent_dir, app_name))
        mocked_app_options['group'] = "group_name"
        mocked_app_options['namespace'] = ""
        mocked_app_options['project'] = app_name
        mocked_app_options['path'] = project_path
        pdv = {'namespace_name': '', 'project_name': app_name, 'project_path': project_path, 'project_type': APP_PRJ}

        try:
            assert not os.path.isdir(project_path)

            _renew_prj_dir(pdv.copy())

            mocked_app_options['path'] = ""
            _renew_prj_dir(pdv.copy())
            assert not os.path.isdir(os.path.join(project_path, TEMPLATES_FOLDER))

            pdv['project_type'] = ROOT_PRJ
            _renew_prj_dir(pdv.copy())
            assert os.path.isdir(project_path)
            assert os.path.isdir(os.path.join(project_path, DOCS_FOLDER))
            assert os.path.isdir(os.path.join(project_path, TESTS_FOLDER))
            assert os.path.isfile(os.path.join(project_path, 'main' + PY_EXT))
            assert os.path.isfile(os.path.join(project_path, BUILD_CONFIG_FILE))

            assert not os.path.isdir(os.path.join(project_path, TEMPLATES_FOLDER))
            assert not os.path.exists(app_name)
            assert not os.path.exists(BUILD_CONFIG_FILE)

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_renew_project_change_prj_type(self, mocked_app_options):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        app_name = 'cpl_prj_app_name'
        project_path = os.path.join(parent_dir, app_name)
        mocked_app_options['group'] = "group_name"
        mocked_app_options['namespace'] = ""
        mocked_app_options['project'] = app_name
        mocked_app_options['path'] = project_path

        module_version_file = os.path.join(project_path, app_name + PY_EXT)
        sister_prj_path = os.path.join(os.path.dirname(os.getcwd()), app_name)
        try:
            write_file(os.path.join(project_path, BUILD_CONFIG_FILE), "", make_dirs=True)
            _renew_project({}, MODULE_PRJ)   # project_type change creates module_version_file in the project folder
            assert os.path.exists(module_version_file)
            assert not os.path.exists(sister_prj_path)

            os.remove(module_version_file)
            with _in_prj_dir_venv(project_path):    # fix for error happening only in console / not-in-PyCharm-pytest
                _cl(0, "git remote remove origin")  # remove remote to prevent ask for password in the next git fetch
            _renew_project({}, APP_PRJ)
            assert not os.path.exists(module_version_file)
            assert not os.path.exists(sister_prj_path)

            assert os.path.isdir(project_path)
            assert os.path.isdir(os.path.join(project_path, DOCS_FOLDER))
            assert not os.path.isdir(os.path.join(project_path, TEMPLATES_FOLDER))
            assert os.path.isdir(os.path.join(project_path, TESTS_FOLDER))
            assert os.path.isfile(os.path.join(project_path, 'main' + PY_EXT))
            assert os.path.isfile(os.path.join(project_path, BUILD_CONFIG_FILE))

            assert not os.path.exists(app_name)
            assert not os.path.exists(BUILD_CONFIG_FILE)

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_renew_project_exits(self, mocked_app_options, patched_exit_call_wrapper):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        app_name = 'tst_app_prj_name'
        project_path = norm_path(os.path.join(parent_dir, app_name))
        mocked_app_options['branch'] = MAIN_BRANCH
        mocked_app_options['domain'] = None
        mocked_app_options['group'] = "group_name"
        mocked_app_options['namespace'] = ""
        mocked_app_options['project'] = app_name
        mocked_app_options['path'] = project_path

        sister_prj_path = os.path.join(os.path.dirname(os.getcwd()), app_name)
        cur_dir = os.getcwd()
        try:
            assert not os.path.isdir(project_path)

            ini_pdv = {}
            _renew_project(ini_pdv, APP_PRJ)
            assert os.path.isdir(project_path)

            assert not os.path.exists(sister_prj_path)
            mocked_app_options['path'] = ""              # exit reason, NO fallback to the package option on prj typ chg
            os.chdir(project_path)
            patched_exit_call_wrapper(_renew_project, ini_pdv, APP_PRJ)
            os.chdir(cur_dir)
            assert not os.path.exists(sister_prj_path)

            mocked_app_options['project'] = ""           # exit reason
            patched_exit_call_wrapper(_renew_project, ini_pdv, APP_PRJ)
            assert not os.path.exists(sister_prj_path)

            mocked_app_options['project'] = app_name
            os.chdir(project_path)
            patched_exit_call_wrapper(_renew_project, ini_pdv, APP_PRJ)
            os.chdir(cur_dir)
            assert not os.path.exists(sister_prj_path)

            patched_exit_call_wrapper(_renew_project, ini_pdv, ROOT_PRJ)
            assert not os.path.exists(sister_prj_path)

            ini_pdv['namespace_name'] = ""
            ini_pdv['project_type'] = APP_PRJ
            ini_pdv['project_path'] = project_path
            mocked_app_options['group'] = None  # exit reason
            with _in_prj_dir_venv(project_path):
                _cl(0, "git remote remove origin")  # remove remote to prevent ask for password in the next git fetch
            patched_exit_call_wrapper(_renew_project, ini_pdv, APP_PRJ)
            assert not os.path.exists(sister_prj_path)

            # an alternative fix to mocked_get_opt_values['repo_group'] = 'group_name'
            ini_pdv['repo_group'] = "group_name"
            os.chdir(project_path)
            with _in_prj_dir_venv(project_path):
                _cl(0, "git remote remove origin")  # remove remote to prevent ask for password in the next git fetch
            patched_exit_call_wrapper(_renew_project, ini_pdv, APP_PRJ)
            os.chdir(cur_dir)
            assert not os.path.exists(sister_prj_path)

            mocked_app_options['path'] = parent_dir  # no parent-dir exit reason
            patched_exit_call_wrapper(_renew_project, ini_pdv, APP_PRJ)
            assert not os.path.exists(sister_prj_path)

            assert os.path.isdir(project_path)
            assert os.path.isdir(os.path.join(project_path, DOCS_FOLDER))
            assert not os.path.isdir(os.path.join(project_path, TEMPLATES_FOLDER))
            assert os.path.isdir(os.path.join(project_path, TESTS_FOLDER))
            assert os.path.isfile(os.path.join(project_path, 'main' + PY_EXT))
            assert os.path.isfile(os.path.join(project_path, BUILD_CONFIG_FILE))

        finally:
            os.chdir(cur_dir)
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_renew_project_new_app_from_parent_via_package(self, mocked_app_options):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        pkg_name = "tst_app_prj"
        project_path = norm_path(os.path.join(parent_dir, pkg_name))
        mocked_app_options['group'] = None
        mocked_app_options['namespace'] = ""
        mocked_app_options['project'] = pkg_name
        mocked_app_options['path'] = ""
        cur_dir = os.getcwd()
        try:
            os.makedirs(parent_dir)
            os.chdir(parent_dir)
            parent_pdv = project_dev_vars()
            assert parent_pdv['project_type'] == PARENT_PRJ
            assert parent_pdv['project_path'] == norm_path("")

            _renew_project(parent_pdv, APP_PRJ)

            app_pdv = project_dev_vars(project_path=pkg_name)
            assert app_pdv['project_type'] == APP_PRJ
            assert app_pdv['project_path'] == project_path
            assert os.path.isdir(project_path)
            assert os.path.isfile(os.path.join(project_path, 'main' + PY_EXT))
            assert os.path.isfile(os.path.join(project_path, BUILD_CONFIG_FILE))
            assert os.path.isdir(os.path.join(project_path, DOCS_FOLDER))
            assert not os.path.isdir(os.path.join(project_path, TEMPLATES_FOLDER))
            assert os.path.isdir(os.path.join(project_path, TESTS_FOLDER))

        finally:
            os.chdir(cur_dir)
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_renew_project_new_app_from_parent_via_path(self, mocked_app_options):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        pkg_name = "tst_app_prj"
        project_path = norm_path(os.path.join(parent_dir, pkg_name))
        mocked_app_options['group'] = None
        mocked_app_options['namespace'] = ""
        mocked_app_options['project'] = ""
        mocked_app_options['path'] = pkg_name
        cur_dir = os.getcwd()
        try:
            os.makedirs(parent_dir)
            os.chdir(parent_dir)

            _renew_project(project_dev_vars(), APP_PRJ)

            app_pdv = project_dev_vars(project_path=pkg_name)
            assert app_pdv['project_type'] == APP_PRJ
            assert app_pdv['project_path'] == project_path
            assert os.path.isdir(project_path)
            assert os.path.isfile(os.path.join(project_path, 'main' + PY_EXT))
            assert os.path.isfile(os.path.join(project_path, BUILD_CONFIG_FILE))
            assert os.path.isdir(os.path.join(project_path, DOCS_FOLDER))
            assert not os.path.isdir(os.path.join(project_path, TEMPLATES_FOLDER))
            assert os.path.isdir(os.path.join(project_path, TESTS_FOLDER))

        finally:
            os.chdir(cur_dir)
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_renew_project_new_ns_module_from_parent_via_package(self, mocked_app_options):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        nsn = "mnx"
        ns_root_dir = norm_path(os.path.join(parent_dir, nsn + '_' + nsn))
        por_name = "tst_ns_mod_prj"
        pkg_name = nsn + '_' + por_name
        project_path = norm_path(os.path.join(parent_dir, pkg_name))
        mocked_app_options['branch'] = ""
        mocked_app_options['domain'] = None
        mocked_app_options['group'] = None
        mocked_app_options['namespace'] = nsn
        mocked_app_options['project'] = por_name
        mocked_app_options['path'] = ""
        mocked_app_options['verbose'] = False
        mocked_app_options[_template_version_option(nsn + '.' + nsn)] = ""
        REGISTERED_TPL_PROJECTS[nsn] = {
            'import_name': nsn + '.' + nsn,
            'tpl_path': os.path.join(ns_root_dir, nsn, nsn, TEMPLATES_FOLDER),
            'version': '3.6.9'}
        cur_dir = os.getcwd()
        try:
            write_file(os.path.join(ns_root_dir, REQ_DEV_FILE_NAME), "", make_dirs=True)   # extended with new ns module
            os.chdir(parent_dir)

            _renew_project(project_dev_vars(), MODULE_PRJ)

            new_pdv = project_dev_vars(project_path=pkg_name)
            assert new_pdv['project_type'] == MODULE_PRJ
            assert norm_path(pkg_name) == project_path
            assert new_pdv['project_path'] == project_path
            assert os.path.isdir(project_path)
            assert os.path.isfile(os.path.join(project_path, nsn, por_name + PY_EXT))
            assert not os.path.isfile(os.path.join(project_path, BUILD_CONFIG_FILE))
            assert not os.path.isdir(os.path.join(project_path, DOCS_FOLDER))
            assert not os.path.isdir(os.path.join(project_path, TEMPLATES_FOLDER))
            assert os.path.isdir(os.path.join(project_path, TESTS_FOLDER))

            assert os.path.isfile(os.path.join(nsn + '_' + nsn, REQ_DEV_FILE_NAME))
            assert read_file(os.path.join(nsn + '_' + nsn, REQ_DEV_FILE_NAME)) == pkg_name + os.linesep

            # repeat to check for no duplicate entry in dev-req-file
            with _in_prj_dir_venv(project_path):
                _cl(0, "git remote remove origin")  # remove remote to prevent ask for password in the next git fetch
            _renew_project(project_dev_vars(project_path=project_path), MODULE_PRJ)
            assert os.path.isfile(os.path.join(nsn + '_' + nsn, REQ_DEV_FILE_NAME))
            assert read_file(os.path.join(nsn + '_' + nsn, REQ_DEV_FILE_NAME)) == pkg_name + os.linesep

            assert _git_current_branch(new_pdv) == f"new_{MODULE_PRJ}_{pkg_name}"

        finally:
            os.chdir(cur_dir)
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)
            del REGISTERED_TPL_PROJECTS[nsn]

    def test_renew_project_new_ns_package_from_parent_via_path(self, mocked_app_options):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        nsn = "mns"
        ns_root_dir = norm_path(os.path.join(parent_dir, nsn + '_' + nsn))
        por_name = "tst_ns_pkg_prj"
        pkg_name = nsn + '_' + por_name
        project_path = norm_path(os.path.join(parent_dir, pkg_name))
        mocked_app_options['branch'] = ""
        mocked_app_options['domain'] = None
        mocked_app_options['group'] = None
        mocked_app_options['namespace'] = nsn
        mocked_app_options['project'] = ""
        mocked_app_options['path'] = project_path
        mocked_app_options['verbose'] = False
        mocked_app_options[_template_version_option(nsn + '.' + nsn)] = ""
        REGISTERED_TPL_PROJECTS[nsn] = {
            'import_name': nsn + '.' + nsn,
            'tpl_path': os.path.join(ns_root_dir, nsn, nsn, TEMPLATES_FOLDER),
            'version': '3.6.12'}
        cur_dir = os.getcwd()
        try:
            write_file(os.path.join(ns_root_dir, REQ_DEV_FILE_NAME), pkg_name + os.linesep, make_dirs=True)
            os.chdir(parent_dir)

            _renew_project(project_dev_vars(), PACKAGE_PRJ)

            new_pdv = project_dev_vars(project_path=pkg_name)
            assert new_pdv['project_type'] == PACKAGE_PRJ
            assert norm_path(pkg_name) == project_path
            assert new_pdv['project_path'] == project_path
            assert os.path.isdir(project_path)
            assert os.path.isfile(os.path.join(project_path, nsn, por_name, PY_INIT))
            assert not os.path.isfile(os.path.join(project_path, BUILD_CONFIG_FILE))
            assert not os.path.isdir(os.path.join(project_path, DOCS_FOLDER))
            assert not os.path.isdir(os.path.join(project_path, TEMPLATES_FOLDER))
            assert os.path.isdir(os.path.join(project_path, TESTS_FOLDER))

            assert os.path.isfile(os.path.join(nsn + '_' + nsn, REQ_DEV_FILE_NAME))
            assert read_file(os.path.join(nsn + '_' + nsn, REQ_DEV_FILE_NAME)) == pkg_name + os.linesep  # no extend/dup

            assert _git_current_branch(new_pdv) == f"new_{PACKAGE_PRJ}_{pkg_name}"

        finally:
            del REGISTERED_TPL_PROJECTS[nsn]
            os.chdir(cur_dir)
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_renew_project_new_package_from_parent_via_package(self, mocked_app_options):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        pkg_name = "new_tst_pkg_prj"
        project_path = norm_path(os.path.join(parent_dir, pkg_name))
        mocked_app_options['branch'] = ""
        mocked_app_options['domain'] = None
        mocked_app_options['group'] = None
        mocked_app_options['namespace'] = ""
        mocked_app_options['project'] = pkg_name
        mocked_app_options['path'] = ""
        mocked_app_options['verbose'] = False
        cur_dir = os.getcwd()
        try:
            os.makedirs(parent_dir)
            os.chdir(parent_dir)

            _renew_project(project_dev_vars(), PACKAGE_PRJ)

            new_pdv = project_dev_vars(project_path=pkg_name)
            assert new_pdv['project_type'] == PACKAGE_PRJ
            assert norm_path(pkg_name) == project_path
            assert new_pdv['project_path'] == project_path
            assert os.path.isdir(project_path)
            assert os.path.isfile(os.path.join(project_path, pkg_name, PY_INIT))
            assert not os.path.isfile(os.path.join(project_path, BUILD_CONFIG_FILE))
            assert os.path.isdir(os.path.join(project_path, DOCS_FOLDER))
            assert not os.path.isdir(os.path.join(project_path, TEMPLATES_FOLDER))
            assert os.path.isdir(os.path.join(project_path, TESTS_FOLDER))

            assert _git_current_branch(new_pdv) == f"new_{PACKAGE_PRJ}_{pkg_name}"

        finally:
            os.chdir(cur_dir)
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_template_projects_new_dev_req(self, mocked_app_options, module_repo_path):
        # mocked_app_options needed to reset all _template_version_options
        root_prj_imp_name = 'aedev.aedev'
        root_prj_pgk_name, root_prj_ver = project_version(root_prj_imp_name, list(REGISTERED_TPL_PROJECTS.keys()))
        assert root_prj_pgk_name == norm_name(root_prj_imp_name)
        assert root_prj_ver

        dev_req_list = []
        pdv = {'namespace_name': 'aedev', 'dev_require': dev_req_list, 'project_path': module_repo_path,
               'project_type': MODULE_PRJ}

        tpl_projects = _template_projects(pdv)
        assert len(tpl_projects) == 2
        assert tpl_projects[0]['import_name'] == root_prj_imp_name
        assert tpl_projects[0] == REGISTERED_TPL_PROJECTS[root_prj_imp_name + PROJECT_VERSION_SEP + root_prj_ver]
        assert tpl_projects[1]['import_name'] == 'aedev.tpl_project'
        assert pdv['dev_require'] is dev_req_list
        assert len(pdv['dev_require']) == 2

    def test_template_projects_dev_req_lock(self, mocked_app_options, module_repo_path):
        # mocked_app_options needed to reset all _template_version_options
        dev_req_list = ['any_non_tpl_prj']
        drl_copy = dev_req_list.copy()
        pdv = {'namespace_name': 'aedev', 'dev_require': dev_req_list, 'project_path': module_repo_path,
               'project_type': MODULE_PRJ}

        tpl_projects = _template_projects(pdv)
        assert len(tpl_projects) == 0
        assert pdv['dev_require'] is dev_req_list
        assert pdv['dev_require'] == drl_copy

    def test_wait(self, mocked_app_options):
        mocked_app_options['delay'] = 0
        _wait()


@skip_gitlab_ci  # skip on gitlab because of a missing remote repository user account token
class TestHiddenHelpersRemote:
    """ test private helper functions that need authentication against git remote hosts. """
    def test_init_act_exec_args_show_repo(self, mocked_app_options, patched_exit_call_wrapper):
        mocked_app_options['action'] = 'show_repo'
        mocked_app_options['arguments'] = []
        mocked_app_options['domain'] = 'gitlab.com'
        mocked_app_options['force'] = False
        mocked_app_options['group'] = 'tst_user'
        mocked_app_options['namespace'] = ""
        mocked_app_options['path'] = ""
        mocked_app_options['project'] = 'repo'
        mocked_app_options['token'] = "anyInvalidTstToken"

        patched_exit_call_wrapper(_init_act_exec_args)    # fails on authenticating if --force is false / not specified

        mocked_app_options['token'] = cae.get_variable('token')
        ini_pdv, act_name, act_args, act_flags = _init_act_exec_args()

        assert isinstance(ini_pdv, dict)    # PdvType
        assert 'host_api' in ini_pdv
        assert act_name == 'show_repo'
        assert act_args == []
        assert act_flags == {}
        assert isinstance(ini_pdv['host_api'], GitlabCom)
        assert ini_pdv['repo_group'] == mocked_app_options['group']
        # package option will not be propagated onto ini_pdv['project_name']


def test_temp_context_teardown():
    if git_repo_manager_main.TEMP_CONTEXT:
        git_repo_manager_main.TEMP_CONTEXT.cleanup()
        git_repo_manager_main.TEMP_CONTEXT = None
    assert git_repo_manager_main.TEMP_CONTEXT is None
