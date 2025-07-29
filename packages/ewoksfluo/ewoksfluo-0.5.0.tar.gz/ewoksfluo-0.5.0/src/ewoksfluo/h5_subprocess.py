def initializer():
    # Needs to happen before h5py is imported
    import os

    os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

    import h5py

    return

    try:
        h5py._objects.phil.release()
    except Exception:
        pass

    h5py._objects.nonlocal_close()

    print("HDF5 OBJECTS pid = ", os.getpid())
    h5py._objects.print_reg()


def main(module_name: str, func_name: str, *arg, **kwargs):
    import importlib

    mod = importlib.import_module(module_name)
    func = getattr(mod, func_name)

    return func(*arg, **kwargs)
