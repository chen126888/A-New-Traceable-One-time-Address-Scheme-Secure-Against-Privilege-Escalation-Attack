CC = gcc
CFLAGS = -Wall -fPIC -I. -O2
LIBS = -lpbc -lgmp -lcrypto -lssl
OUT = ../../lib/libstealth.so

# Source files
CORE_SRC = stealth_core.c
API_SRC = stealth_python_api.c
HEADERS = stealth_core.h stealth_python_api.h

# Object files
CORE_OBJ = stealth_core.o
API_OBJ = stealth_python_api.o

# Main target: build the shared library
all: $(OUT)

$(OUT): $(CORE_OBJ) $(API_OBJ)
	@mkdir -p ../../lib
	$(CC) $(CFLAGS) -shared -o $(OUT) $(CORE_OBJ) $(API_OBJ) $(LIBS)
	@echo "✅ Stealth shared library built: $(OUT)"
	@echo "📁 Architecture: Core ($(CORE_SRC)) + API ($(API_SRC))"

# Compile core cryptographic functions
$(CORE_OBJ): $(CORE_SRC) stealth_core.h
	$(CC) $(CFLAGS) -c $(CORE_SRC) -o $(CORE_OBJ)
	@echo "🔐 Stealth core cryptographic functions compiled"

# Compile Python API layer
$(API_OBJ): $(API_SRC) stealth_python_api.h stealth_core.h
	$(CC) $(CFLAGS) -c $(API_SRC) -o $(API_OBJ)
	@echo "🐍 Stealth Python API interface compiled"

# Test the library
test: test_stealth
	./test_stealth ../../param/a.param

test_stealth: test_main.c $(CORE_OBJ) $(API_OBJ)
	$(CC) $(CFLAGS) -o test_stealth test_main.c $(CORE_OBJ) $(API_OBJ) $(LIBS)
	@echo "✅ Stealth test executable built"

# Debug with existing debug scripts
debug: $(OUT)
	@echo "🔍 Running stealth debug scripts..."
	@python3 debug_advanced.py
	
debug-flask: $(OUT)
	@echo "🔍 Running stealth Flask debug..."
	@python3 debug_flask_app.py

test-lib: $(OUT)
	@echo "🔍 Running stealth library test..."
	@python3 test_library.py

# Check if library loads correctly
check: $(OUT)
	@echo "🔍 Checking stealth library..."
	@ldd $(OUT) 2>/dev/null || echo "❌ Library dependencies missing"
	@echo "📊 Stealth library info:"
	@file $(OUT)
	@ls -la $(OUT)
	@echo "✅ Stealth library check complete"

# Debug: show what symbols are exported
symbols: $(OUT)
	@echo "🔍 Exported stealth symbols:"
	@nm -D $(OUT) | grep " T " | grep stealth || echo "No stealth symbols found"

# Clean build artifacts
clean:
	rm -f *.o test_stealth
	@echo "🧹 Cleaned stealth build artifacts"

# Clean including library
clean-all: clean
	rm -f $(OUT)
	@echo "🧹 Cleaned all stealth artifacts including library"

# Development help
help:
	@echo "📚 Stealth scheme build targets:"
	@echo "  all       - Build stealth shared library (default)"
	@echo "  test      - Build and run test executable"
	@echo "  debug     - Run advanced debug script"
	@echo "  debug-flask - Run Flask debug script"  
	@echo "  test-lib  - Run library test script"
	@echo "  check     - Check library dependencies and info"
	@echo "  symbols   - Show exported function symbols"
	@echo "  clean     - Remove build artifacts"
	@echo "  clean-all - Remove all artifacts including library"
	@echo "  help      - Show this help"

.PHONY: all test debug debug-flask test-lib check symbols clean clean-all help