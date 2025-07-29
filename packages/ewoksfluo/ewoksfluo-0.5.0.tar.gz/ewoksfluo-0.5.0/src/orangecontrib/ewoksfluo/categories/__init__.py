import sysconfig

WIDGET_HELP_PATH = (
    # Development documentation (make htmlhelp in ./doc)
    ("{DEVELOP_ROOT}/doc/_build/htmlhelp/index.html", None),
    # Documentation included in wheel
    ("{}/help/ewoksfluo/index.html".format(sysconfig.get_path("data")), None),
    # Online documentation url
    ("https://ewoksfluo.readthedocs.io", ""),
)


# Entry point for main Orange categories/widgets discovery
def widget_discovery(discovery):
    from ewoksorange.pkg_meta import get_distribution

    dist = get_distribution("ewoksfluo")
    pkgs = [
        "orangecontrib.ewoksfluo.categories.input",
        "orangecontrib.ewoksfluo.categories.fit",
        "orangecontrib.ewoksfluo.categories.sum_detectors",
        "orangecontrib.ewoksfluo.categories.normalization",
        "orangecontrib.ewoksfluo.categories.regrid",
        "orangecontrib.ewoksfluo.categories.raw_counters",
        "orangecontrib.ewoksfluo.categories.demo",
    ]
    for pkg in pkgs:
        discovery.process_category_package(pkg, distribution=dist)
