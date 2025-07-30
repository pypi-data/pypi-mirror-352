import codecs
import os.path
import sys
from pathlib import Path
from setuptools import setup, Extension, find_packages
from distutils.command.build import build as build_orig

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.lstrip().startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

here = Path(__file__).parent
readme_file = (here / "README.md").read_text()

exts = [
    Extension(name="tactigon_gear.middleware.Tactigon_Gesture", sources=["tactigon_gear/middleware/Tactigon_Gesture.c"]),
    Extension(name="tactigon_gear.middleware.Tactigon_Recorder", sources=["tactigon_gear/middleware/Tactigon_Recorder.c"]),
    Extension(name="tactigon_gear.middleware.Tactigon_Audio", sources=["tactigon_gear/middleware/Tactigon_Audio.c"]),
    Extension(name="tactigon_gear.middleware.utilities.Data_Preprocessor", sources=["tactigon_gear/middleware/utilities/Data_Preprocessor.c"]),
    Extension(name="tactigon_gear.middleware.utilities.Tactigon_RT_Computing", sources=["tactigon_gear/middleware/utilities/Tactigon_RT_Computing.c"]),
]

class build(build_orig):

    def finalize_options(self):
        super().finalize_options()
        __builtins__.__NUMPY_SETUP__ = False

        from Cython.Build import cythonize
        self.distribution.ext_modules = cythonize(self.distribution.ext_modules,
                                                  language_level=3)

version = sys.version_info
install_requires = [
    "requests",
    "scipy",
    "bleak==0.22.0"
]
if version.minor == 8:
    python_requires = ">=3.8.0"
    install_requires.append("scikit-learn==1.3.1")
    install_requires.append("pandas==2.0.3")
else:
    python_requires = ">=3.12.0"
    install_requires.append("scikit-learn==1.6.0")
    install_requires.append("pandas==2.2.3")

setup(
    name="tactigon_gear",
    version=get_version("tactigon_gear/__init__.py"),
    maintainer="Next Industries s.r.l.",
    maintainer_email="info@thetactigon.com",
    url="https://www.thetactigon.com",
    description="Tactigon Gear to connect to Tactigon Skin wereable platform",
    long_description=readme_file,
    long_description_content_type='text/markdown',
    keywords="tactigon,wereable,gestures controller,human interface",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    license_files=None,
    packages=find_packages(),
    python_requires=python_requires,
    setup_requires=["cython"],
    install_requires=install_requires,
    ext_modules=exts,
    include_package_data=True
)