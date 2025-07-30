"""
Methods for otptokens
otp - one time password, used for two factor & multifactor authentication.
"""
from typing import Union
from datetime import datetime


def otptoken_find(
        self,
        searchstring: Union[str, None]=None,
        uniqueid: Union[str, None]=None,
        owner: Union[str, None]=None,
        no_members: Union[bool, None]=None,
        allattrs: Union[bool, None]=None,
        raw: Union[bool, None]=None
):
    """
    @brief Partial implementation the otptoken_show request, only searches by parameters below

    @param self The object
    @param uniqueid, the unique identifier (`iparokenuniqueid`) attribute of the token to find
    @param owner, the owner (`iparokenowner`) attribute of the token to find
    @param no_members, if true this suppresses processing of membershib attributes
    @param all, retrieves all attributes
    @param raw, returns the raw response, only changes output format

    @return the request.Response from the otpoken_show request
    """

    method = 'otptoken_find'

    args = None

    if searchstring:
        args = searchstring

    params = {}

    if uniqueid is not None:
        params['ipatokenuniqueid'] = uniqueid

    if owner is not None:
        params['ipatokenowner'] = owner

    if no_members is not None:
        params['no_members'] = no_members

    if allattrs is not None:
        params['all'] = allattrs

    if raw is not None:
        params['raw'] = raw

    return self.request(
        method,
        args=args,
        params=params
    )


def otptoken_show(
        self,
        uniqueid: str,
        no_members: Union[bool, None]=None,
        allattrs: Union[bool, None]=None,
        raw: Union[bool, None]=None
):
    """
    @brief Complete implementation the otptoken_show request

    @param self The object
    @param uniqueid, the unique identifier (`iparokenuniqueid`) attribute of the token to show
    @param no_members, if true this suppresses processing of membershib attributes
    @param all, retrieves all attributes
    @param raw, returns the raw response, only changes output format

    @return the request.Response from the otpoken_show request
    """

    method = 'otptoken_show'

    args = uniqueid

    params = {}

    if no_members is not None:
        params['no_members'] = no_members

    if allattrs is not None:
        params['all'] = allattrs

    if raw is not None:
        params['raw'] = raw

    return self.request(
        method,
        args=args,
        params=params
    )


# Write methods that may cause changes to the directory
# These methods MUST require dryrun to be false to write changes
def otptoken_add(
        self,
        # Arguments
        uniqueid: str,
        # Options
        otptype: Union[str, None]=None,
        description: Union[str, None]=None,
        owner: Union[str, None]=None,
        disabled: Union[bool, None]=None,
        notbefore: Union[datetime, None]=None,
        notafter: Union[datetime, None]=None,
        vendor: Union[str, None]=None,
        model: Union[str, None]=None,
        serial: Union[str, None]=None,
        otpkey: Union[str, None]=None,
        otpalgorithm: Union[str, None]=None,
        otpdigits: Union[int, None]=None,
        otpclockoffset: Union[int, None]=None,
        otptimestep: Union[int, None]=None,
        otpcounter: Union[int, None]=None,
        no_qrcode: Union[bool, None]=None,
        no_members: Union[bool, None]=None,
        otpsetattr: Union[list, None]=None,
        addattr: Union[list, None]=None,
        # Custom
        managedby: Union[list, None]=None
):

    method = 'otptoken_add'

    args = uniqueid

    params = {}

    # These options need some checking before submitting a request
    typevalues = ['totp', 'hotp', 'TOTP', 'HOTP']
    if otptype is not None:
        if otptype in typevalues:
            params['type'] = otptype
        else:
            raise ValueError(
                "otptoken_add: otptype must be one of %r" % typevalues
            )

    algovalues = ['sha1', 'sha256', 'sha384', 'sha512']
    if otpalgorithm is not None:
        if otpalgorithm.lower() in algovalues:
            params['ipatokenotpalgorithm'] = otpalgorithm.lower()
        else:
            raise ValueError(
                "otptoken_add: otpalgorithm must be one of %r" % typevalues
            )

    # These options just need to be mapped to request parameters
    if description is not None:
        params['description'] = description

    if owner is not None:
        params['ipatokenowner'] = owner

    if disabled is not None:
        params['ipatokendisabled'] = disabled

    if notafter is not None:
        params['ipatokennotafter'] = notafter

    if notbefore is not None:
        params['ipatokennotbefore'] = notbefore

    if vendor is not None:
        params['ipatokenvendor'] = vendor

    if model is not None:
        params['ipatokenmodel'] = model

    if serial is not None:
        params['ipatokenserial'] = serial

    if otpkey is not None:
        params['ipatokenotpkey'] = otpkey

    if otpdigits is not None:
        params['ipatokenotpdigits'] = otpdigits

    if otpclockoffset is not None:
        params['ipatokentotpclockoffset'] = otpclockoffset

    if otptimestep is not None:
        params['ipatokentotptimestep'] = otptimestep

    if otpcounter is not None:
        params['ipatokenhotpcounter'] = otpcounter

    if no_qrcode is not None:
        params['no_qrcode'] = no_qrcode

    if no_members is not None:
        params['no_members'] = no_members

    if otpsetattr is not None:
        params['setattr'] = otpsetattr

    if addattr is not None:
        params['addattr'] = addattr
    # Custom
    if managedby is not None:
        print("I'm special")

    prepared = self.preprequest(
        method,
        args=args,
        params=params
    )

    if not self._dryrun:
        response = self._session.send(prepared)
    else:
        response = prepared

    return response


def otptoken_add_managedby(
        self,
        # Arguments
        uniqueid: str,
        user: Union[list, str],
        no_members: Union[bool, None]=None,
        allattrs: Union[bool, None]=None,
        raw: Union[bool, None]=None
):
    """
    @brief adds a user to the managedBy attributes

    @return the response from the otptoken_add_managedby request, unless dry run where it returns the prepared response
    """

    method = 'otptoken_add_managedby'

    args = uniqueid

    if not isinstance(user, list):
        user = [user]

    params = {
        'user': user
    }

    if no_members is not None:
        params['no_members'] = no_members

    if allattrs is not None:
        params['all'] = allattrs

    if raw is not None:
        params['raw'] = raw

    prepared = self.preprequest(
        method,
        args=args,
        params=params
    )

    if not self._dryrun:
        response = self._session.send(prepared)
    else:
        response = prepared

    return response


def otptoken_remove_managedby(
        self,
        # Arguments
        uniqueid: str,
        user: Union[list, str],
        no_members: Union[bool, None]=None,
        allattrs: Union[bool, None]=None,
        raw: Union[bool, None]=None
):
    """
    @brief removes a user to the managedBy attributes

    @return the response from the otptoken_add_managedby request, unless dry run where it returns the prepared response
    """

    method = 'otptoken_remove_managedby'

    args = uniqueid

    if not isinstance(user, list):
        user = [user]

    params = {
        'user': user
    }

    if no_members is not None:
        params['no_members'] = no_members

    if allattrs is not None:
        params['all'] = allattrs

    if raw is not None:
        params['raw'] = raw

    prepared = self.preprequest(
        method,
        args=args,
        params=params
    )

    if not self._dryrun:
        response = self._session.send(prepared)
    else:
        response = prepared

    return response

# The next methods produce objects, or lists or objects
# These are intended for simple operations that don't require
# full feedback from the response objects
# e.g. won't say why a request found nothing


def otptoken(
        self,
        uniqueid: str
):
    """
    @brief      { function_description }

    @param      self      The object
    @param      uniqueid  The uniqueid of he token to be returned

    @return     { description_of_the_return_value }
    """

    response = self.otptoken_show(uniqueid, allattrs=True)

    if response.json()['result']:
        return response.json()['result']['result']
    else:
        return None


def otptokens(
        self,
        searchstring: Union[str, None]=None,
        uniqueid: Union[str, None]=None,
        owner: Union[str, None]=None
):
    """
    @brief      { function_description }

    @param      self          The object
    @param      searchstring  The searchstring used on any otptoken attribute
    @param      uniqueid      substring used to match otptoken uniqueid
    @param      owner         search for tokens owned but specified user

    @return     { description_of_the_return_value }
    """

    response = self.otptoken_find(
        searchstring=searchstring,
        uniqueid=uniqueid,
        owner=owner,
        allattrs=True
    )

    if response.json()['result']:
        return response.json()['result']['result']
    else:
        return []
