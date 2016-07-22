from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager
from api import dispatcher
import sys


manager = JSONRPCResponseManager()
@Request.application
def application(request):
    response = manager.handle(request.get_data(cache=False, as_text=True), dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    try:
        ip = sys.argv[0]
        port = int(sys.argv[1])
    except IndexError:
        ip = 'localhost'
        port = 8080
    run_simple(ip, port, application)
