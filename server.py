from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager
from api import dispatcher, init_nlp
import sys


manager = JSONRPCResponseManager()
@Request.application
def application(request):
    response = manager.handle(request.get_data(cache=False, as_text=True), dispatcher)
    return Response(response.json, mimetype='application/json')

if __name__ == '__main__':
    mode = sys.argv[1]
    try:
        ip = sys.argv[2]
        port = int(sys.argv[3])
    except IndexError:
        ip = 'localhost'
        port = 8080

    init_nlp(mode)
    run_simple(ip, port, application)
