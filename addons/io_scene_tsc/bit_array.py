"""Bit Array."""

import ctypes


class BitArray:
    """Bit Array."""

    bits: list[int]

    def __init__(self, bits: list[int]) -> None:
        """Initialize a BitArray."""
        self.bits = bits

    def get_bit(self, index: int) -> bool:
        """Get bit as bool."""
        return (self.bits[index >> 5] & (1 << (index & 0x1F))) != 0

    def get_bits_unsigned(self, index: int, count: int) -> int:
        """Get bits as unsigned int."""
        if count == 0:
            return 0

        bit_array_index = index >> 5
        bit_array_index_end = ((index + count) - 1) >> 5
        bit_offset = index & 0x1F
        if bit_array_index == bit_array_index_end:
            mask = (1 << (count & 0x1F)) - 1
            if mask == 0:
                return self.bits[bit_array_index]
            return (self.bits[bit_array_index] >> bit_offset) & mask

        int_1_mask = (1 << ((index + count) & 0x1F)) - 1
        int_0 = self.bits[bit_array_index]
        int_1 = self.bits[bit_array_index_end] & int_1_mask

        return (int_1 << (-bit_offset & 0x1F)) | (int_0 >> bit_offset)

    def get_bits_signed(self, index: int, count: int) -> int:
        """Get bits as signed int."""
        if count == 0:
            return 0

        count = count - 1
        sign = self.get_bit(index + count)

        if sign:
            bits = self.get_bits_unsigned(index, count)
            return (-1 << (count & 0x1F)) | bits

        return self.get_bits_unsigned(index, count)

    def get_float(self, index: int) -> float:
        """Get bits as float."""
        bits = self.get_bits_unsigned(index, 32)

        return ctypes.c_float.from_buffer(ctypes.c_uint32(bits)).value

    def signed_bits_to_float_scaler(self, bits: int) -> float:
        """Calculate the float scaler from signed bits."""
        return 1.0 / float((1 << (bits - 1)) - 1)

    def unsigned_bits_to_float_scaler(self, bits: int) -> float:
        """Calculate the float scaler from unsigned bits."""
        return 1.0 / float((1 << bits) - 1)
