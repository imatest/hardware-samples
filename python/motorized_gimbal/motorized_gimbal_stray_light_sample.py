"""
motorized_gimbal_stray_light.py

This is a sample script that demonstrates:
    1. Control of the Imatest Motorized Gimbal for capturing stray light (flare) images, using the Python "Zaber Motion
        Library (ASCII)". See Dependencies below for details.
    2. Stray light data analysis and results generation, using the "Imatest IT" stray light analysis API.

This script is meant to be edited and/or used as an example.

Dependencies:
    - Python 3.8 or 3.9
    - zaber-motion Python ASCII library:
        https://www.zaber.com/software/docs/motion-library/ascii/tutorials/install/py/
        Can be installed using "pip" via the following command: pip install zaber-motion
    - (Optional) Imatest IT library
        https://www.imatest.com/docs/imatest-it-instructions/#Python

Imatest Stray Light (Flare) Documentation:
    https://www.imatest.com/support/docs/22-2/stray-light-flare/

Imatest LLC, 2022
"""
from zaber_motion import Units, Library
from zaber_motion.ascii import Connection
import pathlib
import time
import typing
import json

# Type aliases
CapturePlanType = typing.Dict[str, typing.List[float]]


def capture_image(im_file_path: pathlib.Path) -> None:
    """
    Capture and save an image file to a specified path

    Parameters
    ----------
    im_file_path : pathlib.Path
        Path to output file image file, including file extension

    Notes
    -----
    * The contents of this function should be overwritten to call the desired image capture command which should save an
      image file as the input path (im_file_path).
    * The as-written im_file_path is constructed in the run_sample_mg_capture_plan() function and is formatted with the
      Python "pathlib.Path" module to be, for example: WindowsPath('C:/path/to/output_dir/cap00001.png')

    See Also
    --------
    run_sample_mg_capture_plan : Run a sample Motorized Gimbal capture plan
    """
    # convert pathlib.Path object to str:
    image_file_path_str = im_file_path.resolve().as_posix()

    # ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !
    pass  # REMOVE "pass" and INSERT IMAGE CAPTURE COMMAND HERE
    # ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !


def run_sl_analysis(
    config_file_path: pathlib.Path = pathlib.Path(""),
    ini_file_path: pathlib.Path = pathlib.Path(""),
) -> int:
    """
    Run stray light analysis using the Imatest IT interface

    Parameters
    ----------
    config_file_path : pathlib.Path
        Path to the config file (JSON-encoded text file) associated with the captured images to analyze
    ini_file_path : pathlib.Path
        Path to an Imatest INI file that defines the [straylight] settings to use for analysis
    Returns
    -------
    exit_code: int
        Exit code representing success (0) or failure (1) to run analysis, e.g., to use for the Python exit() command
    """
    from imatest.it import (
        ImatestLibrary,
        ImatestException,
    )

    exit_code = 0  # 0 = ok, 1 = not ok

    # Check if input files exist
    if not config_file_path.is_file():
        print(f"Input config file does not exist: {config_file_path}")
        exit_code = 1
        return exit_code

    if not ini_file_path.is_file():
        print(f"Input Imatest INI file does not exist: {ini_file_path}")
        exit_code = 1
        return exit_code

    # Initialize Imatest Library
    # Note: The ImatestLibrary should only be instantiated once per process
    imatest = ImatestLibrary()

    # Call to stray_light_batch module with ini file argument and StrayLightConfig (object/file) argument.
    try:
        result = imatest.stray_light_batch(
            ini_file=ini_file_path.resolve().as_posix(),
            config=config_file_path.resolve().as_posix(),
        )  # paths are converted to absolute paths (resolve) and to strings with forward slashes (as_posix)

        # The result is a JSON-encoded object that lists the file paths to all outputs that were generated.
        print(result)
    except ImatestException as iex:
        if iex.error_id == ImatestException.FloatingLicenseException:
            print(
                "All floating license seats are in use.  Exit Imatest on another computer and try again."
            )
        elif iex.error_id == ImatestException.LicenseException:
            print("License Exception: " + iex.message)
        else:
            print(iex.message)

        exit_code = iex.error_id
    except Exception as ex:
        print(str(ex))
        exit_code = 1

    # When finished terminate the library
    imatest.terminate_library()

    return exit_code


def make_sample_mg_horizontal_sweep_capture_plan() -> CapturePlanType:
    """
    Make a sample Motorized Gimbal capture plan that provides a simple horizontal sweep

    Returns
    -------
    capture_plan : CapturePlanType
        Dictionary defining a list of "azimuthAngles" and a list of "fieldAngles" (in degrees) for the Motorized Gimbal
    """
    capture_plan: CapturePlanType = dict()
    # List of "azimuth angles" for the Motorized Gimbal:
    # In this example, we use only 0 (horizontal) to create a horizontal sweep when used in combination with the field
    # angles defined below
    capture_plan["azimuthAngles"] = [0]
    # List of "field angles" for the Motorized Gimbal:
    # In this example, we use 5 degree increments from -45 to 45 degrees (although field angle is technically absolute)
    # to create a simple horizontal sweep
    capture_plan["fieldAngles"] = list(range(-45, 46, 5))

    return capture_plan


def make_sample_mg_star_capture_plan() -> CapturePlanType:
    """
    Make a sample Motorized Gimbal capture plan that provides a star pattern

    Returns
    -------
    capture_plan : CapturePlanType
        Dictionary defining a list of "azimuthAngles" and a list of "fieldAngles" (in degrees) for the Motorized Gimbal
    """
    capture_plan: CapturePlanType = dict()
    # List of "azimuth angles" for the Motorized Gimbal:
    # In this example, we use 0, 45, and 90 degrees (horizontal, diagonal, and vertical camera orientations)
    # to create a star-like pattern when used in combination with the field angles defined below
    capture_plan["azimuthAngles"] = [0, 45, 90]
    # List of "field angles" for the Motorized Gimbal:
    # In this example, we use 5 degree increments from -45 to 45 degrees (although field angle is technically absolute)
    # to create a sweep of positions across the camera's FOV at the azimuth angles defined above
    capture_plan["fieldAngles"] = list(range(-45, 46, 5))

    return capture_plan


def run_sample_mg_capture_plan(
    capture_plan: typing.Optional[CapturePlanType] = None,
    output_dir: pathlib.Path = pathlib.Path(""),
    im_file_ext: str = "png",
    pause_time_s: float = 0.5,
    ref_az: int = 0,
    ref_fa: int = 0,
    do_home: bool = False,
    com_port: str = "COM4",
    az_zaber_device_idx: int = 1,
    fa_zaber_device_idx: int = 0,
) -> None:
    """
    Run a sample Motorized Gimbal capture plan

    Parameters
    ----------
    capture_plan : CapturePlanType
        dictionary defining a list of "azimuthAngles" and a list of "fieldAngles" (in degrees) for the Motorized Gimbal
    output_dir : pathlib.Path
        Path to directory for saving image files and other output files to. If empty or if the path doesn't exist, image
        capture will be skipped.
    im_file_ext : str
        Image file extension to use for captures, e.g., "png"
    pause_time_s : float
        Pause time (seconds) between Motorized Gimbal movement and image capture call
    ref_az : float
        Reference azimuth angle (degrees) for the Motorized Gimbal, corresponding to the absolute position where the
        camera is aligned with or perpendicular to the light source
    ref_fa : float
        Reference field angle (degrees) for the Motorized Gimbal, corresponding to the absolute position where the
        camera is aligned with or perpendicular to the light source
    do_home : bool
        Logical that determines whether to home all Motorized Gimbal axes before executing the movements from the
        capture_plan
    com_port : str
        COM port associated with the Motorized Gimbal Zaber connection, e.g., "COM3"
    az_zaber_device_idx : int
        Zaber device index corresponding to the Motorized Gimbal axis that controls azimuth angle (roll)
    fa_zaber_device_idx : int
        Zaber device index corresponding to the Motorized Gimbal axis that controls field angle (yaw)
    """
    if capture_plan is None:  # Input validation
        print("No capture_plan specified. Exiting function run_sample_mg_capture_plan.")
        return

    if output_dir.is_dir():  # Input validation
        do_captures = True
    else:
        do_captures = False
        print(
            f'The specified output_dir (path to output directory) does not exist: "{output_dir.resolve().as_posix()}"\nImage capture will be skipped.'
        )

    # Create a "capture configuration" dictionary that will contain key info about each capture, pertinent to the
    # analysis and plotting of the data. The contents of this dictionary are populated after capturing each image.
    # This dictionary is saved as a JSON-encoded text file after finishing with captures.
    capture_config = dict(
        {
            "captures": [],
            "run_name": "sample_run_123abc",
            "comment": "This is a sample capture config",
            "version": -1,
        }
    )

    # ============================================================
    # Get the azimuth angles and field angles from the pre-defined capture_plan
    # ============================================================

    az = capture_plan["azimuthAngles"]
    fa = capture_plan["fieldAngles"]

    # ============================================================
    # Connect to the Motorized Gimbal using Zaber's Python library
    # ============================================================

    # The library connects to the internet to retrieve information about Zaber devices.
    # Calling the method enable_device_db_store makes the library store the downloaded information to later allow for
    # offline use. This line can optionally be commented out after the first run.
    Library.enable_device_db_store()

    # Initialize connection to Zaber devices
    with Connection.open_serial_port(com_port) as connection:
        # Get list of Zaber devices
        device_list = connection.detect_devices()
        print(f"Found {len(device_list)} devices:")
        print(device_list)

        # (Optional) Home all axes of the detected Zaber devices
        if do_home:
            for device in device_list:
                print(
                    f"Homing all axes of device with address {device.device_address}."
                )
                device.all_axes.home()

        axis_az = device_list[az_zaber_device_idx].get_axis(1)
        axis_fa = device_list[fa_zaber_device_idx].get_axis(1)

        # ============================================================
        # Move to predefined positions and capture images
        # ============================================================

        # Move to each of the defined azimuth angle and field angle positions
        num_positions = len(az) * len(fa)  # Total number of positions
        position_idx = 0
        for a in range(len(az)):
            for f in range(len(fa)):
                position_idx += 1

                # Adjust angles based on center-aligned/reference position
                azimuth_angle = az[a] - ref_az
                field_angle = fa[f] - ref_fa

                # Construct the path to the output image file to be captured for this position
                # The as-written image file naming is, for example: WindowsPath('C:/path/to/output_dir/cap00001.png')
                im_file_path = pathlib.Path(
                    output_dir, f"cap{position_idx:05d}.{im_file_ext}"
                )

                print(
                    f"Moving to absolute position ({position_idx}/{num_positions}) with azimuth angle {azimuth_angle}"
                    f" and field angle {field_angle} (degrees)..."
                )
                # Move both axes simultaneously, wait until both axes are done moving
                axis_az.move_absolute(
                    azimuth_angle,
                    Units.ANGLE_DEGREES,
                    wait_until_idle=False,
                    velocity=50,
                    acceleration=50,
                    velocity_unit=Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND,
                    acceleration_unit=Units.ANGULAR_ACCELERATION_DEGREES_PER_SECOND_SQUARED,
                )
                axis_fa.move_absolute(
                    field_angle,
                    Units.ANGLE_DEGREES,
                    wait_until_idle=False,
                    velocity=50,
                    acceleration=50,
                    velocity_unit=Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND,
                    acceleration_unit=Units.ANGULAR_ACCELERATION_DEGREES_PER_SECOND_SQUARED,
                )
                axis_az.wait_until_idle()
                axis_fa.wait_until_idle()
                print("Movement complete.")

                # Pause before capture
                time.sleep(pause_time_s)

                # Capture and save image
                if do_captures:
                    print("Capturing image...")
                    capture_image(im_file_path)
                    print("Image capture complete.")

                # Add information about this capture to the capture_config dictionary:
                # This dictionary is saved as a JSON-encoded text file after finishing with captures.
                capture_config["captures"].append(
                    dict(
                        {
                            "image_paths": im_file_path,
                            "source_field_angle_deg": fa[f],
                            "source_azimuth_angle_deg": az[a],
                            "source_comment": "",
                        }
                    )
                )

        # Move both axes back to the center-aligned/reference position
        axis_az.move_absolute(
            ref_az,
            Units.ANGLE_DEGREES,
            velocity=50,
            acceleration=50,
            velocity_unit=Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND,
            acceleration_unit=Units.ANGULAR_ACCELERATION_DEGREES_PER_SECOND_SQUARED,
        )
        axis_fa.move_absolute(
            ref_fa,
            Units.ANGLE_DEGREES,
            velocity=50,
            acceleration=50,
            velocity_unit=Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND,
            acceleration_unit=Units.ANGULAR_ACCELERATION_DEGREES_PER_SECOND_SQUARED,
        )
        print("Captures complete.")

        # Save the capture_config dictionary as a JSON-encoded text file to the output_dir
        # This file will contain key information about each capture, pertinent to analysis and plotting of the data
        print("Writing configuration file...")
        capture_config_file_path = pathlib.Path(output_dir, "config.slconf")
        with capture_config_file_path.open(mode="w") as capture_config_file:
            json.dump(capture_config, capture_config_file)

        print("Done.")


def main():
    # First define the Path (pathlib.Path) to an output directory, used for saving images and output files
    # (Paste your directory path between the two quotes)
    output_dir = pathlib.Path(r"C:/path/to/existing/output_dir")  # Example: WindowsPath('C:/path/to/output_dir')
    # If left empty or if the path doesn't exist, the run_sample_mg_capture_plan() function will not perform image
    # capture at each Motorized Gimbal position

    im_file_ext = "png"  # File extension to use for saving image files

    com_port = "COM4"  # COM port associated with the Motorized Gimbal Zaber connection

    # In order to connect to and control the Motorized Gimbal, the Zaber-motion command Connection.detect_devices() is
    # used which returns a list of "Devices" corresponding to the two Motorized Gimbal axes.
    # These variables define the index for the respective axis representing azimuth angle (roll) and field angle (yaw):
    az_zaber_device_idx = 1  # azimuth angle device index
    fa_zaber_device_idx = 0  # field angle device index

    pause_time_s = 0.5  # Pause time (seconds) between Motorized Gimbal movement and image capture call
    do_home = False  # Home all Motorized Gimbal axes before executing capture plan?

    # Reference azimuth and field angle (in degrees) for the Motorized Gimbal, corresponding to the absolute position
    # where the camera is aligned with or perpendicular to the light source
    ref_az = 0  # reference / source-aligned field angle
    ref_fa = 0  # reference / source-aligned azimuth angle

    # Define a sample capture plan for the Motorized Gimbal
    # Use a simple horizontal sweep capture plan or, alternatively (commented out), a star pattern capture plan
    capture_plan = make_sample_mg_star_capture_plan()
    # capture_plan = make_sample_mg_horizontal_sweep_capture_plan()

    # Run sample Motorized Gimbal capture plan and capture image at each position
    run_sample_mg_capture_plan(
        capture_plan=capture_plan,
        output_dir=output_dir,
        im_file_ext=im_file_ext,
        pause_time_s=pause_time_s,
        ref_az=ref_az,
        ref_fa=ref_fa,
        do_home=do_home,
        com_port=com_port,
        az_zaber_device_idx=az_zaber_device_idx,
        fa_zaber_device_idx=fa_zaber_device_idx,
    )

    # Run stray light analysis via calls to the Imatest IT API
    # The lines below can be uncommented if the user has an Imatest IT license and wants to run analysis on the
    # captured images within this script.
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    """
    # Path to the stray light config file generated from run_sample_mg_capture_plan()
    config_file_path = pathlib.Path(output_dir, "config.slconf")

    # Path to an "imatest-v2.ini" file that defines the [straylight] settings to use for analysis
    ini_file_path = pathlib.Path(
        pathlib.Path(__file__).parent.parent.absolute(),
        "sample_ini_file",
        "stray-light-sample-imatest-v2.ini",
    )

    exit_code = run_sl_analysis(config_file_path, ini_file_path)

    exit(exit_code)
    """
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == "__main__":
    main()
