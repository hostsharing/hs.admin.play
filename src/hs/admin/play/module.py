""" This module provides a class that implements a generic Ansible module againt the HSAdmin API.
"""

from shlex import split
from ast import literal_eval
from json import dumps

from hs.admin.api import API

from .exceptions import MissingArgumentError, InvalidArgumentError
from .exceptions import APIInitializationError, APIInvokationError
from .exceptions import AmbiguousResultsError

try:
    string = (str, unicode,)
except:
    string = (str,)



class Module(object):
    """ This class implements a generic Ansible module againt the HSAdmin API.
    """

    def __init__(self, module, ids, argsfile):

        def parse_argsfile(argsfile):
            """ Returns parsed params provided by argsfile """

            args = split(open(argsfile).read())
            params = dict()
            for arg in args:

                if '=' in arg:
                    key, value = arg.split('=', 1)
                    try:
                        params[key] = literal_eval(value)
                    except (SyntaxError, TypeError, ValueError,):
                        params[key] = value
                else:
                    params[arg] = None
            return params


        def check_hsadmin_param(hsadmin):
            """ Checks whether the hsadmin parameter has a valid structure """

            if not isinstance(hsadmin, dict):
                return False

            if not (('cas' in hsadmin) and
                    isinstance(hsadmin['cas'], dict)):
                return False
            else:
                cas = hsadmin['cas']
                if not (isinstance(cas, dict) and
                        ('uri' in cas) and
                        isinstance(cas['uri'], string) and
                        ('service' and cas) and
                        isinstance(cas['service'], string)):
                    return False

            if 'credentials' not in hsadmin:
                return False
            else:
                credentials = hsadmin['credentials']
                if not (isinstance(credentials, dict) and
                        ('username' in credentials) and
                        isinstance(credentials['username'], string) and
                        ('password' in credentials) and
                        isinstance(credentials['password'], string)):
                    return False

            if 'backends' not in hsadmin:
                return False
            else:
                backends = hsadmin['backends']
                if not isinstance(backends, list) or (len(backends) == 0):
                    return False
                for backend in backends:
                    if not isinstance(backend, string):
                        return False

            return True


        params = parse_argsfile(argsfile)

        if 'hsadmin' not in params:
            raise MissingArgumentError('Module argument "hsadmin" is missing.')

        hsadmin = params['hsadmin']
        del params['hsadmin']

        if not check_hsadmin_param(hsadmin):
            raise InvalidArgumentError('Module argument "hsadmin" is invalid.')

        try:
            api = API(**hsadmin)
        except Exception as exception:
            raise APIInitializationError('HSAdmin API initialization failed: ' + exception.message)

        if module not in api.modules:
            raise NotImplementedError('HSAdmin API does not implement the module: ' + module)

        if 'state' in params:
            state = params['state']
            del params['state']
            if not state in ('present', 'absent'):
                raise InvalidArgumentError('Module argument "state" is invalid.')
        else:
            state = 'present'

        # Patch module properties to provide information
        # about the property being part of the unique identifier
        # until that information is provided by the backends theirselves
        properties = api.modules[module].properties
        for key in properties.keys():
            properties[key]['id'] = (key in ids)

        self.module = api.modules[module]
        self.params = params
        self.state = state


    def __call__(self):

        def build_where_params(module, params):
            """ Returns where data structure """

            ids = list()
            properties = module.properties
            for key in module.properties.keys():
                if ('id' in properties[key]) and properties[key]['id']:
                    ids.append(key)

            where_params = dict()
            for key in ids:
                if key not in params:
                    raise MissingArgumentError('Module argument "%s" is missing.' % key)
                where_params[key] = self.params[key]

            return where_params


        def build_set_params(module, current, params):
            """ Returns where data structure """

            set_params = dict()
            for key in params.keys():
                if key not in module.properties:
                    raise InvalidArgumentError('Module argument "%s" is invalid.' % key)
                if (key not in current) or (current[key] != params[key]):
                    set_params[key] = params[key]

            return set_params


        def retrieve(module, params):
            """ Returns record if found """

            where = build_where_params(module, params)

            try:
                results = module.search(where=where)
            except Exception as exception:
                raise APIInvokationError('HSAdmin API invokation failed: ' + exception.message)

            if len(results) > 1:
                raise AmbiguousResultsError('Retrieved ambiguous results.')

            if len(results) == 1:
                return results[0]
            else:
                return None


        def add(module, params):
            """ Adds record """

            set_params = build_set_params(module, dict(), params)

            try:
                module.add(set=set_params)
            except Exception as exception:
                raise APIInvokationError('HSAdmin API invokation failed: ' + exception.message)

            return True


        def update(module, current, params):
            """ Updates record if modified """

            set_params = build_set_params(module, current, params)
            if len(set_params) > 0:
                where_params = build_where_params(module, params)

                try:
                    module.update(where=where_params, set=set_params)
                except Exception as exception:
                    raise APIInvokationError('HSAdmin API invokation failed: ' + exception.message)

                return True
            else:
                return False


        def delete(module, params):
            """ Deletes record """

            where_params = build_where_params(module, params)

            try:
                module.delete(where=where_params)
            except Exception as exception:
                raise APIInvokationError('HSAdmin API invokation failed: ' + exception.message)

            return True


        module = self.module
        params = self.params
        state = self.state

        changed = False

        retrieved = retrieve(module, params)

        if (state == 'present') and not retrieved:
            changed = add(module, params)
        if (state == 'present') and retrieved:
            changed = update(module, retrieved, params)
        if (state == 'absent') and retrieved:
            changed = delete(module, params)

        print(dumps({'changed': changed}))
