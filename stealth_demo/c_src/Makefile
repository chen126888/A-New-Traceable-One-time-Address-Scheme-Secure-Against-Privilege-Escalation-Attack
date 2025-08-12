# Master Makefile for building multiple cryptographic schemes
.PHONY: all stealth sitaiba clean clean-all help

# Default: build all schemes
all: stealth sitaiba

# Build stealth scheme
stealth:
	@echo "🔐 Building Stealth scheme..."
	@$(MAKE) -C stealth

# Build sitaiba scheme
sitaiba:
	@echo "🔐 Building SITAIBA scheme..."
	@$(MAKE) -C sitaiba

# Clean all schemes
clean:
	@echo "🧹 Cleaning all schemes..."
	@$(MAKE) -C stealth clean
	@if [ -f sitaiba/Makefile ]; then $(MAKE) -C sitaiba clean; fi

# Clean all including libraries
clean-all:
	@echo "🧹 Deep cleaning all schemes..."
	@$(MAKE) -C stealth clean-all
	@if [ -f sitaiba/Makefile ]; then $(MAKE) -C sitaiba clean-all; fi
	@rm -rf ../lib/
	@echo "✅ All artifacts cleaned"

# Test all schemes
test: stealth
	@echo "🧪 Testing all schemes..."
	@$(MAKE) -C stealth test
	@if [ -f sitaiba/Makefile ]; then $(MAKE) -C sitaiba test; fi

# Check all schemes
check: stealth
	@echo "🔍 Checking all schemes..."
	@$(MAKE) -C stealth check
	@if [ -f sitaiba/Makefile ]; then $(MAKE) -C sitaiba check; fi

# Show structure
structure:
	@echo "📁 Multi-scheme project structure:"
	@echo "c_src/"
	@echo "├── Makefile            # This master makefile"
	@echo "├── stealth/"
	@echo "│   ├── stealth_core.c      # Stealth cryptographic core"
	@echo "│   ├── stealth_core.h      # Stealth headers"
	@echo "│   ├── stealth_python_api.c # Stealth Python interface"
	@echo "│   ├── stealth_python_api.h"
	@echo "│   ├── Makefile            # Stealth build system"
	@echo "│   ├── debug_*.py          # Stealth debug scripts"
	@echo "│   └── test_*.py           # Stealth test scripts"
	@echo "├── sitaiba/"
	@echo "│   ├── sitaiba_core.c        # SITAIBA cryptographic core"
	@echo "│   ├── sitaiba_core.h        # SITAIBA headers"
	@echo "│   ├── sitaiba_python_api.c  # SITAIBA Python interface"
	@echo "│   ├── sitaiba_python_api.h"
	@echo "│   ├── Makefile              # SITAIBA build system"
	@echo "│   └── debug_*.c             # SITAIBA debug programs"
	@echo "└── ../lib/"
	@echo "    ├── libstealth.so       # Stealth shared library"
	@echo "    └── libsitaiba.so       # SITAIBA shared library"

# Help
help:
	@echo "🏗️  Multi-Scheme Cryptographic Library Build System"
	@echo ""
	@echo "📚 Available targets:"
	@echo "  all        - Build all schemes (default)"
	@echo "  stealth    - Build only stealth scheme"
	@echo "  sitaiba    - Build only sitaiba scheme"
	@echo "  test       - Run tests for all schemes"
	@echo "  check      - Check all libraries"
	@echo "  clean      - Clean build artifacts"
	@echo "  clean-all  - Deep clean including libraries"
	@echo "  structure  - Show project structure"
	@echo "  help       - Show this help"
	@echo ""
	@echo "🔍 For scheme-specific targets, cd into the scheme directory:"
	@echo "  cd stealth && make help"