from bane.scanners.vulnerabilities.utils import *

class Mixed_Content_Scanner:

    @staticmethod
    def scan_url(u, timeout=10,proxy=None, user_agent=None, cookie=None,content=None,logs=True,request_headers=None,headers={},http_proxies=None,socks4_proxies=None,socks5_proxies=None):
        proxies=Proxies_Interface.get_requests_proxies_from_parameters(http_proxies=http_proxies,socks4_proxies=socks4_proxies,socks5_proxies=socks5_proxies)
        if user_agent:
            us = user_agent
        else:
            us = random.choice(Common_Variables.user_agents_list)
        if cookie:
            heads = {"User-Agent": us, "Cookie": cookie}
        else:
            heads = {"User-Agent": us}
        heads.update(headers)
        vul=[]
        try:
            if content==None:
                if proxy==None:
                    proxy=Vulnerability_Scanner_Utilities.setup_proxy(proxies)
                r=requests.Session().get(u,headers=heads,timeout=timeout,verify=False,proxies=proxy)
                for x in r.headers:
                        if x.lower().strip() == "strict-transport-security":
                            if logs == True:
                                print("\n[-] Not vulnerable: Strict-Transport-Security is set")
                            return []
                soup = BeautifulSoup(r.content, 'html.parser')
            else:
                soup = BeautifulSoup(content, 'html.parser')
                if request_headers!=None:
                    for x in request_headers:
                        if x.lower().strip() == "strict-transport-security":
                            if logs == True:
                                print("\n[-] Not vulnerable: Strict-Transport-Security is set")
                            return []
            if u:
                    parsed_url = urlparse(u)
                    if parsed_url.netloc == urlparse(u).netloc:
                        if parsed_url.scheme != 'https' and parsed_url.geturl().startswith('//')==False:
                            parsed_url=parsed_url.geturl()
                            if parsed_url not in vul:
                                vul.append(parsed_url)
                                if logs==True:
                                    print('\t[+] Vulnerable : {}'.format(parsed_url))
            media_elements=soup.find_all(['img', 'audio', 'video', 'source','embed', 'script', 'link', 'a'])
            for element in media_elements:
                src_or_href = element.get('src') or element.get('href')
                if src_or_href:
                    parsed_url = urlparse(urljoin(u,src_or_href))
                    if parsed_url.netloc == urlparse(u).netloc:
                        if parsed_url.scheme != 'https' and parsed_url.geturl().startswith('//')==False:
                            parsed_url=parsed_url.geturl()
                            if parsed_url not in vul:
                                vul.append(parsed_url)
                                if logs==True:
                                    print('\t[+] Vulnerable : {}'.format(parsed_url))
        except Exception as ex:
            return vul
        return vul
        

    @staticmethod
    def scan(
        u, 
        max_pages=5,
        proxy=None,
        timeout=10,
        user_agent=None,
        cookie=None,
        content=None,
        logs=True,
        pages=[],
        headers={},
        http_proxies=None,
        socks4_proxies=None,
        socks5_proxies=None
    ):
        l=[]
        proxies=Proxies_Interface.get_requests_proxies_from_parameters(http_proxies=http_proxies,socks4_proxies=socks4_proxies,socks5_proxies=socks5_proxies)
        if pages==[]:
            pages=Pager_Interface.spider_url(u,cookie=cookie,max_pages=max_pages,timeout=timeout,user_agent=user_agent,proxy=random.choice(proxies),headers={})
        for x in pages:
            if logs==True:
                print('\n\nPage: {}\n'.format(x))
            result=Mixed_Content_Scanner.scan_url(x,
                            proxy=proxy,
                            timeout=timeout,
                            user_agent=user_agent, 
                            cookie=cookie,
                            content=content,
                            logs=logs,
                            headers=headers,
                            http_proxies=http_proxies,
                            socks4_proxies=socks4_proxies,
                            socks5_proxies=socks5_proxies
                            )
            if logs==True:
                for r in result:
                    print(r)
            l.append({'page':x,'result':result})
        return  [x for x in l if x['result']!=[]]

