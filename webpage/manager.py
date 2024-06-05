
import threading
import time
import gettext
import queue
import os,sys

_ = gettext.gettext
TEST_QUEUE_MAX = 100

class Worker(threading.Thread):
    """
    A threaded worker class. Use :meth:`start` to start it's activity.
    To stop it you can set the :attr:`stop` to :const:`true`.

    :param data: Data to be passed to the :class:`TestCase_` objects before
                 running.
    :param queue_in: Process queue. Every item has to be an instance of
                     :class:`TestCase_`
    :param queue_out: Message queue. In this queue the :attr:`results` object
                      will log its messages.
    :param interval: The time in seconds to wait for new test cases.
    """
    def __init__(self, data, queue_in, queue_out, interval=0.5):
        #: The data (:class:`dict`) which is set for each test case before
        #: executing
        self.data = data
        threading.Thread.__init__(self, name="BlogWorker")
        #: Update interval.
        self.interval = float(interval)
        #: Test case queue
        self.queue_in = queue_in
        #: Message queue
        self.message_queue = queue_out
        #: Stopbit. The thread will exit if this attribut is set to
        #: :const:`true`
        self.stop = False
        self.reset()

    def reset(self):
        """
        Resets the result.
        """
        #: An instance of :class:`TestResult_`
        self.results = TestResult_(self.message_queue)
        self.stop = False

    def run(self):
        """
        The actual thread activity. Do not run this method directly. Call
        :meth:`start` instead.
        """
        print("started")
        while not self.stop:
            try:
                # Get Test from Queue (nonblocking)
                print( "queue_in" + str(self.queue_in))
                current_test = self.queue_in.get_nowait()
            except queue.Empty:
                # Wait for new testcases
                time.sleep(self.interval)
                continue

            current_test.data = self.data
            print( "test: " + str(self.results))
            print("data: " + str(self.data))
            current_test.run(self.results)



class TestCaseManager(object):
    """
    A high level controller for the test-cases. It searches and import the
    test modules from a directory and controls messages and results.
    """
    thread = None

    def __init__(self):
        self.lock = threading.Lock()
        self.__session_data = dict()
        self.reset(restart=False)

    def reset(self, restart=True):
        """
        Reset the manager. This will stop the thread, clear all results and
        start the thread again. The only thing to remain uncleared is the
        :attr:`session_data`.
        """
        # stop thread
        self.stop()
        with self.lock:
            # create new queue for the messages
            self.message_queue = queue.Queue(1000)
            # create new queue for the execution
            self.test_queue = queue.Queue(maxsize=TEST_QUEUE_MAX)
            # clear all messages
            self.messages = {}
            # clear all tests
            self.blog_message_list = []
        # load tests again
        self.load_blogs()
        # start thread again
        if restart:
            self.start()

    def get_data(self):
        """
        Returns the data set by :meth:`set_data`.
        """
        return dict(self.__session_data)

    def set_data(self, cherrypy_session):
        """
        Update the data to be set for each test before executing.
        :param cherrypy_session: The data will be get from this cherrypy session.
        """
        with self.lock:
            self.__session_data.update(cherrypy_session)
            # Updated threads data
            if self.thread:
                self.thread.data = self.__session_data

    #: The data for the worker :attr:`thread`
    #: See also :meth:`set_data` and :meth:`get_data`.
    data = property(get_data, set_data)

    def load_blogs(self, 
                   module=None,
                   prefix='blog_',
                   suffix='.py',
                   baseclass='BlogPost_'):
        """
        :param module: 
        :param prefix: The filename prefix.
        :param suffix: The filename suffix ('.py' by default).

        Raises a :exc:`ValueError` if the directory does not exist.
        """
        with self.lock:
            module = module or 'blog_posts'

            if isinstance(module, str):
                __import__(module)
                base_module = sys.modules[module]
            else:
                base_module = module
                module = module.__name__

            directory = os.path.split(base_module.__file__)[0]
            files = [os.path.splitext(x)[0] for x in os.listdir(directory) \
                     if x.startswith(prefix) and x.endswith(suffix)] 

            print(module, globals(), locals(), [baseclass] + files)
            __import__(module, globals(), locals(), [baseclass] + files)
            self.test_base = getattr(base_module, baseclass)
            self.blog_message_list = []
            for _file in files:
                module_name = os.path.splitext(_file)[0]
                try:
                    temp_module = getattr(base_module, _file)
                except:
                    print("Error while importing %r\n%s" % (_file,
                                                            traceback.format_exc()))
                    continue
                for _, obj in inspect.getmembers(temp_module):
                    if inspect.isclass(obj) and \
                       issubclass(obj, self.test_base):
                        try:
                            obj = obj(self.get_data())
                        except ValueError:
                            print("Invalid Blog post")
                        self.blog_message_list.append(obj)
            self.__sort_list()

    

    def run_tests(self, blog_message_list, timeout=0.5):
        """
        Run a list of tests.

        :param tests: A list containing the tests to run.
        :type tests: list
        :param timeout: The timeout in seconds to wait for a free slot.
        """
        blog_message_list = list(blog_message_list)
        while blog_message_list:
            test = blog_message_list.pop(0)
            if not self.run_test(test, timeout=timeout):
                blog_message_list.insert(0)
        return blog_message_list

    def run_test(self, test, timeout=0.5, reset=True):
        """
        Adds a single test to the queue for the :class:`Worker`.

        :param test: The Testfuntion to be run.
        :param timeout: The timeout in seconds to wait for a free slot.
        """
        #:param reset: If :const:`True` all messages and the State associated
        #              with the tests are cleared.
        if not self.thread:
            self.start()
        test_case = None
        if type(test) is str:
            for t in self.blog_message_list:
                if test == t.id() or test == t.identifier:
                    test_case = t
            if not test_case:
                raise ValueError('invalid test identifier', test)
        elif isinstance(test, self.test_base):
            test_case = test
        else:
            raise TypeError('str or TestCase is required.', test)

        try:
            self.test_queue.put(test_case, True, timeout)
        except queue.Full:
            return False
        return True

    def start(self):
        """
        Start the :class:`Worker` thread.
        """
        with self.lock:
            if not self.thread:
                self.thread = Worker(self.get_data(),
                                     self.test_queue,
                                     self.message_queue)
                self.thread.start()

    def stop(self, timeout=10):
        """
        Stop the :class:`Worker` thread.
        Returns :const:`True` if it has stopped and :const:`False` if not.

        :param timeout: Timeout in seconds to wait for the thread to quit.
        :type timeout: int
        """
        with self.lock:
            result = True
            if self.thread:
                self.thread.stop = True
                # wait until the thread exits
                self.thread.join(timeout=timeout)
                # check if the thread has really finished
                if not self.thread.isAlive():
                    self.thread = None
                else:
                    result = False
        return result


    def get_new_messages(self, limit=None):
        """
        Returns a list of all new messages. Once the messages are returned
        they will never be returned by this function again.
        """
        counter = 0
        result = []
        while limit is None or counter < limit:
            try:
                msg = self.message_queue.get_nowait()
                counter += 1
                if not msg[0] in self.messages:
                    self.messages[msg[0]] = []
                self.messages[msg[0]].append(msg[1])
                result.append((msg[0].identifier, msg[1]))
            except queue.Empty:
                break
        return result

    def get_all_messages(self):
        """
        Returns a dictionary of all result messages. The keys are the test 
        case identifiers and the values are lists of messages in chronological
        ordner (position 0 is the oldest).

        .. note:: All new messages are also returned. After you call
                  this method, :meth:`get_new_messages` will never return 
                  anything.
        """
        # call this method to get ALL messages. Otherwise only not-new
        # messages would be gattered by get_all_messages
        self.get_new_messages()
        r = dict((test.identifier, results) for (test, results) in \
                 self.messages.items())
        return r


    def get_all_results(self):
        """
        Returns a list of all result messages. The keys are the test case
        identifiers and the values are lists of messages in chronological ordner
        (position 0 is the oldest).

        The difference to :meth:`get_all_messages` is that the return value
        will contain test without messages (empty message list).
        """
        all_messages = self.get_all_messages()
        result = []
        with self.lock:
            for test_class in self.blog_message_list:
                messages = []
                for test in self.thread.results.tests:
                    if test.identifier != test_class.identifier:
                        continue
                    if test.identifier in all_messages:
                        messages = all_messages[test.identifier]
                    break
                result.append((test_class, messages))
        return result

    def get_new_states(self):
        """
        Returns a list of all new states.
        """
        with self.lock:
            if not self.thread:
                states = []
            else:
                states = self.thread.results.get_new_states()
        return states

    def get_all_states(self):
        """
        Returns a list containing each test and its state.
        """
        if not self.thread:
            return []
        return self.thread.results.get_all_states()

    def __sort_list(self):
        """
        Sort the :attr:`blog_message_list` by its dependencies
        ..note:: This method does not acquire the lock.
        """
        self.blog_message_list = list(self.test_base.sort(self.blog_message_list))


    def get_list(self):
        """
        Returns a list of all Tests.
        """
        return list(self.blog_message_list)

if __name__ == '__main__':

    class TestTestCaseManager():
        def setUp(self):
            self.mgr = TestCaseManager()

        def test_load(self):
            self.mgr.load_blogs()
            self.assertNotEqual(self.mgr.blog_message_list, [])
            for test in self.mgr.blog_message_list:
                self.assertIsInstance(test, unittest.TestCase)
            r = timeit.timeit('TestCaseManager()', number=1000, setup="from __main__ import TestCaseManager")
            print('%.3f ms' % r)
        def test_get_messages(self):
            messages = self.mgr.get_new_messages()
            messages = list(messages)
            self.assertEqual(messages, [])
    test = TestTestCaseManager()

    test.setUp()
    test.test_load()