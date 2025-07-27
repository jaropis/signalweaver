from app import app
from signalweaver.callbacks import prepare_callbacks
from signalweaver.ecgs.manager import add_ecg
from signalweaver.layouts.main import prepare_layout
import glob

server = app.server

with app.server.app_context():
    first_file = glob.glob('data/*.csv')[0]
    add_ecg(first_file)

prepare_layout(app)
#prepare_css(app)
prepare_callbacks()

if __name__ == '__main__':
    app.run(debug=True)
