from .utils import to_date

servicename_map = {
    'AD':'Active Directory', 
    'AD-UPG': 'AD UserPrivateGroup', 
    'BiolAuth': 'BiolAuth', 
    'ItetAuth': 'ItetAuth', 
    'HestAuth': 'HestAuth',
    'LDAPS-Proxy': 'LDAPS-Proxy',
    'LDAP': 'LDAP',
    'Mailbox': 'Mailbox', 
    'OpenDirectory': 'OpenDirectory', 
    'Physik-Mail': 'Physik-Mail', 
    'wlan':  'Wlan_Vpn'
}

class Service:
    def __init__(self, conn, username, service_name, data):
        self.__dict__["username"] = username
        self.__dict__["service_name"] = service_name
        self.__dict__["conn"] = conn
        # self.__dict__['data'] = data
        if data:
            for key in data:
                if key in ["delete_after", "login_until"]:
                    d = to_date(data[key])
                    data[key] = d.strftime("%Y-%m-%d")
                setattr(self, key, data[key])
        self.__dict__["updated_attrs"] = {}

    def revoke(self):
        endpoint = f"users/{self.username}/service/{self.service_name}"
        success_msg = f"service {self.service_name} for user {self.username} successfully revoked."
        not_allowed_msg = f"you are not allowed to revoke service {self.service_name} for user {self.username}."
        failed_msg = (
            f"failed to revoke service {self.service_name} for user {self.username}"
        )
        self.conn._delete_request(
            endpoint,
            success_msg=success_msg,
            not_allowed_msg=not_allowed_msg,
            failed_msg=failed_msg,
        )

    def save(self):
        if not self.updated_attrs:
            return

        endpoint = f"users/{self.username}/service/{self.service_name}"
        success_msg = f"service {self.service_name} for user {self.username} successfully updated."
        not_allowed_msg = f"you are not allowed to update these {self.service_name} service attributes for user {self.username}."
        failed_msg = f"failed to update {self.service_name} service attributes for user {self.username}"
        self.conn._put_request(
            endpoint,
            body=self.updated_attrs,
            success_msg=success_msg,
            not_allowed_msg=not_allowed_msg,
            failed_msg=failed_msg,
        )


class Mailbox(Service):
    def __dir__(self):
        return [
            "sn",
            "givenName",
            "displayName",
            "description",
            "mail",
            "isHidden",
            "noMailReceive",
            "quota",
            "homeDrive",
            "homeDirectory",
            "profilePath",
            "unixHomeDirectory",
            "loginShell",
            "primaryGroup",
            "unifiedMessagingTask",
            "telephoneNumber",
            "forward_address",
            "proxyAddresses",
        ]

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        self.__dict__["updated_attrs"][name] = value

    def __getattr__(self, name):
        return self.__dict__[name]
