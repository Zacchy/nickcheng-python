from django.shortcuts import render_to_response

def ex4_1(request):
    MUSICIANS = [
        {'name': 'Django Reinhardt', 'genre': 'jazz'},
        {'name': 'Jimi Hendrix',     'genre': 'rock'},
        {'name': 'Louis Armstrong',  'genre': 'jazz'},
        {'name': 'Pete Townsend',    'genre': 'rock'},
        {'name': 'Yanni',            'genre': 'new age'},
        {'name': 'Ella Fitzgerald',  'genre': 'jazz'},
        {'name': 'Wesley Willis',    'genre': 'casio'},
        {'name': 'John Lennon',      'genre': 'rock'},
        {'name': 'Bono',             'genre': 'rock'},
        {'name': 'Garth Brooks',     'genre': 'country'},
        {'name': 'Duke Ellington',   'genre': 'jazz'},
        {'name': 'William Shatner',  'genre': 'spoken word'},
        {'name': 'Madonna',          'genre': 'pop'},
    ]
    ms = []
    hasStar = False
    for i in MUSICIANS:
        if ' ' not in i['name']:
            hasStar = True
        ms.append({
            'name': i['name'],
            'genre': i['genre'],
            'isBold': i['genre'] in ('rock', 'jazz'),
            'isStar': ' ' not in i['name'],
        })
    return render_to_response('ex4_1.html', {'musicians': ms, 'hs': hasStar})

