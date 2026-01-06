# qr_matrix.py
import qr_tables as qrt

class QRCodeMatrix:
    def __init__(self):
        # Version 1 is always 21x21
        self.size = 21
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]

    def _place_finder_pattern(self, r_start, c_start):
        '''
        Draws the 7x7 Finder Pattern (The "Eye")
        '''
        for r in range(7):
            for c in range(7):
                # Logic: Outer ring (0,6) is Black, Inner ring (1,5) is White, Center is Black
                if (r == 0 or r == 6 or c == 0 or c == 6):
                    self.grid[r_start + r][c_start + c] = 1
                elif (r == 1 or r == 5 or c == 1 or c == 5):
                    self.grid[r_start + r][c_start + c] = 0
                else:
                    self.grid[r_start + r][c_start + c] = 1

    def _place_separators(self):
        '''
        Draws the white "Safety Zones" around the Finder Patterns.
        These are just lines of white pixels (0).
        '''
        # Top Left Separator (Horizontal len 8, Vertical len 8)
        for i in range(8):
            self.grid[7][i] = 0  # Bottom horizontal line
            self.grid[i][7] = 0  # Right vertical line
            
        # Top Right Separator
        for i in range(8):
            self.grid[7][self.size - 1 - i] = 0 # Bottom horizontal
            self.grid[i][self.size - 8] = 0     # Left vertical

        # Bottom Left Separator
        for i in range(8):
            self.grid[self.size - 8][i] = 0     # Top horizontal
            self.grid[self.size - 1 - i][7] = 0 # Right vertical

    def place_data_bits(self, bit_data):
        '''
        Places the data bits into the grid using the standard zig-zag pattern.
        bit_data: A string of "1"s and "0"s (e.g., "10110...")
        '''
        bit_idx = 0
        direction = -1 # -1 = Up, 1 = Down
        row = self.size - 1
        col = self.size - 1
        
        while col > 0:
            # 1. Skip the Vertical Timing Pattern (Column 6)
            if col == 6:
                col -= 1
                
            # 2. Iterate through the current 2-column strip
            while 0 <= row < self.size:
                for c_offset in range(2): # Check right col then left col
                    current_col = col - c_offset
                    
                    # 3. If the pixel is empty (None), place a bit
                    if self.grid[row][current_col] is None and not self._is_function_pattern(row, current_col):
                    
                        if bit_idx < len(bit_data):
                            self.grid[row][current_col] = int(bit_data[bit_idx])
                            bit_idx += 1
                        else:
                            # QR Standard requires padding remainder bits with 0 (Light/White), not 1
                            self.grid[row][current_col] = 0
                            
                # Move to next row
                row += direction
                
            # 4. Switch Direction and move to next column pair
            direction = -direction # Flip direction
            row += direction       # Step back one row to stay in bounds
            col -= 2               # Move left 2 columns

    def _place_timing_patterns(self):
        '''
        Draws the horizontal and vertical Timing Patterns.
        These are always on Row 6 and Column 6.
        '''
        # We run from index 8 to (Size - 8) to skip the Finder Patterns
        for i in range(8, self.size - 8):
            val = 1 if i % 2 == 0 else 0
            
            # Horizontal Timing Pattern (Row 6)
            self.grid[6][i] = val
            
            # Vertical Timing Pattern (Column 6)
            self.grid[i][6] = val

    def _place_dark_module(self):
        '''
        A single black pixel that is ALWAYS at (4 * Version) + 9.
        For Version 1, that is (4 * 1) + 9 = Row 13.
        Column is always 8.
        '''
        # Coordinates: (Row 13, Col 8) for Version 1
        self.grid[4 * 1 + 9][8] = 1

    def add_finders(self):
        # 1. Place the 3 Eyes
        self._place_finder_pattern(0, 0)                   # Top-Left
        self._place_finder_pattern(0, self.size - 7)       # Top-Right
        self._place_finder_pattern(self.size - 7, 0)       # Bottom-Left
        
        # 2. Place the White Separators
        self._place_separators()

        # 3. Place Timing Patterns & Dark Module  <-- NEW
        self._place_timing_patterns()
        self._place_dark_module()

    def _is_function_pattern(self, row, col):
        '''
        Returns True if the coordinate is part of a Finder, Separator, 
        Timing Pattern, Dark Module, or Reserved Format Area.
        '''
        # 1. Finder Patterns & Separators (Top-Left, Top-Right, Bottom-Left)
        # They occupy 9x9 zones in the corners (7+1 buffer, but we check 9 to be safe)
        if row < 9 and col < 9: return True          # Top-Left
        if row < 9 and col > self.size - 9: return True  # Top-Right
        if row > self.size - 9 and col < 9: return True  # Bottom-Left
        
        # 2. Timing Patterns (Row 6 and Col 6)
        if row == 6 or col == 6: return True
        
        # 3. Dark Module (Always (self.size - 8, 8)) (Wait, it's 4*V + 9 -> Row 13, Col 8)
        if row == 13 and col == 8: return True
        
        # 4. Reserved Format Information Areas (Strips near finders)
        # We haven't drawn them yet, but we must not put data mask there.
        # Top-Left L-shape
        if (row < 9 and col == 8) or (row == 8 and col < 9): return True
        # Top-Right strip
        if row == 8 and col > self.size - 9: return True
        # Bottom-Left strip
        if row > self.size - 9 and col == 8: return True
        
        return False

    def apply_mask(self, mask_pattern):
        '''
        Applies the mask to the data modules.
        mask_pattern: Integer 0-7.
        '''
        for r in range(self.size):
            for c in range(self.size):
                if self._is_function_pattern(r, c):
                    continue
                
                # The Formulas for the 8 Masks
                should_flip = False
                if mask_pattern == 0:
                    should_flip = (r + c) % 2 == 0
                elif mask_pattern == 1:
                    should_flip = r % 2 == 0
                elif mask_pattern == 2:
                    should_flip = c % 3 == 0
                elif mask_pattern == 3:
                    should_flip = (r + c) % 3 == 0
                elif mask_pattern == 4:
                    should_flip = ((r // 2) + (c // 3)) % 2 == 0
                elif mask_pattern == 5:
                    should_flip = ((r * c) % 2) + ((r * c) % 3) == 0
                elif mask_pattern == 6:
                    should_flip = (((r * c) % 2) + ((r * c) % 3)) % 2 == 0
                elif mask_pattern == 7:
                    should_flip = (((r + c) % 2) + ((r * c) % 3)) % 2 == 0
                
                # XOR operation to flip the bit
                if should_flip:
                    self.grid[r][c] ^= 1

    def _place_format_info(self, mask_pattern, ec_level):
        '''
        Places the 15-bit Format Information string.
        '''
        # 1. Retrieve the 15-bit string (MSB is index 0, LSB is index 14)
        bits = qrt.format_info_table[ec_level.upper()][mask_pattern]
        
        # --- COPY 1 (Top-Left) ---
        # Your original coordinates were correct for MSB->LSB placement
        # (8,0) is Bit 14 (Index 0), (0,8) is Bit 0 (Index 14)
        coords = [
            (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 7), (8, 8), 
            (7, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8)          
        ]
        
        for i in range(15):
            r, c = coords[i]
            self.grid[r][c] = int(bits[i])

        # --- COPY 2 (Top-Right & Bottom-Left) ---
        
        # 1. Bottom-Left: Holds Bits 0-6 (Indices 14 down to 8)
        # Coordinates go from Bit 0 location to Bit 6 location
        bs_coords = [
            (self.size - 1, 8), (self.size - 2, 8), (self.size - 3, 8), 
            (self.size - 4, 8), (self.size - 5, 8), (self.size - 6, 8), (self.size - 7, 8)
        ]
        for i in range(7):
            r, c = bs_coords[i]
            # FIX: We need Bit 0 (Index 14), then Bit 1 (Index 13)...
            bit_index = 14 - i 
            self.grid[r][c] = int(bits[bit_index])

        # 2. Top-Right: Holds Bits 7-14 (Indices 7 down to 0)
        # Coordinates go from Bit 7 location to Bit 14 location
        tr_coords = [
            (8, self.size - 8), (8, self.size - 7), (8, self.size - 6), 
            (8, self.size - 5), (8, self.size - 4), (8, self.size - 3), 
            (8, self.size - 2), (8, self.size - 1)
        ]
        for i in range(8):
            r, c = tr_coords[i]
            # FIX: We need Bit 7 (Index 7), then Bit 8 (Index 6)...
            bit_index = 7 - i
            self.grid[r][c] = int(bits[bit_index])

    def print_grid(self):
        quiet_zone = 4 # Must be 4 modules wide
        
        # 1. Define the "White" and "Black" pixels for your terminal
        # Since you have a black background, we use "██" to make light
        # and "  " (empty space) to make dark.
        white_pixel = "██"
        black_pixel = "  "
        
        # 2. Create the Padding Strings (Side margins)
        # We multiply the pixel string by the NUMBER of modules (4)
        pad_str = white_pixel * quiet_zone
        
        # 3. Create the Top/Bottom Border
        # Total width = Left Pad + Grid(21) + Right Pad
        total_width_modules = quiet_zone + self.size + quiet_zone
        white_line = white_pixel * total_width_modules
        
        print("\n" + white_pixel * total_width_modules) # Top Safety Line
        
        # --- Top Quiet Zone ---
        for _ in range(quiet_zone):
            print(white_line)
            
        # --- The Grid ---
        for row in self.grid:
            line = pad_str # Left Padding
            for cell in row:
                if cell == 0:
                    line += white_pixel # Logic 0 = White = Block
                elif cell == 1:
                    line += black_pixel # Logic 1 = Black = Space
                else:
                    line += ".." 
            line += pad_str # Right Padding
            print(line)

        # --- Bottom Quiet Zone ---
        for _ in range(quiet_zone):
            print(white_line)
            
        print(white_pixel * total_width_modules + "\n") # Bottom Safety Line