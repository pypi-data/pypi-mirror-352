from setuptools import setup, find_packages

setup(
    name='obliqueslice',  
    version='0.1',        
    packages=find_packages(),
    install_requires=[     
        'numpy', 
        'scipy',
    ],
    description='A package for slicing 3D numpy arrays along an oblique plane. Equivalent to obliqueslice in MATLAB.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Juna Santos',
    author_email='junapsantos@tecnico.ulisboa.pt',
    url='https://github.com/junapsantos/obliqueslice',  # Replace with your repository link
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)