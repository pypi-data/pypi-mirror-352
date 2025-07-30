import argparse
import ast
import os
import random
import re
import shlex
from pathlib import Path
from urllib.request import urlopen

import pytest
from pypigeon.client import make_base_url
from pypigeon.pcmd import cli
from pypigeon.pcmd.commands import Commands as PcmdCommands
from pypigeon.pigeon_core import Client as CoreClient
from pypigeon.pigeon_core.api.user import user_create_user
from pypigeon.pigeon_core.login import Login
from pypigeon.pigeon_core.login import LoginError
from pypigeon.pigeon_core.login import to_token_file
from pypigeon.pigeon_core.models import NewUser
from yaml import dump as yaml_dump
from yaml import safe_load


# The tests in this test suite are designed to be run against a local
# development instance of Pigeon hosted at localhost:8170, similar to
# the Cypress tests in `pigeon-nuxt`. In order to be able to run these
# tests, be sure to have the local development instance running in the
# background with the command:
#
#    flask run --debug
#


@pytest.fixture
def local_user(tmp_path):
    # try to log in with the credentials
    username, password = "pcmd.tester", "insecure"
    base_url = make_base_url("localhost:8170", "http")
    try:
        authenticated = Login(CoreClient(base_url=base_url)).with_password(
            username, password
        )
    except LoginError:
        print("Login failed, trying to create new user...")
        user_create_user.sync(
            body=NewUser(
                given_name="pcmd",
                last_name="tester",
                user_email="john.doe@example.com",
                user_name=username,
                password=password,
            ),
            client=CoreClient(base_url=base_url),
        )
        authenticated = Login(CoreClient(base_url=base_url)).with_password(
            username, password
        )

    token_file = tmp_path / "token"
    to_token_file(authenticated, token_file)

    yield str(token_file)


def random_id():
    return f"rr{random.randint(0, 1048576):05x}rr"


def mask(rv):
    # mask UUIDs
    rv = re.sub(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "00000000-0000-0000-0000-000000000000",
        rv,
    )
    # mask timestamps
    rv = re.sub(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.[0-9+:]*)?",
        "1970-01-02T03:04:05.000000",
        rv,
    )
    # mask task worker
    rv = re.sub(r"worker: .*", "worker: pcmd-test-mask", rv)
    # mask random ID
    rv = re.sub(r"rr[0-9a-f]{5}rr", "random-id", rv)
    # mask bundle ID
    rv = re.sub(r"b-[a-zA-Z0-9]{8}", "b-00000000", rv)

    return rv


@pytest.fixture
def pcmd(local_user, capsys):
    def _cmd(args, masked=True):
        if isinstance(args, str):
            args = shlex.split(args)
        cli.main(["-H", "localhost:8170", "--insecure", "-k", local_user] + args)

        outv = capsys.readouterr()
        if not outv.err:
            rv = outv.out
            if masked:
                rv = mask(rv)
            return rv

        return outv

    yield _cmd


@pytest.fixture
def test_target_user(pcmd):
    response = user_create_user.sync(
        body=NewUser(
            given_name="pcmd",
            last_name="test target",
            user_email="john.doe@example.com",
            user_name="pcmd.test.target",
            password=random_id(),
        ),
        client=CoreClient(base_url=make_base_url("localhost:8170", "http")),
    )

    yield response.subject_id

    pcmd("users delete pcmd.test.target")


@pytest.fixture
def scratch_collection(pcmd):
    collection_name = f"pcmd-test.{random_id()}"
    rv = safe_load(pcmd(f"collection new {collection_name}", masked=False))

    yield collection_name, rv["id"]

    pcmd(f"collection delete {rv['id']}")


def test_pcmd_auth_whoami(pcmd, snapshot):
    pcmd('auth set-metadata x-tos \'{"toc":3,"coc":6,"priv":3,"com":1}\'')

    assert pcmd("auth whoami") == snapshot


# NOTE: If the following tests are failing with "Unexpected status
# code: 403", you should grant the `pcmd.tester` user full admin
# access to your local development instance with the command:
#
#   flask admin grant pcmd.tester
#


def test_pcmd_tasks(pcmd, snapshot):
    stats = safe_load(pcmd("tasks stats"))
    assert stats.keys() == {"queued", "results", "schedules"}

    schedules = safe_load(pcmd("tasks schedules"))["schedules"]
    assert len(schedules) >= 2

    results = safe_load(pcmd("tasks results --idemkey tasks-backends-sqlite-vacuum"))[
        "results"
    ]
    if len(results) > 0:
        assert results[0] == snapshot


def test_pcmd_users(pcmd, test_target_user):
    rv = pcmd("users list")
    assert set(rv.splitlines()[0].split()) == {
        "account_id",
        "created_on",
        "metadata",
        "subject_id",
        "user_name",
        "visibility_level",
        "given_name",
        "groups",
        "last_name",
        "user_email",
    }
    assert "pcmd.test.target" in rv

    # disable and enable
    rv = safe_load(pcmd("users disable pcmd.test.target"))
    assert rv["disabled_on"] is not None

    rv = safe_load(pcmd("users enable pcmd.test.target"))
    assert rv["disabled_on"] is None


def test_pcmd_groups(pcmd, test_target_user, snapshot):
    group_name = f"test-pcmd-group.{random_id()}"
    new_group = pcmd(f"groups new {group_name}", masked=False)
    group_id = safe_load(new_group)["id"]
    assert mask(new_group) == snapshot

    groups = safe_load(pcmd("groups list"))["groups"]
    assert safe_load(mask(new_group)) in groups

    pcmd(f"groups join {group_id} {test_target_user}")

    assert len(safe_load(pcmd(f"groups list-members {group_id}"))["members"]) == 2

    pcmd(f"groups update --name new-test-group {group_id}")

    pcmd(f"groups delete {group_id}")


def test_pcmd_accounts(pcmd, snapshot, tmp_path, scratch_collection):
    collection_name, collection_id = scratch_collection

    account_name = f"test-pcmd-account.{random_id()}"
    new_account = pcmd(f"accounts new {account_name} --description heyyo", masked=False)
    account_id = safe_load(new_account)["id"]
    assert mask(new_account) == snapshot

    accounts = safe_load(pcmd("accounts list", masked=False))["accounts"]
    assert safe_load(new_account) in accounts

    # update space
    index_file = tmp_path / "index.md"
    with open(index_file, "w") as fp:
        fp.write("# Hello world!\n")
    pcmd(f"collection upload {collection_name} {index_file}")
    pcmd(f"accounts update-space {account_id} {collection_id}")
    response = urlopen(
        f"http://localhost:8170/api/v1/account/{account_id}/pages/index.md"
    )
    assert response.code == 200

    pcmd(f"accounts delete {account_id}")

    accounts = safe_load(pcmd("accounts list", masked=False))["accounts"]
    assert safe_load(new_account) not in accounts


def test_pcmd_admin_grant(pcmd, test_target_user):
    pcmd(f"admin grant-admin -o group {test_target_user}")

    rv = pcmd("admin list-admins", masked=False)
    assert test_target_user in rv

    pcmd(f"admin revoke-admin {test_target_user}")

    rv = pcmd("admin list-admins", masked=False)
    assert test_target_user not in rv


def test_pcmd_admin_config(pcmd, tmp_path, capsys):
    rv = safe_load(pcmd("admin config get"))
    assert "datastores" in rv
    assert "authentication" in rv

    pcmd(
        "admin config set datastores.pcmd_test"
        + f' \'{{"enabled": false, "path": "{tmp_path}", "type": "local"}}\''
    )

    rv = safe_load(pcmd("admin config get", masked=False))
    assert "pcmd_test" in rv["datastores"]

    newdir = tmp_path / "new"
    rv["datastores"]["pcmd_test"]["path"] = str(newdir)

    config_fn = tmp_path / "config.yaml"
    with open(config_fn, "w") as fp:
        yaml_dump(rv, fp)

    pcmd(f"admin config put {config_fn}")

    rv = safe_load(pcmd("admin config get"))
    assert "pcmd_test" in rv["datastores"]
    assert rv["datastores"]["pcmd_test"]["path"] == str(newdir)

    pcmd("admin config delete datastores.pcmd_test")

    rv = safe_load(pcmd("admin config get"))
    assert "pcmd_test" not in rv["datastores"]


def test_pcmd_collection(pcmd, tmp_path, scratch_collection):
    collection_name, collection_id = scratch_collection
    rv = pcmd("collection list", masked=False)
    assert collection_name in rv
    assert collection_id in rv

    test_file = tmp_path / "test.txt"
    with open(test_file, "w") as fp:
        fp.write("hello world this is a test\n")

    pcmd(f"collection upload {collection_name} {test_file}")

    test_file.unlink()

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    pcmd(f"collection download {collection_name} test.txt")
    os.chdir(old_cwd)

    assert test_file.exists()


def test_pcmd_pdd(pcmd, scratch_collection, snapshot):
    collection_name, collection_id = scratch_collection
    common_pdd_fn = Path(__file__).parent / "common_pdd.json"

    rv = pcmd(f"pdd upload {collection_id} {common_pdd_fn}", masked=False)
    assert mask(rv) == snapshot
    safe_load(rv)["id"]

    assert pcmd(f"pdd list {collection_name} common_pdd.json") == snapshot

    pcmd(f"pdd set-order {collection_name} common_pdd.json 6fr70ICV O8zPEsiM")

    assert pcmd(f"pdd list {collection_name} common_pdd.json") == snapshot

    assert (
        pcmd(f"pdd bundle {collection_name} common_pdd.json MyBundle O8zPEsiM 6fr70ICV")
        == snapshot
    )

    assert pcmd(f"pdd list {collection_name} common_pdd.json") == snapshot


def test_pcmd_cdeset(pcmd, scratch_collection):
    collection_name, collection_id = scratch_collection
    common_pdd_fn = Path(__file__).parent / "common_pdd.json"

    rv = pcmd(f"pdd upload {collection_id} {common_pdd_fn}", masked=False)
    item_id = safe_load(rv)["id"]

    cdeset_name = f"pcmd.{random_id()}"
    pcmd(f"cdeset new {cdeset_name} 'pcmd test cde set'")

    rv = pcmd("cdeset list", masked=False)
    assert cdeset_name in rv

    pcmd(f"cdeset copy-from-pdd {cdeset_name} {collection_id} LIVE {item_id}")

    rv = safe_load(pcmd("cdeset list", masked=False))
    cdeset = {"f": c for c in rv["cdesets"] if c["name"] == cdeset_name}.get("f")
    assert cdeset["num_cdes"] == 2
    assert cdeset["description"] == "pcmd test cde set"

    pcmd(f"cdeset delete {cdeset_name}")


###
### Coverage Verification
###


class CoverageScanner(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.actions = {}

    def register_actions(self, parser, actlevel=None):
        if actlevel is None:
            actlevel = self.actions

        actions = parser._get_positional_actions()
        if actions and actions[0].choices:
            for arg, subparser in actions[0].choices.items():
                self.register_actions(subparser, actlevel.setdefault(arg, {}))

    def coverage_needed(self):
        needed = set()

        def _walk(d, s=None):
            if s is None:
                s = []
            if "SEEN" in d:
                return
            if not d:
                needed.add(" ".join(s))
            for k in d:
                _walk(d[k], s + [k])

        _walk(self.actions)
        return needed

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            return self.generic_visit(node)
        if node.func.id != "pcmd":
            return self.generic_visit(node)
        if not node.args:
            return self.generic_visit(node)

        def _resolve(arg):
            if isinstance(arg, ast.Constant):
                return arg.value
            elif isinstance(arg, ast.JoinedStr):
                return _resolve(arg.values[0])
            elif isinstance(arg, ast.BinOp):
                return _resolve(arg.left)
            else:
                print(ast.dump(node, indent=2))
                raise Exception(
                    f"unexpected pcmd call on line {node.lineno}: {ast.unparse(node)}"
                )

        pcmd_arg = _resolve(node.args[0])

        actlevel = self.actions
        for word in shlex.split(pcmd_arg):
            if word in actlevel:
                actlevel = actlevel[word]

        if not actlevel:
            actlevel["SEEN"] = True


def test_pcmd_coverage():
    # This checks all of the pcmd() calls in the AST of this file and
    # matches them up with commands defined in the pcmd command set.
    # Any commands not called will show up in
    # `scanner.coverage_needed()`.

    argparser = argparse.ArgumentParser()
    PcmdCommands._add_to_parser(
        argparser.add_subparsers(title="commands", required=True)
    )
    scanner = CoverageScanner()
    scanner.register_actions(argparser)

    test_ast = ast.parse(open(__file__).read(), filename=__file__)
    scanner.visit(test_ast)

    assert scanner.coverage_needed() == set()
