from setuptools import setup

setup(
        name='ssh_authorizer',
        version='1.1',
        description='Manager for remote ~/.ssh/authorized_keys.',
        author='Alexander Zelenyak aka ZZZ',
        author_email='zzz.sochi@gmail.com',
        url='https://github.com/zzzsochi/ssh-authorizer/',
        packages=['ssh_authorizer'],
        scripts=['scripts/ssh-authorizer'],
        install_requires=['sh'],
        classifiers=[
                'Operating System :: Unix',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.3',
        ],
)
