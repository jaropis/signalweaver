import warnings
import numpy as np
from mne.preprocessing import ecg
from numba import njit, prange


# We disable the floating point error changes under JIT since Numba may not support np.seterr fully
# old_err = np.seterr(divide='raise')  # optional or put behind a condition

@njit
def find_max_qrs(qrs_pos, ecg_line, dist=100):
    """
    Find the maximum amplitude around a given QRS position.
    """
    # Numba doesn't allow negative indexing in the same way as Python,
    # so we explicitly check array bounds
    left_idx = max(qrs_pos - dist, 0)
    right_idx = min(qrs_pos + dist, ecg_line.shape[0])
    return np.argmax(ecg_line[left_idx:right_idx]) + left_idx


@njit
def clean_peaks(qrs_complexes, dist=20):
    """
    Resolve closely spaced QRS detections by merging them (median).
    """
    new_peaks = []
    accumulator = []
    push = True
    length = len(qrs_complexes)

    for idx in range(length - 1):
        if qrs_complexes[idx + 1] - qrs_complexes[idx] < dist:
            accumulator.append(qrs_complexes[idx])
            push = False
        elif not push:  # last of close-by QRS complexes
            accumulator.append(qrs_complexes[idx])
            new_peaks.append(int(np.median(np.array(accumulator))))
            push = True
            accumulator = []
        else:
            # We do a sanity check here in normal Python,
            # but in Numba you can't do `assert` the same way
            # So either remove or keep them if they are important
            # assert (len(accumulator) == 0), "accumulator length is not 0!"
            # assert push, "pop is not True!"
            new_peaks.append(qrs_complexes[idx])

    # handle the very last QRS
    if len(accumulator) == 0:
        new_peaks.append(qrs_complexes[-1])
    else:
        accumulator.append(qrs_complexes[-1])
        new_peaks.append(int(np.median(np.array(accumulator))))

    return np.array(new_peaks, dtype=np.int64)


@njit
def get_template(qrs_voltage, qrs_position, template_length=101, n_sample=8, hi_corr=0.8):
    """
    Calculate a QRS template by picking random QRS segments and averaging
    those that correlate highly with each other.
    """
    # If too few QRS positions, return [-1]
    if len(qrs_position) < 3:
        return np.array([-1], dtype=np.float64)

    np.random.seed(777)  # reproducibility
    # If there aren't enough unique QRS to sample from, just return [-1]
    if len(qrs_position) < n_sample:
        return np.array([-1], dtype=np.float64)

    random_qrs = np.random.choice(qrs_position[2:], n_sample, replace=False)

    # Dictionary of correlations
    correlations = {}
    half_len = (template_length - 1) // 2

    # Compute pairwise correlations among random QRS segments
    for idx in range(n_sample):
        start_i = random_qrs[idx] - half_len
        end_i = random_qrs[idx] + half_len + 1
        # Bound-check
        if start_i < 0 or end_i > qrs_voltage.shape[0]:
            return np.array([-1], dtype=np.float64)
        vec_i = qrs_voltage[start_i:end_i]

        for idy in range(idx + 1, n_sample):
            start_j = random_qrs[idy] - half_len
            end_j = random_qrs[idy] + half_len + 1
            if start_j < 0 or end_j > qrs_voltage.shape[0]:
                return np.array([-1], dtype=np.float64)
            vec_j = qrs_voltage[start_j:end_j]

            # np.corrcoef() is not fully supported by Numba directly,
            # you can implement your own correlation if you encounter errors.
            # We'll assume it works for this example:
            c = np.corrcoef(vec_i, vec_j)[0, 1]
            correlations[(idx, idy)] = c

    # Filter out QRS that correlate above hi_corr
    high_corr_indices = set()
    for (ix, iy), val in correlations.items():
        if val > hi_corr:
            high_corr_indices.add(ix)
            high_corr_indices.add(iy)

    if len(high_corr_indices) == 0:
        # None are highly correlated, fallback
        return np.array([-1], dtype=np.float64)

    # Build the template
    template = np.zeros(template_length, dtype=np.float64)
    count = 0
    for idx in high_corr_indices:
        start = random_qrs[idx] - half_len
        end = random_qrs[idx] + half_len + 1
        template += qrs_voltage[start:end]
        count += 1

    if count > 0:
        template /= count

    return template


@njit
def correlation_machine(vector, template):
    """
    Slide a window the size of template across 'vector' and compute correlation.
    """
    len_vec = len(vector)
    len_temp = len(template)
    out = np.empty(len_vec, dtype=np.float64)
    extended = np.concatenate([vector, np.zeros(len_temp)])

    for idx in range(len_vec):
        # If going out of range, we just handle that portion
        slice_ = extended[idx: idx + len_temp]
        # again, if np.corrcoef or np.dot is an issue, do a manual correlation
        try:
            out[idx] = np.corrcoef(template, slice_)[0, 1]
        except FloatingPointError:
            out[idx] = 0.0
    return out


@njit
def find_correlated_peaks(correlations_vector, voltage, template, threshold=0.75, search_width=10):
    """
    Find peaks in correlation vector above a threshold, then locate maxima in the raw signal.
    """
    template_length = len(template)
    template_ptp = np.ptp(template)
    boo = correlations_vector >= threshold  # boolean mask

    # find rising/falling edges
    diff_bool = boo[1:] != boo[:-1]
    indices = np.flatnonzero(diff_bool) + 1

    # split correlation into sub-regions
    index_vector = np.arange(len(correlations_vector))
    regions = []
    start_idx = 0
    for idx in indices:
        region = index_vector[start_idx:idx]
        regions.append(region)
        start_idx = idx
    # Add the last region
    if start_idx < len(index_vector):
        regions.append(index_vector[start_idx:])

    # Pick only the True sections
    true_regions = []
    flag = boo[0]
    for i, region in enumerate(regions):
        if flag:
            true_regions.append(region)
        flag = not flag

    # Shift everything by half a template
    half_temp = template_length // 2
    peaks = []

    for segment in true_regions:
        # shift the segment to the middle
        segment_mid = segment + half_temp
        left_ext = max(segment_mid[0] - search_width, 0)
        right_ext = min(segment_mid[-1] + search_width + 1, len(voltage))

        # Argmax in the raw ECG
        peak_position = np.argmax(voltage[left_ext:right_ext]) + left_ext

        # If the peak is not out of range, check amplitude conditions
        seg_ptp = np.ptp(voltage[left_ext:right_ext])
        if (seg_ptp >= 0.5 * template_ptp) and (seg_ptp <= 2.0 * template_ptp):
            peaks.append(peak_position)

    return np.array(peaks, dtype=np.int64)


def detect_r_waves(time_track, voltage, frequency=200):
    """
    Wrapper function that calls MNE’s ecg.qrs_detector (pure Python)
    and then refines peaks via correlation with a computed template.
    """
    global_peaks = ecg.qrs_detector(
        frequency,
        ecg=voltage,
        thresh_value=0.3,
        h_freq=99,
        l_freq=1,
        filter_length=frequency * 3
    )

    # Refine with find_max_qrs
    global_peaks = np.array([find_max_qrs(pos, voltage, 100) for pos in global_peaks], dtype=np.int64)
    global_peaks = clean_peaks(global_peaks)

    # Build template
    template_length = int(frequency / 4 + 1)
    template = get_template(voltage, global_peaks, template_length=template_length)
    # If template is [-1], return empty
    if len(template) == 1 and template[0] == -1:
        return np.transpose(np.array([[], []]))

    # Correlate across the entire signal
    corr = correlation_machine(voltage, template)
    # Find correlated peaks
    global_peaks = find_correlated_peaks(corr, voltage, template=template)
    peaks_values = voltage[global_peaks]
    peaks_positions = time_track[global_peaks]

    return np.transpose(np.array([peaks_positions, peaks_values]))


# Simple artifact detection stubs
@njit
def detect_ventriculars(r_waves_positions, r_waves_values):
    """
    Placeholder that returns an empty array.
    Would do additional checks on amplitude, shapes, etc.
    """
    # Example check:
    # return np.where((r_waves_values > 200) & (r_waves_values < 500))[0]
    return np.array([], dtype=np.int64)


@njit
def detect_supraventriculars(r_waves_positions, r_waves_values):
    """
    Placeholder that returns an empty array.
    """
    # Example check:
    # return np.where((r_waves_values > 500) & (r_waves_values < 1000))[0]
    return np.array([], dtype=np.int64)


@njit
def noise_profile(r_waves, time, signal, reasonable_rr, n_sample=100, half_template_length=50):
    """
    Collect the average noise profile by sampling intervals between R-waves.
    """
    if len(r_waves) < 6:
        return -1.0

    if n_sample > len(r_waves) - 2:
        # reduce n_sample if we have fewer R waves
        n_sample = len(r_waves) - 2

    np.random.seed(777)
    # random choice among valid indices
    valid_indices = np.arange(2, len(r_waves))
    if len(valid_indices) < n_sample:
        n_sample = len(valid_indices)
    random_r_pos = np.random.choice(valid_indices, n_sample, replace=False)

    noise_levels = []
    for r in random_r_pos:
        rr = r_waves[r] - r_waves[r - 1]
        if rr < reasonable_rr[0] or rr > reasonable_rr[1]:
            continue

        peak_position = np.searchsorted(time, r_waves[r])
        prev_peak_position = np.searchsorted(time, r_waves[r - 1])

        seg_start = prev_peak_position + half_template_length
        seg_end = peak_position - half_template_length
        if seg_start >= seg_end:
            continue

        seg = signal[seg_start:seg_end]
        noise_levels.append(np.std(seg))

    if len(noise_levels) == 0:
        return -1.0

    # compute IQR-based range
    noise_levels_arr = np.array(noise_levels)
    q25, q75 = np.percentile(noise_levels_arr, [25, 75])
    noise_range = np.array([q25, q75]) * np.array([0.7, 1.3])
    return noise_range[1]


@njit
def noise(r_waves, time_track, signal, half_template_length=50):
    """
    Calculate noise between consecutive R-peaks.
    """
    rr_noise = []
    for idx in range(1, len(r_waves)):
        peak_position = np.searchsorted(time_track, r_waves[idx])
        prev_peak_position = np.searchsorted(time_track, r_waves[idx - 1])

        seg_start = prev_peak_position + half_template_length
        seg_end = peak_position - half_template_length
        if seg_start < seg_end:
            seg = signal[seg_start:seg_end]
            rr_noise.append(np.std(seg))
        else:
            rr_noise.append(0.0)
    return rr_noise


def detect_artifacts(r_waves_positions, time_track, signal, rr_filter=(0.3, 1.75)):
    """
    Mark R-waves that are either too close or too far apart in time,
    or that are accompanied by unusually high noise.
    """
    # We keep this function in normal Python because it calls noise_profile (Numba),
    # but also does some logic that might involve lists, etc.
    reasonable_rr = np.array(rr_filter) * np.array([2.0, 0.75])
    current_noise_profile = noise_profile(r_waves_positions, time_track, signal, reasonable_rr)

    noise_for_all = noise(r_waves_positions, time_track, signal)
    artifact_positions = []

    for idx in range(1, len(r_waves_positions)):
        current_rr = r_waves_positions[idx] - r_waves_positions[idx - 1]
        local_noise = noise_for_all[idx - 1]
        if (current_rr < rr_filter[0]) or (current_rr > rr_filter[1]):
            artifact_positions.append(idx)
        elif (current_rr < reasonable_rr[0] or current_rr > reasonable_rr[
            1]) and local_noise > current_noise_profile * 2:
            artifact_positions.append(idx)
        elif local_noise > 4 * current_noise_profile:
            artifact_positions.append(idx)
    return artifact_positions
