from setuptools import setup, find_packages

setup(
    name="streamlit-secure-context",
    version="0.1.6",
     packages=find_packages(),
     include_package_data=True,
     package_data={
         "streamlit_secure_context": [
             "frontend/build/*",
             "frontend/build/**/*"
         ]
     },
    install_requires=["streamlit>=0.63", "pyarrow"],
    description="Streamlit Secure Context Component",
    author="Edward Joseph",
    license="MIT",
 )
