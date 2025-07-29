from setuptools import setup, find_packages

setup(
    name="ortho_polys",
    version="0.1",
    description="Классические ортогональные полиномы: Лежандра, Чебышёва, Лагерра, Эрмита и Якоби и их свойства",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "sympy",
        "matplotlib"
    ],
    author_email='alex.rudakovskii@gmail.com',
    zip_safe=False,
    license="MIT"
)