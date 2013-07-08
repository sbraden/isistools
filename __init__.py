#__init__.py

import re
from pysis.commands import isis
from pysis.util import write_file_list
from pysis.labels import parse_file_label, parse_label


# TODO: normalize inputs to functions:
# filename or image, not "name"

content_re = re.compile(r'(Group.*End_Group)', re.DOTALL)

def band_means(bands):
    return bands.mean(axis=(1,2))

def band_stds(bands):
    return bands.std(axis=(1,2))

def get_img_stats(name):
    cube = CubeFile.open(name)
    return band_means(cube.data), band_stds(cube.data)


def spice(image, model):
	"""
	Args:
		image: image filename
		model: full path to dtm model name
	"""
    isis.spiceinit(
        from_      = image,
        spksmithed = True,
        shape      = 'user',
        model      = model
    )


def get_pixel_scale(img_name):
    """
    Args: image filename
    Returns: the pixel_scale
    """
    output = isis.campt.check_output(from_=img_name)
    output = content_re.search(output).group(1) 
    pixel_scale = parse_label(output)['GroundPoint']['SampleResolution']
    
    return pixel_scale


def get_img_center(img_name):
	"""
	Args: image filename
	Returns: center latitude and center longitude of image
	"""
    output = isis.campt.check_output(from_=img_name)
    output = content_re.search(output).group(1) 
    clon = parse_label(output)['GroundPoint']['PositiveEast360Longitude']
    clat = parse_label(output)['GroundPoint']['PlanetographicLatitude']

    return clat, clon


def project_wac(image, map):
	"""
	Args: 
		image: filename
		map: isis maptemplate mapfile
	"""
    isis.cam2map(
        from_    = frame.photrim,
        to       = frame.proj,
        map      = map,
        matchmap = True
    )


def automos(images, mosaic):
	"""
	Args: 
		images: files to mosaic together
		mosaic: output mosaic filename
	"""
    with listfile as NamedTemporaryFile():
        write_file_list(listfile, [image.proj.cub for image in images])
        listfile.flush()

        isis.automos(
            fromlist = listfile.name,
            mosaic   = mosaic
        )


def get_image_info(image):
    """
    GATHER INFORMATION ABOUT SINGLE OBSERVATION
    BASED ON VIS mosaic only
    """
    # Get label info
    label = parse_file_label(image)
    instrument = label['IsisCube']['Instrument']

    # Get campt info
    output = isis.campt.check_output(from_=image)
    gp = parse_label(GROUP_RE.search(output).group(1))['GroundPoint']

    return pd.Series({
        'start_time':              instrument['StartTime'],
        'exp_time':                instrument['ExposureDuration'],
        'fpa_temp':                instrument['MiddleTemperatureFpa'],
        'subsolar_azimuth':        gp['SubSolarAzimuth'],
        'subsolar_ground_azimuth': gp['SubSolarGroundAzimuth'],
        'solar_distance':          gp['SolarDistance']
    })

