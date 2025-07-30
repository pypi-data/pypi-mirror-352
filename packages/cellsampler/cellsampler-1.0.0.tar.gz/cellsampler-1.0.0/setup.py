from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            # as it would be imported
            name="cellsampler.preprocessing.nice_filters",
            # may include packages/namespaces separated by `.`
            sources=[
                "cellsampler/preprocessing/nice_filters.c"
            ],  # all sources are compiled into a single binary file
        ),
    ]
)
