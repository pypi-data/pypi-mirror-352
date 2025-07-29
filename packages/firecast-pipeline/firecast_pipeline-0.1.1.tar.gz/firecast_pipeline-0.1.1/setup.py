from setuptools import setup, find_packages

setup(
    name="firecast_pipeline",
    version="0.1.1",
    description="Unified regression pipeline for fire risk prediction.",
    author="Allan Zhang",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "statsmodels",
        "xgboost",
        "torch",
        "optuna",
        "openpyxl",
        "joblib",
        "plotly"
    ],
    entry_points={
        "console_scripts": [
            "firecast-train=regressorpipeline.train:main",
            "firecast-predict=regressorpipeline.predict:main",
            "firecast-visualize=regressorpipeline.visualize:main"
        ]
    },
    include_package_data=True,
    python_requires=">=3.7",
)
