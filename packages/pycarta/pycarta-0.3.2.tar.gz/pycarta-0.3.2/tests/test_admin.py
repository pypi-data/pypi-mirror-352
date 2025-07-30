import logging
import pytest
from pprint import pformat
from pycarta.admin.file import *
from pycarta.admin.group import *
from pycarta.admin.permission import *
from pycarta.admin.secret import *
from pycarta.admin.types.resource_type import ResourceType, get_resource_class
from pycarta.admin.user import *
from requests.exceptions import HTTPError


logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def caplog(caplog):
    caplog.set_level(logging.INFO, logger=logger.name)
    yield caplog


@pytest.fixture()
def test_file():
    filename = "pytest_test_file.txt"
    with open(filename, "w") as ofs:
        ofs.write("This is a test file.\n")
    yield filename
    import os
    os.remove(filename)


@pytest.fixture()
def test_file_byte_contents(test_file):
    with open(test_file, "r") as ifs:
        contents = ifs.read().encode()
        yield contents


EXPECTED = {
    "list_file_sources": ["Carta", "HyperThought"],
    "file_source_support": {
        "Carta": ['Containers', 'FileUpdate', 'FullFileList'],
        "HyperThought": ['Containers', 'PartialFileList'],
    },
    "list_files": [("Carta", "/")],
}


# region file.py
# @pytest.mark.skip(reason="Skipping temporarily to reduce Carta API calls.")
class TestFile:
    def test_list_file_sources(self):
        sources = list_file_sources()
        logger.info(f"File sources: {pformat(sources)}")
        assert set(sources) == set(EXPECTED["list_file_sources"])

    @pytest.mark.parametrize("source", EXPECTED["list_file_sources"])
    def test_file_source_support(self, source):
        support = file_source_support(source)
        assert set(support) == set(EXPECTED["file_source_support"][source])

    @pytest.mark.parametrize(
            "source,path",
            [(src, p) for src in EXPECTED["list_file_sources"] for p in ("/", None)])
    def test_list_files(self, source, path):
        files = None
        if source == "HyperThought":
            with pytest.raises(HTTPError) as e_info:
                files = list_files(source, path)
        else:
            files = list_files(source, path)
        logger.info(f"{(source, path)}: {pformat(files)}")

    @pytest.mark.parametrize("source_path", EXPECTED["list_files"])
    def test_get_file(self, source_path):
        import csv
        import random
        from tempfile import TemporaryFile
        source, path = source_path
        csv_files = [f for f in list_files(source, path) if f.name.endswith(".csv")]
        file_ = random.choice(csv_files)
        with TemporaryFile("w+") as f:
            f.write(get_file(source, file_id=file_.id).decode(errors="replace"))
            f.seek(0)
            reader = csv.reader(f)
            for irow in range(5):
                row = next(reader)
                logger.info(f"Row {irow}: {row}")
        assert True

# These tests exposed issues with the Carta files API. Functions in file.py
# have been commented out as well to avoid setting unmanaged expectations for
# the pycarta API.
    # @pytest.mark.parametrize("source_path", EXPECTED["list_files"])
    # def test_upload_file(self, source_path, test_file, test_file_byte_contents):
    #     source, _ = source_path
    #     # contents = test_file_byte_contents
    #     fileInfo : FileInformation | None = None
    #     try:
    #         fileInfo = upload_file(
    #             source,
    #             test_file_byte_contents.encode(), # open(test_file, "rb"),
    #             file_name=test_file)
    #         logger.info(f"{test_file!r} uploaded.")
    #     finally:
    #         if getattr(fileInfo, "id", None):
    #             delete_file(source, fileInfo.id)
    #             logger.info(f"{test_file!r} deleted.")
    #     assert False


#     def test_replace_file(self):
#         pass

#     def test_delete_file(self):
#         pass

#     def test_file_presigned(self):
#         pass

#     def test_delete_presigned(self):
#         pass

#     def test_get_presigned(self):
#         pass

#     def test_complete_file_presigned(self):
#         pass

#     def test_abort_file_presigned(self):
#         pass
# endregion


# region user.py
# @pytest.mark.skip(reason="Skipping temporarily to reduce Carta API calls.")
class TestUser:
    def setup_method(self):
        from pycarta.admin.types import User
        self.user = User(name="pycarta-pytest",
                         email="pytest@example.com",)
        
    def test_get_current_user(self):
        from pycarta import get_agent
        agent = get_agent()
        user = get_current_user()
        logger.info(f"Current user: {pformat(user.model_dump())}")
        assert agent.username == user.name

    def test_create_user(self):
        from pycarta.admin.types import User
        user = create_user(self.user, exists_ok=True)
        with pytest.raises(InvalidParameterException) as e_info:
            user = create_user(self.user)
        logger.info(f"Created user: {pformat(user.model_dump())}")
        assert user.name == self.user.name

    @pytest.mark.skip(reason="No convenient way to test password reset.")
    def test_reset_user_password(self):
        reset_user_password("pycarta-pytest")

    def test_list_users(self):
        users = [u.model_dump() for u in list_users()]
        logger.info(f"Users: {pformat(users[:5])}")
        assert len(users) > 0

    def test_get_user(self):
        user_ = get_current_user()
        user = get_user(
            username=user_.name,
            email=user_.email,
        )
        assert user.id == user_.id
        user = get_user(
            username=user_.name[:3],
            email=user_.email[:3],
            partial_match=True
        )
        try:
            # check if the user matches
            assert user.id == user_.id
        except AttributeError:
            # if multiple users match the partial search, check each.
            assert any([u.id == user_.id for u in user])
# endregion

# region group.py
# @pytest.mark.skip(reason="Skipping temporarily to reduce Carta API calls.")
class TestGroup:
    from pycarta.admin.types import User, Group
    from pycarta.exceptions import InvalidParameterException

    def setup_method(self):
        self.user = get_current_user()
        self.group = Group(name="Pytest", organization="Test")

    def test_create_group(self):
        create_group(self.group, exists_ok=True)
        with pytest.raises(InvalidParameterException) as e_info:
            create_group(self.group)

    def test_add_user_to_group(self):
        add_user_to_group(
            self.user,
            self.group,)

    def test_list_members(self):
        users = [u.model_dump() for u in list_members(self.group)]
        logger.info(f"Group members: {pformat(users[:5])}")
        assert len([u for u in users if u["id"] == self.user.id])
# endregion


# region permission.py
# @pytest.mark.skip(reason="Skipping temporarily to reduce Carta API calls.")
class TestPermission:
    from requests import HTTPError
    def setup_method(self):
        from pycarta.admin.types import UserType
        self.user = get_current_user()
        self.user_types = [
            UserType.NAMESPACE,
            UserType.PROJECT,
            UserType.USER,
            UserType.GROUP,
            UserType.WORKFLOW,
            UserType.WORKSPACE,
        ]
        self.resource_types = resource_types()
        self.resources = {
            rtype.value: get_user_resources(rtype)
            for rtype in self.resource_types
        }
        self.permissions = [
            {
                'resource_id': '7cc67a79-490f-4bcc-aa5c-bab6d2835bc2',
                'user_type': 'ProjectItem',
            },
            {
                'resource_id': 'eec68fba-ecc8-438e-8bbb-b30a988df06c',
                'user_type': 'User',
            },
            {
                'resource_id': '34c60924-d315-c8a2-1a3f-2390da720339',
                'user_type': 'User',
            },
            {
                'resource_id': 'f6c50017-f301-d761-a3d2-83156edbdcab',
                'user_type': 'User',
            },
            {
                'resource_id': '46c67a6d-92d8-1b5c-3777-bd5da253ae35',
                'user_type': 'User',
            },
        ]

    def test_resource_types(self):
        rtypes = resource_types()
        logger.info(f"Resource types: {pformat(rtypes)}")

    def test_get_user_resources(self):
        for i, rtype in enumerate(self.resource_types):
            if i % 2:
                # enum access
                _ = get_user_resources(rtype)
            else:
                # string access (by value)
                _ = get_user_resources(rtype.value)

    def test_get_resource(self):
        import random
        for rtype, resources in self.resources.items():
            try:
                rid = random.choice(resources).id
            except IndexError:
                # Empty resources list
                continue
            resource = get_resource(rtype, rid)
            logger.info(f"Resource: {pformat(resource.model_dump())}")

    def test_get_user_permission(self):
        import random
        from pycarta.exceptions import PermissionDeniedException, CartaServerException
        for rtype, resources in self.resources.items():
            try:
                resource = random.choice(resources)
            except IndexError:
                # Empty resources list
                continue
            for i, utype in enumerate(self.user_types):
                try:
                    if i % 2:
                        # By value
                        permission = get_user_permission(
                            resource.id,
                            self.user.id,
                            utype.value,)
                    else:
                        # By enum
                        permission = get_user_permission(
                            resource.id,
                            self.user.id,
                            utype,)
                except (PermissionDeniedException, CartaServerException) as e:
                    logger.info(f"Raised {type(e)} Exception: {str(e)}")
                    pass
                else:
                    logger.info(f"Permission for {str(resource)}: {pformat(permission.model_dump())}")

    @pytest.mark.skip(reason="No convenient way to test setting user permissions.")
    def test_set_user_permission(self):
        pass

    @pytest.mark.skip(reason="No convenient way to test removing user permissions.")
    def test_remove_user_permission(self):
        pass

    def test_list_resource_permissions(self):
        for obj in self.permissions:
            _ = list_resource_permissions(**obj)
# endregion


# region project.py
@pytest.mark.skip(reason="No convenient way to test project CRUD operations.")
class TestProject:
    pass
# endregion


# region resource_type.py
class TestResourceType:
    def test_resource_types(self):
        types = [getattr(ResourceType, t) for t in dir(ResourceType)
                 if not t.startswith("_")]
        for n, t in enumerate(types):
            if n % 2:
                # enum access
                _ = get_resource_class(t)
            else:
                # string access (by namd and by value)
                if n//2 % 2:
                    _ = get_resource_class(t.name)
                else:
                    _ = get_resource_class(t.value)
# endregion


# region secret.py
@pytest.fixture()
def secret():
    return {
        "name": "pytest_secret",
        "value": "This is a test secret.",
    }

class TestSecret:
    def test_put_secret(self, secret):
        logger.info(f"Putting secret: {pformat(secret)}")
        put_secret(**secret)

    def test_get_secret(self, secret):
        value = get_secret(secret["name"])
        assert value == secret["value"]

    def test_put_big_secret(self):
        value = (1024 + 1) * "a"
        with pytest.raises(ValueError) as e_info:
            put_secret(name="pytest_big_secret", value=value)

# endregion


# region workspace.py
@pytest.mark.skip(reason="Workspaces are deprecated?")
class TestWorkspace:
    pass
# endregion