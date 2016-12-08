from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='readme2tex',
      version='0.1',
      description='Render LaTeX within your Github Readmes',
      long_description=readme(),
      url='http://github.com/leegao/readme2tex',
      author='Lee Gao',
      author_email='lg342@cornell.edu',
      license='MIT',
      packages=['readme2tex'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Text Processing :: Markup :: LaTeX',
      ],
      keywords='github readme markdown latex tex equations math svg markup',
      install_requires=[
          'markdown',
      ],
      include_package_data=True,
      zip_safe=False)