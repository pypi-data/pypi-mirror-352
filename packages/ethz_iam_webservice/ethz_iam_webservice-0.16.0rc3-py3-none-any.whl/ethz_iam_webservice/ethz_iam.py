import json

from .conn import IAMApi
from .group import Group, GroupAlternative
from .mailinglist import Mailinglist
from .guest import Guest
from .user import User
from .verbose import VERBOSE


class ETH_IAM:
    def __init__(
        self,
        admin_username,
        admin_password,
    ):
        self._admin_username = admin_username
        self._admin_password = admin_password
        self.group = Group(admin_username=admin_username, admin_password=admin_password)
        self.new_group = self.group.create
        self.update_group = self.group.update
        self.user = User(
            admin_username=admin_username, admin_password=admin_password
        )
        self.group_alternative = GroupAlternative(admin_username, admin_password)
        self.search_groups = self.group_alternative.search_groups
        self.search_users = self.user.search_users
        self.update_persona = self.user.update_persona
        self.guest = Guest(admin_username=admin_username, admin_password=admin_password)
        self.get_guest = self.guest.get_guest
        self.new_guest = self.guest.create
        self.extend_guest = self.guest.extend
        self.update_guest = self.guest.update
        self.delete_guest = self.guest.delete

    def get_services(self, username, service_name=None):
        """
        Get all services of a user or a specific service.
        If service_name is None, all services are returned.
        """
        endpoint = f"/users/{username}/services"
        if service_name:
            endpoint += f"/{service_name}"
        iam = IAMApi(self._admin_username, self._admin_password)
        data = iam.get_request(endpoint)
        return data

    def grant_service(self, username, service_name, **kwargs):
        """
        Grant a service to a user.
        Additional parameters can be passed as keyword arguments.
        """
        endpoint = f"/users/{username}/services/{service_name}"
        iam = IAMApi(self._admin_username, self._admin_password)
        resp = iam.put_request(endpoint, kwargs)
        if resp.ok:
            if VERBOSE:
                print(f"Service {service_name} for user {username} successfully granted.")
            return resp.json()
        else:
            data = json.loads(resp.content.decode())
            raise ValueError(data["message"])


    def revoke_service(self, username, service_name):
        """
        Revoke a service for a user.
        """
        endpoint = f"/users/{username}/services/{service_name}"
        iam = IAMApi(self._admin_username, self._admin_password)
        resp = iam.delete_request(endpoint)
        if resp.ok:
            if VERBOSE:
                print(f"Service {service_name} for user {username} successfully revoked.")
        else:
            data = json.loads(resp.content.decode())
            raise ValueError(data["message"])
    

    def get_request(self, endpoint, hostname=None, endpoint_base=None):
        resp = self.get_request(
            endpoint=endpoint, hostname=hostname, endpoint_base=endpoint_base
        )
        if resp.ok:
            data = json.loads(resp.content.decode())
            return data
        elif resp.status_code == 401:
            raise ValueError(
                "Provided admin-username/password is incorrect or you are not allowed to do this operation"
            )
        elif resp.status_code == 404:
            raise ValueError("No such user/person/group.")
        else:
            print(resp.status_code)
            try:
                data = json.loads(resp.content.decode())
            except json.decoder.JSONDecodeError as exc:
                raise ValueError(f"received http status: {resp.status_code}") from exc

    def get_user(self, identifier):
        return self.user.get_user(identifier)

    def get_guests_of_lz(self, lz):
        return self.guest.search_guests(host_leitzahl=lz)

    def del_group(self, name):
        """Delete a group and remove it from all its target systems."""
        group = self.group.get_group(name)
        group.delete()

    def get_groups(self, **kwargs):
        """
        agroup=<Admin Group>  -- Get all groups of a given admin group
        name=group_name*      -- all groups starting with «group_name*»
        """
        if kwargs:
            args = "&".join("{}={}".format(key, val) for key, val in kwargs.items())
            endpoint = f"/groups?{args}"
        else:
            raise ValueError("please provide a name or agroup parameter (or both)")
        iam = IAMApi(self._admin_username, self._admin_password)
        data = iam.get_request(endpoint)
        groups = []
        for data_entry in data:
            groups.append(Group.new_from_data(data=data_entry))
        return groups

    def get_group(self, identifier):
        return self.group.get_group(identifier)

    def recertify_group(self, identifier):
        iam = IAMApi(self._admin_username, self._admin_password)
        endpoint = f"/groups/{identifier}/recertify"
        data = iam.put_request(endpoint)
        group = Group.new_from_data(data)
        return group

    def _to_from_group(self, members, action="add", mess="{}"):
        endpoint = f"/groups/{self.name}/members/{action}"
        resp = self.conn.put_request(endpoint, members)
        if resp.ok:
            if VERBOSE:
                print(mess.format(self.name))
            group = Group.new_from_data(resp.json())
            self.replace_field_values(group)
        else:
            data = json.loads(resp.content.decode())
            raise ValueError(data["message"])

    def get_mailinglist(self, identifier: str = None, **kwargs):
        if not identifier:
            raise ValueError("please provide an identifier")

        if "@" in identifier:
            endpoint = f"/mailinglists?mail={identifier}"
        elif kwargs:
            args = "&".join(f"{key}={val}" for key, val in kwargs.items())
            endpoint = f"/mailinglists/?{args}"
        else:
            endpoint = f"/mailinglists/{identifier}"

        iam = IAMApi(self._admin_username, self._admin_password)
        data = iam.get_request(endpoint=endpoint)
        if len(data) > 1:
            raise ValueError(
                f"Identifier {identifier} returned more than one group, it returned {len(data)}."
            )
        return Mailinglist(iam=iam, data=data[0])
