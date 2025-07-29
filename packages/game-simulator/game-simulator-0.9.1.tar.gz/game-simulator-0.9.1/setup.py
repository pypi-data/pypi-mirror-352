from setuptools import setup
import os

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()
setup(
  name = 'game-simulator',         
  packages = ['game_simulator'],   
  version = '0.9.1',      
  license='MIT',        
  description = 'A Python library that simulates agent interactions in normal-form games, uncovering how strategies evolve and adapt over time.',   
  long_description=read_file('README.md'),
  long_description_content_type='text/markdown',
  author = 'ankurtutlani',                   
  author_email = 'ankur.tutlani@gmail.com',      
  url = 'https://github.com/ankur-tutlani/game-simulator',   
  download_url = 'https://github.com/ankur-tutlani/game-simulator/archive/refs/tags/v_09.1.tar.gz',    
  keywords = ['game theory', 'evolution','multi-agents','equilibrium','simulation','agent-based modeling','game dynamics','norms'],   
  install_requires=[  
          'numpy>=1.24.3',
		  'pandas>=2.0.3',
		  'matplotlib>=3.7.2',
		  'setuptools>=68.0.0'  
   
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
												
	'Programming Language :: Python :: 3.11',
  ],
)