from ewoksfluo.math import scan_shape


def test_scan_shape():
    nfast = 49
    nslow = 53

    npoints = [nfast * nslow, (nfast + 1) * nslow]
    equations = ["nfast * nslow", "(nfast + 1) * nslow"]

    solution = scan_shape.solve_scan_shape(npoints, equations)
    assert solution == {"nfast": nfast, "nslow": nslow}


def test_scan_shape_over_determined():
    nfast = 49
    nslow = 53

    npoints = [nfast * nslow, (nfast + 1) * nslow, 2 * (nfast + 1) * nslow]
    equations = ["nfast * nslow", "(nfast + 1) * nslow", "2 * (nfast + 1) * nslow"]

    solution = scan_shape.solve_scan_shape(npoints, equations)
    assert solution == {"nfast": nfast, "nslow": nslow}


def test_scan_shape_under_determined():
    nfast = 49
    nslow = 53

    npoints = [nfast * nslow]
    equations = ["nfast * nslow"]

    solution = scan_shape.solve_scan_shape(npoints, equations)
    assert solution is None


def test_solve_nnls_posint():
    nfast = 49
    nslow = 53

    equations_dict = {
        "npoints1": "nfast * nslow",
        "npoints2": "(nfast + 1) * nslow",
        "npoints3": "2 * (nfast + 1) * nslow",
        "npoints4": "npoints1",
    }

    values_dict = {
        "npoints1": nfast * nslow,
        "npoints2": (nfast + 1) * nslow,
        "npoints3": 2 * (nfast + 1) * nslow,
        "npoints4": nfast * nslow,
    }

    solution = scan_shape.solve_nnls_posint(equations_dict, values_dict)
    assert solution == {"nfast": nfast, "nslow": nslow}
