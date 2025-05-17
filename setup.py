from distutils.core import setup

setup(name='adrts_comm_layer',
      version='1.0',
      description='the communication layer for attack defend rts, includes the postgres interface as well as other server related functions',
      author='MrForkle',
      url='https://github.com/MrForkle/Attack_Defend_RTS_Communication_Layer',
      packages=['pscopg2'],
     )
