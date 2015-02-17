import functools
import json
from functools import wraps

from django.http import HttpResponse
from django.utils.encoding import iri_to_uri

from pulp.common import error_codes
from pulp.server.exceptions import PulpCodedValidationException
from pulp.server.webservices.controllers.base import json_encoder as pulp_json_encoder


def generate_json_response(content=None, response_class=HttpResponse, default=None,
                           content_type='application/json'):
    """
    Serialize an object and return a djagno response

    :param content        : content to be serialized
    :type  content        : anything that is serializable by json.dumps
    :param response_class : Django response ojbect
    :type  response_class : HttpResponse class or subclass
    :param default        : function used by json.dumps to serialize content (also called default)
    :type  default        : function or None
    :param content_type   : type of returned content
    :type  content_type   : str

    :raises               : TypeError if response does not implement Django response object API
    :return               : response containing the serialized content
    :rtype                : HttpResponse or subclass
    """
    json_obj = json.dumps(content, default=default)
    return response_class(json_obj, content_type=content_type)


"""
Shortcut function to generate a json response using the in house json_encoder.

This function is equivalent to:
generate_json_response(content, default=pulp_json_encoder)
"""
generate_json_response_with_pulp_encoder = functools.partial(
    generate_json_response,
    default=pulp_json_encoder,
)


def generate_redirect_response(response, href):
    response['Location'] = iri_to_uri(href)
    response.status_code = 201
    response.reason_phrase = 'CREATED'
    return response


def json_body_required(func, allow_empty=False):

    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[1]
        if allow_empty and not request.body:
            request.body_as_json = {}
            return func(*args, **kwargs)

        try:
            request.body_as_json = json.loads(request.body)
        except ValueError:
            raise PulpCodedValidationException(error_code=error_codes.PLP1009)
        return func(*args, **kwargs)
    return wrapper

json_body_allow_empty = functools.partial(json_body_required, allow_empty=True)
