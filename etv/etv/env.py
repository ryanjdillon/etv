
def get_project_path():
    from django.shortcuts import render_to_response
    from os import environ

    path_project = environ.get('PATH_ETV')
    if path_project is None:
        error_message = ('You need to create a project directory with the '
                         'required configuration files and point '
                         'PATH_ETV to it.')
        return render_to_response('error.html', {'error_message': error_message})
    return path_project


def get_json_path():
    from django.shortcuts import render_to_response
    from os import environ

    json_path = environ.get('PATH_JSON')
    if json_path is None:
        error_message = ('You need to scp JSON data from the server and point '
                         'PATH_JSON to it. The demo JSON data has been removed '
                         'from the repo.')
        return render_to_response('error.html', {'error_message': error_message})
    return json_path
