import ctypes
import os
from typing import List, Optional

from scaler.utility.object_storage_config import ObjectStorageConfig


DEFAULT_OBJECT_STORAGE_LIB_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "lib", "libserver.so"),
    os.path.join(os.path.dirname(__file__), "..", "..", "build", "scaler", "object_storage", "libserver.so"),
]


class ObjectStorageServer:
    def __init__(self, config: ObjectStorageConfig, lib_paths: List[str] = DEFAULT_OBJECT_STORAGE_LIB_PATHS):
        self._config = config

        self._lib_paths = lib_paths

        self._on_server_ready_fd = os.eventfd(0, os.EFD_SEMAPHORE)
        os.set_inheritable(self._on_server_ready_fd, True)  # allows the FD to be passed to a spawned process

    def run(self) -> None:
        """Runs the object storage server, does not return."""

        for lib_path in self._lib_paths:
            print(lib_path)
            lib = self._load_library(lib_path=lib_path)
            if lib is not None:
                break

        if lib is None:
            raise RuntimeError(f"failed to load object storage server library.")

        # Define the argument and return types for the main_entrance function
        lib.run_object_storage_server.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
        lib.run_object_storage_server.restype = None

        # Call the function
        name_bytes = self._config.host.encode("utf-8")
        port_bytes = str(self._config.port).encode("utf-8")

        lib.run_object_storage_server(name_bytes, port_bytes, self._on_server_ready_fd)

    def wait_until_ready(self) -> None:
        """Blocks until the object storage server is available to server requests."""
        os.eventfd_read(self._on_server_ready_fd)

    @staticmethod
    def _load_library(lib_path) -> Optional[ctypes.CDLL]:
        try:
            return ctypes.CDLL(lib_path)
        except OSError as e:
            return None
