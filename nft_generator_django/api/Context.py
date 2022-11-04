import json
import threading as mt
import multiprocessing as mp
import sys, os
p = os.path.abspath("..")
sys.path.insert(0, p)

from nft_generator.Collection import Collection
from nft_generator.Printers import *
from nft_generator.Errors import NFTGError as E


class Context:
    def __init__(self, jsonstr: str):
        self.collection = Collection(jsonstr)           # type: Collection
        self.jsonstr = jsonstr                          # type: str
        self.executing = False                          # type: bool
        self.success = False                            # type: bool
        self.error_msg = "Not yet started."             # type: str
        self.thread = None                              # type: mt.Thread
        self.process = None                             # type: mp.Process
        self.parent_conn = None                         # type: mp.connection.Connection
        # self.destroyable = False                        # type: bool

    def run(self, enable_render: bool, enable_metadata: bool, enable_excel: bool):
        self.thread = mt.Thread(target=self.__run_thread, args=(enable_render, enable_metadata, enable_excel))
        self.thread.start()

    def __run_thread(self, enable_render: bool, enable_metadata: bool, enable_excel: bool):
        """
        This function runs in the child thread
        :param enable_render:
        :param enable_metadata:
        :return:
        """
        self.executing = True
        self.error_msg = ""
        try:
            self.collection.generate()

            if enable_render:
                self.parent_conn, child_conn = mp.Pipe()
                self.process = mp.Process(target=self.collection.render, args=(child_conn,))
                self.process.start()
                try:
                    while True:
                        jsonobj = json.loads(self.parent_conn.recv())
                        if jsonobj["success"] == False:
                            if jsonobj["code"] != 0:
                                raise E(jsonobj["code"], *jsonobj["data"])
                            else:
                                raise Exception(jsonobj["message"])
                        else:
                            i_plus_one = jsonobj["data"]
                            if i_plus_one == -1:
                                raise EOFError("Context: Finished.")
                            progress, total = self.collection.inc_progress()
                            if progress != i_plus_one:
                                raise E(E.ERR_RT_REND_INT)
                except EOFError:
                    progress, total = self.collection.get_progress()
                    print_info("Pipe closed: %d, %d." % (progress, total))
                    if progress != total:
                        raise E(E.ERR_RT_REND_TERM_EARLY)
                # pass E

            if enable_metadata:
                self.collection.generate_metadata()

            if enable_excel:
                self.collection.generate_excel()
        except E as e:
            self.error_msg = E.errmsg(e)
            self.success = False
        except Exception as e:
            self.error_msg = str(e)
            self.success = False
        else:
            self.success = True

        # kill anyway
        if self.process is not None and self.process.is_alive():
            self.process.kill()
            self.process = None
            self.parent_conn.close()
        self.executing = False



