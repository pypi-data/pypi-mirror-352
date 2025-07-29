import setuptools

setuptools.setup(
	name='ldap-server-lib',
	version='0.3',
	author='idk_wdym_i_needa_un',
	author_email='',
	description='noncommercial',
	packages=['ldap-server-lib'],
	install_requires=["datemath"],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.11',
)