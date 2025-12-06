# SignalWeaver - ECG Analysis Tool

Professional ECG signal analysis tool for polysomnographic use with automatic QRS complex detection and manual annotation capabilities.

## New Architecture (Flask + Vue.js)

The application has been migrated to a modern architecture:
- **Backend**: Flask REST API (Python)
- **Frontend**: Vue.js 3 + Plotly.js (JavaScript)

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+ and npm
- Virtual environment (recommended)

### Backend Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Start the Flask backend:
```bash
# From project root
PYTHONPATH=/home/jaropis/projects/signalweaver python backend/app.py
```

The backend will run on `http://localhost:5001`

### Frontend Setup

1. Install Node dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:5173`

### Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

The frontend will automatically proxy API requests to the backend.

## Features

- **Automatic QRS Detection**: Powered by MNE library
- **Manual Annotation**: Click on peaks to classify as:
  - Normal (green)
  - Ventricular (blue)
  - Supraventricular (magenta)
  - Artifact (red)
- **Peak Insertion/Removal**: Click on ECG trace to insert, click on artifact to remove
- **Poincaré Plot**: Heart rate variability visualization
- **Navigation**: Move through long ECG recordings
- **Multiple Window Lengths**: 15s, 1min, 3min, 5min, 10min
- **ECG Inversion**: Toggle for better peak detection
- **Data Export**: Download RR intervals with annotations
- **Persistent Storage**: Results saved to JSON files

## Project Structure

```
signalweaver/
├── backend/                  # Flask API
│   ├── app.py               # Main Flask application
│   ├── api/
│   │   ├── ecg_routes.py    # API endpoints
│   │   └── utils.py         # Helper functions
│   └── requirements.txt
│
├── frontend/                 # Vue.js SPA
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── services/        # API service layer
│   │   ├── stores/          # Pinia state management
│   │   ├── App.vue          # Main app component
│   │   └── main.js          # Entry point
│   ├── package.json
│   └── vite.config.js
│
├── signalweaver/            # Core ECG processing (unchanged)
│   ├── signal_classes.py    # ECG and Signal classes
│   ├── signal_processing/   # R-wave detection algorithms
│   ├── HRAExplorer/         # HRV/HRA analysis
│   └── ecgs/
│       └── manager.py       # Session management
│
└── data/                    # ECG CSV files
```

## API Endpoints

### File Operations
- `GET /api/files` - List available ECG files
- `POST /api/ecg/load` - Load ECG file
- `GET /api/ecg/metadata` - Get current ECG metadata

### ECG Data
- `GET /api/ecg/trace` - Get ECG trace for current window
- `GET /api/ecg/poincare` - Get Poincaré plot data

### Manipulation
- `POST /api/ecg/invert` - Toggle ECG inversion
- `POST /api/ecg/navigate` - Move window left/right
- `POST /api/ecg/window` - Update window length
- `POST /api/ecg/navigate/poincare` - Navigate to Poincaré point

### Annotations
- `POST /api/ecg/peak/classify` - Change peak classification
- `POST /api/ecg/peak/insert` - Insert new R-wave
- `POST /api/ecg/peak/remove` - Remove R-wave
- `POST /api/ecg/save` - Save annotations to JSON

### Export
- `GET /api/ecg/export/rr` - Download RR intervals file

## Development

### Backend Development
The backend uses Flask with automatic reloading in debug mode. Any changes to Python files will auto-reload the server.

### Frontend Development
Vite provides hot module replacement (HMR). Changes to Vue components will update instantly in the browser.

### Production Build
```bash
cd frontend
npm run build
```

This creates optimized static files in `frontend/dist/` that can be served by Flask or any static file server.

## Data Format

### Input (CSV)
ECG files should be 2-column CSV format:
- Column 1: Time (seconds or datetime)
- Column 2: Voltage

### Output (JSON)
Processed results are cached in JSON files with the same name as the CSV:
- R-wave positions and amplitudes
- Annotations (0=normal, 1=ventricular, 2=supraventricular, 3=artifact)
- RR intervals
- Separate data for normal and inverted ECG

## Technology Stack

### Backend
- Flask 2.3+ - Web framework
- Flask-CORS - Cross-origin resource sharing
- NumPy - Numerical computations
- Pandas - Data manipulation
- SciPy - Signal processing
- MNE - R-wave detection

### Frontend
- Vue.js 3 - UI framework
- Pinia - State management
- Axios - HTTP client
- Plotly.js - Interactive plots
- Vite - Build tool and dev server

## Migration from Dash

The original Dash-based application is still available in:
- `dash_gui.py` - Original entry point
- `app.py` - Dash app configuration
- `signalweaver/callbacks/` - Dash callbacks
- `signalweaver/layouts/` - Dash layouts

These files are preserved but no longer used in the new architecture.

## License

GPL 3 (inherited from HRAExplorer component)

## Credits

- ECG processing core: SignalWeaver team
- HRV/HRA analysis: HRAExplorer project
