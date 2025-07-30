from setuptools import setup, find_packages

str_version = '0.1.0'

setup(name='hunyuan-life',
      version=str_version,
      description='Hunyuan Life',
      author='YuanqiMcp',
      author_email='yuanqi_mcp@tencent.com',
      license_text='MIT',
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            # 定义命令行工具，用户运行 uvx your-mcp-server 时会执行 your_mcp_server.main:main
            'hunyuan-life=hunyuan_life.main:run_mcp',
        ],
      },
      zip_safe=False,
      include_package_data=True,
      install_requires=['mcp', 'httpx', 'uvicorn'],
      python_requires='>=3.10')
