CC = gcc
CFLAGS = -Wall -fPIC -I. -O2
LIBS = -lpbc -lgmp -lcrypto -lssl
OUT = ../../lib/libsitaiba.so

# Source files
CORE_SRC = sitaiba_core.c
API_SRC = python_api.c
HEADERS = sitaiba_core.h python_api.h

# Object files
CORE_OBJ = sitaiba_core.o
API_OBJ = python_api.o

# Main target: build the shared library
all: $(OUT)

$(OUT): $(CORE_OBJ) $(API_OBJ)
	@mkdir -p ../lib
	$(CC) $(CFLAGS) -shared -o $(OUT) $(CORE_OBJ) $(API_OBJ) $(LIBS)
	@echo "✅ SITAIBA shared library built: $(OUT)"
	@echo "📁 Architecture: Core ($(CORE_SRC)) + API ($(API_SRC))"

# Compile core cryptographic functions
$(CORE_OBJ): $(CORE_SRC) sitaiba_core.h
	$(CC) $(CFLAGS) -c $(CORE_SRC) -o $(CORE_OBJ)
	@echo "🔐 SITAIBA core cryptographic functions compiled"

# Compile Python API layer
$(API_OBJ): $(API_SRC) python_api.h sitaiba_core.h
	$(CC) $(CFLAGS) -c $(API_SRC) -o $(API_OBJ)
	@echo "🐍 SITAIBA Python API interface compiled"

# Optional: build a test executable for debugging
test: test_sitaiba_core
	./test_sitaiba_core ../param/pbc/a.param

test_sitaiba_core: test_sitaiba_core.c $(CORE_OBJ)
	$(CC) $(CFLAGS) -o test_sitaiba_core test_sitaiba_core.c $(CORE_OBJ) $(LIBS)
	@echo "✅ SITAIBA core test executable built: test_sitaiba_core"

# Legacy test (if test_main.c exists)
test_sitaiba: test_main.c $(CORE_OBJ) $(API_OBJ)
	$(CC) $(CFLAGS) -o test_sitaiba test_main.c $(CORE_OBJ) $(API_OBJ) $(LIBS)
	@echo "✅ SITAIBA test executable built: test_sitaiba"

# Check if library loads correctly
check: $(OUT)
	@echo "🔍 Checking SITAIBA library..."
	@ldd $(OUT) 2>/dev/null || echo "❌ Library dependencies missing"
	@echo "📊 Library info:"
	@file $(OUT)
	@ls -la $(OUT)
	@echo "✅ SITAIBA library check complete"

# Debug: show what symbols are exported
symbols: $(OUT)
	@echo "🔍 Exported SITAIBA symbols:"
	@nm -D $(OUT) | grep " T " | grep sitaiba || echo "No sitaiba symbols found"

# Clean build artifacts
clean:
	rm -f *.o $(OUT) test_sitaiba test_sitaiba_core
	@echo "🧹 Cleaned SITAIBA build artifacts"

# Install library (optional)
install: $(OUT)
	sudo cp $(OUT) /usr/local/lib/
	sudo ldconfig
	@echo "📦 SITAIBA library installed to /usr/local/lib/"

# Development help
help:
	@echo "📚 Available SITAIBA targets:"
	@echo "  all      - Build SITAIBA shared library (default)"
	@echo "  test     - Build and run SITAIBA test executable"
	@echo "  check    - Check library dependencies and info"
	@echo "  symbols  - Show exported function symbols"
	@echo "  clean    - Remove build artifacts"
	@echo "  install  - Install library system-wide"
	@echo "  help     - Show this help"
	@echo ""
	@echo "📁 Project structure:"
	@echo "  $(CORE_SRC)  - SITAIBA core cryptographic functions"
	@echo "  $(API_SRC)   - Python interface layer"
	@echo "  $(HEADERS)    - Header files"

# Show project structure
structure:
	@echo "📁 Current SITAIBA project structure:"
	@echo "c_src/sitaiba/"
	@echo "├── $(CORE_SRC)      # Core SITAIBA cryptographic functions"
	@echo "├── sitaiba_core.h      # Core function declarations"
	@echo "├── $(API_SRC)       # Python interface functions"
	@echo "├── python_api.h        # Python interface declarations"
	@echo "├── sitaiba.c           # Original implementation (reference)"
	@echo "├── Makefile            # This makefile"
	@echo "└── test_main.c         # Test program (optional)"
	@echo ""
	@echo "Generated:"
	@echo "└── ../lib/$(notdir $(OUT))  # Compiled SITAIBA shared library"

# Performance test with original sitaiba.c (for comparison)
test_original: sitaiba.c
	$(CC) -O2 -o test_original sitaiba.c $(LIBS)
	@echo "✅ Original SITAIBA test built: test_original"
	@echo "🧪 Run with: ./test_original ../param/pbc/a.param"

.PHONY: all test check symbols clean install help structure test_original