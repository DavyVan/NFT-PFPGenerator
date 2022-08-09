import threading as mt
import multiprocessing as mp
import sys, os
p = os.path.abspath("..")
sys.path.insert(0, p)

from nft_generator.Collection import Collection
from nft_generator.Printers import *


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

    def run(self, enable_render: bool, enable_metadata: bool):
        self.thread = mt.Thread(target=self.__run_thread, args=(enable_render, enable_metadata))
        self.thread.start()

    def __run_thread(self, enable_render: bool, enable_metadata: bool):
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
                        i_plus_one = self.parent_conn.recv()
                        if i_plus_one == -1:
                            raise EOFError("Context: Finished.")
                        progress, total = self.collection.inc_progress()
                        if progress != i_plus_one:
                            raise ValueError("Context: Progress interrupted!")
                except EOFError:
                    progress, total = self.collection.get_progress()
                    print_info("Pipe closed: %d, %d." % (progress, total))
                    if progress != total:
                        raise EOFError("Context: The process terminated early.")
                except ValueError as e:
                    raise e

            if enable_metadata:
                self.collection.generate_metadata()
        except Exception as e:
            self.executing = False
            self.error_msg = str(e)

        if self.process is not None and self.process.is_alive():
            self.process.kill()
            self.process = None
            self.parent_conn.close()

        self.executing = False
        self.success = True



