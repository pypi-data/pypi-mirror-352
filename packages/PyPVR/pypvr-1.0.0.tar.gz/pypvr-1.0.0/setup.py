# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = {
    '': 'src'
}

modules = [
    'pypvr'
]

setup_kwargs = {
    'name': 'pypvr',
    'version': '1.0.0',
    'description': 'PyPVR is an unofficial, modern tool written in Python for encoding / decoding PowerVR2 images used by SEGA Dreamcast and SEGA Naomi.',
    'long_description': '# PyPVR\nA Python module to easily convert Dreamcast/Naomi .PVR and .PVP files to images + palettes\nPlease note it requires Pillow (PIL) module installed\n\n## Installation\n\n```bash\npip3 install pypvr\n```\n\n## Credits\n\n- Rob2d for K-means idea leading to quality VQ encoding\n- Egregiousguy for YUV420 to YUV420p conversion\n- Kion for VQ handling and logic\n- tvspelsfreak for SR conversion info on Bump to normal map\n- MetalliC for hardware knowledge\n- Testing Credits: Esppiral, Alexvgz, PkR, Derek, dakrk, neSneSgB, woofmute, TVi, Sappharad',
    'author': 'VincentNL',
    'author_email': 'zgoro@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/VincentNLOBJ/PyPVR',
    'package_dir': package_dir,
    'py_modules': modules,
    'python_requires': '>=3.9',
}

setup(**setup_kwargs)
