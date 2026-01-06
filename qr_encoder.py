import qr_tables as qrt

class QRCodeV1:
    def __init__(self, data, ec_level):
        self.version = 1
        self.data = data
        self.ec_level = ec_level.upper()
        self.mode = self._detect_mode()
        self._validate_capacity()
        self.bit_stream = ""
        self.codewords = []

    def _detect_mode(self):
        if all(char in qrt.alphanumeric_table for char in self.data):
            return 'A'
        return 'B'

    def _validate_capacity(self):
        '''
        Checks if the data fits in Version 1 for the chosen EC level.
        Raises ValueError if data is too long.
        '''
        # 1. Calculate Data Bits needed
        data_bits = 0
        if self.mode == 'A':
            # Alphanumeric: 11 bits per pair, 6 bits for remainder
            pairs = len(self.data) // 2
            remainder = len(self.data) % 2
            data_bits = (pairs * 11) + (remainder * 6)
            
            # Header: 4 bits Mode + 9 bits Count Indicator (Version 1-9)
            header_bits = 4 + 9 
            
        elif self.mode == 'B':
            # Byte: 8 bits per character
            data_bits = len(self.data) * 8
            
            # Header: 4 bits Mode + 8 bits Count Indicator (Version 1-9)
            header_bits = 4 + 8

        total_needed = header_bits + data_bits

        # 2. Get Max Capacity from Tables
        # codeword_capacity_table gives bytes, so multiply by 8 for bits
        max_bytes = qrt.codeword_capacity_table[self.ec_level]
        max_bits = max_bytes * 8

        # 3. Raise Error if Overflow
        if total_needed > max_bits:
            raise ValueError(
                f"Data too long for Version 1-{self.ec_level}. "
                f"Needed {total_needed} bits, but only {max_bits} available."
            )

    def _get_mode_indicator(self):
        return qrt.mode_indicator_table[self.mode]

    def _get_count_indicator(self):
        # Version 1 Specific lengths
        if self.mode == 'A':
            return f'{len(self.data):09b}'
        elif self.mode == 'B':
            return f'{len(self.data):08b}'

    def encode_data(self):
        data_bits = ""
        i = 0
        
        if self.mode == 'A':
            while i < len(self.data):
                if i + 1 < len(self.data):
                    val1 = qrt.alphanumeric_table[self.data[i]]
                    val2 = qrt.alphanumeric_table[self.data[i+1]]
                    pair_val = (val1 * 45) + val2
                    data_bits += f'{pair_val:011b}'
                    i += 2
                else:
                    val1 = qrt.alphanumeric_table[self.data[i]]
                    data_bits += f'{val1:06b}'
                    i += 1
                    
        elif self.mode == 'B':
            for char in self.data:
                if ord(char) > 255:
                    raise ValueError("Character is not a valid ASCII character")
                data_bits += f'{ord(char):08b}'
        
        return data_bits

    def build_bit_stream(self):
        # 1. Header
        header = self._get_mode_indicator() + self._get_count_indicator()
        encoded_data = self.encode_data()
        self.bit_stream = header + encoded_data

        # 2. Padding
        max_bits = qrt.codeword_capacity_table[self.ec_level] * 8
        
        # Terminator
        terminator_len = min(4, max_bits - len(self.bit_stream))
        self.bit_stream += '0' * terminator_len

        # Bit Alignment
        if len(self.bit_stream) % 8 != 0:
            self.bit_stream += '0' * (8 - (len(self.bit_stream) % 8))

        # Byte Padding
        pad_bytes = ['11101100', '00010001']
        pad_idx = 0
        while len(self.bit_stream) < max_bits:
            self.bit_stream += pad_bytes[pad_idx % 2]
            pad_idx += 1
            
        # 3.C Convert to Integers (Codewords)
        self.codewords = []
        for i in range(0, len(self.bit_stream), 8):
            byte = self.bit_stream[i:i+8]
            self.codewords.append(int(byte, 2))
