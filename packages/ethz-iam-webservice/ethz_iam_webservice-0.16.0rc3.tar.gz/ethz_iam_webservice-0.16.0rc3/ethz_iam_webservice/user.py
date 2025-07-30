import json
from dataclasses import asdict, dataclass, field
from typing import List
from datetime import date

from .conn import IAMApi, IAMApiAlternative
from .service import Mailbox, Service
from .utils import to_date
from .verbose import VERBOSE

service_map = {
    "LDAP": "LDAP",
    "LDAPS": "LDAP",
    "MAILBOX": "Mailbox",
    "AD": "AD",
    "ACTIVE DIRECTORY": "AD",
    "VPN": "WLAN_VPN",
    "WLAN_VPN": "WLAN_VPN",
}

map_iamfields2internal = {
    "username": "username",
    "firstname": "firstname",
    "lastname": "lastname",
    "displayName": "displayname",
    "description": "description",
    "gender": "gender",
    "salutation": "salutation",
    "preferredLanguage": "preferred_language",
    "mail": "mail",
    "department": "department",
    "nuid": "nuid",
    "npid": "npid",
    "persid": "persid",
    "uidNumber": "uidNumber",
    "gidnumber": "gidNumber",
    "orcID": "orcid",
    "startDate": "start_date",
    "createTimestamp": "cre_date",
    "endDate": "valid_until",
    "modifyTimestamp": "mod_date",
    "services": "services",
    "userState": "status",
    "persCat": "persCat",
    "persCatText": "persCatText",
    "officePlace": "office_place",
    "officeAddressLine1": "office_address_line1",
}

@dataclass
class UserRelation():
    """Represents a relation of a user in the IAM system.
    Relations are used to manage the employment or affiliation of a user with ETH Zurich.
    """
    beschaeftigungsgrad: str = ""
    beziehung: str = ""
    description: str = ""
    dienstverhaeltnis: str = "" # Employment relationship
    dienstverhaeltnisCode: str = ""
    effectiveEndDate: str = ""  # "9999-12-31T00:00:00.000Z"
    endDate: str = ""  # "9999-12-31T00:00:00.000Z"
    hauptbeziehung: str = ""  # "TRUE"
    leitzahl: str = ""  # "06006"
    orgeinheit: str = ""  # "Scientific Software and Data Mgmt."
    persCat: list[str] = field(default_factory=list)  # ["P00"]
    persid: str = ""  # "55327"
    pnr: str = ""  # "00033018" 
    startDate: str = ""  # "2019-01-01T00:00:00.000Z"

@dataclass
class Persona():
    """
    Represents a persona in the IAM system.
    Personas are used to manage different roles or identities for a user.
    """

    npid: str = ""
    nuid: str = ""
    username: str = ""
    cre_date: date = field(default_factory=date.today)
    start_date: date = field(default_factory=date.today)
    mod_date: date = field(default_factory=date.today)
    description: str = ""
    createTimestamp: str = ""
    state: str = ""
    uidNumber: str = ""


@dataclass
class User(IAMApi):
    username: str = ""
    lastname: str = ""
    firstname: str = ""
    displayname: str = ""
    salutation: str = ""
    preferred_language: str = ""
    mail: list[str] = field(default_factory=list)
    persCat: list[str] = field(default_factory=list)
    persCatText: list[str] = field(default_factory=list)
    office_place: str = ""
    office_address_line1: str = ""
    persid: int = -1
    npid: int = 1
    nuid: int = -1
    uidNumber: int = -1
    gidNumber: int = -1
    cre_date: str = ""
    start_date: date = field(default_factory=date.today)
    mod_date: date = field(default_factory=date.today)
    valid_until: str = ""
    description: str = ""
    department: str = ""
    gender: str = ""
    status: str = ""
    orcid: str = ""
    relations: list[UserRelation] = field(default_factory=list)
    personas: list[Persona] = field(default_factory=list)

    @property
    def data(self):
        return asdict(self)

    def delete(self):
        # Deletes a persona from the IAM system.
        endpoint = f"users/{self.username}/personas/{self.username}"
        resp = self.delete_request(endpoint)
        if resp.ok:
            if VERBOSE:
                print(f"User {self.username} deleted.")
        else:
            data = json.loads(resp.content.decode())
            raise ValueError(data["message"])

    def new_from_data(self, data):
        new_user = {}
        for data_field in data:
            if data_field in ("createTimestamp", "modifyTimestamp", "startDate", "endDate"):
                data[data_field] = to_date(data[data_field]).strftime("%Y-%m-%d")
            if data_field in map_iamfields2internal:
                new_user[map_iamfields2internal[data_field]] = data[
                    data_field
                ]
            else:
                pass

        for service in new_user.get("services", []):
            service["login_until"] = to_date(service["login_until"]).strftime(
                "%Y-%m-%d"
            )
            service["delete_after"] = to_date(service["delete_after"]).strftime(
                "%Y-%m-%d"
            )

        user = User(admin_username=self._admin_username, admin_password=self._admin_password, **new_user)
        return user

    def get_user(self, identifier):
        endpoint = f"users/{identifier}"
        user_info = self.get_request(endpoint)
        return self.new_from_data(user_info)

    def search_users(
        self,
        firstname=None,
        lastname=None,
        persid=None,
        npid=None,
        uidNumber=None,
        matrikelNr=None,
        pnr=None,
        leitzahl=None,
        email=None,
    ):
        """
        Get the data of the user/s with the attribute specified in the query parameters.
        The only allowed query parameters are (at the moment): matrikelNr,PNR,leitzahl,firstname,lastname,npid,persid,email,uidNumber. 
        """
        endpoint = "/users?"
        query = {}
        if firstname:
            query["firstname"] = firstname
        if lastname:
            query["lastname"] = lastname
        if persid:      # persid is the ETHZ person ID
            query["persid"] = persid 
        if npid:        # npid is the nethz person ID
            query["npid"] = npid
        if uidNumber:
            query["uidNumber"] = uidNumber
        if matrikelNr:
            query["matrikelNr"] = matrikelNr
        if pnr:         # pnr is the ETHZ personalnummer
            query["pnr"] = pnr
        if leitzahl:    # leitzahl is the ETHZ organizational unit number
            query["leitzahl"] = leitzahl
        if email:
            query["email"] = email
        if not query:
            raise ValueError(
                "Please provide at least one query item: email, firstname, lastname, persid, npid, uidNumber, matrikelNr, pnr or leitzahl"
            )
        querystring = "&".join(f"{k}={v}" for k, v in query.items())
        full_endpoint = endpoint + querystring
        data = self.get_request(full_endpoint)
        users = []
        for d in data:
            users.append(self.new_from_data(d))
        return users
        

    def _to_from_group(self, group_name, action="add", mess="{} {}"):
        endpoint = f"/groups/{group_name}/members/{action}"
        body = [self.username]
        self.put_request(endpoint, body)
        if VERBOSE:
            print(mess.format(self.username, group_name))

    def add_to_group(self, group_name):
        self._to_from_group(
            group_name, action="add_forgiving", mess="Added user {} to group {}"
        )

    def remove_from_group(self, group_name):
        self._to_from_group(group_name, "del", mess="Removed user {} from group {}")

    def get_relations(self):
        endpoint = f"/users/{self.username}/relations"
        relations = self.get_request(endpoint=endpoint)
        for relation in relations:
            relation["startDate"] = to_date(relation.pop("startDate", ""))
            relation["endDate"] = to_date(relation.pop("endDate", ""))
            relation["effectiveEndDate"] = to_date(
                relation.pop("effectiveEndDate", "")
            )
            relation["leitzahl"] = relation.pop("leitzahl", "")
            relation["persCat"] = relation.pop("persCat", [])
            self.relations.append(UserRelation(**relation))
        return self.relations

    def get_personas(self):
        endpoint = f"/users/{self.username}/personas"
        personas = self.get_request(endpoint=endpoint)
        for persona in personas:
            persona["cre_date"] = to_date(persona.pop("createTimestamp", ""))
            persona["start_date"] = to_date(persona.pop("startDate", ""))
            persona["mod_date"] = to_date(persona.pop("modifyTimestamp", ""))
            persona["npid"] = persona.pop("NPID", "")
            persona["nuid"] = persona.pop("NUID", "")
            persona["username"] = persona.pop("cn", "")
            self.personas.append(Persona(**persona))
        return self.personas

    def update_persona(self, host_username, username, description):
        endpoint = f"/users/{host_username}/personas/{username}"
        body = {"description": description}
        return self.put_request(endpoint=endpoint, body=body)

    def grant_service(self, service_name) -> List:
        if service_name.upper() in service_map:
            service_name = service_map[service_name.upper()]
        endpoint = f"users/{self.username}/service/{service_name}"
        info = self.post_request(endpoint, {})
        return info

    def revoke_service(self, service_name):
        if service_name.upper() in service_map:
            service_name = service_map[service_name.upper()]
        endpoint = f"users/{self.username}/service/{service_name}"
        resp = self.delete_request(endpoint)
        if resp.ok:
            if VERBOSE:
                print("Service {} revoked from {}".format(service_name, self.username))
        elif resp.status_code == 401:
            raise ValueError(
                "Provided admin-username/password is incorrect or you are not allowed to do this operation"
            )
        else:
            data = json.loads(resp.content.decode())
            raise ValueError(data["message"])

    def get_service(self, service_name):
        clean_service_name = service_map.get(service_name.upper())
        if not clean_service_name:
            raise ValueError(f"No such service: {service_name}")
        service_name = clean_service_name
        endpoint = f"users/{self.username}/service/{service_name}"
        resp = self.get_request(endpoint)
        data = json.loads(resp.content.decode())
        if resp.ok:
            if service_name == "Mailbox":
                return Mailbox(
                    username=self.username,
                    service_name=service_name,
                    data=data,
                )
            else:
                return Service(
                    username=self.username,
                    service_name=service_name,
                    data=data,
                )
        elif resp.status_code == 401:
            raise ValueError(
                "Provided admin-username/password is incorrect or you are not allowed to do this operation"
            )
        else:
            raise ValueError(data["message"])

    def set_password(self, password, service_name="LDAPS"):
        """Sets a password for a given service"""

        if service_name.upper() not in service_map:
            raise ValueError(f"Cannot set password for service: {service_name}. Sorry!")

        endpoint = f"users/{self.username}/service/{service_map[service_name.upper()]}/password"
        body = {"password": password}
        self.put_request(endpoint, body)


@dataclass
class UserAlternative(IAMApiAlternative):
    uid: str = ""
    mail: str = ""
    firstname: str = ""
    lastname: str = ""
    company: str = ""
    title: str = ""
    npid: str = ""
    uidNumber: str = ""
    orcid: str = ""

    def new_from_data(self, data):
        return UserAlternative(**data)

    def search_users(
        self,
        username=None,
        mail=None,
        firstname=None,
        lastname=None,
        uidNumber=None,
    ):
        endpoint = "/usermgr/persons?"
        query = {}
        if username:
            query["uid"] = username
        if mail:
            query["mail"] = mail
        if firstname:
            query["firstname"] = firstname
        if lastname:
            query["lastname"] = lastname
        if uidNumber:
            query["uidNumber"] = uidNumber
        if not query:
            raise ValueError(
                "please provide at least one query item: username, mail, firstname or lastname."
            )

        querystring = "&".join(f"{k}={v}" for k, v in query.items())
        full_endpoint = endpoint + querystring
        data = self.get_request(full_endpoint)
        persons = []
        for d in data:
            persons.append(self.new_from_data(d))
        return persons
