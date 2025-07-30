"""
Methods for groups
"""
from typing import Union
from pyfreeipa.Api._utils import delist, listdelist


def group(
        self,
        cn: str
):
    """
    @brief      Returns only the group response

    @param      self  The object
    @param      cn   The cn of the group to return

    @return     the group account as a dictionary
    """

    group = None
    response = self.group_show(cn, allattrs=True)

    if response.json()['result']:
        group = delist(response.json()['result']['result'])

    return group


def groups(
        self,
        searchstring: Union[str, None]=None,
        cn: Union[str, None]=None,
        gidnumber: Union[int, None]=None,
        in_group: Union[str, list, None]=None
):
    """
    @brief      Given a some search parameters find all the group acounts that match

    @param      self          The object
    @param      searchstring  The searchstring used on any otptoken attribute
    @param      uniqueid      substring used to match otptoken uniqueid
    @param      owner         search for tokens owned but specified group

    @return     { description_of_the_return_value }
    """

    grouplist = []
    response = self.group_find(
        searchstring=searchstring,
        cn=cn,
        gidnumber=gidnumber,
        in_group=in_group,
        allattrs=True
    )

    if response.json()['result']:
        grouplist = listdelist(response.json()['result']['result'])

    return grouplist


def grouplist(
        self,
        groups: Union[str, list, None]=None
):
    """
    @brief      Given a list of gids and/or groups, return a list of groupnames that match or are members

    @param      self          The object
    @param      searchstring  The searchstring used on any otptoken attribute
    @param      uniqueid      substring used to match otptoken uniqueid
    @param      owner         search for tokens owned but specified group

    @return     { description_of_the_return_value }
    """

    grouplist = []

    if groups:
        if isinstance(groups, list):
            for groupname in groups:
                response = self.group(groupname)
                if response:
                    grouplist.append(groupname)
                    response = self.groups(in_group=groupname)
                    if isinstance(response, list):
                        for group in response:
                            grouplist.append(group['cn'])
                    else:
                        grouplist.append(response['cn'])
        else:
            response = self.group(groupname)
            if response:
                grouplist.append(groupname)
                response = self.groups(in_group=groups)
                if isinstance(response, list):
                    for group in response:
                        grouplist.append(group['cn'])
                else:
                    grouplist.append(response['cn'])
    else:
        for group in self.groups():
            grouplist.append(group['cn'])

    if len(grouplist) > 1:
        grouplist = sorted(set(grouplist))

    return grouplist


def group_show(
        self,
        cn: str,
        no_members: Union[bool, None]=None,
        rights: Union[bool, None]=None,
        allattrs: Union[bool, None]=None,
        raw: Union[bool, None]=None
):
    """
    @brief      A complete implementation of the group_show command

    @param      self  The object

    @param      cn of the group to be shown

    @param      rights, if true, displays the access rights of this group

    @param      all, retrieves all attributes

    @param      raw, returns the raw response, only changes output format

    @return     the requests.Response from the ping request
    """

    method = 'group_show'

    args = cn

    params = {}

    if rights is not None:
        params['rights'] = rights

    if allattrs is not None:
        params['all'] = allattrs

    if raw is not None:
        params['raw'] = raw

    if no_members is not None:
        params['no_members'] = no_members

    return self.request(
        method,
        args=args,
        params=params
    )


def group_find(
        self,
        searchstring: Union[str, None]=None,
        cn: Union[str, None]=None,
        gidnumber: Union[int, None]=None,
        private: Union[bool, None]=None,
        posix: Union[bool, None]=None,
        external: Union[bool, None]=None,
        nonposix: Union[bool, None]=None,
        user: Union[str, list, None]=None,
        no_user: Union[str, list, None]=None,
        group: Union[str, list, None]=None,
        no_group: Union[str, list, None]=None,
        in_group: Union[str, list, None]=None,
        not_in_group: Union[str, list, None]=None,
        in_netgroup: Union[str, list, None]=None,
        not_in_netgroup: Union[str, list, None]=None,
        in_role: Union[str, list, None]=None,
        not_in_role: Union[str, list, None]=None,
        in_hbacrule: Union[str, list, None]=None,
        not_in_hbacrule: Union[str, list, None]=None,
        in_sudorule: Union[str, list, None]=None,
        not_in_sudorule: Union[str, list, None]=None,
        no_members: Union[bool, None]=None,
        rights: Union[bool, None]=None,
        allattrs: Union[bool, None]=None,
        raw: Union[bool, None]=None,
        pkey_only: Union[bool, None]=None
):
    """
    @brief      A partial implementation of the group_find request

    @param      self  The object

    @param      gid of the group to be shown

    @param      rights, if true, displays the access rights of this group

    @param      all, retrieves all attributes

    @param      raw, returns the raw response, only changes output format

    @return     the requests.Response from the ping request
    """

    method = 'group_find'

    args = None

    if searchstring:
        args = searchstring

    params = {}

    if cn is not None:
        params['cn'] = cn

    if gidnumber is not None:
        params['gidnumber'] = gidnumber

    if private is not None:
        params['private'] = private

    if posix is not None:
        params['posix'] = posix

    if external is not None:
        params['external'] = external

    if nonposix is not None:
        params['nonposix'] = nonposix

    if user is not None:
        params['user'] = user

    if no_user is not None:
        params['no_user'] = no_user

    if group is not None:
        params['group'] = group

    if no_group is not None:
        params['no_group'] = no_group

    if in_group is not None:
        params['in_group'] = in_group

    if not_in_group is not None:
        params['not_in_group'] = not_in_group

    if in_netgroup is not None:
        params['in_netgroup'] = in_netgroup

    if not_in_netgroup is not None:
        params['not_in_netgroup'] = not_in_netgroup

    if in_role is not None:
        params['in_role'] = in_role

    if not_in_role is not None:
        params['not_in_role'] = not_in_role

    if in_hbacrule is not None:
        params['in_hbacrule'] = in_hbacrule

    if not_in_hbacrule is not None:
        params['not_in_hbacrule'] = not_in_hbacrule

    if in_sudorule is not None:
        params['in_sudorule'] = in_sudorule

    if not_in_sudorule is not None:
        params['not_in_sudorule'] = not_in_sudorule

    if no_members is not None:
        params['no_members'] = no_members

    if rights is not None:
        params['rights'] = rights

    if allattrs is not None:
        params['all'] = allattrs

    if raw is not None:
        params['raw'] = raw

    if pkey_only is not None:
        params['pkey_only'] = pkey_only

    return self.request(
        method,
        args=args,
        params=params
    )

# Write methods that may cause changes to the directory
# These methods MUST require dryrun to be false to write changes

def group_add_member(
    self,
    cn: str,
    ipexternalmember: Union[str, list, None]=None,
    no_members: Union[bool, None]=None,
    user: Union[str, list, None]=None,
    group: Union[str, list, None]=None,
    service: Union[str, list, None]=None,
    idoverriduser: Union[str, list, None]=None,
    raw: Union[bool, None]=None,
    version:Union[bool, None]=None
):
    method = 'group_add_member'

    args = cn

    params = {}

    if ipexternalmember is not None:
        params['ipexternalmember'] = ipexternalmember

    if no_members is not None:
        params['no_members'] = no_members
    
    if user is not None:
        params['user'] = user
    
    if group is not None:
        params['group'] = group
    
    if service is not None:
        params['service'] = service
    
    if idoverriduser is not None:
        params['idoverriduser'] = idoverriduser

    if raw is not None:
        params['raw'] = raw

    if version is not None:
        params['version'] = version

    # This is a write method so, prepare the request
    prepared = self.preprequest(
        method,
        args=args,
        params=params
    )

    # then check if it's a dryrun before executing it
    if not self._dryrun:
        response = self._session.send(prepared)
    else:
        response = prepared

    return response
