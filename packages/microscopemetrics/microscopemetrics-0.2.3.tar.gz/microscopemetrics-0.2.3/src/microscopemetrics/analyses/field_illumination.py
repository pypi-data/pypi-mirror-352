from datetime import datetime
from math import hypot
from typing import Dict, Tuple

import microscopemetrics_schema.datamodel as mm_schema
import numpy as np
import pandas as pd
import scipy
from skimage.exposure import rescale_intensity
from skimage.filters import gaussian
from skimage.measure import regionprops

import microscopemetrics as mm
from microscopemetrics.analyses import tools as mm_tools


def _get_center_region_mask(channel: np.ndarray, fraction: float = 0.1) -> np.ndarray:
    """
    Compute the mask of the center region of a channel
    Parameters
    ----------
    channel : np.array.
        image on a 2d np.ndarray format.
    Returns
    -------
    center_region_mask : np.ndarray
        2d bool np.ndarray representing the center region of the chosen channel.
    """
    channel = rescale_intensity(channel, in_range=(0, channel.max()), out_range=(0.0, 1.0))
    mask = channel > (1 - fraction)
    return mask


def _channel_line_profile(
    channel: np.ndarray, start: Tuple[int, int], end: Tuple[int, int], profile_size: int
) -> np.ndarray:
    """
    Compute the intensity profile along a line between x0-y0 and x1-y1 using cubic interpolation. The mode used is
    'nearest' to avoid edge artifacts.
    Parameters
    ----------
    channel : np.array.
        image on a 2d np.ndarray format.
    start : (int, int)
        coordinates of the starting pixel
    end : (int, int)
        coordinates of the ending pixel
    Returns
    -------
    line_pixel_values : np.ndarray
        1d np.ndarray representing the values of the chosen line of pixels.
    """
    x, y = np.linspace(start[0], end[0], profile_size), np.linspace(start[1], end[1], profile_size)

    return scipy.ndimage.map_coordinates(
        input=channel,
        coordinates=np.vstack((x, y)),
        mode="nearest",
    )


def _image_line_profile(image: np.ndarray, profile_size: int) -> Dict[str, list]:
    """
    Compute the intensity profile along a line between x0-y0 and x1-y1
    Parameters
    ----------
    image : np.ndarray.
        image on a 5d np.ndarray format tzyxc.
    profile_size : int
        size of the intensity profile.
    Returns
    -------
    line_pixel_values : dict
        dictionary representing the values of the chosen line of pixels for each channel.
    """
    profile_coordinates = {
        "leftTop_to_rightBottom": ((0, 0), (image.shape[-2], image.shape[-3])),
        "leftBottom_to_rightTop": ((0, image.shape[-3]), (image.shape[-2], 0)),
        "center_horizontal": (
            (0, image.shape[-3] // 2),
            (image.shape[-2], image.shape[-3] // 2),
        ),
        "center_vertical": (
            (image.shape[-2] // 2, 0),
            (image.shape[-2] // 2, image.shape[-3]),
        ),
    }
    output = {}
    for profile_name, (start, end) in profile_coordinates.items():
        profiles = np.zeros((image.shape[-1], 255))
        for c in range(image.shape[-1]):
            profiles[c, :] = _channel_line_profile(
                np.squeeze(image[0, 0, :, :, c]), start, end, profile_size
            )
        output = output | {
            f"ch{c:02}_{profile_name}": profiles[c].tolist() for c in range(image.shape[-1])
        }

    return output


def _line_profile_shapes(image: np.ndarray):
    stroke_color = {"r": 0, "g": 0, "b": 255, "alpha": 200}
    return [
        mm_schema.Line(
            name="leftTop_to_rightBottom",
            x1=0,
            y1=0,
            x2=image.shape[-2],
            y2=image.shape[-3],
            stroke_color=stroke_color,
        ),
        mm_schema.Line(
            name="leftBottom_to_rightTop",
            x1=0,
            y1=image.shape[-3],
            x2=image.shape[-2],
            y2=0,
            stroke_color=stroke_color,
        ),
        mm_schema.Line(
            name="center_horizontal",
            x1=0,
            y1=image.shape[-3] // 2,
            x2=image.shape[-2],
            y2=image.shape[-3] // 2,
            stroke_color=stroke_color,
        ),
        mm_schema.Line(
            name="center_vertical",
            x1=image.shape[-2] // 2,
            y1=0,
            x2=image.shape[-2] // 2,
            y2=image.shape[-3],
            stroke_color=stroke_color,
        ),
    ]


def _c_shape(name, x, y, size, s_col):
    return mm_schema.Rectangle(name=name, x=x, y=y, w=size, h=size, stroke_color=s_col)


def _corner_shapes(image: np.ndarray, corner_fraction: float):
    cfp = int(corner_fraction * (image.shape[-3] + image.shape[-2]) / 2)
    cr_y = int((image.shape[-3] - cfp) / 2)
    cr_x = int((image.shape[-2] - cfp) / 2)
    stroke_color = {"r": 0, "g": 255, "b": 0, "alpha": 200}

    return [
        _c_shape("top_left", x=0, y=0, size=cfp, s_col=stroke_color),
        _c_shape("top_center", x=cr_x, y=0, size=cfp, s_col=stroke_color),
        _c_shape("top_right", x=image.shape[-2] - cfp, y=0, size=cfp, s_col=stroke_color),
        _c_shape("middle_left", x=0, y=cr_y, size=cfp, s_col=stroke_color),
        _c_shape("middle_center", x=cr_x, y=cr_y, size=cfp, s_col=stroke_color),
        _c_shape(
            "middle_right",
            x=image.shape[-2] - cfp,
            y=cr_y,
            size=cfp,
            s_col=stroke_color,
        ),
        _c_shape("bottom_left", x=0, y=image.shape[-3] - cfp, size=cfp, s_col=stroke_color),
        _c_shape(
            "bottom_center",
            x=cr_x,
            y=image.shape[-3] - cfp,
            size=cfp,
            s_col=stroke_color,
        ),
        _c_shape(
            "bottom_right",
            y=image.shape[-3] - cfp,
            x=image.shape[-2] - cfp,
            size=cfp,
            s_col=stroke_color,
        ),
    ]


def _channel_max_intensity_properties(
    channel: np.ndarray,
    sigma: float,
) -> dict:
    """
    Compute the maximum intensity properties of a channel
    """
    if sigma is not None:
        proc_channel = gaussian(image=channel, sigma=sigma, preserve_range=True, channel_axis=None)
    else:
        proc_channel = channel

    # When images are very flat, the max intensity region is always detected in the center. We need to stretch the
    # intensity of the image to detect the actual center. We loop over a list of number of bins to get a central region
    # that is not too big. We consider 0.25 as the maximum fraction of the image that can be considered as the center.
    center_region_area_fraction = 1
    center_region_intensity_fraction = None
    properties = None
    for n_bins in [11, 21, 51, 101, 201, 501]:
        if center_region_area_fraction < 0.2:
            break
        rescaled_channel = rescale_intensity(
            # We scale in 1 value more than the bins we want to achieve.
            # Like that the top value is not included in the last bin.
            proc_channel.astype(float),
            in_range=(0, proc_channel.max()),
            out_range=(0, n_bins),
        )
        labels_channel = rescaled_channel.astype(int)
        properties = regionprops(labels_channel, proc_channel)
        center_region_area_fraction = properties[-2].area / (channel.shape[0] * channel.shape[1])
        center_region_intensity_fraction = 1 / (n_bins - 1)

    # Fitting the intensity profile to a gaussian
    _, _, _, (_, _, center_fitted_y, _) = mm_tools.fit_gaussian(np.max(channel, axis=1))
    _, _, _, (_, _, center_fitted_x, _) = mm_tools.fit_gaussian(np.max(channel, axis=0))

    return {
        "center_region_intensity_fraction": center_region_intensity_fraction,
        "center_region_area_fraction": center_region_area_fraction,
        "center_of_mass_y": properties[-2].centroid[0],
        "center_of_mass_y_relative": properties[-2].centroid[0] / (channel.shape[0] / 2) - 1,
        "center_of_mass_x": properties[-2].centroid[1],
        "center_of_mass_x_relative": properties[-2].centroid[1] / (channel.shape[1] / 2) - 1,
        "center_of_mass_distance_relative": hypot(
            properties[-2].centroid[0] / (channel.shape[0] / 2) - 1,
            properties[-2].centroid[1] / (channel.shape[1] / 2) - 1,
        ),
        "center_geometric_y": properties[-2].centroid[0],
        "center_geometric_y_relative": properties[-2].centroid[0] / (channel.shape[0] / 2) - 1,
        "center_geometric_x": properties[-2].centroid[1],
        "center_geometric_x_relative": properties[-2].centroid[1] / (channel.shape[1] / 2) - 1,
        "center_geometric_distance_relative": hypot(
            properties[-2].centroid[0] / (channel.shape[0] / 2) - 1,
            properties[-2].centroid[1] / (channel.shape[1] / 2) - 1,
        ),
        "center_fitted_y": center_fitted_y,
        "center_fitted_y_relative": center_fitted_y / (channel.shape[0] / 2) - 1,
        "center_fitted_x": center_fitted_x,
        "center_fitted_x_relative": center_fitted_x / (channel.shape[1] / 2) - 1,
        "center_fitted_distance_relative": hypot(
            center_fitted_y / (channel.shape[0] / 2) - 1,
            center_fitted_x / (channel.shape[1] / 2) - 1,
        ),
        "max_intensity": properties[-2].intensity_max,
        "max_intensity_pos_y": properties[-1].centroid[0],
        "max_intensity_pos_y_relative": properties[-1].centroid[0] / (channel.shape[0] / 2) - 1,
        "max_intensity_pos_x": properties[-1].centroid[1],
        "max_intensity_pos_x_relative": properties[-1].centroid[1] / (channel.shape[1] / 2) - 1,
        "max_intensity_distance_relative": hypot(
            properties[-1].centroid[0] / (channel.shape[0] / 2) - 1,
            properties[-1].centroid[1] / (channel.shape[1] / 2) - 1,
        ),
    }


def _channel_corner_properties(channel: np.ndarray, corner_fraction: float) -> dict:
    max_intensity = np.max(channel)

    # Calculate the corner fraction in pixels (cfp) of the image size
    # to use as the corner size and the center range (cr)
    cfp = int(corner_fraction * (channel.shape[0] + channel.shape[1]) / 2)
    cr_y = int((channel.shape[0] - cfp) / 2)
    cr_x = int((channel.shape[1] - cfp) / 2)

    return {
        "top_left_intensity_mean": np.mean(channel[0:cfp, 0:cfp]),
        "top_left_intensity_ratio": np.mean(channel[0:cfp, 0:cfp]) / max_intensity,
        "top_center_intensity_mean": np.mean(channel[0:cfp, cr_x:-cr_x]),
        "top_center_intensity_ratio": np.mean(channel[0:cfp, cr_x:-cr_x]) / max_intensity,
        "top_right_intensity_mean": np.mean(channel[0:cfp, -cfp:-1]),
        "top_right_intensity_ratio": np.mean(channel[0:cfp, -cfp:-1]) / max_intensity,
        "middle_left_intensity_mean": np.mean(channel[cr_y:-cr_y, 0:cfp]),
        "middle_left_intensity_ratio": np.mean(channel[cr_y:-cr_y, 0:cfp]) / max_intensity,
        "middle_center_intensity_mean": np.mean(channel[cr_y:-cr_y, cr_x:-cr_x]),
        "middle_center_intensity_ratio": np.mean(channel[cr_y:-cr_y, cr_x:-cr_x]) / max_intensity,
        "middle_right_intensity_mean": np.mean(channel[cr_y:-cr_y, -cfp:-1]),
        "middle_right_intensity_ratio": np.mean(channel[cr_y:-cr_y, -cfp:-1]) / max_intensity,
        "bottom_left_intensity_mean": np.mean(channel[-cfp:-1, 0:cfp]),
        "bottom_left_intensity_ratio": np.mean(channel[-cfp:-1, 0:cfp]) / max_intensity,
        "bottom_center_intensity_mean": np.mean(channel[-cfp:-1, cr_x:-cr_x]),
        "bottom_center_intensity_ratio": np.mean(channel[-cfp:-1, cr_x:-cr_x]) / max_intensity,
        "bottom_right_intensity_mean": np.mean(channel[-cfp:-1, -cfp:-1]),
        "bottom_right_intensity_ratio": np.mean(channel[-cfp:-1, -cfp:-1]) / max_intensity,
    }


def _image_properties(images: list[mm_schema.Image], corner_fraction: float, sigma: float):
    """
    given FI input images, this function return intensities for the corner and central regions
    and their ratio over the maximum intensity value of the array.
    Parameters
    ----------
    images : list[mm_schema.Image]
        input images from the field illumination dataset.
    Returns
    -------
    profiles_statistics : pandas.DataFrame
        Dictionary showing the intensity values of the different regions and
        their ratio over the maximum intensity value of the array.
        Dictionary values will be lists in case of multiple channels.
    """
    properties = pd.DataFrame()
    for image in images:
        # For the analysis we are using only the first z and time-point
        image_data = image.array_data[0, 0, :, :, :]

        im_properties = pd.DataFrame()
        for c in range(image_data.shape[-1]):
            ch_properties = pd.DataFrame(
                columns=[
                    "image_name",
                    "image_id",
                    "channel_name",
                    "channel_nr",
                    "channel_id",
                ]
            )
            ch_properties.loc[0] = [
                image.name,
                mm.analyses.get_object_id(image),
                image.channel_series.channels[c].name,
                c,
                mm.analyses.get_object_id(image.channel_series.channels[c]),
            ]
            ch_properties = ch_properties.join(
                pd.DataFrame(
                    _channel_max_intensity_properties(image_data[:, :, c], sigma),
                    index=[0],
                )
            )
            ch_properties = ch_properties.join(
                pd.DataFrame(
                    _channel_corner_properties(image_data[:, :, c], corner_fraction),
                    index=[0],
                )
            )
            im_properties = pd.concat([im_properties, ch_properties], axis=0)

        properties = pd.concat([properties, im_properties], axis=0)

    return properties


def analyse_field_illumination(dataset: mm_schema.FieldIlluminationDataset) -> bool:
    mm.analyses.validate_requirements()

    channel_names = []
    for image in dataset.input_data.field_illumination_images:
        # We want to verify that the input images all have different channel names
        # As it does not make sense to average file illumination between images from the same channel
        if image.channel_series is not None:
            mm.logger.info("Checking duplicate channel names...")
            for channel in image.channel_series.channels:
                if channel.name in channel_names:
                    mm.logger.error(
                        f"Channel name {channel.name} is not unique. "
                        "We cannot average field illumination between images from the same channel."
                    )
                    return False
                channel_names.append(channel.name)

        # Check image shape
        mm.logger.info("Checking image shape...")
        if len(image.array_data.shape) != 5:
            mm.logger.error("Image must be 5D")
            return False
        if image.array_data.shape[0] != 1 or image.array_data.shape[1] != 1:
            mm.logger.warning(
                "Image must be in TZYXC order, single z and single time-point. Using first z and time-point."
            )

        # Check image saturation
        mm.logger.info("Checking image saturation...")
        saturated_channels = []
        for c in range(image.array_data.shape[-1]):
            if mm_tools.is_saturated(
                channel=image.array_data[..., c],
                threshold=dataset.input_parameters.saturation_threshold,
                detector_bit_depth=dataset.input_parameters.bit_depth,
            ):
                mm.logger.error(f"Channel {c} is saturated")
                saturated_channels.append(c)
        if len(saturated_channels):
            mm.logger.error(f"Channels {saturated_channels} are saturated")
            raise mm.SaturationError(f"Channels {saturated_channels} are saturated")

    key_measurements = _image_properties(
        images=dataset.input_data.field_illumination_images,
        corner_fraction=dataset.input_parameters.corner_fraction,
        sigma=dataset.input_parameters.sigma,
    )

    key_measurements = mm_schema.FieldIlluminationKeyMeasurements(
        name="field_illumination_key_measurements",
        description="Key measurements of the field illumination channels",
        table_data=key_measurements,
        **key_measurements.to_dict(orient="list"),
    )

    intensity_profiles = [
        mm.analyses.dict_to_table(
            dictionary=_image_line_profile(image.array_data, profile_size=255),
            name=f"{image.name}_intensity_profiles",
            description=f"Intensity profiles of {image.name}",
        )
        for image in dataset.input_data.field_illumination_images
    ]

    roi_profiles = [
        mm_schema.Roi(
            name="Profile ROIs",
            description="ROIs used to compute the intensity profiles",
            linked_references=image.data_reference,
            lines=_line_profile_shapes(image.array_data),
        )
        for image in dataset.input_data.field_illumination_images
    ]

    roi_corners = [
        mm_schema.Roi(
            name="Corner ROIs",
            description="ROIs used to compute the corner intensities",
            linked_references=image.data_reference,
            rectangles=_corner_shapes(image.array_data, dataset.input_parameters.corner_fraction),
        )
        for image in dataset.input_data.field_illumination_images
    ]

    roi_centers_of_mass = [
        mm_schema.Roi(
            name="Centers of mass ROIs",
            description="Point ROI marking the centroids of the max intensity regions",
            linked_references=image.data_reference,
            points=[
                mm_schema.Point(
                    name=f"ch{c:02}_center",
                    y=key_measurements.center_of_mass_y[
                        key_measurements.channel_name.index(image.channel_series.channels[c].name)
                    ],
                    x=key_measurements.center_of_mass_x[
                        key_measurements.channel_name.index(image.channel_series.channels[c].name)
                    ],
                    c=c,
                    stroke_color={"r": 255, "g": 0, "b": 0, "alpha": 200},
                    fill_color={"r": 255, "g": 0, "b": 0, "alpha": 200},
                    stroke_width=5,
                )
                for c in range(image.array_data.shape[-1])
            ],
        )
        for image in dataset.input_data.field_illumination_images
    ]

    roi_centers_geometric = [
        mm_schema.Roi(
            name="Geometric centers ROIs",
            description="Point ROI marking the centroids of the max intensity regions",
            linked_references=image.data_reference,
            points=[
                mm_schema.Point(
                    name=f"ch{c:02}_center",
                    y=key_measurements.center_geometric_y[
                        key_measurements.channel_name.index(image.channel_series.channels[c].name)
                    ],
                    x=key_measurements.center_geometric_x[
                        key_measurements.channel_name.index(image.channel_series.channels[c].name)
                    ],
                    c=c,
                    stroke_color={"r": 255, "g": 0, "b": 0, "alpha": 200},
                    fill_color={"r": 255, "g": 0, "b": 0, "alpha": 200},
                    stroke_width=5,
                )
                for c in range(image.array_data.shape[-1])
            ],
        )
        for image in dataset.input_data.field_illumination_images
    ]

    roi_centers_fitted = [
        mm_schema.Roi(
            name="Fitted centers ROIs",
            description="Point ROI marking the centroids of the max intensity regions",
            linked_references=image.data_reference,
            points=[
                mm_schema.Point(
                    name=f"ch{c:02}_center",
                    y=key_measurements.center_fitted_y[
                        key_measurements.channel_name.index(image.channel_series.channels[c].name)
                    ],
                    x=key_measurements.center_fitted_x[
                        key_measurements.channel_name.index(image.channel_series.channels[c].name)
                    ],
                    c=c,
                    stroke_color={"r": 255, "g": 0, "b": 0, "alpha": 200},
                    fill_color={"r": 255, "g": 0, "b": 0, "alpha": 200},
                    stroke_width=5,
                )
                for c in range(image.array_data.shape[-1])
            ],
        )
        for image in dataset.input_data.field_illumination_images
    ]

    roi_centers_max_intensity = [
        mm_schema.Roi(
            name="Max intensity ROIs",
            description="Point ROI marking the centroids of the max intensity regions",
            linked_references=image.data_reference,
            points=[
                mm_schema.Point(
                    name=f"ch{c:02}_center",
                    y=key_measurements.max_intensity_pos_y[
                        key_measurements.channel_name.index(image.channel_series.channels[c].name)
                    ],
                    x=key_measurements.max_intensity_pos_x[
                        key_measurements.channel_name.index(image.channel_series.channels[c].name)
                    ],
                    c=c,
                    stroke_color={"r": 255, "g": 0, "b": 0, "alpha": 200},
                    fill_color={"r": 255, "g": 0, "b": 0, "alpha": 200},
                    stroke_width=5,
                )
                for c in range(image.array_data.shape[-1])
            ],
        )
        for image in dataset.input_data.field_illumination_images
    ]

    roi_center_region = [
        mm_schema.Roi(
            name="Center region ROIs",
            description="Mask ROIs marking the center region of the image",
            linked_references=image.data_reference,
            masks=[
                mm_schema.Mask(
                    name=f"ch{c:02}_center_region",
                    x=0,
                    y=0,
                    c=c,
                    mask=mm.analyses.numpy_to_mm_image(
                        array=_get_center_region_mask(image.array_data[0, 0, :, :, c])
                    ),
                    fill_color={"r": 255, "g": 200, "b": 60, "alpha": 128},
                )
                for c in range(image.array_data.shape[-1])
            ],
        )
        for image in dataset.input_data.field_illumination_images
    ]

    dataset.output = mm_schema.FieldIlluminationOutput(
        processing_application="microscopemetrics",
        processing_version=mm.__version__,
        processing_datetime=datetime.now(),
        key_measurements=key_measurements,
        intensity_profiles=intensity_profiles,
        roi_profiles=roi_profiles,
        roi_corners=roi_corners,
        roi_centers_of_mass=roi_centers_of_mass,
        roi_centers_geometric=roi_centers_geometric,
        roi_centers_fitted=roi_centers_fitted,
        roi_centers_max_intensity=roi_centers_max_intensity,
        roi_center_region=roi_center_region,
    )

    dataset.processed = True

    return True
