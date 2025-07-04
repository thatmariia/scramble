from scramble.app.session_persistence import SessionPersistence


def get_current_session():
    return SessionPersistence.load()


def set_current_session(session):
    SessionPersistence.save(session)
