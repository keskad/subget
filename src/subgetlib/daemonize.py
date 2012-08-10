import subgetcore, sys, os

####
PluginInfo = {'Requirements' : { 'OS' : 'Unix, Linux'}, 'API': 2, 'Authors': 'webnull', 'domain': '', 'type': 'extension', 'isPlugin': False, 'Description': 'Simple plugin to fork Subget to console\'s background'}

class PluginMain(subgetcore.SubgetPlugin):
    def daemonize (self, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        '''This forks the current process into a daemon.
        The stdin, stdout, and stderr arguments are file names that
        will be opened and be used to replace the standard file descriptors
        in sys.stdin, sys.stdout, and sys.stderr.
        These arguments are optional and default to /dev/null.
        Note that stderr is opened unbuffered, so
        if it shares a file with stdout then interleaved output
        may not appear in the order that you expect.
        '''

        # Do first fork.
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)   # Exit first parent.
        except OSError as e:
            sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) )
            sys.exit(1)

        # Decouple from parent environment.
        os.chdir("/")
        os.umask(0)
        os.setsid()

        # Do second fork.
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)   # Exit second parent.
        except OSError as e:
            sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )
            sys.exit(1)

        # Redirect standard file descriptors.
        si = open(stdin, 'r')
        so = open(stdout, 'a+')
        se = open(stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())



    def _pluginInit(self):
        """ Initialize plugin """

        #if self.Subget.configGetKey("daemonize", "active") == "True":
            #self.Subget.Logging.output("Going to background...", "", False)
        if os.name != "nt":
            self.daemonize()

    def _pluginDestroy(self):
        """ Unload plugin """
        del self
