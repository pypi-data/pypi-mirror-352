# import aiobastion.exceptions
from .exceptions import AiobastionException, AiobastionConfigurationException
from typing import Union

# class AamObject:
#     def __init__(self, appid: str, params: dict, cert_file: str = None, cert_key: str = None):
#         self.appid = appid
#         self.params = params
#         if cert_file is not None and cert_key is not None:
#             self.cert = (cert_file, cert_key)
#         else:
#             self.cert = None


class Applications:
    # _APPLICATIONS_DEFAULT_XXX = <value>

    # List of attributes from configuration file and serialization
    _SERIALIZED_FIELDS = []

    def __init__(self, epv, **kwargs):
        self.epv = epv

        _section = "applications"
        _config_source = self.epv.config.config_source

        # Check for unknown attributes
        if kwargs:
            raise AiobastionConfigurationException(f"Unknown attribute in section '{_section}' from {_config_source}: {', '.join(kwargs.keys())}")

    async def add(self, app_name: str, description: str = "", location: str = "\\", access_from: int = None,
                  access_to: int = None, expiration:str = None, disabled:bool = None,
                  owner_first_name: str = "", owner_last_name: str = "", owner_email: str = None, owner_phone: str = ""
                  ):
        """
        Create a new application

        :param app_name: Name of the application ("AppID") - Required
        :param description: Description - Optional
        :param location: Location - Defaults to \\ - Optional
        :param access_from: The start hour that access is permitted to the application. - Defaults to None - Optional
        :param access_to: The end hour that access is permitted to the application. - Defaults to None - Optional
        :param expiration: The date when the application expires (format mm-dd-yyyy) - Defaults to None - Optional
        :param disabled: Whether the application is disabled (True / False) - Defaults to None (False) - Optional
        :param owner_first_name: Product Owner first name - Defaults to empty - Optional
        :param owner_last_name: Product Owner last name - Defaults to empty - Optional
        :param owner_email: Product Owner email - Defaults to empty - Optional
        :param owner_phone: Product Owner phone - Defaults to empty - Optional
        :return: True if created
        """
        url = "WebServices/PIMServices.svc/Applications/"

        data = {
            "application": {
                "AppID": app_name,
                "Description": description,
                "Location": location,
                "BusinessOwnerFName": owner_first_name,
                "BusinessOwnerLName": owner_last_name,
                "BusinessOwnerPhone": owner_phone
              }
            }

        if access_from is not None:
            if access_from not in list(range(23)):
                raise AiobastionException(f"access_from argument must be int between 0 and 23, given : {access_from}")
            data["application"]["AccessPermittedFrom"] = access_from

        if access_to is not None:
            if access_to not in list(range(23)):
                raise AiobastionException(f"access_from argument must be int between 0 and 23, given : {access_to}")
            data["application"]["AccessPermittedTo"] = access_to

        if expiration is not None:
            # Format mm-dd-yyy
            data["application"]["ExpirationDate"] = expiration

        if disabled is not None:
            data["application"]["Disabled"] = disabled

        if owner_email is not None:
            import re
            if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", owner_email):
                raise AiobastionException(f"owner_email argument must be valid mail, given : {owner_email}")
            data["application"]["BusinessOwnerEmail"] = owner_email

        return await self.epv.handle_request("post", url, data=data)


    def to_json(self):
        serialized = {}

        for attr_name in Applications._SERIALIZED_FIELDS:
            v = getattr(self, attr_name, None)

            if v is not None:
                serialized[attr_name] = v

        return serialized


    async def delete(self, app_name:str):
        """
        Delete an application

        :param app_name: The application name (AppID)
        :return: True if deleted
        """
        url = f"WebServices/PIMServices.svc/Applications/{app_name}"

        return await self.epv.handle_request("delete", url)


    async def details(self, app_name: str):
        """
        Get application details

        :param app_name: The application name (AppID)
        :return: A dict with the application information
        """
        url = "WebServices/PIMServices.svc/Applications/"
        params = {
            "AppID": app_name,
        }
        apps = await self.epv.handle_request("get", url, params=params, filter_func=lambda x: x["application"])
        for app in apps:
            if app["AppID"] == app_name:
                return app

        if len(apps) > 1:
            app_names = [x["AppID"] for x in apps]
            raise AiobastionException(f"Provided name {app_name} returns more than one application : {app_names}")
        elif len(apps) == 0:
            raise AiobastionException(f"No results found for {app_name}")

    async def search(self, search: str):
        """
        Search applications by name

        :param search: free text to search application
        :return: list of application names
        """
        url = "WebServices/PIMServices.svc/Applications/"
        params = {
            "AppID": search,
        }
        apps = await self.epv.handle_request("get", url, params=params, filter_func=lambda x: x["application"])
        return [x["AppID"] for x in apps]

    async def add_authentication(self, app_name: str, path: str = None, hash_string: str = None, os_user: str = None,
                                 address: str = None, serial_number: str = None, issuer: list = None,
                                 subject: list = None,
                                 subject_alternative_name: list = None, is_folder: bool = False,
                                 allow_internal_scripts: bool = False, comment: str = "") -> bool:
        """
        Add one or more authentication methods to a given app_id with a named param

        :param app_name: the name of the application
        :param path: path to authenticated
        :param hash_string: hash of script / binary
        :param os_user: os user that is running the script / binary
        :param address: IP address
        :param serial_number: certificate serial number
        :param issuer: list of certificate issuer (PVWA >= 11.4)
        :param subject: list of certificate subject (PVWA >= 11.4)
        :param subject_alternative_name: list of certificate SAN (eg ["DNS Name=www.example.com","IP Address=1.2.3.4"])
        :param allow_internal_scripts: relevant for path authentication only (False by default)
        :param is_folder: relevant for path authentication only (False by default)
        :param comment: relevant for hash and certificate serial number
        :return: boolean telling whether the application was updated or not
        """

        updated = False

        url = f'WebServices/PIMServices.svc/Applications/{app_name}/Authentications/'

        if path is not None:
            body = {
                "authentication": {
                    "AuthType": "path",
                    "AuthValue": path,
                    "IsFolder": is_folder,
                    "AllowInternalScripts": allow_internal_scripts
                }
            }
            updated = await self.epv.handle_request("post", url, data=body)

        if hash_string is not None:
            body = {
                "authentication": {
                    "AuthType": "hash",
                    "AuthValue": hash_string,
                    "Comment": comment
                }
            }
            updated = await self.epv.handle_request("post", url, data=body)

        if os_user is not None:
            body = {
                "authentication": {
                    "AuthType": "osUser",
                    "AuthValue": os_user
                }
            }
            updated = await self.epv.handle_request("post", url, data=body)

        if address is not None:
            body = {
                "authentication": {
                    "AuthType": "machineAddress",
                    "AuthValue": address
                }
            }
            updated = await self.epv.handle_request("post", url, data=body)

        if serial_number is not None:
            body = {
                "authentication": {
                    "AuthType": "certificateserialnumber",
                    "AuthValue": serial_number,
                    "Comment": comment
                }
            }
            updated = await self.epv.handle_request("post", url, data=body)

        if issuer is not None or subject is not None or subject_alternative_name is not None:
            if isinstance(issuer, str):
                issuer = [issuer]
            if isinstance(subject, str):
                subject = [subject]
            if isinstance(subject_alternative_name, str):
                subject_alternative_name = [subject_alternative_name]

            body = {
                "authentication": {
                    "AuthType": "certificateattr",
                }
            }

            if issuer:
                body["authentication"]["Issuer"] = issuer
            if subject:
                body["authentication"]["Subject"] = subject
            if subject_alternative_name:
                body["authentication"]["SubjectAlternativeName"] = subject_alternative_name

            updated = await self.epv.handle_request("post", url, data=body)

        if updated:
            return True
        else:
            return False

    async def get_authentication(self, app_name: str) -> Union[list, bool]:
        """
        Get authenticated methods for an application

        :param app_name: The name of the application
        :return: a list of authentication methods
        """
        return await self.epv.handle_request(
            "get",
            f'WebServices/PIMServices.svc/Applications/{app_name}/Authentications',
            filter_func=lambda x: x['authentication'])

    async def del_authentication(self, app_name: str, auth_id: str) -> Union[list, bool]:
        """
        Delete authentication method identified by auth_id for the application

        :param app_name: name of the application
        :param auth_id: retrieved with the get_authentication function
        :return: a boolean
        """
        return await self.epv.handle_request(
            "delete",
            f'WebServices/PIMServices.svc/Applications/{app_name}/Authentications/{auth_id}',
            filter_func=lambda x: x['authentication'])
