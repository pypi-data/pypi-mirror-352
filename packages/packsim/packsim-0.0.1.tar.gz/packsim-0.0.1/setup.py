import setuptools

with open("/home/wzf/Workspace/rl/pypi/simulator/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("/home/wzf/Workspace/rl/pypi/simulator/requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="packsim",
    version="0.0.1",
    author="wzf",
    author_email="wangzhoufeng7346@gmail.com",
    description="packsim",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    include_package_data=True,
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    python_requires=">=3.7",
)
