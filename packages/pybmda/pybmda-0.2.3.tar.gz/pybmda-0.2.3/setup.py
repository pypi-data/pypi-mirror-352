import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pybmda',
    version='v0.2.3',
    author='Lynkz Instruments Inc',
    author_email='xavier@lynkz.ca',
    description='Python interface for BlackMagicDebugApplication (BMDA)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Lynkz-Instruments/pybmda',
    license='MIT',
    packages=['pybmda'],
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',                # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',                # Define that your audience are developers
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
    ],

)
