"""
Some common utilities for the API
"""
import requests
import json
from datetime import datetime
from typing import List



def delist(
    thedict: dict
):
    """
    @brief      Given a dictionary, check all the key values and if
                the value is a list, and the list has one item, then
                replace the list with the single item in the list

    @param      thedict  The dictionary to process

    @return     a dictionary with no single element lists
    """
    cleandict = {}
    timeformat = '%Y%m%d%H%M%SZ'
    for key in thedict:
        cleandict[key] = thedict[key]
        if isinstance(thedict[key], list):
            if len(thedict[key]) == 1:
                cleandict[key] = thedict[key][0]

        # Convert serialised datetime dicts back into a datetime object
        if isinstance(cleandict[key], dict):
            if '__datetime__' in cleandict[key]:
                cleandict[key] = datetime.strptime(
                    cleandict[key]['__datetime__'],
                    timeformat
                )

    return cleandict


def listdelist(
    thelist: List[dict]
):
    """
    @brief      Uses the delist functio on a list of Dictioaries

    @param      thelist  The list of dictionaries

    @return     a list of dictionaries with no single element lists
    """
    cleanlist = []
    for item in thelist:
        cleanlist.append(delist(item))

    return cleanlist

def jsonprepreq(
    preprequest: type=requests.PreparedRequest
):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared". but we need it as JSONable dict
    """
    jsonprepreq = {
        'headers': {},
        'body': {}
    }

    jsonprepreq['method'] = preprequest.method
    jsonprepreq['url'] = preprequest.url
    for key, value in preprequest.headers.items():
        jsonprepreq['headers'][key] = value

    jsonprepreq['body'] = json.loads(preprequest.body)
    return jsonprepreq
