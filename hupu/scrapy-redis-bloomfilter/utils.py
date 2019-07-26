
import six
import scrapy
from hupu.settings import IGNORE_PARAMS
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs


def bytes_to_str(s, encoding='utf-8'):
    """Returns a str if a bytes object is given."""
    if six.PY3 and isinstance(s, bytes):
        return s.decode(encoding)
    return s


def ignore_params(request):
    """
    del params and formdata in request
    :return:
    """
    if not IGNORE_PARAMS:
        return request

    u = urlparse(request.url)
    query = parse_qs(u.query)
    for param in IGNORE_PARAMS:
        query.pop(param, None)
    u = u._replace(query=urlencode(query, True))
    request_duplicate = request.replace(
        url=urlunparse(u),
    )

    if request_duplicate.body:
        formdata = parse_qs(request_duplicate.body.decode())
        for param in IGNORE_PARAMS:
            formdata.pop(param, None)
        request_duplicate = request_duplicate.replace(
            body=urlencode(formdata, True),
        )

    return request_duplicate

