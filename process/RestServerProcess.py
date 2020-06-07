from multiprocessing import Process
from bottle import route, run, get, post, request, static_file, abort

class RestServerProcess(Process):
    def __init__(self, state, basedir, port=1883):
        super(RestServerProcess, self).__init__()
        self.state = state
        self.port = port
        self.basedir = basedir

    def run(self):
        state = self.state

        @route('/')
        def docroot():
            return static_file('index.html',self.basedir)

        @route('/<filepath:path>')
        def servfile(filepath):
            return static_file(filepath,self.basedir)

        @route('/curtemp')
        def curtemp():
            return str(state['avgtemp'])

        @get('/settemp')
        def settemp():
            return str(state['settemp'])

        @post('/settemp')
        def post_settemp():
            try:
                settemp = float(request.forms.get('settemp'))
                if settemp >= 90 and settemp <= 125 :
                    state['settemp'] = settemp
                    return str(settemp)
                else:
                    abort(400,'Set temp out of range 90-125.')
            except:
                abort(400,'Invalid number for set temp.')

        @get('/is_awake')
        def get_is_awake():
            return str(state['is_awake'])

        @get('/allstats')
        def allstats():
            return dict(state)

        @get('/healthcheck')
        def healthcheck():
            return 'OK'

        run(host='0.0.0.0', port=self.port)