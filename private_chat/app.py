from aiohttp import web
from collections import defaultdict
from random import choice
from random import randint
from random import shuffle
import os
import socketio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
room_sids = defaultdict(set)
sid_code_name_map = {}
used_names = set()

dir_path = os.path.dirname(os.path.realpath(__file__))
code_names = None
with open(os.path.join(dir_path, 'names.txt'), 'r', encoding='utf-8') as f:
    code_names = [i.strip() for i in f.readlines()]

# happens in place
shuffle(code_names)

# Used for when we run out of usernames that are not suffixed by a number
static_code_names = None

async def index(request):
    """Serve the client-side application."""
    with open('static/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.on('connect', namespace='/test')
async def connect(sid, environ):
    print("connect ", sid)
    if code_names:
        sid_code_name_map[sid] = code_names.pop()
        used_names.add(sid_code_name_map[sid])
    else:
        if not static_code_names:
            # Reload in the list of usernames into a list that wont change
            # so that we can use them with suffixes.
            with open(os.path.join(dir_path, 'names.txt'),
                      'r', encoding='utf-8') as f:
                static_code_names = [i.strip() for i in f.readlines()]
                shuffle(static_code_names)
        count = 0
        while True:
            try_name = ''.join([choice(static_code_names),
                                str(randint(10))])
            if try_name not in used_names:
                sid_code_name_map[sid] = try_name
                used_names.add(sid_code_name_map[sid])
                break
            count += 1
            if count > 1000:
                raise Exception('Too many users, can not generate username')
    await sio.emit(
        'system_message',
        {'data': '&lt;{}&gt;Connected'\
         .format(sid_code_name_map[sid])},
        namespace='/test')
    await sio.emit(
        'system_message',
        {'data': 'Your username is {}'.format(sid_code_name_map[sid])},
        namespace='/test',
        room=sid)


@sio.on('join_room', namespace='/test')
async def join_room(sid, data):
    room = data['room']
    sio.enter_room(sid, room, '/test')
    room_sids[room].add(sid)
    print("{} entered room {}".format(sid, room))
    await sio.emit(
        'connections_response',
        data={'data': 'New connection, total: {}'
                      .format(len(room_sids[room]))},
        namespace='/test')


@sio.on('send_message', namespace='/test')
async def message(sid, data):
    username = sid_code_name_map[sid]
    await sio.emit(
        'my_response',
        room=data['room'],
        data={'data': data['data'], 'username': username},
        namespace='/test')


@sio.on('disconnect', namespace='/test')
async def disconnect(sid):
    print('disconnect ', sid)
    for room, sids in room_sids.items():
        if sid in sids:
            username = sid_code_name_map[sid]
            sids.remove(sid)
            # No, it is important to not re-use codenames, at least not in
            # a short period of time. Re-using a code name in a short period
            # of time could result in a person being confused for someone
            # else.
            # In time we will run out of code names, but the intention
            # is that this service will run for a short period of time anyway.
            # And lastly, the max users is probably 2 anyway.
            # used_names.remove(sid_code_name_map[sid])
            del sid_code_name_map[sid]
            await sio.emit('system_message',
                 # {'data': "Unique connections: {}".format(', '.join(room_sids[room]))},
                 {'data': "&lt;{}&gt; disconnected, total left: {}".format(username, len(room_sids[room]))},
                 room=room, namespace='/test')

app.router.add_static('/static', 'static')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app, port=7632)
