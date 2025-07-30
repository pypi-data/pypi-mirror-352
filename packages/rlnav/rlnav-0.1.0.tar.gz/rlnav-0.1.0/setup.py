from setuptools import setup, find_packages

setup(
    name="rlnav",
    version="0.1.0",
    description="Reinforcement Learning Navigation Environments for Gym and Gymnasium",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "gym>=0.26",
        "gymnasium>=1.1",
        "pygame",
        "mujoco-py",
        "numpy",
        "opencv-python",
        "matplotlib",
        "scipy",
        "scikit-image",
        "imageio",
        "networkx"
    ],
    include_package_data=True,
    python_requires=">=3.8",
)
