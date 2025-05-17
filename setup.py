from distutils.core import setup

setup(name='adrts_comm_layer',
      description='the communication layer for attack defend rts, includes the postgres interface as well as other server related functions',
      author='MrForkle',
      url='https://github.com/MrForkle/Attack_Defend_RTS_Communication_Layer',
      install_requires=['psycopg2-binary',],
     )
