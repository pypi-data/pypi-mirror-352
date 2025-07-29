import os
import sys
import logging
import click

from pywander.text.encoding import convert_encoding

logger = logging.getLogger(__name__)


def detect_output_file_exist(basedir, img_name, outputformat, overwrite):
    filename = '{}.{}'.format(img_name, outputformat)
    filename = os.path.join(basedir, filename)

    if os.path.exists(filename) and not overwrite:
        click.echo('output image file exists. i will give it up.')
        return None
    return filename


def fix_filename_encoding_problem(output_img_name, outputformat, overwrite=True,
                                  pdftocairo_fix_encoding=''):
    if 'win32' == sys.platform.lower():
        if pdftocairo_fix_encoding:
            output_img_name2 = convert_encoding(output_img_name,
                                                'utf8',
                                                pdftocairo_fix_encoding)

            if overwrite:
                os.replace('{}.{}'.format(output_img_name2,
                                          outputformat),
                           '{}.{}'.format(output_img_name,
                                          outputformat))
            else:
                try:
                    os.rename('{}.{}'.format(output_img_name2,
                                             outputformat),
                              '{}.{}'.format(output_img_name,
                                             outputformat))
                except FileExistsError as e:
                    logger.info(
                        'FileExists , i will do nothing.')
                    os.remove('{}.{}'.format(output_img_name2,
                                             outputformat))
