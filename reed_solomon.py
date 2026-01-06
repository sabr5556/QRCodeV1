class ReedSolomon:
    def __init__(self, n_error_codewords):
        self.n_codewords = n_error_codewords
        self.log_table = [0] * 256
        self.exp_table = [0] * 256
        
        self._init_tables()

    def _init_tables(self):
        primitive = 285
        value = 1

        for i in range(256):
            self.exp_table[i] = value
            self.log_table[value] = i
            # Multiply by 2 (which is equivalent shifting left by 1 bit)
            value = value << 1 
            # If we went over 255 (8th bit is set), we XOR with the primitive
            if value > 255:
                value = value ^ primitive

    def gf_multiply(self, x, y):
        if x == 0 or y == 0:
            return 0
        idx_x = self.log_table[x]
        idx_y = self.log_table[y]
        final_exponent = (idx_x + idx_y) % 255
        return self.exp_table[final_exponent]   

    def gf_poly_mul(self, p, q):
        # Create result list of correct size, initialized to 0
        r = [0] * (len(p) + len(q) - 1)
        
        # Compute the polynomial product
        for j in range(len(q)):
            for i in range(len(p)):
                product = self.gf_multiply(p[i], q[j])
                r[i + j] ^= product
        return r

    def get_generator_poly(self):
        # Start with polynomial "1"
        g = [1]
        
        # Multiply (x - a^0) * (x - a^1) ... * (x - a^n-1)
        for i in range(self.n_codewords):
            # Create term (x - alpha^i)
            # In GF(256), subtraction is XOR, so (x + alpha^i) is same
            term = [1, self.exp_table[i]]
            g = self.gf_poly_mul(g, term)
        return g
    
    def encode(self, data):
        gen = self.get_generator_poly()
        enc_msg = data + [0] * self.n_codewords
        for i in range(len(data)):
            coef = enc_msg[i]
            if coef != 0:
                for j in range(len(gen)):
                    enc_msg[i + j] ^= self.gf_multiply(gen[j], coef)
        return enc_msg[-self.n_codewords:]
