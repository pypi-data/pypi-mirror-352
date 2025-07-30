from urllib import parse


class HttpRawExtr:
    def __init__(self, raw_str=''):
        headers = {}
        cookie = []
        """
        :method: GET
        :scheme: https
        :authority: www.zhihu.com
        :path: /api/v4/answers/3617856327/relationship?desktop=true
        """
        url = {':method': '', ':scheme': 'https', ':authority': '', ':path': ''}
        _ = raw_str.split("\n")
        for row in _:
            row = row.strip()
            if '' == row:
                continue
            if '#' == row[0]:
                continue
            if 'GET' == row[0:3]:
                url[':method'] = 'GET'
                url[':path'] = row.replace('GET', '').strip()
                continue
            if 'POST' == row[0:4]:
                url[':method'] = 'POST'
                url[':path'] = row.replace('POST', '').strip()
                continue

            k, v = row.split(': ')
            if 'Host' == k:
                url[':authority'] = v
            elif k in [':method', ':authority', ':scheme', ':path']:
                url[k] = v.strip()
            elif 'cookie' == k:
                cookie.append(v.strip())
            else:
                headers[k] = v.strip()

        if cookie:
            # 根据HTTP规范，HTTP头字段名称是不区分大小写的。这意味着理论上 Cookie 和 cookie 在HTTP协议层面是等效的。
            # 标准实践：虽然协议不区分大小写，但标准的写法通常是将每个单词的首字母大写，如 Cookie、Content-Type、User-Agent 等。
            # 服务器实现差异：某些服务器或框架的实现可能对大小写敏感，尤其是在处理自定义头时。
            headers['Cookie'] = '; '.join(cookie)
        self.headers = headers
        self.cookie = cookie
        self.url = url

    def get_headers(self, key=None):
        if key is None:
            return self.headers
        return self.headers[key]

    def get_cookie(self, key=None):
        dic = dict()
        for _ in self.cookie:
            k, v = _.split('=', 1)
            dic[k] = v
        if key is None:
            return dic
        return dic[key]

    def get_params(self, key=None):
        path = self.url[':path'].split('?', 1)
        if len(path) < 2:
            params = dict()
        else:
            params = parse.parse_qs(path[1])
            params = {key: params[key][0] for key in params}
        if key is None:
            return params
        return params[key]

    def get_host(self):
        return self.url[':scheme'] + '://' + self.url[':authority']

    def get_api(self):
        return self.get_host() + self.url[':path'].split('?', 1)[0]

    def get_api_with_up(self, up=None):
        api = self.get_api()
        params = self.get_params()
        if type(up) is dict:
            params.update(up)
        qs = parse.urlencode(params)
        if qs:
            return api + '?' + qs
        return api

    def __repr__(self):
        print('self.url', self.url)
        print('self.headers', self.headers)
        print('self.cookie', self.cookie)
        print('self.get_headers', self.get_headers())
        print('self.get_cookie', self.get_cookie())
        print('self.get_params', self.get_params())
        print('self.get_api', self.get_api())
        print('self.get_api_with_up', self.get_api_with_up())

        return ''


# 一定要记得加：user-agent
def fetch(url, params=None):
    if params is None:
        params = dict()

    extr = HttpRawExtr()
    extr.headers = params.get('headers', dict())
    if extr.headers.get('user-agent') is None:
        extr.headers['user-agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    if cookie := extr.headers.get('cookie'):
        extr.cookie = cookie.split('; ')

    parsed = parse.urlparse(url)
    """
    scheme：协议，如 http、https
    host：主机名，如 www.zhihu.com
    port：端口号，如 80、443
    path：路径，指向服务器上的特定资源，如 /api/v4/questions/12345
    query：查询参数，以 ? 开始，如 ?limit=10&offset=0
    fragment：片段标识符，以 # 开始，如 #answer-123456
    """
    path = parsed.path
    if parsed.query:
        path += '?' + parsed.query
    extr.url = {
        ':method': params.get('method'),
        ':authority': parsed.netloc,
        ':scheme': parsed.scheme,
        ':path': path
    }
    extr.body = params.get('body')
    return extr


# 把URL中的参数转成字典
def query_parse(url, get_param=None):
    rst = parse.urlparse(url)
    params = parse.parse_qs(rst.query)
    params = {key: params[key][0] for key in params}
    if get_param:
        return params.get(get_param)
    return params


# URL只允许一部分ASCII字符，其他字符（如汉字）是不符合标准的，此时就要进行编码
def url_encode(url):
    return parse.quote(url)


# URL解码
def url_decode(url):
    return parse.unquote(url)


# 把字典转成url参数
def build_query(params):
    return parse.urlencode(params)


if '__main__' == __name__:
    ex = fetch('https://so.toutiao.com/search?dvpf=pc&source=input&keyword=%E9%83%BD%E5%B8%82%E5%B0%8F%E8%AF%B4&pd=synthesis&filter_vendor=site&index_resource=site&filter_period=month&min_time=1739870515&max_time=1742289715')
    print(ex)
