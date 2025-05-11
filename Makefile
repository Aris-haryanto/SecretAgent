PYTHON = python3
PYINSTALLER = pyinstaller
SCRIPT = main.py
OUTPUT_DIR = dist
BUILD_DIR = build
BINARY_NAME = SecretAgent

.PHONY: all clean build run

all: clean build

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(OUTPUT_DIR) $(BUILD_DIR) $(BINARY_NAME).spec
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.spec" -exec rm -f {} +

# Build standalone binary using PyInstaller
build:
	@echo "Building standalone binary $(BINARY_NAME) for Apple Silicon (arm64)..."
# Make sure to run this on Apple Silicon macOS with an arm64 Python environment
	$(PYINSTALLER) --onefile --name $(BINARY_NAME) $(SCRIPT)
	@echo "Build complete! Find the binary at $(OUTPUT_DIR)/$(BINARY_NAME)"

# Run the standalone binary with sample startup arguments
run: build
	@echo "Running $(BINARY_NAME) with startup arguments..."
	./$(OUTPUT_DIR)/$(BINARY_NAME) --startup
