from urllib.parse import urlparse, parse_qs, urlencode

def is_url(url:str):
    try:
        urlparse(url)
        return True
    except:
        return False

def check_url_in_domains(url:str, domains:list[str]):
    parsed_url = urlparse(url)
    return parsed_url.netloc in domains


def set_url_params(url:str, params:dict, remove_none:bool=True):
    if remove_none:
        params = {k: v for k, v in params.items() if v is not None}
    parsed_url = urlparse(url)
    old_params = parse_qs(parsed_url.query)
    for key, value in params.items():
        old_params[key] = value
    return parsed_url._replace(query=urlencode(query=old_params, doseq=True) ).geturl()


def encode_url_params(params:dict , remove_none:bool=True):
    if remove_none:
        params = {k: v for k, v in params.items() if v is not None}
    return urlencode(params, doseq=True)

def replace_url_host(url:str, host:str):
    parsed_url = urlparse(url)
    host_url = urlparse(host)
    return parsed_url._replace(netloc=host_url.netloc, scheme=host_url.scheme).geturl()