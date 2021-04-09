# project configuration
PROJECT ?= 
CASE ?= 

STARTUP_FILE_PATH ?=
STARTUP = startup_$(PROJECT).S
STARTUP_FILE = $(STARTUP_FILE_PATH)/$(STARTUP)

SYSTEM_FILE_PATH ?= 
SYSTEM = system_$(PROJECT).c
SYSTEM_FILE = $(SYSTEM_FILE_PATH)/$(SYSTEM)

LINKER = link_$(PROJECT).ld
LINKER_FILE_PATH ?= 
LINKER_FILE = $(LINKER_FILE_PATH)/$(LINKER)

# tool configuration
TOOL_DIR = 
ARCH = arm
VENDOR = none
OS = eabi
TOOL_VERSION = $(TOOL_DIR)$(ARCH)-$(VENDOR)-$(OS)

CC = $(TOOL_VERSION)-gcc
OBJDUMP = $(TOOL_VERSION)-objdump
OBJCOPY = $(TOOL_VERSION)-objcopy

# CC configuration
LEVEL = 0
CPU_TYPE = -mcpu=cortex-m0 -DCORTEX_M0
ifeq ($(LEVEL),0)
CXX_FLAGS = -O0 -g
else ifeq ($(LEVEL),1)
CXX_FLAGS = -O2 -g
else ifeq ($(LEVEL),2)
CPPFLAGS = -Os -ffunction-sections -fdata-sections -Wl,--gc-sections
else ifeq ($(LEVEL),3)
CPPFLAGS = -Oz -ffunction-sections -fdata-sections -Wl,--gc-sections
else
CPPFLAGS = -O3 -g
endif

CFLAGS = $(CPU_TYPE) -mthumb $(CPPFLAGS)
LDFLAGS = 

.PHONY: all clean

all:
	# compile case
	$(CC) $(CFLAGS) $(STARTUP_FILE) $(SYSTEM_FILE) -L $(STARTUP_FILE_PATH) -T $(LINKER_FILE) $(CASE).c -o $(CASE).o
	# generate list file
	$(OBJDUMP) -S $(CASE).o > $(CASE).list
	# generate binary file
	$(OBJCOPY) -S $(CASE).o -o binary $(CASE).bin
	# generate hex file
	$(OBJCOPY) -S $(CASE).o -o verilog $(CASE).hex

clean:
	-rm -f $(CASE).o $(CASE).list $(CASE).bin $(CASE).hex