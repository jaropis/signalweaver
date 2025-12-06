from flask import Blueprint, request, session, send_file
import sys
import os
import glob
import io
import numpy as np

# Add parent directories to path to import signalweaver modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from signalweaver.ecgs.manager import get_ecg, add_ecg
from signalweaver.traces.trace_rep import TraceECGSignal
from api.utils import success_response, error_response, numpy_to_list

ecg_bp = Blueprint('ecg', __name__)


# ============================================================================
# DATA ENDPOINTS
# ============================================================================

@ecg_bp.route('/files', methods=['GET'])
def list_files():
    """List available ECG files in data directory"""
    try:
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
        csv_files = glob.glob(os.path.join(data_path, '*.csv'))

        files = []
        for file_path in csv_files:
            file_name = os.path.basename(file_path)
            files.append({
                'label': file_name,
                'value': file_path
            })

        return success_response(files)
    except Exception as e:
        return error_response(str(e), 500)


@ecg_bp.route('/ecg/load', methods=['POST'])
def load_ecg():
    """Load ECG file by path"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')

        if not file_path:
            return error_response('file_path is required', 400)

        if not os.path.exists(file_path):
            return error_response(f'File not found: {file_path}', 404)

        # Use existing manager to load ECG
        add_ecg(file_path)
        ecg = get_ecg(reload=True)

        return success_response({
            'filename': ecg.name,
            'message': 'ECG loaded successfully'
        })
    except Exception as e:
        return error_response(str(e), 500)


@ecg_bp.route('/ecg/metadata', methods=['GET'])
def get_metadata():
    """Get current ECG metadata"""
    try:
        ecg = get_ecg()

        metadata = {
            'filename': ecg.name,
            'duration': float(ecg.time_track[-1] - ecg.time_track[0]),
            'sampling_rate': int(ecg.sampling_rate),
            'sampling_period': float(ecg.sampling_period),
            'inverted': bool(ecg.inverted),
            'total_peaks': int(len(ecg.r_waves_all_pos)),
            'position': float(ecg.position),
            'window_length': float(ecg.window_length),
            'window_config': {
                'number_of_lines': int(ecg.number_of_lines),
                'single_line_height': float(ecg.single_line_height)
            }
        }

        return success_response(metadata)
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================================
# ECG DATA ENDPOINTS
# ============================================================================

@ecg_bp.route('/ecg/trace', methods=['GET'])
def get_trace():
    """Get ECG trace data for current window"""
    try:
        ecg = get_ecg()

        # Get position and window_length from query params (optional)
        position = request.args.get('position', type=float)
        window_length = request.args.get('window_length', type=float)

        # Update window length if provided (directly set, bypassing string lookup)
        if window_length is not None:
            from signalweaver.traces.trace_rep import POSSIBLE_LINE_No, POSSIBLE_LINE_HEIGHTS, POSSIBLE_WINDOWS
            # Find matching window config or set directly
            if window_length in POSSIBLE_WINDOWS.values():
                # Find the key for this value
                window_key = [k for k, v in POSSIBLE_WINDOWS.items() if v == window_length][0]
                ecg.window_length = window_length
                ecg.number_of_lines = POSSIBLE_LINE_No[window_key]
                ecg.single_line_height = POSSIBLE_LINE_HEIGHTS[window_key]
            else:
                # Custom window length - use sensible defaults
                ecg.window_length = window_length
                # Adjust lines based on window length
                if window_length <= 15:
                    ecg.number_of_lines = 1
                    ecg.single_line_height = 4
                elif window_length <= 60:
                    ecg.number_of_lines = 3
                    ecg.single_line_height = 2
                else:
                    ecg.number_of_lines = 10
                    ecg.single_line_height = 1

        if position is not None:
            ecg.position = position

        # Get current window data
        time = ecg.get_current_time_track()
        voltage = ecg.get_current_ecg_track()

        # Get peaks for current window
        normal_pos, normal_vals, first_peak = ecg.get_current_peaks_positions(
            ecg.r_waves_all_pos, ecg.r_waves_all_vals, get_first_peak=True
        )
        vent_pos, vent_vals, _ = ecg.get_current_peaks_positions(*ecg.get_ventriculars())
        supra_pos, supra_vals, _ = ecg.get_current_peaks_positions(*ecg.get_supraventriculars())
        artif_pos, artif_vals, _ = ecg.get_current_peaks_positions(*ecg.get_artifacts())

        trace_data = {
            'time': numpy_to_list(time),
            'voltage': numpy_to_list(voltage),
            'peaks': {
                'normal': {
                    'time': numpy_to_list(normal_pos),
                    'voltage': numpy_to_list(normal_vals)
                },
                'ventricular': {
                    'time': numpy_to_list(vent_pos),
                    'voltage': numpy_to_list(vent_vals)
                },
                'supraventricular': {
                    'time': numpy_to_list(supra_pos),
                    'voltage': numpy_to_list(supra_vals)
                },
                'artifacts': {
                    'time': numpy_to_list(artif_pos),
                    'voltage': numpy_to_list(artif_vals)
                }
            },
            'position': float(ecg.position),
            'window_length': float(ecg.window_length),
            'window_config': {
                'number_of_lines': int(ecg.number_of_lines),
                'single_line_height': float(ecg.single_line_height)
            },
            'first_peak_position': int(first_peak) if first_peak is not None else None
        }

        return success_response(trace_data)
    except Exception as e:
        return error_response(str(e), 500)


@ecg_bp.route('/ecg/poincare', methods=['GET'])
def get_poincare():
    """Get Poincaré plot data"""
    try:
        ecg = get_ecg()

        if ecg.RRSignal is None or ecg.RRSignal.poincare is None:
            return error_response('Poincaré data not available', 400)

        poincare_data = {
            'xi': numpy_to_list(ecg.RRSignal.poincare.xi),
            'xii': numpy_to_list(ecg.RRSignal.poincare.xii),
            'range': {
                'start': float(ecg.poincare_range_start),
                'end': float(ecg.poincare_range_end)
            }
        }

        return success_response(poincare_data)
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================================
# ECG MANIPULATION ENDPOINTS
# ============================================================================

@ecg_bp.route('/ecg/invert', methods=['POST'])
def invert_ecg():
    """Toggle ECG inversion"""
    try:
        ecg = get_ecg()
        ecg.invert_ecg()

        return success_response({
            'inverted': bool(ecg.inverted),
            'message': 'ECG inversion toggled'
        })
    except Exception as e:
        return error_response(str(e), 500)


@ecg_bp.route('/ecg/navigate', methods=['POST'])
def navigate():
    """Move viewing window left or right"""
    try:
        data = request.get_json()
        direction = data.get('direction')
        window_length = data.get('window_length')

        if direction not in ['left', 'right']:
            return error_response('direction must be "left" or "right"', 400)

        ecg = get_ecg()

        # Update window length if provided
        if window_length is not None:
            ecg.update_window_length(window_length)

        # Simulate button click by incrementing counters
        if direction == 'right':
            ecg.n_right_secondary_counter += 1
            n_right = ecg.n_right_secondary_counter
            n_left = ecg.n_left_secondary_counter
        else:
            ecg.n_left_secondary_counter += 1
            n_right = ecg.n_right_secondary_counter
            n_left = ecg.n_left_secondary_counter

        # Execute navigation
        ecg.step_right_left(n_right, n_left)

        return success_response({
            'position': float(ecg.position),
            'direction': direction
        })
    except Exception as e:
        return error_response(str(e), 500)


@ecg_bp.route('/ecg/window', methods=['POST'])
def update_window():
    """Update window length"""
    try:
        data = request.get_json()
        window_length = data.get('window_length')

        if window_length is None:
            return error_response('window_length is required', 400)

        ecg = get_ecg()
        ecg.update_window_length(window_length)

        return success_response({
            'window_length': float(ecg.window_length),
            'window_config': {
                'number_of_lines': int(ecg.number_of_lines),
                'single_line_height': float(ecg.single_line_height)
            }
        })
    except Exception as e:
        return error_response(str(e), 500)


@ecg_bp.route('/ecg/navigate/poincare', methods=['POST'])
def navigate_poincare():
    """Navigate to position from Poincaré plot click"""
    try:
        data = request.get_json()
        point_number = data.get('point_number')

        if point_number is None:
            return error_response('point_number is required', 400)

        ecg = get_ecg()

        # Create clickData structure
        click_data = {
            'points': [{'pointNumber': point_number}]
        }

        # Use existing method
        ecg.set_position_on_pp_click(click_data)

        return success_response({
            'position': float(ecg.position),
            'message': 'Position updated from Poincaré click'
        })
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================================
# ANNOTATION ENDPOINTS
# ============================================================================

@ecg_bp.route('/ecg/peak/classify', methods=['POST'])
def classify_peak():
    """Change peak classification"""
    try:
        data = request.get_json()
        time_position = data.get('time_position')
        annotation = data.get('annotation')

        if time_position is None:
            return error_response('time_position is required', 400)
        if annotation not in [0, 1, 2, 3]:
            return error_response('annotation must be 0, 1, 2, or 3', 400)

        ecg = get_ecg()

        # Find the peak closest to the clicked position
        positions, _, _ = ecg.get_current_peaks_positions(ecg.r_waves_all_pos, ecg.r_waves_all_vals)
        if len(positions) == 0:
            return error_response('No peaks in current window', 400)

        peak_index = np.argmin(np.abs(positions - time_position))
        clicked_at = peak_index + ecg.first_peak_position

        # Update annotation
        ecg.annotations[clicked_at] = annotation

        # Update derived peak collections
        ecg.ventriculars_pos, ecg.ventriculars_vals = ecg.get_ventriculars()
        ecg.supraventriculars_pos, ecg.supraventriculars_vals = ecg.get_supraventriculars()
        ecg.artifacts_pos, ecg.artifacts_vals = ecg.get_artifacts()
        ecg.rr_intervals, ecg.rr_annotations = ecg.get_rrs()
        ecg.update_poincare()
        ecg.update_results_dict()
        ecg.change += 1

        return success_response({
            'changed': True,
            'annotation': int(annotation),
            'change_count': int(ecg.change)
        })
    except Exception as e:
        return error_response(str(e), 500)


@ecg_bp.route('/ecg/peak/insert', methods=['POST'])
def insert_peak():
    """Insert new R-wave at position"""
    try:
        data = request.get_json()
        time_position = data.get('time_position')

        if time_position is None:
            return error_response('time_position is required', 400)

        ecg = get_ecg()

        # Use existing insert method
        changed = ecg.insert_new_rr(time_position)

        if changed:
            # Update derived peak collections
            ecg.ventriculars_pos, ecg.ventriculars_vals = ecg.get_ventriculars()
            ecg.supraventriculars_pos, ecg.supraventriculars_vals = ecg.get_supraventriculars()
            ecg.artifacts_pos, ecg.artifacts_vals = ecg.get_artifacts()
            ecg.rr_intervals, ecg.rr_annotations = ecg.get_rrs()
            ecg.update_poincare()
            ecg.update_results_dict()
            ecg.change += 1

        return success_response({
            'changed': bool(changed),
            'change_count': int(ecg.change) if changed else None
        })
    except Exception as e:
        return error_response(str(e), 500)


@ecg_bp.route('/ecg/peak/remove', methods=['POST'])
def remove_peak():
    """Remove R-wave at position"""
    try:
        data = request.get_json()
        time_position = data.get('time_position')

        if time_position is None:
            return error_response('time_position is required', 400)

        ecg = get_ecg()

        # Use existing remove method
        ecg.remove_rr(time_position)

        # Update derived peak collections
        ecg.ventriculars_pos, ecg.ventriculars_vals = ecg.get_ventriculars()
        ecg.supraventriculars_pos, ecg.supraventriculars_vals = ecg.get_supraventriculars()
        ecg.artifacts_pos, ecg.artifacts_vals = ecg.get_artifacts()
        ecg.rr_intervals, ecg.rr_annotations = ecg.get_rrs()
        ecg.update_poincare()
        ecg.update_results_dict()
        ecg.change += 1

        return success_response({
            'changed': True,
            'change_count': int(ecg.change)
        })
    except Exception as e:
        return error_response(str(e), 500)


@ecg_bp.route('/ecg/save', methods=['POST'])
def save_ecg():
    """Save annotations to JSON file"""
    try:
        ecg = get_ecg()
        ecg.update_results_dict()
        ecg.save_processed_data()

        return success_response({'message': 'ECG data saved successfully'})
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================================
# EXPORT ENDPOINT
# ============================================================================

@ecg_bp.route('/ecg/export/rr', methods=['GET'])
def export_rr():
    """Export RR intervals and annotations as downloadable file"""
    try:
        ecg = get_ecg()

        # Create RR data array
        rr_download = np.asarray([ecg.rr_intervals * 1000, ecg.rr_annotations]).T

        # Create text buffer
        text_buffer = io.BytesIO()
        np.savetxt(text_buffer, rr_download, fmt=['%5f', '%1d'],
                   header='RRinterval\tannotation', delimiter='\t', newline='\n')

        # Get filename
        filename = ecg.name[0:-4] + "_RR.txt"

        # Prepare for download
        text_buffer.seek(0)

        # Remove '# ' from header (numpy adds this)
        content = text_buffer.getvalue().decode('utf-8').replace('# ', '')
        final_buffer = io.BytesIO(content.encode('utf-8'))
        final_buffer.seek(0)

        return send_file(
            final_buffer,
            mimetype='text/plain',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return error_response(str(e), 500)
