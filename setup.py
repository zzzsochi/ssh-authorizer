from setuptools import setup

setup(
        name='ssh_authorizer',
        description='Manager for remote ~/.ssh/authorized_keys.',
        author='Alexander Zelenyak aka ZZZ',
        author_email='zzz.sochi@gmail.com',
        url='http://github.com/zzzsochi/ssh_authorized/',
        version='1.0',
        packages=['ssh_authorizer'],
        scripts=['scripts/ssh-authorizer'],
        install_requires=['sh'],
        classifiers=[
                'Operating System :: Unix',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.3',
              ],
)
