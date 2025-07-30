from setuptools import setup, find_packages

setup(
    name='ipchecker_fajar',  # Gunakan nama unik di PyPI
    version='0.1.0',
    description='Simple IP address checking utilities (validity, private/public, subnet, public IP)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Fajar P',
    author_email='fajarp@example.com',  # Ganti dengan email kamu
    url='https://github.com/fajarp/ipchecker_fajar',  # Opsional
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    python_requires='>=3.7',
)
