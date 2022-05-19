from app import app
from signalweaver.callbacks import prepare_callbacks
from signalweaver.ecgs.manager import add_ecg
from signalweaver.layouts.main import prepare_layout

server = app.server

name = "/home/jaropis/Dropbox/Praca2/staff/wyniki/AVA02_2017-01-11 i-.csv"
#ecg = DashECGSignal(name)  # this is global an constant for now
with app.server.app_context():
    add_ecg(name)

prepare_layout(app)
#prepare_css(app)
prepare_callbacks()

if __name__ == '__main__':
    app.run_server(debug=True)
