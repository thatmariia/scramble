from scramble.app import AppSession

_current_session: AppSession | None = None


def get_current_session():
    return _current_session


def set_current_session(session):
    global _current_session
    _current_session = session