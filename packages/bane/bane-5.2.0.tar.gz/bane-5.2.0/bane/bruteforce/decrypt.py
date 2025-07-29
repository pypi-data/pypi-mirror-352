from bane.bruteforce.utils import *


class Decryptor:
    __slots__ = ["stop", "finish", "result", "logs"]

    def __init__(
        self,
        u,
        word_list=[],
        threads_daemon=True,
        md5_hash=False,
        sha1_hash=False,
        sha256_hash=False,
        sha224_hash=False,
        sha384_hash=False,
        sha512_hash=False,
        base64_string=False,
        caesar_hash=False,
        logs=False,
    ):
        self.logs = logs
        word_list=Userful_Utilities.load_word_list(word_list)
        self.stop = False
        self.finish = False
        self.result = {}
        t = threading.Thread(
            target=self.crack,
            args=(
                u,
                word_list,
                md5_hash,
                sha1_hash,
                sha256_hash,
                sha224_hash,
                sha384_hash,
                sha512_hash,
                base64_string,
                caesar_hash,
                logs,
            ),
        )
        t.daemon = threads_daemon
        t.start()

    def crack(
        self,
        u,
        word_list,
        md5_hash,
        sha1_hash,
        sha256_hash,
        sha224_hash,
        sha384_hash,
        sha512_hash,
        base64_string,
        caesar_hash,
        logs,
    ):
        started_at=time.time()
        if self.logs == True:
            print("[!]hash: " + u + "\nbruteforcing has started!!!\n")
        for x in word_list:
            if self.stop == True:
                break
            if md5_hash == True:
                if MD5.compare_hash(x, u) == True:
                    if self.logs == True:
                        print("[+]Hash match found: " + x + " | Type: md5")
                    self.result = {"input":u, "type":'md5',"value": x,"start_date":started_at,"end_date":time.time()}
                    break
            if sha1_hash == True:
                if SHA1.compare_hash(x, u) == True:
                    if self.logs == True:
                        print("[+]Hash match found: " + x + " | Type: sha1")
                    self.result = {"input":u, "type":'sha1',"value": x,"start_date":started_at,"end_date":time.time()}
                    break
            if sha256_hash == True:
                if SHA256.compare_hash(x, u) == True:
                    if self.logs == True:
                        print("[+]Hash match found: " + x + " | Type: sha256")
                    self.result = {"input":u, "type":'sha256',"value": x,"start_date":started_at,"end_date":time.time()}
                    break
            if sha224_hash == True:
                if SHA224.compare_hash(x, u) == True:
                    if self.logs == True:
                        print("[+]Hash match found: " + x + " | Type: sha224")
                    self.result = {"input":u, "type":'sha224',"value": x,"start_date":started_at,"end_date":time.time()}
                    break
            if sha384_hash == True:
                if SHA348.compare_hash(x, u) == True:
                    if self.logs == True:
                        print("[+]Hash match found: " + x + " | Type: sha384")
                    self.result = {"input":u, "type":'sha348',"value": x,"start_date":started_at,"end_date":time.time()}
                    break
            if sha512_hash == True:
                if SHA512.compare_hash(x, u) == True:
                    if self.logs == True:
                        print("[+]Hash match found: " + x + " | Type: sha512")
                    self.result = {"input":u, "type":'sha512',"value": x,"start_date":started_at,"end_date":time.time()}
                    break
            if base64_string == True:
                if BASE64.decode(x) == u:
                    if self.logs == True:
                        print("[+]Hash match found: " + x + " | Type: base64")
                    self.result = {"input":u, "type":'base64',"value": x,"start_date":started_at,"end_date":time.time()}
                    break
            if caesar_hash == True:
                for i in range(1, 27):
                    if CAESAR.decode(x, i) == True:
                        if self.logs == True:
                            print(
                                "[+]Hash match found: "
                                + x
                                + " | Type: caesar | Key: "
                                + str(i)
                            )
                        self.result = {"input":u, "type":'caesar',"value": x,"start_date":started_at,"end_date":time.time()}
                        break
        if self.result == {}:
            if self.logs == True:
                print("[-]No match found")
        self.finish = True

    def done(self):
        return self.finish