CC = gcc
CFLAGS = -Wall -fPIC -I. -O2
LIBS = -lpbc -lgmp -lcrypto -lssl
OUT = ../../lib/libmy_stealth.so

# Source files
CORE_SRC = my_scheme_core.c
API_SRC = python_api.c
HEADERS = my_scheme_core.h python_api.h

# Object files
CORE_OBJ = my_scheme_core.o
API_OBJ = python_api.o

# Main target: build the shared library
all: $(OUT)

$(OUT): $(CORE_OBJ) $(API_OBJ)
	@mkdir -p ../../lib
	$(CC) $(CFLAGS) -shared -o $(OUT) $(CORE_OBJ) $(API_OBJ) $(LIBS)
	@echo "✅ My Stealth library built: $(OUT)"
	@echo "📁 Architecture: Core ($(CORE_SRC)) + API ($(API_SRC))"

# Compile core cryptographic functions
$(CORE_OBJ): $(CORE_SRC) my_scheme_core.h
	$(CC) $(CFLAGS) -c $(CORE_SRC) -o $(CORE_OBJ)
	@echo "🔐 My Stealth core functions compiled"

# Compile Python API layer
$(API_OBJ): $(API_SRC) python_api.h my_scheme_core.h
	$(CC) $(CFLAGS) -c $(API_SRC) -o $(API_OBJ)
	@echo "🐍 My Stealth Python API compiled"

# Clean build artifacts
clean:
	rm -f *.o $(OUT)
	@echo "🧹 My Stealth cleaned"

# Check if library loads correctly
check: $(OUT)
	@echo "🔍 Checking My Stealth library..."
	@ldd $(OUT) 2>/dev/null || echo "❌ Library dependencies missing"
	@echo "📊 Library info:"
	@file $(OUT)
	@ls -la $(OUT)
	@echo "✅ My Stealth library check complete"

# Debug: show what symbols are exported
symbols: $(OUT)
	@echo "🔍 My Stealth exported symbols:"
	@nm -D $(OUT) | grep " T " | grep stealth || echo "No stealth symbols found"

.PHONY: all clean check symbols