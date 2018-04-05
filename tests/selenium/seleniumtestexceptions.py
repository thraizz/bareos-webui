class BadJobException(Exception):
    '''Raise when a started job doesn't result in ID'''
    def __init__(self, msg=None):
        msg = 'Job ID could not be saved after starting the job.'
        super(BadJobException, self).__init__(msg)

class ClientStatusException(Exception):
    '''Raise when a client does not have the expected status'''
    def __init__(self,client, status, msg=None):
        if status=='enabled':
            msg = '%s is enabled and cannot be enabled again.' % client
        if status=='disabled':
            msg = '%s is disabled and cannot be disabled again.' % client
        super(ClientStatusException, self).__init__(msg)

class ClientNotFoundException(Exception):
    '''Raise when the expected client is not found'''
    def __init__(self, client, msg=None):
        msg = 'The client %s was not found.' % client
        super(ClientNotFoundException, self).__init__(msg)

class ElementCoveredException(Exception):
    '''Raise when an element is covered by something'''
    def __init__(self, value):
        msg = 'Click on element %s failed as it was covered by another element.' % value
        super(ElementCoveredException, self).__init__(msg)

class ElementTimeoutException(Exception):
    '''Raise when waiting on an element times out'''
    def __init__(self, value):
        if value != 'spinner':
            msg = 'Waiting for element %s returned a TimeoutException.' % value
        else:
            msg = 'Waiting for the spinner to disappear returned a TimeoutException.' % value
        super(ElementTimeoutException, self).__init__(msg)

class ElementNotFoundException(Exception):
    '''Raise when an element is not found'''
    def __init__(self, value):
        msg = 'Element %s was not found.' % value
        super(ElementNotFoundException, self).__init__(msg)

class FailedClickException(Exception):
    '''Raise when wait_and_click fails'''
    def __init__(self, value):
        msg = 'Waiting and trying to click %s failed.' % value
        super(FailedClickException, self).__init__(msg)

class LocaleException(Exception):
    '''Raise when wait_and_click fails'''
    def __init__(self, expected_languages, elements):
        if len(expected_languages)!=len(elements):
            msg = 'The available languages in login did not meet expectations.\n Expected '+str(len(expected_languages))+' languages but got '+str(len(elements))+'. Dropdown menue misses '+''.join(list(set(expected_languages) - set(elements)))+'.'
        else:
             msg = 'The available languages in login did not meet expectations.\n'+'Dropdown menue misses language '+''.join(list(set(expected_languages) - set(elements)))+' or the name changed.'
        super(LocaleException, self).__init__(msg)

class WrongCredentialsException(Exception):
    '''Raise when wait_and_click fails'''
    def __init__(self, username, password):
        msg = 'Username "%s" or password "%s" is wrong.' % (username,password)
        super(WrongCredentialsException, self).__init__(msg)
