"""
Harvester scripts

Currently only supports AVR atdf files
"""
# Python 3 compatibility for Python 2
from __future__ import print_function

import collections
import argparse
import textwrap
import ast
from xml.etree import ElementTree
from xml.dom import minidom
from datetime import datetime

from pymcuprog.deviceinfo.memorynames import MemoryNames
from pymcuprog.deviceinfo.deviceinfokeys import DeviceMemoryInfoKeys, DeviceInfoKeysAvr
from pymcuprog.deviceinfo.configgenerator import add_register, make_register, add_data, add_comment

# High voltage implementations as defined on https://confluence.microchip.com/x/XVxcE
HV_IMPLEMENTATION_SHARED_UPDI = "0"
HV_IMPLEMENTATION_DEDICATED_UPDI = "1"
HV_IMPLEMENTATION_SEPARATE_PIN = "2"
HV_IMPLEMENTATION_UPDI_HANDSHAKE = "3"

# NVM variants using Paged writes, i.e. page buffer
# Note that these variants are the NVMCTRL variants in the atdf files and not the NVM variants given in the SIB
# nvm_ctrl_avr_v2: SIB variant P:0 - tiny0, 1, 2, mega0
# nvm_ctrl_avr_v3: SIB variant P:3 - EA and P:5 - EB
NVM_VARIANTS_PAGED = ['nvm_ctrl_avr_v2', 'nvm_ctrl_avr_v3']

def map_atdf_memory_name_to_pymcuprog_name(atdf_name):
    """
    Mapping a memory name in atdf files to the corresponding memory name used in the pymcuprog device models

    Note that the same memory can have different names in the same atdf file depending on the element used as
    definition, i.e. memory-segment element or module element
    :param atdf_name: Name of memory in atdf files
    :return: Name of memory in pymcuprog device models
    """
    pymcuprog_name = 'unknown'
    atdf_name = atdf_name.lower()
    if atdf_name == 'progmem':
        pymcuprog_name = MemoryNames.FLASH
    if atdf_name in ['user_signatures', 'userrow']:
        # Datasheets actually use user_row for UPDI devices at least
        pymcuprog_name = MemoryNames.USER_ROW
    if atdf_name == 'bootrow':
        pymcuprog_name = MemoryNames.BOOT_ROW
    if atdf_name == 'eeprom':
        pymcuprog_name = MemoryNames.EEPROM
    if atdf_name in ['fuses', 'fuse']:
        pymcuprog_name = MemoryNames.FUSES
    if atdf_name in ['lockbits', 'lock']:
        pymcuprog_name = MemoryNames.LOCKBITS
    if atdf_name in ['signatures', 'sigrow']:
        pymcuprog_name = MemoryNames.SIGNATURES
    if atdf_name == 'internal_sram':
        pymcuprog_name = MemoryNames.INTERNAL_SRAM

    return pymcuprog_name

def determine_chiperase_effect(memoryname, architecture):
    """
    Determine if memory is erased by a chip erase

    :param memoryname: Name of memory as defined in pymcuprog.deviceinfo.memorynames
    :type memoryname: string
    :param architecture: Architecture as defined in atdf file
    :type architecture: string
    :return: Chip erase effect
    :rtype: string
    """
    if 'avr' in architecture:
        if memoryname in [MemoryNames.USER_ROW, MemoryNames.FUSES, MemoryNames.SIGNATURES, MemoryNames.INTERNAL_SRAM]:
            return 'ChiperaseEffect.NOT_ERASED'
        elif memoryname in [MemoryNames.LOCKBITS, MemoryNames.FLASH]:
            return 'ChiperaseEffect.ALWAYS_ERASED'
        elif memoryname in [MemoryNames.EEPROM, MemoryNames.BOOT_ROW]:
            return 'ChiperaseEffect.CONDITIONALLY_ERASED_AVR'

    return '# To be filled in manually'

def determine_isolated_erase(memoryname, architecture):
    """
    Determine if memory can be erased without side effects

    :param memoryname: Name of memory as defined in pymcuprog.deviceinfo.memorynames
    :type memoryname: string
    :param architecture: Architecture as defined in atdf file
    :type architecture: string
    :return: 'True' if memory can be erased in isolation, 'False' if not.
    :rtype: string
    """
    if 'avr' in architecture:
        if 'avr8x' in architecture and memoryname in [MemoryNames.FLASH]:
            # UPDI devices now supports isolated erase for flash
            return 'True'
        if memoryname in [MemoryNames.USER_ROW, MemoryNames.EEPROM, MemoryNames.BOOT_ROW]:
            return 'True'
        elif memoryname in [MemoryNames.INTERNAL_SRAM, MemoryNames.LOCKBITS, MemoryNames.FLASH, MemoryNames.FUSES, MemoryNames.SIGNATURES]:
            return 'False'

    return '# To be filled in manually'

def determine_write_size(memoryname, pagesize, devicename, nvm_variant):
    """
    Determine write granularity for memory

    :param memoryname: Name of memory as defined in pymcuprog.deviceinfo.memorynames
    :type memoryname: string
    :param pagesize: Page size of memory
    :type pagesize: string or int
    :param nvm_variant: Which NVM variant is used in the device
    :type nvm_variant: string
    :return: Write granularity as string
    :rtype: string
    """
    write_size = "0x01"
    devicename = devicename.lower()
    if memoryname == 'flash':
        if nvm_variant in NVM_VARIANTS_PAGED:
            write_size = pagesize
        else:
            write_size = "0x02"
    if memoryname == "user_row":
        if devicename.find('avr') != -1 and devicename.find('ea') != -1:
            # For AVR EA user row the complete page must be written
            write_size = pagesize
    elif memoryname == 'signatures':
        write_size = "0x00"
    return write_size

def determine_read_size(memoryname):
    """
    Determine read granularity for memory

    :param memoryname: Name of memory as defined in pymcuprog.deviceinfo.memorynames
    :type memoryname: string
    :return: Read granularity as string
    :rtype: string
    """
    # Read size is always 1 byte except for flash that can only read complete words
    readsize = "0x01"
    if memoryname in [MemoryNames.FLASH]:
        readsize = "0x02"

    return readsize

def capture_memory_segment_attributes(attributes, memories):
    """
    Capture memory attributes for memory segment

    :param attributes: Memory attributes to capture (from atdf)
    :type attributes: class:`xml.etree.ElementTree.Element`
    :param memories: Dictionary with memory information. Captured data will be added to this dict.
    :type memories: dict
    """
    name = attributes['name'].lower()
    size = attributes['size']
    start = attributes['start']

    try:
        pagesize = attributes['pagesize']
    except KeyError:
        pagesize = "0x01"
    # For some AVRs the ATDF gives a pagesize of fuses and lockbits equal to flash or EEPROM page size but fuses and
    # lockbits are always byte accessible.
    if name in ['fuses', 'lockbits']:
        pagesize = '0x01'

    # These names are the names used in the atdf files and might differ from the pymcuprog MemoryNames
    if map_atdf_memory_name_to_pymcuprog_name(name) != 'unknown':
        print_name = map_atdf_memory_name_to_pymcuprog_name(name)
        if not print_name in memories:
            memories[print_name] = {}
            memories[print_name][DeviceMemoryInfoKeys.ADDRESS] = start
            memories[print_name][DeviceMemoryInfoKeys.SIZE] = size
            memories[print_name][DeviceMemoryInfoKeys.PAGE_SIZE] = pagesize

def capture_register_offset(name, offset):
    """
    Wrapper to create a string definition

    :param name: register name
    :type name: string
    :param offset: register offset
    :type offset: string
    :return: string of register and offset
    :rtype: string
    """
    return capture_field(f"{name.lower()}_base", offset)


def capture_field(field, value):
    """
    Macro to create text format field

    :param field: register name
    :type field: string
    :param value: register value
    :type value: string
    :return: string of definition
    :rtype: string
    """
    try:
        _test_value = int(value, 16)
    except (ValueError, AttributeError):
        # Can't convert string to int, assumed to be string
        return f"    '{field}': '{value}',\n"
    return F"    '{field}': {value},\n"

def capture_device_data_from_device_element(element):
    """
    Capture device data from a device element

    :param element: element with tag='device'
    :type element: class`xml.etree.ElementTree.Element`
    :return: captured data from the device element as a string
    :rtype: string
    """
    architecture = element.attrib['architecture'].lower()
    output = capture_field('name', element.attrib['name'].lower())
    output += capture_field('architecture', architecture)
    return output

def capture_memory_segments_from_device_element(element, memories):
    """
    Capture memory segment data from a device element

    :param element: element with tag='device'
    :type element: class:`xml.etree.ElementTree.Element instance`
    :return: captured data from the device element as a string
    :rtype: string
    """
    output = ""
    for i in element.iterfind("address-spaces/address-space/memory-segment"):
        capture_memory_segment_attributes(i.attrib, memories)
    return output

def capture_module_element(element):
    """
    Capture data from a module element

    This function will return data captured from the module element but will also check if the module
    element contains info about an UPDI fuse (fuse to configure a shared UPDI pin)
    :param element: element with tag='module'
    :type element: class:`xml.etree.ElementTree.Element`
    :return: tuple of
    * output - captured module element data as a string
    * found_updi_fuse - True if the module element contained info about an UPDI fuse
    :rtype: tuple
    """
    output = ""
    found_updi_fuse = False
    for i in element.iterfind("instance/register-group"):
        name = i.attrib['name']
        offset = f"0x{int(i.attrib['offset'], 16):08X}"
        if i.attrib['name'] == 'SYSCFG':
            output += capture_register_offset(name, offset)
            output += capture_register_offset('OCD', f"0x{int(offset, 16) + 0x80:08X}")
        if i.attrib['name'] == 'NVMCTRL':
            output += capture_register_offset(name, offset)
    for i in element.iterfind("instance/signals/signal"):
        if i.attrib['group'] == 'UPDI' and i.attrib['pad'] is not None:
            output += capture_field('prog_clock_khz', '900')
            found_updi_fuse = True
    return output, found_updi_fuse

def capture_memory_module_element(element, memories):
    """
    Capture memory information from a memory module element

    :param element: Element with tag='module'
    :type element: class:`xml.etree.ElementTree.Element`
    :param memories: Dictionary with memory information. Captured memory information will be added to this
        dictionary
    :type memories: dict
    """
    memoryname = map_atdf_memory_name_to_pymcuprog_name(element.attrib['name'])
    if not memoryname in memories:
        # Discovered new memory, add it to the dictionary
        memories[memoryname] = {}
        # All memories defined as memory modules in the device element can be read and written a single byte at a time
        memories[memoryname][DeviceMemoryInfoKeys.READ_SIZE] = "0x01"
        memories[memoryname][DeviceMemoryInfoKeys.PAGE_SIZE] = "0x01"
        if memoryname in ['sigrow']:
            # Signatures can't be written at all
            memories[memoryname][DeviceMemoryInfoKeys.WRITE_SIZE] = "0x00"
        else:
            memories[memoryname][DeviceMemoryInfoKeys.WRITE_SIZE] = "0x01"
    for rg in element.iterfind("instance/register-group"):
        # Offset is found in the module instance register group
        memories[memoryname][DeviceMemoryInfoKeys.ADDRESS] = rg.attrib['offset']
    for rg in element.iterfind("register-group"):
        # Size is found in the module register group
        if 'size' in rg.attrib:
            memories[memoryname][DeviceMemoryInfoKeys.SIZE] = rg.attrib['size']
            if memoryname in [MemoryNames.USER_ROW]:
                # For user row set the page size equal to the size since this makes most sense when printing memory
                # content and when erasing, even though the write granularity is one byte
                memories[memoryname][DeviceMemoryInfoKeys.PAGE_SIZE] = rg.attrib['size']
            elif memoryname in [MemoryNames.FUSES]:
                # For fuses there might be some fuse registers with size bigger than one.
                # The register-group size only counts number of registers so each register size must be checked to find
                # total size in bytes
                for reg in rg:
                    regsize = int(reg.attrib['size'], 0)
                    print(f"REGSIZE: {regsize}")
                    if regsize > 1:
                        memories[memoryname][DeviceMemoryInfoKeys.SIZE] = f"0x{int(memories[memoryname][DeviceMemoryInfoKeys.SIZE], 0) + (regsize - 1):X}"

        else:
            memories[memoryname][DeviceMemoryInfoKeys.SIZE] = "UNKNOWN"

def capture_signature_from_property_groups_element(element):
    """
    Capture signature (Device ID) data from a property-group element

    :param element: element with tag='property-groups'
    :type element: class:`xml.etree.ElementTree.Element instance`
    :return: bytearray with 3 bytes of Device ID data
    :rtype: bytearray
    """
    signature = bytearray(3)
    for i in element.findall('property-group/property'):
        if i.attrib['name'] == 'SIGNATURE0':
            signature[0] = int(i.attrib['value'], 16)
        if i.attrib['name'] == 'SIGNATURE1':
            signature[1] = int(i.attrib['value'], 16)
        if i.attrib['name'] == 'SIGNATURE2':
            signature[2] = int(i.attrib['value'], 16)
    return signature

def capture_nvm_version_from_nvmctrl_module(element):
    """Capture NVM controller variant from module element

    :param element: element with tag='module'
    :type element: class:`xml.etree.ElementTree.Element instance`
    """

    return element.attrib['id'].lower()

def get_flash_offset(element):
    """
    Fetch flash memory offset from element

    :param element: Element with tag='property-groups'
    :type element: class:`xml.etree.ElementTree.Element instance`
    :return: Flash offset as string
    :rtype: string
    """
    flash_offset = "0x00000000"
    for i in element.iterfind("property-group/property"):
        if i.attrib['name'] == 'PROGMEM_OFFSET':
            flash_offset = i.attrib['value']
    return flash_offset

def get_hv_implementation(element):
    """
    Fetch High Voltage implementation from element

    :param element: Element with tag='property-groups'
    :type element: class:`xml.etree.ElementTree.Element instance`
    :return: High Voltage implementation as string (defined on https://confluence.microchip.com/x/XVxcE)
    :rtype: string
    """
    hv_implementation = None
    for i in element.iterfind("property-group/property"):
        if i.attrib['name'] == 'HV_IMPLEMENTATION':
            hv_implementation = i.attrib['value']

    return hv_implementation

def determine_address_size(flash_offset):
    """
    Determine number of address bits needed for Flash

    :param flash_offset: Flash offset from atdf
    :type flash_offset: string
    :return: Address size ('16-bit' or '24-bit')
    :rtype: string
    """
    address_size = '16-bit'
    if flash_offset is not None:
        flash_offset = int(flash_offset, 16)
        if flash_offset > 0xFFFF:
            address_size = '24-bit'
    return address_size

def harvest_from_file(filename):
    """
    Harvest parameters from a file

    :param filename: Path to file to parse
    :type filename: string
    :return: deviceinfo, device_config
    :rtype: string, string
    """
    xml_iter = ElementTree.iterparse(filename)
    deviceinfo = ""
    device_fields = ""
    extra_fields_comment = "# Some extra AVR specific fields"
    extra_fields = f"\n    {extra_fields_comment}\n"

    shared_updi = False
    progmem_offset = None
    hv_implementation = None
    memories = {}
    for event, elem in xml_iter:
        if event == 'end':
            if elem.tag == 'device':
                devicename = elem.attrib['name']
                # Note module elements are part of the device element so the memories represented by modules will
                # already be collected when reaching end of device element
                capture_memory_segments_from_device_element(elem, memories)
                device_fields += capture_device_data_from_device_element(elem)
                architecture = elem.attrib['architecture'].lower()
            if elem.tag == 'module':
                # Some memories are defined as module elements (in addition to memory segments). These module
                # definitions are preferred as they give more accurate size definitions for some memories like fuses
                # and lockbits.
                if elem.attrib['name'].lower() in ['sigrow', 'fuse', 'lock', 'userrow']:
                    capture_memory_module_element(elem, memories)
                elif elem.attrib['name'].lower() == 'nvmctrl':
                    nvm_variant = capture_nvm_version_from_nvmctrl_module(elem)
                module, found_updi_fuse = capture_module_element(elem)
                extra_fields += module
                if found_updi_fuse:
                    shared_updi = True
            if elem.tag == 'interface':
                device_fields += capture_field(elem.tag, elem.attrib['name'])
            if elem.tag == 'property-groups':
                signature = capture_signature_from_property_groups_element(elem)
                progmem_offset = get_flash_offset(elem)
                hv_implementation = get_hv_implementation(elem)

    extra_fields += capture_field('address_size', determine_address_size(progmem_offset))
    if not shared_updi:
        extra_fields += capture_field(DeviceInfoKeysAvr.PROG_CLOCK_KHZ, '1800')

    hv_comment = None
    if not hv_implementation:
        if shared_updi:
            hv_implementation = HV_IMPLEMENTATION_SHARED_UPDI
            hv_comment = f"    # Missing hv_implementation property in ATDF file\n    # Defaulting to {hv_implementation} for devices with UPDI fuse\n"
        else:
            hv_implementation = HV_IMPLEMENTATION_DEDICATED_UPDI
            hv_comment = f"    # Missing hv_implementation property in ATDF file\n    # Defaulting to {hv_implementation} for devices without UPDI fuse\n"

    if hv_comment:
        extra_fields += hv_comment
    extra_fields += capture_field(DeviceInfoKeysAvr.HV_IMPLEMENTATION, hv_implementation)


    extra_fields += capture_field(DeviceInfoKeysAvr.DEVICE_ID,
                            f"0x{signature[0]:02X}{signature[1]:02X}{signature[2]:02X}")

    # Replace "flash start" with "progmem_offset"
    if progmem_offset and int(progmem_offset, 16) > 0:
        memories[MemoryNames.FLASH][DeviceMemoryInfoKeys.ADDRESS] = progmem_offset

    # Build the deviceinfo
    deviceinfo += device_fields
    sorted_memories = collections.OrderedDict(sorted(memories.items()))
    for memory in sorted_memories:
        deviceinfo += f"\n    # {memory}\n"
        deviceinfo += capture_field(f"{memory}_{DeviceMemoryInfoKeys.ADDRESS}_byte",
                                sorted_memories[memory][DeviceMemoryInfoKeys.ADDRESS])
        deviceinfo += capture_field(f"{memory}_{DeviceMemoryInfoKeys.SIZE}_bytes",
                                sorted_memories[memory][DeviceMemoryInfoKeys.SIZE])
        deviceinfo += capture_field(f"{memory}_{DeviceMemoryInfoKeys.PAGE_SIZE}_bytes",
                                sorted_memories[memory][DeviceMemoryInfoKeys.PAGE_SIZE])
        deviceinfo += f"    '{memory}_{DeviceMemoryInfoKeys.READ_SIZE}_bytes': {determine_read_size(memory)},\n"
        writesize = determine_write_size(memory, sorted_memories[memory][DeviceMemoryInfoKeys.PAGE_SIZE], devicename, nvm_variant)
        deviceinfo += f"    '{memory}_{DeviceMemoryInfoKeys.WRITE_SIZE}_bytes': {writesize},\n"
        deviceinfo += f"    '{memory}_{DeviceMemoryInfoKeys.CHIPERASE_EFFECT}': {determine_chiperase_effect(memory, architecture)},\n"
        deviceinfo += f"    '{memory}_{DeviceMemoryInfoKeys.ISOLATED_ERASE}': {determine_isolated_erase(memory, architecture)},\n"

    deviceinfo += extra_fields

    # Generate dictionary with the extra info from the harvested device info
    extrainfo_string = deviceinfo.split(f"{extra_fields_comment}\n")[1]
    extrainfo_string = f"{{\n{extrainfo_string}}}"

    extrainfo = ast.literal_eval(extrainfo_string)


    config = generate_config_xml(devicename, extrainfo, memories)

    return deviceinfo, config

def generate_config_xml(devicename, extrainfo, memories):
    """Build device-config xml file content

    :return: Device config XML content as string
    :rtype: string
    """

    config = ''

    # Construct the root
    deviceconf = ElementTree.Element("deviceconf")
    deviceconf.attrib["name"] = devicename.upper()
    now = datetime.now().strftime("%Y.%m.%d, %H:%M:%S")
    comment = ElementTree.Comment(f"device config for {devicename} generated {now}")
    deviceconf.append(comment)

    # Construct basic version info:
    # These values are hardcoded, and thus need to be updated when the spec updates :/
    # It would be nice to fetch them from somewhere...
    add_register(deviceconf, "DEVICE_CONFIG_MAJOR", "1")
    add_register(deviceconf, "DEVICE_CONFIG_MINOR", "10")
    add_register(deviceconf, "DEVICE_CONFIG_BUILD", "4")
    # Not used yet:
    add_register(deviceconf, "CONTENT_LENGTH", "0")
    add_register(deviceconf, "CONTENT_CHECKSUM", "0")
    # Default to start at 0
    add_register(deviceconf, "INSTANCE", "0")
    # UPDI_TINYX_API
    add_register(deviceconf, "INTERFACE_TYPE", "0x01")
    # Not used for AVR
    add_register(deviceconf, "DEVICE_VARIANT", "0x00")

    # Create blob-holder node
    blob = make_register("BLOB", "")

    xml_blob = ElementTree.Element("blob")

    # Add LIST token: <token>LIST</token>
    token = ElementTree.Element("token")
    token.text = "LIST"
    xml_blob.append(token)

    # Add device info only as there is no script content for AVR devicess

    # Create new entry
    entry = ElementTree.Element("entry")

    # Add type
    d_type = ElementTree.Element("type")
    d_type.text = "D_TINYX"
    entry.append(d_type)

    # Add fields
    todo_comment = " TODO value(s) must be checked/updated manually "

    add_data(entry, "DEVICE_ID", f"0x{extrainfo['device_id'] & 0xFFFF:04X}")

    add_comment(entry, "Flash information ")
    add_data(entry, "PROG_BASE", f"0x{int(memories[MemoryNames.FLASH][DeviceMemoryInfoKeys.ADDRESS], 0) & 0xFFFF:04X}")
    add_data(entry, "PROG_BASE_MSB", f"0x{(int(memories[MemoryNames.FLASH][DeviceMemoryInfoKeys.ADDRESS], 0) >> 16) & 0xFF:02X}")
    add_data(entry, "FLASH_BYTES", f"0x{int(memories[MemoryNames.FLASH][DeviceMemoryInfoKeys.SIZE], 0) & 0xFFFFFFFF:08X}")
    add_data(entry, "FLASH_PAGE_BYTES", f"0x{int(memories[MemoryNames.FLASH][DeviceMemoryInfoKeys.PAGE_SIZE], 0) & 0xFF:02X}")
    add_data(entry, "FLASH_PAGE_BYTES_MSB", f"0x{(int(memories[MemoryNames.FLASH][DeviceMemoryInfoKeys.PAGE_SIZE], 0) >> 8) & 0xFF:02X}")

    add_comment(entry, " EEPROM information ")
    add_data(entry, "EEPROM_BASE", f"0x{int(memories[MemoryNames.EEPROM][DeviceMemoryInfoKeys.ADDRESS], 0) & 0xFFFF:04X}")
    add_data(entry, "EEPROM_BYTES", f"0x{int(memories[MemoryNames.EEPROM][DeviceMemoryInfoKeys.SIZE], 0) & 0xFFFF:04X}")
    add_data(entry, "EEPROM_PAGE_BYTES", f"0x{int(memories[MemoryNames.EEPROM][DeviceMemoryInfoKeys.PAGE_SIZE], 0) & 0xFF:02X}")

    add_comment(entry, " User row information ")
    add_data(entry, "USER_ROW_BASE", f"0x{int(memories[MemoryNames.USER_ROW][DeviceMemoryInfoKeys.ADDRESS], 0) & 0xFFFF:04X}")
    add_data(entry, "USER_SIG_BYTES", f"0x{int(memories[MemoryNames.USER_ROW][DeviceMemoryInfoKeys.SIZE], 0) & 0xFFFF:04X}")

    add_comment(entry, " Signature row information ")
    add_data(entry, "SIGROW_BASE", f"0x{int(memories[MemoryNames.SIGNATURES][DeviceMemoryInfoKeys.ADDRESS], 0) & 0xFFFF:04X}")

    add_comment(entry, " FUSE/LOCK information ")
    add_data(entry, "FUSE_BASE", f"0x{int(memories[MemoryNames.FUSES][DeviceMemoryInfoKeys.ADDRESS], 0) & 0xFFFF:04X}")
    add_data(entry, "FUSE_BYTES", f"0x{int(memories[MemoryNames.FUSES][DeviceMemoryInfoKeys.SIZE], 0) & 0xFFFF:04X}")
    add_data(entry, "LOCK_BASE", f"0x{int(memories[MemoryNames.LOCKBITS][DeviceMemoryInfoKeys.ADDRESS], 0) & 0xFFFF:04X}")

    if MemoryNames.BOOT_ROW in memories:
        comment = " Boot row information "
        boot_base = f"0x{int(memories[MemoryNames.BOOT_ROW][DeviceMemoryInfoKeys.ADDRESS], 0) & 0xFFFF:04X}"
        boot_bytes = f"0x{int(memories[MemoryNames.BOOT_ROW][DeviceMemoryInfoKeys.SIZE], 0) & 0xFFFF:04X}"
    else:
        comment = " No Boot row on this device "
        boot_base = 0x0000
        boot_bytes = 0x0000
    add_comment(entry, comment)
    add_data(entry, "BOOT_ROW_BASE", f"{boot_base}")
    add_data(entry, "BOOT_ROW_BYTES", f"{boot_bytes}")

    add_comment(entry, " Additional UPDI parameters ")
    if extrainfo['address_size'] == '16-bit':
        comment = " This is a 16-bit UPDI variant "
        adr_size = 0x00
    else:
        comment = " This is a 24-bit UPDI variant "
        adr_size = 0x01
    add_comment(entry, comment)
    add_data(entry, "ADDRESS_SIZE", f"0x{adr_size:02X}")

    add_comment(entry, " PROG/DEBUG information ")
    add_data(entry, "NVMCTRL_MODULE", f"0x{extrainfo['nvmctrl_base'] & 0xFFFF:04X}")
    add_data(entry, "OCD_MODULE", f"0x{extrainfo['ocd_base'] & 0xFFFF:04X}")
    add_comment(entry, " 0: HV on the same pin as UPDI; 1: No HV; 2: HV on separate (/RESET) pin to UPDI ")
    add_data(entry, "HV_IMPLEMENTATION", f"{extrainfo['hv_implementation']}")

    add_comment(entry, " UPDI speed limits ")
    add_comment(entry, todo_comment)
    add_comment(entry, " mV ")
    add_data(entry, "PDICLK_DIV1_VMIN", "4500")
    add_comment(entry, " mV ")
    add_data(entry, "PDICLK_DIV2_VMIN", "2700")
    add_comment(entry, " mV ")
    add_data(entry, "PDICLK_DIV4_VMIN", "2200")
    add_comment(entry, " mV ")
    add_data(entry, "PDICLK_DIV8_VMIN", "1500")
    add_comment(entry, " kB ")
    add_data(entry, "PDI_PAD_FMAX", "1500")

    add_comment(entry, " Fuse protection parameters (force certain fuses high or low) ")
    add_comment(entry, todo_comment)
    add_comment(entry, " Offset of the fuse protecting UPDI pin (SYSCFG0 or PINCFG0) within FUSE space ")
    add_data(entry, "PINPROT_OFFSET", "5")
    add_comment(entry, " AND mask to apply to PINPROT when writing. ")
    add_data(entry, "PINPROT_WRITE_MASK_AND", "0xFF")
    add_comment(entry, " OR mask to apply to PINPROT when writing. ")
    add_data(entry, "PINPROT_WRITE_MASK_OR", "0x00")
    add_comment(entry, " AND mask to apply to PINPROT after erase. ")
    add_data(entry, "PINPROT_ERASE_MASK_AND", "0xFF")
    add_comment(entry, " OR mask to apply to PINPROT after erase. ")
    add_data(entry, "PINPROT_ERASE_MASK_OR", "0x00")
    add_comment(entry, " Mask for writing to fuse address space. Bit n applies to byte offset n. ")
    add_comment(entry, " Set bit to 0 to allow access to write; set bit to 1 to prevent writing to this fuse. ")
    add_data(entry, "FUSE_PROTECTION_MASK", "0x0000")

    xml_blob.append(entry)

    # Put the result into the blob-holder
    blob.append(xml_blob)

    # Add the blob-holder to the main node
    deviceconf.append(blob)

    config = minidom.parseString(ElementTree.tostring(deviceconf,
                                             encoding='unicode')).toprettyxml(indent="    ")

    return config

def main():
    """
    Main function for the harvest utility
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
    Harvests device data from a device data file (.atdf) for one device.

    The harvested data can be used to populate a device file in deviceinfo.devices
        '''))

    parser.add_argument("filename",
                        help="name (and path) of file to harvest data from"
                        )

    arguments = parser.parse_args()

    dict_content, device_config = harvest_from_file(arguments.filename)
    content = "\nfrom pymcuprog.deviceinfo.eraseflags import ChiperaseEffect\n\n"
    content += f"DEVICE_INFO = {{\n{dict_content}}}"
    print("Device info for pymcuprog:")
    print(content)
    print()
    print("Device config XML content for pydebuggerconfig:\n")
    print(device_config)

if __name__ == "__main__":
    main()
