"""
Required device info for the dspic33ak512mps506 devices
"""
from pymcuprog.deviceinfo.eraseflags import ChiperaseEffect

DEVICE_INFO = {
    'name': 'dspic33ak512mps506',
    'device_id': 0xA779,
    'architecture': 'dsPIC33A',
    'interface' : 'icsp',

    # Flash
    'flash_address_byte': 0x800000,
    'flash_size_bytes': 0x080000, # 512KiB
    'flash_page_size_bytes': 0x1000,
    # Limited to 512 bytes due to USB chunk size limitation
    'flash_write_size_bytes': 0x200,
    'flash_read_size_bytes': 4,
    'flash_chiperase_effect': ChiperaseEffect.ALWAYS_ERASED,
    # Configuration words are integrated in the flash, but since they are not represented
    # as a separate memory it is correct to state that flash can be erased in isolation
    'flash_isolated_erase': True,

    # ICD memory
    'icd_address_byte': 0x7F0000,
    'icd_size_bytes': 512 * 16,  # 8KiB
    'icd_page_size_bytes': 0x1000,
    # Limited to 512 bytes due to USB chunk size limitation
    'icd_write_size_bytes': 0x200,
    'icd_read_size_bytes': 4,
    'icd_chiperase_effect': ChiperaseEffect.NOT_ERASED,
    'icd_isolated_erase': True,

    # Config words
    'config_words_address_byte': 0x7F3000,
    'config_words_size_bytes': 0x2000,
    # Strictly speaking config words have same page size as normal flash, but since quad-word writes are used for
    # config words the write size can be 16 bytes (4 words * 4 bytes per word) and a page size of 16 bytes makes the
    # output more readable
    'config_words_page_size_bytes': 16,
    'config_words_write_size_bytes': 16,
    'config_words_read_size_bytes': 4,
    'config_words_chiperase_effect': ChiperaseEffect.ALWAYS_ERASED,
    'config_words_isolated_erase': False,
}
