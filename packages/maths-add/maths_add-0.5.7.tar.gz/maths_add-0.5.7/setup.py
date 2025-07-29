from setuptools import setup,find_packages

setup(
	name='maths_add',
	version='0.5.7',
	description='A extended math library',
	long_description=open('README.md',encoding="utf-8").read(),
	long_description_content_type='text/markdown',
	author='fourth-dimensional_universe',
	author_email='3817201131@qq.com',
	url='https://github.com/fourth-dimensional/maths_add',
	license='MIT',
	classifiers=[
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
		'Programming Language :: Python :: 3.10',
		'Programming Language :: Python :: 3.11',
		'Programming Language :: Python :: 3.12',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	packages=find_packages(),
	python_requires='>=3.7',
	install_requires=[
		'pycryptodome',
		'cryptography'
	]
	)




