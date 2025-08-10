CC = gcc
CFLAGS = -Wall -fPIC -I. -O2
LIBS = -lpbc -lgmp -lcrypto -lssl
OUT = ../lib/libstealth.so

# Source files
CORE_SRC = stealth_core.c
API_SRC = python_api.c
HEADERS = stealth_core.h python_api.h

# Object files
CORE_OBJ = stealth_core.o
API_OBJ = python_api.o

# Main target: build the shared library
all: $(OUT)

$(OUT): $(CORE_OBJ) $(API_OBJ)
	@mkdir -p ../lib
	$(CC) $(CFLAGS) -shared -o $(OUT) $(CORE_OBJ) $(API_OBJ) $(LIBS)
	@echo "✅ Shared library built: $(OUT)"
	@echo "📁 Architecture: Core ($(CORE_SRC)) + API ($(API_SRC))"

# Compile core cryptographic functions
$(CORE_OBJ): $(CORE_SRC) stealth_core.h
	$(CC) $(CFLAGS) -c $(CORE_SRC) -o $(CORE_OBJ)
	@echo "🔐 Core cryptographic functions compiled"

# Compile Python API layer
$(API_OBJ): $(API_SRC) python_api.h stealth_core.h
	$(CC) $(CFLAGS) -c $(API_SRC) -o $(API_OBJ)
	@echo "🐍 Python API interface compiled"

# Optional: build a test executable for debugging
test: test_stealth
	./test_stealth ../param/a.param

test_stealth: test_main.c $(CORE_OBJ) $(API_OBJ)
	$(CC) $(CFLAGS) -o test_stealth test_main.c $(CORE_OBJ) $(API_OBJ) $(LIBS)
	@echo "✅ Test executable built: test_stealth"

# Check if library loads correctly
check: $(OUT)
	@echo "🔍 Checking library..."
	@ldd $(OUT) 2>/dev/null || echo "❌ Library dependencies missing"
	@echo "📊 Library info:"
	@file $(OUT)
	@ls -la $(OUT)
	@echo "✅ Library check complete"

# Debug: show what symbols are exported
symbols: $(OUT)
	@echo "🔍 Exported symbols:"
	@nm -D $(OUT) | grep " T " | grep stealth || echo "No stealth symbols found"

# Clean build artifacts
clean:
	rm -f *.o $(OUT) test_stealth
	@echo "🧹 Cleaned build artifacts"

# Install library (optional)
install: $(OUT)
	sudo cp $(OUT) /usr/local/lib/
	sudo ldconfig
	@echo "📦 Library installed to /usr/local/lib/"

# Development help
help:
	@echo "📚 Available targets:"
	@echo "  all      - Build shared library (default)"
	@echo "  test     - Build and run test executable"
	@echo "  check    - Check library dependencies and info"
	@echo "  symbols  - Show exported function symbols"
	@echo "  clean    - Remove build artifacts"
	@echo "  install  - Install library system-wide"
	@echo "  help     - Show this help"
	@echo ""
	@echo "📁 Project structure:"
	@echo "  $(CORE_SRC)  - Core cryptographic functions"
	@echo "  $(API_SRC)   - Python interface layer"
	@echo "  $(HEADERS)    - Header files"

# Show project structure
structure:
	@echo "📁 Current project structure:"
	@echo "c_src/"
	@echo "├── $(CORE_SRC)      # Core cryptographic functions"
	@echo "├── my_scheme_core.h    # Core function declarations"
	@echo "├── $(API_SRC)       # Python interface functions"
	@echo "├── python_api.h        # Python interface declarations"
	@echo "├── Makefile            # This makefile"
	@echo "└── test_main.c         # Test program (optional)"
	@echo ""
	@echo "Generated:"
	@echo "└── ../lib/$(notdir $(OUT))  # Compiled shared library"

.PHONY: all test check symbols clean install help structure