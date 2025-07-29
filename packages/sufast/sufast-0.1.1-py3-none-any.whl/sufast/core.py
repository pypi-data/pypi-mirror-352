import ctypes
import json
import warnings
import os

class App:
    def __init__(self, dll_path=None):
        self.routes = {method: {} for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]}
        self.dll_path = dll_path or self._find_dll()

    def _find_dll(self):
        """Auto-locate the sufast_server.dll in common relative locations"""
        candidates = [
            './sufast_server.dll'
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def _load_sufast_lib(self):
        """Load sufast_server.dll with safe error reporting"""
        if not self.dll_path:
            raise FileNotFoundError(
                "❌ sufast_server.dll not found. You can also set it manually: SufastApp(dll_path='path/to/sufast_server.dll')"
            )
        try:
            lib = ctypes.CDLL(os.path.abspath(self.dll_path))

            # Configure route setter
            lib.set_routes.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t]
            lib.set_routes.restype = ctypes.c_bool

            # Configure server starter
            lib.start_server.argtypes = [ctypes.c_bool, ctypes.c_uint16]
            lib.start_server.restype = ctypes.c_bool

            return lib
        except OSError as e:
            raise ImportError(
                f"❌ Failed to load sufast_server.dll at {self.dll_path}: {str(e)}\n"
                "💡 Check: 1) DLL exists  2) Architecture match (32/64-bit)  3) Dependencies are installed"
            ) from e

    def _register(self, method, path, handler):
        """Immediately execute and store static handler output for the route"""
        try:
            result = handler()
            self.routes[method][path] = json.dumps(result) if not isinstance(result, str) else result
        except Exception as e:
            error_msg = f"⚠️ Handler error for {method} {path}: {e}"
            self.routes[method][path] = json.dumps({"error": error_msg})
            warnings.warn(error_msg)

    # Decorator methods for each HTTP verb
    def get(self, path): return self._decorator("GET", path)
    def post(self, path): return self._decorator("POST", path)
    def put(self, path): return self._decorator("PUT", path)
    def patch(self, path): return self._decorator("PATCH", path)
    def delete(self, path): return self._decorator("DELETE", path)

    def _decorator(self, method, path):
        def decorator(func):
            self._register(method, path, func)
            return func
        return decorator

    def run(self, port=8080, production=False):
        """Launch the Sufast server with all registered routes"""
        lib = self._load_sufast_lib()

        # Encode routes to JSON
        json_routes = json.dumps(self.routes).encode('utf-8')
        buffer = (ctypes.c_ubyte * len(json_routes)).from_buffer_copy(json_routes)

        print("\n🔧 Booting up ⚡ sufast web server engine...\n")
        print(f"🌐 Mode     : {'🔒 Production' if production else '🧪 Development'}")
        print(f"🛣️  Routes   : {sum(len(r) for r in self.routes.values())} registered")
        print(f"🚪 Port     : {port}")
        print("🟢 Status   : Server is up and running!")
        print(f"➡️  Visit    : http://localhost:{port}")
        print("🔄 Press Ctrl+C to stop the server.\n")

        if not production:
            print(f"🔗 Listening on: http://localhost:{port}")

        # Send routes to Rust
        if not lib.set_routes(buffer, len(json_routes)):
            raise RuntimeError("❌ sufast_server failed to accept route configuration.")

        # Start server from DLL
        if not lib.start_server(production, port):
            raise RuntimeError("❌ sufast_server failed to start.")

        try:
            while True:
                pass  # Block main thread
        except KeyboardInterrupt:
            print("🛑 Server stopped by user.")
        except Exception as e:
            print(f"🔥 Unexpected error: {str(e)}")
