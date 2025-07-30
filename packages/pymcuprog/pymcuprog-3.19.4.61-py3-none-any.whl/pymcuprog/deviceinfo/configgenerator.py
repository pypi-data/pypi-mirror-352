"""
Utilities that uses the pymcuprog stack to build device config blobs for PIC devices

This is the backend part of the generateconfig utility
"""
import sys
import os
import xml.etree.ElementTree as ETree
import inspect
from xml.dom import minidom
from datetime import datetime
from logging import getLogger

from pymcuprog.programmer import Programmer
from pymcuprog.pymcuprog_errors import PymcuprogError
from pymcuprog.deviceinfo.memorynames import MemoryNames
from pymcuprog.deviceinfo.deviceinfokeys import DeviceMemoryInfoKeys

def make_register(name, value):
    """Create a register element

    :param name: Name of register
    :type name: string
    :param value: Register value
    :type value: string
    :return: Register element
    :rtype: class:`xml.etree.ElementTree.Element`
    """

    reg = ETree.Element("register")
    reg.attrib["name"] = name
    reg.attrib["value"] = value
    return reg

def add_register(element, name, value):
    """
    Add a register into the XML element

    :param element: XML element
    :type element: class:`xml.etree.ElementTree.Element`
    :param name: <register name="xxx">
    :type name: string
    :param value: <register value="xxx">
    :type value: string
    """

    element.append(make_register(name, value))

def add_data(element, name, value):
    """
    Add a data type into the XML element

    :param element: XML element
    :type element: class:`xml.etree.ElementTree.Element`
    :param name: <data type="xxx">
    :type name: string
    :param value: value
    :type value: string
    """
    data = ETree.Element("data")
    data.attrib["type"] = name
    data.text = value
    element.append(data)

def add_comment(element, comment):
    """Add comment into the XML element

    :param element: XML element
    :type element: class:`xml.etree.ElementTree.Element`
    :param comment: Comment string
    :type comment: string
    """
    comment_element = ETree.Comment(comment)
    element.append(comment_element)

class ConfigGenerator(object):
    """
    This class provides functions to build device config blobs for PIC devices
    """
    def __init__(self):
        self.pic = None
        self.tool = None
        self.device_memory_info = None
        self.source = None

    def load_device_model(self, device_name, packpath):
        """
        Load the device model

        :param device_name: device name
        :param packpath: path to pack
        """

        # Locate and load the model from the pack

        if packpath is None:
            raise PymcuprogError("No path to pack repo provided!")

        # Import from pack.
        sys.path.append(os.path.normpath(packpath))
        sys.path.append(os.path.normpath(packpath + "//common"))

        # Use tool-type indicating a Config generator
        try:
            from debugprovider import ConfigGeneratorTool #pylint: disable=import-error, import-outside-toplevel
        except ImportError:
            raise PymcuprogError("Unable to import debugprovider from '{}'! Is this path correct?".format(packpath))

        self.tool = ConfigGeneratorTool()

        # Load the programming model
        programmer = Programmer(self.tool)
        # Load the device
        programmer.load_device(device_name)
        # Setup the device
        programmer.setup_device(interface=None, packpath=packpath)
        # Fetch the memory model
        self.device_memory_info = programmer.get_device_memory_info()
        # Extract the pic from level n of the stack
        self.pic = programmer.device_model.pic
        # Extract the source from level n+1 of the same stack
        self.source = inspect.getsource(programmer.device_model.pic.device_model)

        # Check to see if this device model can be abstracted:
        # Some devices are so antiquated that they only have support for incrementing the PC and reseting to 0
        # These devices currently abstract in Python in such a way that drag and drop will not work with these scripts.
        if 'RESET_ADDRESS' in dir(self.pic.device_model):
            raise PymcuprogError("This device model does not support drag and drop by primitives")

    # This function do access some private methods, but it should be acceptable as this utility is using pymcuprog in a
    # non-common way and is not a part of the pymcuprog CLI functionality.
    #pylint: disable=protected-access
    def process_programming_functions(self):
        """
        Crunch through all programming functions and accumulate results
        """
        if not self.pic:
            raise PymcuprogError("Device model not loaded!")

        # Enter TMOD
        self.pic.enter_tmod()
        # Read ID
        self.pic.read_id()
        # Exit TMOD
        self.pic.exit_tmod()
        # Erase
        self.pic.erase()

        # Parameterised

        # This import must be late as it depends on the common folder in the packpath which is not available until
        # after load_device_model has been called
        from primitiveutils import ParametricValueToken #pylint: disable=import-error, import-outside-toplevel
        # Flash
        if MemoryNames.FLASH in self.device_memory_info.mem_by_name:
            flash_info = self.device_memory_info.memory_info_by_name(MemoryNames.FLASH)
            flash_page_size = flash_info[DeviceMemoryInfoKeys.PAGE_SIZE]
            self.pic.write_flash_page(byte_address=ParametricValueToken(ParametricValueToken.TOKEN_ADDRESS_LE32),
                                        data=bytearray(flash_page_size))
        # Config
        if MemoryNames.CONFIG_WORD in self.device_memory_info.mem_by_name:
            config_words_info = self.device_memory_info.memory_info_by_name(MemoryNames.CONFIG_WORD)
            config_words_write_size = config_words_info[DeviceMemoryInfoKeys.WRITE_SIZE]
            if config_words_write_size == 1:
                self.pic.write_config_byte(byte_address=ParametricValueToken(ParametricValueToken.TOKEN_ADDRESS_LE32),
                                           data=bytearray(config_words_write_size))
            elif config_words_write_size == 2:
                self.pic.write_config_word(byte_address=ParametricValueToken(ParametricValueToken.TOKEN_ADDRESS_LE32),
                                           data=bytearray(config_words_write_size))
            else:
                raise ValueError("config_words_write_size must either be 1 or 2; {} is not supported".format(config_words_write_size))
        # EEPROM
        if MemoryNames.EEPROM in self.device_memory_info.mem_by_name:

            eeprom_info = self.device_memory_info.memory_info_by_name(MemoryNames.EEPROM)
            eeprom_write_size = eeprom_info[DeviceMemoryInfoKeys.WRITE_SIZE]
            if "PIC16" in self.pic.device_name.upper():
                # Multiply EEPROM write size by 2, since config has to always deal with phantom bytes which are in the hex files (for PIC16 devices)
                self.pic.write_eeprom_block(byte_address=ParametricValueToken(ParametricValueToken.TOKEN_ADDRESS_LE32),
                                            data=bytearray(eeprom_write_size * 2))
            else:
                self.pic.write_eeprom_block(byte_address=ParametricValueToken(ParametricValueToken.TOKEN_ADDRESS_LE32),
                                            data=bytearray(eeprom_write_size))

        # User IDs
        if MemoryNames.USER_ID in self.device_memory_info.mem_by_name:
            user_id_info = self.device_memory_info.memory_info_by_name(MemoryNames.USER_ID)
            user_id_write_size = user_id_info[DeviceMemoryInfoKeys.WRITE_SIZE]
            self.pic.write_user_id_word(byte_address=ParametricValueToken(ParametricValueToken.TOKEN_ADDRESS_LE32),
                                         data=bytearray(user_id_write_size))

    def get_xml_element(self):
        """
        Creates an xml element from the generator output

        :return: xml element
        """
        xml_blob = ETree.Element("blob")
        # Add source as comment
        add_comment(xml_blob, "Source code used to generate this blob:\n{}".format(self.source))

        # Add LIST token: <token>LIST</token>
        token = ETree.Element("token")
        token.text = "LIST"
        xml_blob.append(token)

        # Collect contents from tool and concatenate elements
        contents = self.tool.get_contents()
        for entry in contents:
            # Append elements
            xml_blob.append(contents[entry])
        return xml_blob

    def populate_device_config_template(self):
        """
        Template for header of device config
        """
        # Construct the root
        deviceconf = ETree.Element("deviceconf")
        deviceconf.attrib["name"] = self.pic.device_name.upper()
        add_comment(deviceconf, "device config for {} generated {}"
                    .format(self.pic.device_name, datetime.now().strftime("%Y.%m.%d, %H:%M:%S")))

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
        # PIC primitive sequences are always interface type 4
        add_register(deviceconf, "INTERFACE_TYPE", "0x04")
        # Variant: PIC16 is 0, PIC18 is 1
        if "PIC16" in self.pic.device_name.upper():
            add_register(deviceconf, "DEVICE_VARIANT", "0x00")
        elif "PIC18" in self.pic.device_name.upper():
            add_register(deviceconf, "DEVICE_VARIANT", "0x01")
        else:
            raise Exception("Unknown device variant - are you sure this is a PIC?")

        return deviceconf

    def add_device_data_template(self):
        """
        Injects device data template
        This must be populated by hand with valid data
        """
        logger = getLogger(__name__)
        # Create new entry
        entry = ETree.Element("entry")

        # Add type
        d_type = ETree.Element("type")
        d_type.text = "D_ICSP"
        entry.append(d_type)

        # Fetch info providers for retrieving device info
        flash_info = self.device_memory_info.memory_info_by_name(MemoryNames.FLASH)
        if MemoryNames.EEPROM in self.device_memory_info.mem_by_name:
            eeprom_info = self.device_memory_info.memory_info_by_name(MemoryNames.EEPROM)
            eeprom_base_w = eeprom_info['address']//2
            eeprom_size_b = eeprom_info['size']
            if "PIC16" in self.pic.device_name.upper():
                # Multiply EEPROM write size by 2, since config has to always deal with phantom bytes which are in the hex files (for PIC16 devices)
                eeprom_write_block_b = eeprom_info['write_size'] * 2
            else:
                eeprom_write_block_b = eeprom_info['write_size']
        else:
            # Some devices do not have EEPROM memory, but it is good to warn the user if it is missing in case it
            # was just forgotten when making the device model file
            logger.warning("No EEPROM memory has been specified for this device, does the device have any EEPROM memory?")
            eeprom_size_b = 0
            # These values must always be present, so just add some dummy values
            eeprom_base_w = 0
            eeprom_write_block_b = 0
        user_id_info = self.device_memory_info.memory_info_by_name(MemoryNames.USER_ID)
        config_word_info = self.device_memory_info.memory_info_by_name(MemoryNames.CONFIG_WORD)
        device_info = self.device_memory_info.device

        # Add fields
        add_data(entry, "PIC_FLASH_BASE_W", "0x{0:08X}".format(flash_info['address']//2))
        add_data(entry, "PIC_EEPROM_BASE_W", "0x{0:08X}".format(eeprom_base_w))
        add_data(entry, "PIC_USER_ID_BASE_W", "0x{0:08X}".format(user_id_info['address']//2))
        add_data(entry, "PIC_CONFIG_BASE_W", "0x{0:08X}".format(config_word_info['address']//2))
        add_data(entry, "PIC_FLASH_SIZE_W", "0x{0:08X}".format((flash_info['size']+1)//2))
        add_data(entry, "PIC_EEPROM_SIZE_B", "0x{0:04X}".format(eeprom_size_b))
        add_data(entry, "PIC_USER_ID_SIZE_W", "{}".format((user_id_info['size']+1)//2))
        add_data(entry, "PIC_CONFIG_SIZE_W", "{}".format((config_word_info['size']+1)//2))
        add_data(entry, "PIC_FLASH_WRITE_BLOCK_B", "{}".format(flash_info['page_size']))
        add_data(entry, "PIC_EEPROM_WRITE_BLOCK_B", "{}".format(eeprom_write_block_b))
        add_data(entry, "PIC_USER_ID_WRITE_BLOCK_B", "{}".format(user_id_info['write_size']))
        add_data(entry, "PIC_CONFIG_WRITE_BLOCK_B", "{}".format(config_word_info['write_size']))
        add_data(entry, "PIC_DEVICE_ID", "0x{0:04X}".format(device_info['device_id']))
        add_comment(entry, "TODO this value must be manually checked/updated")
        add_comment(entry, "Mask for config bytes. Bit n: 0->allow config byte offset n write, 1->block config byte offset n write.")
        # Default generated mask allows writing all config words
        default_config_word_mask = ((0xFFFFFFFE << (config_word_info['size']-1)) & 0xFFFFFFFF)
        add_data(entry, "PIC_CONFIG_PROTECTION_MASK", "0x{0:08X}".format(default_config_word_mask))
        return entry

    def get_xml_string(self):
        """
        Convert to string and returns

        :return: string representation of resultant xml
        """
        # Generate header etc
        deviceconfig = self.populate_device_config_template()

        # Add the blob-holder node
        blob = make_register("BLOB", "")

        # Fetch the generated primitive blob
        scripted_content = self.get_xml_element()

        # Append device info
        scripted_content.append(self.add_device_data_template())

        # Put the result into the blob-holder
        blob.append(scripted_content)

        # Add the blob-holder to the main node
        deviceconfig.append(blob)

        # Make it look nice and return
        return minidom.parseString(ETree.tostring(deviceconfig,
                                                  encoding='unicode')).toprettyxml(indent="    ")
