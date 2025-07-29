from urllib.parse import urlparse

def get_origin(url):
    """
    从URL中提取源（origin）部分
    示例:
        >>> get_origin("https://example.com/path?query=1")
        "https://example.com"
    """
    parsed_url = urlparse(url)
    origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return origin

def get_host_from_url(url):
    '''
    从URL中提取主机名（Host）部分
    '''
    parsed_url = urlparse(url)
    return parsed_url.netloc  # 返回主机名（Host）

def abs_url(service,path):
    '''
    拼接绝对URL
    '''
    if path.startswith('/'):
        return f"{get_origin(service)}{path}"
    else:
        return path