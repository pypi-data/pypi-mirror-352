import setuptools

with open("README.md", "r") as s:
    description = s.read()

setuptools.setup(
    author="Amir Jafari, Martin Hagan, Pedro Uría, Xiao Qi",
    author_email="nndesign.demo@gmail.com",
    name='nndesigndemos',
    license="MIT",
    description='Demos for the Neural Network Design & Deep Learning books',
    version='v1.1.6',
    long_description_content_type="text/markdown",
    # long_description="This is a set of demonstrations paired with the Neural Network Design & Deep Learning books.\n"
    #                  "Each demo is linked to a chapter section of the books. You can find more info at "
    #                  "https://hagan.okstate.edu/nnd.html.\n\nAfter installing (creating a virtual environment is "
    #                  "recommended), just open the Python Shell and type: from nndesigndemos import nndtoc; nndtoc()",
    long_description=description,
    url='https://hagan.okstate.edu/nnd.html',
    # project_urls={
    #     "Documentation": "https://docs.example.com/HelloWorld/",
    #     "Source Code": "https://github.com/amir-jafari/nndesign-demo",
    # },
    packages=["nndesigndemos"],
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=["PyQt6", "numpy", "scipy", "matplotlib"],
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',

    ],
)
