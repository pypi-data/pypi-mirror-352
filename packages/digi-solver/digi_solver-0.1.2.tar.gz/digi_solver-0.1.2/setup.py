from setuptools import setup, find_packages

# Try to read README.md for long_description
try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = 'A comprehensive package for solving digital electronics problems and assignments.'

setup(
    name='digi_solver',
    version='0.1.2',
    author='19uez',
    author_email='phaman5109@gmail.com',
    description='A Python package for digital electronics problem solving, including K-maps, number conversions, and more.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/19uez',
    packages=['digi_solver'] + ['digi_solver.' + pkg for pkg in find_packages(exclude=['tests', '*.tests', '*.tests.*', 'dist', 'build'])],
    package_dir={'digi_solver': '.'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='==3.8',
    install_requires=[
        # ---- PLEASE ADD YOUR PROJECT DEPENDENCIES HERE ----
        # Examples (uncomment and adjust as needed):
        'numpy',
        'pandas',          # For CSV/Excel handling if used in ncalc_python, kmap_tool, etc.
        'openpyxl',        # If kmap_tool or lo_gateimg_tool reads/writes .xlsx files
        'Pillow',          # If lo_gateimg_tool involves image processing
        'requests',        # If any sub-package makes API calls
        # 'matplotlib',      # If any tool generates plots
        'colorclass',      # Used in kmap_tool/QuineMcCluskey
        'terminaltables',  # Used in kmap_tool/QuineMcCluskey
    ],
    entry_points={
        'console_scripts': [
            'ncalc = digi_solver.ncalc_python.cli:main_cli',
            'sbn_converter = digi_solver.signed_binary_conversion.binary_converter:main',
            # For the following entry points, ensure you have a corresponding main function
            # defined in the specified module that handles command-line arguments.
            # 'kmap_generator = digi_solver.kmap_tool.gen_kmap:main_kmap_generator_cli',
            # 'qmc_solver = digi_solver.kmap_tool.QuineMcCluskey.qmccluskey:main_qmc_cli',
        ],
    },
    # If your package includes non-Python data files (e.g., .csv, .txt, images)
    # that need to be included when the package is installed, you might need:
    # include_package_data=True,
    # And potentially a MANIFEST.in file. For data files used internally by the code
    # and located within sub-packages, this is often not needed.
) 