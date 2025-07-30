from datetime import datetime

import microscopemetrics_schema.datamodel as mm_schema
import numpy as np
import pandas as pd
from scipy import ndimage, signal
from skimage.exposure import rescale_intensity
from skimage.feature import peak_local_max
from skimage.filters import gaussian

import microscopemetrics as mm
from microscopemetrics.analyses import tools as mm_tools

MAX_NR_PEAKS = 100


def _add_column_name_level(df: pd.DataFrame, level_name: str, level_value: str):
    if isinstance(df.columns, pd.MultiIndex):
        new_columns = pd.MultiIndex.from_tuples(
            [(level_value, *col) for col in df.columns],
            names=[level_name] + list(df.columns.names),
        )
    else:
        new_columns = pd.MultiIndex.from_tuples(
            [(level_value, col) for col in df.columns],
            names=[level_name, df.columns.name],
        )
    df.columns = new_columns


def _add_row_index_level(df: pd.DataFrame, level_name: str, level_value: str):
    if isinstance(df.index, pd.MultiIndex):
        new_index = pd.MultiIndex.from_tuples(
            [(level_value, *row) for row in df.index],
            names=[level_name] + list(df.index.names),
        )
    else:
        new_index = pd.MultiIndex.from_tuples(
            [(level_value, row) for row in df.index], names=[level_name, df.index.name]
        )
    df.index = new_index


def _concatenate_index_levels(index_names, index_values, pattern="{level_name}-{level_value}_"):
    concatenated_str = "".join(
        pattern.format(level_name=level_name, level_value=level_value)
        for level_name, level_value in zip(index_names, index_values)
    )

    return concatenated_str.rstrip("_")


def _average_beads(group: pd.DataFrame) -> pd.Series:
    """
    Averages the beads in the list by first aligning them to the center of the image and then averaging them.
    """
    dtype = {bead.dtype for bead in group.beads}
    if len(dtype) > 1:
        raise ValueError("All beads must have the same dtype.")
    aligned_beads = [
        ndimage.shift(row.beads, _find_bead_shifts(row.beads), mode="nearest", order=1)
        for row in group.itertuples()
        if row.considered_valid
    ]
    if not aligned_beads:
        mm.logger.warning("No valid beads to average.")
        return pd.Series({"average_bead": np.nan})
    if len(aligned_beads) < 2:
        mm.logger.warning("Less than 2 beads to average.")
    mm.logger.info(f"Averaging {len(aligned_beads)} beads")

    return pd.Series(
        {
            "average_bead": np.mean(aligned_beads, axis=0).astype(dtype.pop()),
        }
    )


def _find_bead_shifts(data1, data2=None):
    """Cross-correlates two 2D or 3D arrays and returns the shifts.
    If a second array is not provided, a Gaussian is used as a reference."""
    if data2 is None:
        data2 = np.zeros_like(data1)
        slices = []
        for dim in data2.shape:
            if dim % 2 == 0:
                slices.append(slice(dim // 2))
            else:
                slices.append(slice(dim // 2, dim // 2 + 1))
        data2[tuple(slices)] = 1
        data2 = gaussian(data2, sigma=1, preserve_range=True)

    if data1.ndim != data2.ndim:
        raise ValueError("Data1 and Data2 must have the same number of dimensions.")

    corr_arr = signal.correlate(data1, data2, mode="same")

    profiles = []
    max_pos = np.unravel_index(np.argmax(corr_arr), corr_arr.shape)
    for dim in range(corr_arr.ndim):
        pos_slices = [slice(pos, pos + 1) for pos in max_pos]
        pos_slices[dim] = slice(None)
        profiles.append(np.squeeze(corr_arr[tuple(pos_slices)]))

    return tuple(
        mm_tools.fit_gaussian(profile)[3][2] - profile.shape[0] // 2 for profile in profiles
    )


def _estimate_threshold(image, tolerance=2):
    """
    This function is finding a range of thresholds for which there is not much
    difference in the number of peaks found.
    """
    threshold_range = np.linspace(0.0, 1.0, 11)
    peak_counts = []

    for threshold in threshold_range:
        peak_counts.append(len(peak_local_max(image=image, threshold_abs=threshold)))

    peak_counts_diff = np.abs(np.diff(peak_counts))
    peak_counts_mask = peak_counts_diff <= tolerance

    plateau_length = 0
    plateau_start = None
    current_length = 0
    current_start = None

    for i, is_plateau in enumerate(peak_counts_mask):
        if is_plateau:
            if current_length == 0:
                current_start = i
            current_length += 1
        else:
            if current_length >= plateau_length:
                plateau_length = current_length
                plateau_start = current_start
            current_length = 0

    # Final check inc ase the plateau extends to the end
    if current_length > plateau_length:
        plateau_length = current_length
        plateau_start = current_start

    if plateau_start is None:
        return None  # No threshold found

    # We return the threshold that best matches the higher end of the plateau
    return threshold_range[plateau_start + int(plateau_length * 0.8)]


def _calculate_bead_intensity_outliers(
    bead_properties: pd.DataFrame, robust_z_score_threshold: float
) -> None:
    bead_properties["max_intensity_robust_z_score"] = pd.Series(dtype="float")
    bead_properties["std_intensity_robust_z_score"] = pd.Series(dtype="float")
    bead_properties["considered_intensity_outlier"] = pd.Series(dtype="bool")

    if len(bead_properties[bead_properties.considered_valid]) == 1:
        bead_properties["max_intensity_robust_z_score"] = 0
        bead_properties["std_intensity_robust_z_score"] = 0
        bead_properties["considered_intensity_outlier"] = False
    else:
        max_int_mean = bead_properties[bead_properties.considered_valid]["intensity_max"].mean()
        max_int_median = bead_properties[bead_properties.considered_valid]["intensity_max"].median()
        max_int_mad = (
            (bead_properties[bead_properties.considered_valid]["intensity_max"] - max_int_mean)
            .abs()
            .mean()
        )

        std_int_mean = bead_properties[bead_properties.considered_valid]["intensity_std"].mean()
        std_int_median = bead_properties[bead_properties.considered_valid]["intensity_std"].median()
        std_int_mad = (
            (bead_properties[bead_properties.considered_valid]["intensity_std"] - std_int_mean)
            .abs()
            .mean()
        )

        bead_properties["max_intensity_robust_z_score"] = (
            0.6745 * (bead_properties["intensity_max"] - max_int_median) / max_int_mad
        )
        bead_properties["std_intensity_robust_z_score"] = (
            0.6745 * (bead_properties["intensity_std"] - std_int_median) / std_int_mad
        )

        if 1 < len(bead_properties[bead_properties.considered_valid]) < 6:
            bead_properties["considered_intensity_outlier"] = False
        else:
            bead_properties["considered_intensity_outlier"] = (
                # abs(bead_positions["max_intensity_robust_z_score"]) > robust_z_score_threshold
                abs(bead_properties["std_intensity_robust_z_score"])
                > robust_z_score_threshold
            )

    bead_properties["considered_intensity_outlier"] = bead_properties[
        "considered_intensity_outlier"
    ].astype(bool)


def _generate_key_measurements(bead_properties, average_bead_properties):
    measurement_aggregation_columns = [
        "channel_name",
        "channel_nr",
        "intensity_max",
        "intensity_min",
        "intensity_std",
        "fit_r2_z",
        "fit_r2_y",
        "fit_r2_x",
        "fwhm_pixel_z",
        "fwhm_pixel_y",
        "fwhm_pixel_x",
        "fwhm_lateral_asymmetry_ratio",
        "fwhm_micron_z",
        "fwhm_micron_y",
        "fwhm_micron_x",
    ]
    count_aggregation_columns = [
        "channel_name",
        "channel_nr",
        "total_bead",
        "considered_valid",
        "considered_self_proximity",
        "considered_lateral_edge",
        "considered_axial_edge",
        "considered_intensity_outlier",
        "considered_bad_fit_z",
        "considered_bad_fit_y",
        "considered_bad_fit_x",
    ]

    reindex_bead_properties_df = bead_properties.reset_index()

    # Add a all True column to count the total number of beads
    reindex_bead_properties_df["total_bead"] = True

    # We aggregate counts for each channel on beads according to their status
    channel_counts = (
        reindex_bead_properties_df[count_aggregation_columns]
        .groupby(["channel_nr", "channel_name"])
        .agg(["sum"])
    )
    channel_counts.columns = [
        "_".join((col[0], "count")).strip() for col in channel_counts.columns.values
    ]

    # We aggregate measurements for each channel only on beads considered valid
    valid_bead_properties_df = reindex_bead_properties_df[
        reindex_bead_properties_df.considered_valid
    ]
    channel_measurements = (
        valid_bead_properties_df[measurement_aggregation_columns]
        .groupby(["channel_nr", "channel_name"])
        .agg(["mean", "median", "std"])
    )
    channel_measurements.columns = [
        "_".join(col).strip() for col in channel_measurements.columns.values
    ]

    average_bead_properties = average_bead_properties.add_prefix("average_bead_")

    key_measurements = pd.concat(
        [channel_counts, channel_measurements, average_bead_properties], axis=1
    )
    key_measurements.reset_index(inplace=True)

    return key_measurements


def _process_bead(bead: np.ndarray, voxel_size_micron: tuple[float, float, float]):
    if not isinstance(bead, np.ndarray) and np.isnan(bead):
        return {
            "z_raw": np.nan,
            "z_fitted": np.nan,
            "y_raw": np.nan,
            "y_fitted": np.nan,
            "x_raw": np.nan,
            "x_fitted": np.nan,
            "fit_r2_z": np.nan,
            "fit_r2_y": np.nan,
            "fit_r2_x": np.nan,
            "fwhm_pixel_z": np.nan,
            "fwhm_pixel_y": np.nan,
            "fwhm_pixel_x": np.nan,
            "fwhm_micron_z": np.nan,
            "fwhm_micron_y": np.nan,
            "fwhm_micron_x": np.nan,
            "fwhm_lateral_asymmetry_ratio": np.nan,
            "considered_axial_edge": np.nan,
            "intensity_integrated": np.nan,
            "intensity_max": np.nan,
            "intensity_min": np.nan,
            "intensity_std": np.nan,
        }
    # TODO: This can be shortened
    # Find the strongest sections to generate profiles
    z_max = np.max(bead, axis=(1, 2))
    z_focus = np.argmax(z_max)
    y_max = np.max(bead, axis=(0, 2))
    y_focus = np.argmax(y_max)
    x_max = np.max(bead, axis=(0, 1))
    x_focus = np.argmax(x_max)

    # Generate profiles
    profile_z_raw = np.squeeze(bead[:, y_focus, x_focus])
    profile_y_raw = np.squeeze(bead[z_focus, :, x_focus])
    profile_x_raw = np.squeeze(bead[z_focus, y_focus, :])

    # Normalize the profiles and subtract the background
    profile_z_raw = (profile_z_raw - profile_z_raw.min()) / (
        profile_z_raw.max() - profile_z_raw.min()
    )
    profile_y_raw = (profile_y_raw - profile_y_raw.min()) / (
        profile_y_raw.max() - profile_y_raw.min()
    )
    profile_x_raw = (profile_x_raw - profile_x_raw.min()) / (
        profile_x_raw.max() - profile_x_raw.min()
    )

    # Fitting the profiles
    profile_z_fitted, r2_z, fwhm_z, (center_pos_z, _) = mm_tools.fit_airy(profile_z_raw)
    profile_y_fitted, r2_y, fwhm_y, (center_pos_y, _) = mm_tools.fit_airy(profile_y_raw)
    profile_x_fitted, r2_x, fwhm_x, (center_pos_x, _) = mm_tools.fit_airy(profile_x_raw)

    fwhm_lateral_asymmetry_ratio = max(fwhm_y, fwhm_x) / min(fwhm_y, fwhm_x)

    if all(voxel_size_micron):
        fwhm_micron_z = fwhm_z * voxel_size_micron[0]
        fwhm_micron_y = fwhm_y * voxel_size_micron[1]
        fwhm_micron_x = fwhm_x * voxel_size_micron[2]
    else:
        fwhm_micron_z = np.nan
        fwhm_micron_y = np.nan
        fwhm_micron_x = np.nan

    considered_axial_edge = (
        # TODO: review the tolerance values for considering beads at axial edge
        # a 2.5x FWHM tolerance is used and that is arbitrary and rather low
        center_pos_z < fwhm_z * 2.5
        or profile_z_raw.shape[0] - center_pos_z < fwhm_z * 2.5
    )

    intensity_max = bead.max()
    intensity_min = bead.min()
    intensity_std = bead.std()
    intensity_integrated = (bead - intensity_min).sum()

    return {
        "z_raw": profile_z_raw,
        "z_fitted": profile_z_fitted,
        "y_raw": profile_y_raw,
        "y_fitted": profile_y_fitted,
        "x_raw": profile_x_raw,
        "x_fitted": profile_x_fitted,
        "fit_r2_z": r2_z,
        "fit_r2_y": r2_y,
        "fit_r2_x": r2_x,
        "fwhm_pixel_z": fwhm_z,
        "fwhm_pixel_y": fwhm_y,
        "fwhm_pixel_x": fwhm_x,
        "fwhm_micron_z": fwhm_micron_z,
        "fwhm_micron_y": fwhm_micron_y,
        "fwhm_micron_x": fwhm_micron_x,
        "fwhm_lateral_asymmetry_ratio": fwhm_lateral_asymmetry_ratio,
        "considered_axial_edge": considered_axial_edge,
        "intensity_integrated": intensity_integrated,
        "intensity_max": intensity_max,
        "intensity_min": intensity_min,
        "intensity_std": intensity_std,
    }


def _find_beads(
    channel: np.ndarray,
    sigma: tuple[float, float, float],
    min_distance: float,
    do_noisy: bool = True,
):
    """
    This function finds the beads in a channel by applying a Gaussian filter and then finding the local maxima.
    """
    mm.logger.debug("Finding beads in channel...")

    if all(sigma):
        mm.logger.debug(f"Gaussian filter applied with sigma {sigma}")
        channel_gauss = gaussian(image=channel, sigma=sigma)
    else:
        mm.logger.debug("No Gaussian filter applied")
        channel_gauss = channel

    # We find the beads in the MIP for performance and to avoid anisotropy issues in the axial direction
    channel_gauss_mip = np.max(channel_gauss, axis=0)

    # We rescale the image intensities to work with relative thresholds
    channel_gauss_mip = rescale_intensity(channel_gauss_mip, out_range=np.float32)

    # Estimate a relative threshold for the peak_local_max function
    if do_noisy:
        threshold = _estimate_threshold(channel_gauss_mip)
        if threshold is None:
            mm.logger.error("No optimal noisy beads threshold found for the channel.")
            threshold = 0.6
    else:
        threshold = 0.3

    # We assume that reaching a maximum number of beads is a sign of a bad thresholding
    # and noise in the image. We report this as an error.
    max_num_peaks = MAX_NR_PEAKS

    # Find bead centers
    positions_all = peak_local_max(
        image=channel_gauss_mip,
        threshold_abs=threshold,
        num_peaks=max_num_peaks,
    )
    if len(positions_all) == max_num_peaks:
        mm.logger.warning(f"Reached the maximum number of peaks ({max_num_peaks}) in the image. ")
        if not do_noisy:  # We did not do noisy this time
            mm.logger.info("Trying noisy beads detected.")
            return _find_beads(channel, sigma, min_distance, do_noisy=True)
        else:
            mm.logger.error("Too many beads detected. The image is probably too noisy.")
            raise mm.AnalysisError("Too many beads detected. The image is probably too noisy.")

    positions_all_not_proximity_not_edge = peak_local_max(
        image=channel_gauss_mip,
        threshold_abs=threshold,
        min_distance=int(min_distance),
        exclude_border=(int(1 + min_distance // 2), int(1 + min_distance // 2)),
        num_peaks=max_num_peaks,
        p_norm=2,
    )
    positions_all_not_proximity = peak_local_max(
        image=channel_gauss_mip,
        threshold_abs=threshold,
        min_distance=int(min_distance),
        exclude_border=False,
        num_peaks=max_num_peaks,
        p_norm=2,
    )

    # We convert the arrays into sets to perform easier to follow filtering logic
    positions_all = set(map(tuple, positions_all))
    positions_all_not_proximity_not_edge = set(map(tuple, positions_all_not_proximity_not_edge))
    positions_all_not_proximity = set(map(tuple, positions_all_not_proximity))

    # positions_proximity_edge = positions_all - positions_all_not_proximity_not_edge
    positions_edge = positions_all_not_proximity - positions_all_not_proximity_not_edge
    positions_proximity = positions_all - positions_all_not_proximity

    positions_df = pd.DataFrame(
        positions_all,
        columns=["center_y", "center_x"],
        index=pd.Index(range(len(positions_all)), name="bead_id"),
    )
    positions_df["center_z"] = positions_df.apply(
        lambda row: int(channel_gauss[:, row["center_y"], row["center_x"]].argmax()),
        axis=1,
    )

    positions_df["considered_valid"] = positions_df.apply(
        lambda row: (row["center_y"], row["center_x"]) in positions_all_not_proximity_not_edge,
        axis=1,
    )
    positions_df["considered_self_proximity"] = positions_df.apply(
        lambda row: (row["center_y"], row["center_x"]) in positions_proximity, axis=1
    )
    positions_df["considered_lateral_edge"] = positions_df.apply(
        lambda row: (row["center_y"], row["center_x"]) in positions_edge, axis=1
    )

    mm.logger.debug(f"Beads found: {len(positions_all)}")
    mm.logger.debug(f"Beads kept for further analysis: {positions_df['considered_valid'].sum()}")
    mm.logger.debug(
        f"Beads considered for being to close to the edge: {positions_df['considered_lateral_edge'].sum()}"
    )
    mm.logger.debug(
        f"Beads considered for being to close to each other: {positions_df['considered_self_proximity'].sum()}"
    )

    def get_bead_image(row, channel, min_distance):
        return channel[
            :,
            max(0, (row["center_y"] - int(min_distance // 2))) : min(
                channel.shape[1], (row["center_y"] + int(min_distance // 2) + 1)
            ),
            max(0, (row["center_x"] - int(min_distance // 2))) : min(
                channel.shape[2], (row["center_x"] + int(min_distance // 2) + 1)
            ),
        ]

    positions_df["beads"] = positions_df.apply(get_bead_image, axis=1, args=(channel, min_distance))

    return positions_df


def _process_channel(
    channel: np.ndarray,
    sigma: tuple[float, float, float],
    min_bead_distance: float,
    snr_threshold: float,
    fitting_r2_threshold: float,
    intensity_robust_z_score_threshold: float,
    voxel_size_micron: tuple[float, float, float],
) -> pd.DataFrame:
    bead_properties = _find_beads(
        channel=channel,
        sigma=sigma,
        min_distance=min_bead_distance,
    )

    bead_properties = bead_properties.assign(
        considered_intensity_outlier=pd.Series(dtype=bool),
    )

    bead_properties = bead_properties.join(
        bead_properties["beads"].apply(lambda x: pd.Series(_process_bead(x, voxel_size_micron)))
    )
    bead_properties["considered_bad_fit_z"] = bead_properties["fit_r2_z"] < fitting_r2_threshold
    bead_properties["considered_bad_fit_y"] = bead_properties["fit_r2_y"] < fitting_r2_threshold
    bead_properties["considered_bad_fit_x"] = bead_properties["fit_r2_x"] < fitting_r2_threshold

    _calculate_bead_intensity_outliers(
        bead_properties, robust_z_score_threshold=intensity_robust_z_score_threshold
    )

    # We need to invalidate all the bad fits and outliers
    bead_properties["considered_valid"] = bead_properties.apply(
        lambda row: not any(
            [
                row["considered_lateral_edge"],
                row["considered_axial_edge"],
                row["considered_bad_fit_z"],
                row["considered_bad_fit_y"],
                row["considered_bad_fit_x"],
                row["considered_intensity_outlier"],
            ]
        ),
        axis=1,
    )

    return bead_properties


def _process_image(
    image: mm_schema.Image,
    sigma: tuple[float, float, float],
    min_bead_distance: float,
    snr_threshold: float,
    fitting_r2_threshold: float,
    intensity_robust_z_score_threshold: float,
) -> tuple:
    channel_names = [c.name for c in image.channel_series.channels]
    voxel_size_micron = (
        image.voxel_size_z_micron,
        image.voxel_size_y_micron,
        image.voxel_size_x_micron,
    )

    # Get image data and remove the time dimension
    image = image.array_data[0, ...]

    # Some images (e.g. OMX-3D-SIM) may contain negative values.
    image = np.clip(image, a_min=0, a_max=None)

    nr_channels = image.shape[-1]

    bead_properties = []

    for ch in range(nr_channels):
        ch_bead_positions = _process_channel(
            channel=image[..., ch],
            sigma=sigma,
            min_bead_distance=min_bead_distance,
            snr_threshold=snr_threshold,
            fitting_r2_threshold=fitting_r2_threshold,
            intensity_robust_z_score_threshold=intensity_robust_z_score_threshold,
            voxel_size_micron=voxel_size_micron,
        )

        _add_row_index_level(ch_bead_positions, "channel_nr", ch)
        _add_row_index_level(ch_bead_positions, "channel_name", channel_names[ch])
        bead_properties.append(ch_bead_positions)

    return pd.concat(bead_properties)


def _estimate_min_bead_distance(dataset: mm_schema.PSFBeadsDataset) -> float:
    # TODO: get the resolution somewhere or pass it as a metadata
    return dataset.input_parameters.min_lateral_distance_factor


def _generate_center_roi(
    dataset: mm_schema.PSFBeadsDataset,
    positions,
    root_name,
    color,
    stroke_width=1,
):
    rois = []

    for image in dataset.input_data.psf_beads_images:
        image_id = mm.analyses.get_object_id(image) or image.name
        if positions.empty or image_id not in positions.index.get_level_values("image_id"):
            continue
        points = []
        for index, row in positions.xs(image_id, level="image_id").iterrows():
            points.append(
                mm_schema.Point(
                    name=index[positions.index.names[1:].index("bead_id")],
                    z=row["center_z"],
                    y=row["center_y"] + 0.5,  # Rois are centered on the voxel
                    x=row["center_x"] + 0.5,
                    c=index[positions.index.names[1:].index("channel_nr")],
                    stroke_color=mm_schema.Color(
                        r=color[0], g=color[1], b=color[2], alpha=color[3]
                    ),
                    stroke_width=stroke_width,
                )
            )

        if points:
            rois.append(
                mm_schema.Roi(
                    name=f"{root_name}_{image_id}",
                    description=f"{root_name} in image {image_id}",
                    linked_references=image.data_reference,
                    points=points,
                )
            )

    return rois


def _extract_profiles(bead_properties, axis: str) -> pd.DataFrame:
    profile_col_names = [
        f"{axis}_raw",
        f"{axis}_fitted",
    ]
    column_indexes = [i for i in bead_properties.index.names if i != "channel_name"]

    profiles = {}
    for index, row in bead_properties.iterrows():
        if isinstance(index, (list, tuple)):
            index = [index[bead_properties.index.names.index(col_i)] for col_i in column_indexes]

            index_str = "_".join([str(i) for i in index])
        else:
            index_str = str(index)
        for profile_name in profile_col_names:
            profiles[f"{index_str}_{profile_name}"] = pd.Series(row[profile_name])

    bead_properties.drop(columns=profile_col_names, inplace=True)

    return pd.DataFrame(profiles)


def analyse_psf_beads(dataset: mm_schema.PSFBeadsDataset) -> bool:
    mm.analyses.validate_requirements()
    # TODO: Implement Nyquist validation??

    # Containers for input data and input parameters
    images = {}
    voxel_sizes_micron = {}
    min_bead_distance = _estimate_min_bead_distance(dataset)
    snr_threshold = dataset.input_parameters.snr_threshold
    fitting_r2_threshold = dataset.input_parameters.fitting_r2_threshold

    # Containers for output data
    saturated_channels = {}
    bead_properties = []

    # First loop to prepare data and do checks
    images_shape = None
    for image in dataset.input_data.psf_beads_images:
        image_id = mm.analyses.get_object_id(image) or image.name
        images[image_id] = image.array_data[0, ...]

        saturated_channels[image_id] = []

        # Check image shape
        mm.logger.info(f"Checking image {image_id} shape...")
        if len(image.array_data.shape) != 5:
            mm.logger.error(f"Image {image_id} must be 5D")
            return False
        if image.array_data.shape[0] != 1:
            mm.logger.warning(
                f"Image {image_id} must be in TZYXC order and single time-point. Using first time-point."
            )

        # Check all shapes equal
        if images_shape is None:
            images_shape = image.array_data.shape
        elif images_shape != image.array_data.shape:
            mm.logger.error("Not all images have the same dimensions")
            return False

        # Check image saturation
        mm.logger.info(f"Checking image {image_id} saturation...")
        for c in range(image.array_data.shape[-1]):
            if mm_tools.is_saturated(
                channel=image.array_data[..., c],
                threshold=dataset.input_parameters.saturation_threshold,
                detector_bit_depth=dataset.input_parameters.bit_depth,
            ):
                mm.logger.error(f"Image {image_id}: channel {c} is saturated")
                saturated_channels[image_id].append(c)

    if any(len(saturated_channels[name]) for name in saturated_channels):
        mm.logger.error(f"Channels {saturated_channels} are saturated")
        raise mm.SaturationError(f"Channels {saturated_channels} are saturated")

    # Second loop main image analysis
    for image in dataset.input_data.psf_beads_images:
        image_id = mm.analyses.get_object_id(image) or image.name
        mm.logger.info(f"Processing image {image_id}...")
        voxel_sizes_micron[image_id] = (
            image.voxel_size_z_micron,
            image.voxel_size_y_micron,
            image.voxel_size_x_micron,
        )

        image_bead_properties = _process_image(
            image=image,
            sigma=(
                dataset.input_parameters.sigma_z,
                dataset.input_parameters.sigma_y,
                dataset.input_parameters.sigma_x,
            ),
            min_bead_distance=min_bead_distance,
            snr_threshold=snr_threshold,
            fitting_r2_threshold=fitting_r2_threshold,
            intensity_robust_z_score_threshold=dataset.input_parameters.intensity_robust_z_score_threshold,
        )

        mm.logger.info(
            f"Image {image_id} processed."
            f"    {image_bead_properties.considered_valid.sum()} beads considered valid."
            f"    {image_bead_properties.considered_lateral_edge.sum()} beads considered lateral edge."
            f"    {image_bead_properties.considered_self_proximity.sum()} beads considered self proximity."
            f"    {image_bead_properties.considered_axial_edge.sum()} beads considered axial edge."
            f"    {image_bead_properties.considered_intensity_outlier.sum()} beads considered intensity outlier."
            f"    {image_bead_properties.considered_bad_fit_z.sum()} beads considered bad fit in z."
            f"    {image_bead_properties.considered_bad_fit_y.sum()} beads considered bad fit in y."
            f"    {image_bead_properties.considered_bad_fit_x.sum()} beads considered bad fit in x."
        )

        _add_row_index_level(image_bead_properties, "image_id", image_id)
        bead_properties.append(image_bead_properties)

    bead_properties = pd.concat(bead_properties)

    # Before averaging any bead we need to verify that all voxel sizes are equal
    if len(set(voxel_sizes_micron.values())) == 1:
        average_beads_properties = bead_properties.groupby(["channel_nr", "channel_name"]).apply(
            _average_beads
        )
        average_beads_properties = average_beads_properties.join(
            average_beads_properties["average_bead"].apply(
                lambda x: pd.Series(_process_bead(x, voxel_sizes_micron[image_id]))
            )
        )
        average_beads_properties.drop(columns=["considered_axial_edge"], inplace=True)
    else:
        mm.logger.error(
            "Voxel sizes are not equal among images. Skipping average bead calculation."
        )
        average_beads_properties = None

    bead_profiles_z = _extract_profiles(bead_properties, "z")
    bead_profiles_y = _extract_profiles(bead_properties, "y")
    bead_profiles_x = _extract_profiles(bead_properties, "x")

    bead_profiles_z = bead_profiles_z.join(_extract_profiles(average_beads_properties, "z"))
    bead_profiles_y = bead_profiles_y.join(_extract_profiles(average_beads_properties, "y"))
    bead_profiles_x = bead_profiles_x.join(_extract_profiles(average_beads_properties, "x"))

    # TODO: get more metadata from the source images
    if any(isinstance(c, np.ndarray) for c in average_beads_properties["average_bead"]):
        average_bead = mm.analyses.numpy_to_mm_image(
            array=np.expand_dims(
                np.stack(
                    [
                        c
                        for c in average_beads_properties["average_bead"]
                        if isinstance(c, np.ndarray)
                    ],
                    axis=-1,
                ),
                axis=0,
            ),
            name="average_bead",
            description="Average bead image extracted from all the beads considered valid in the dataset.",
            source_images=dataset.input_data.psf_beads_images,
            channel_names=[
                i[average_beads_properties.index.names.index("channel_name")]
                for i in average_beads_properties.index
                if isinstance(average_beads_properties.at[i, "average_bead"], np.ndarray)
            ],
        )
    else:
        average_bead = None
    average_beads_properties.drop("average_bead", axis=1, inplace=True)
    bead_properties.drop("beads", axis=1, inplace=True)

    key_measurements = _generate_key_measurements(
        bead_properties=bead_properties,
        average_bead_properties=average_beads_properties,
    )

    key_measurements = mm_schema.PSFBeadsKeyMeasurements(
        name="psf_beads_key_measurements",
        description="Averaged key measurements for all beads considered valid in the dataset.",
        table_data=key_measurements,
        **key_measurements.to_dict("list"),
    )

    considered_valid_bead_centers = _generate_center_roi(
        dataset=dataset,
        positions=bead_properties[bead_properties.considered_valid],
        root_name="considered_valid_bead_centers",
        color=(0, 255, 0, 100),
        stroke_width=8,
    )
    considered_lateral_edge_bead_centers = _generate_center_roi(
        dataset=dataset,
        positions=bead_properties[bead_properties.considered_lateral_edge],
        root_name="considered_lateral_edge_bead_centers",
        color=(255, 0, 0, 100),
        stroke_width=4,
    )
    considered_self_proximity_bead_centers = _generate_center_roi(
        dataset=dataset,
        positions=bead_properties[bead_properties.considered_self_proximity],
        root_name="considered_self_proximity_bead_centers",
        color=(255, 0, 0, 100),
        stroke_width=4,
    )
    considered_axial_edge_bead_centers = _generate_center_roi(
        dataset=dataset,
        positions=bead_properties[bead_properties.considered_axial_edge],
        root_name="considered_axial_edge_bead_centers",
        color=(0, 0, 255, 100),
        stroke_width=4,
    )
    considered_intensity_outlier_bead_centers = _generate_center_roi(
        dataset=dataset,
        positions=bead_properties[bead_properties.considered_intensity_outlier],
        root_name="considered_intensity_outlier_bead_centers",
        color=(0, 0, 255, 100),
        stroke_width=4,
    )
    considered_bad_fit_z_bead_centers = _generate_center_roi(
        dataset=dataset,
        positions=bead_properties[bead_properties.considered_bad_fit_z],
        root_name="considered_bad_fit_z_bead_centers",
        color=(0, 0, 255, 100),
        stroke_width=4,
    )
    considered_bad_fit_y_bead_centers = _generate_center_roi(
        dataset=dataset,
        positions=bead_properties[bead_properties.considered_bad_fit_y],
        root_name="considered_bad_fit_y_bead_centers",
        color=(0, 0, 255, 100),
        stroke_width=4,
    )
    considered_bad_fit_x_bead_centers = _generate_center_roi(
        dataset=dataset,
        positions=bead_properties[bead_properties.considered_bad_fit_x],
        root_name="considered_bad_fit_x_bead_centers",
        color=(0, 0, 255, 100),
        stroke_width=4,
    )

    bead_properties = mm.analyses.df_to_table(bead_properties.reset_index(), "bead_properties")
    bead_profiles_z = mm.analyses.df_to_table(bead_profiles_z, "bead_profiles_z")
    bead_profiles_y = mm.analyses.df_to_table(bead_profiles_y, "bead_profiles_y")
    bead_profiles_x = mm.analyses.df_to_table(bead_profiles_x, "bead_profiles_x")

    dataset.output = mm_schema.PSFBeadsOutput(
        processing_application="microscopemetrics",
        processing_version=mm.__version__,
        processing_datetime=datetime.now(),
        analyzed_bead_centers=considered_valid_bead_centers,
        considered_bead_centers_lateral_edge=considered_lateral_edge_bead_centers,
        considered_bead_centers_self_proximity=considered_self_proximity_bead_centers,
        considered_bead_centers_axial_edge=considered_axial_edge_bead_centers,
        considered_bead_centers_intensity_outlier=considered_intensity_outlier_bead_centers,
        considered_bead_centers_z_fit_quality=considered_bad_fit_z_bead_centers,
        considered_bead_centers_y_fit_quality=considered_bad_fit_y_bead_centers,
        considered_bead_centers_x_fit_quality=considered_bad_fit_x_bead_centers,
        key_measurements=key_measurements,
        bead_properties=bead_properties,
        bead_profiles_z=bead_profiles_z,
        bead_profiles_y=bead_profiles_y,
        bead_profiles_x=bead_profiles_x,
        average_bead=average_bead,
    )

    dataset.processed = True

    return True


# Calculate 2D FFT
# slice_2d = raw_img[17, ...].reshape([1, n_channels, x_size, y_size])
# fft_2D = fft_2d(slice_2d)

# Calculate 3D FFT
# fft_3D = fft_3d(spots_image)
#
# plt.imshow(np.log(fft_3D[2, :, :, 1]))  # , cmap='hot')
# # plt.imshow(np.log(fft_3D[2, 23, :, :]))  # , cmap='hot')
# plt.show()
#
