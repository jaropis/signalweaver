from flask import session


INITIAL_ECG_NAME = None

ECGS = {}


def get_ecg(reload=False):
    try:
        name = session['ecg_name']
    except (RuntimeError, KeyError):
        global INITIAL_ECG_NAME
        name = INITIAL_ECG_NAME

    assert name, "Not ecg name found !"

    ecg = ECGS.get(name)
    if not ecg or reload:
        from signalweaver.dash_files.dash_rep import DashECGSignal
        ecg = DashECGSignal(name)  # this is global an constant for now
        ECGS.clear()
        ECGS[name] = ecg
    return ecg


def add_ecg(name):
    try:
        session['ecg_name'] = name
    except RuntimeError:
        global INITIAL_ECG_NAME
        INITIAL_ECG_NAME = name
