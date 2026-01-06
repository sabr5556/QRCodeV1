
from qr_encoder import QRCodeV1
from reed_solomon import ReedSolomon
from qr_matrix import QRCodeMatrix
import qr_tables as qrt

def main():
    # 1. CONFIGURATION, ENTER STRING AND ERROR CORRECTION LEVEL HERE
    data = input("Enter your website or data: ")
    ec_level = input("Enter your error correction level (L, M, Q, H): ")

    print(f"--- STARTING ENCODE FOR: {data} ---")

    # 2. DATA ENCODING (String -> Codewords)
    qr = QRCodeV1(data, ec_level)
    qr.build_bit_stream()
    
    # 3. ERROR CORRECTION (Codewords -> EC Bytes)
    num_ec_bytes = qrt.ec_codeword_table[ec_level]
    rs = ReedSolomon(n_error_codewords=num_ec_bytes)
    ec_bytes = rs.encode(qr.codewords)

    # 4. FINAL ASSEMBLY
    final_message = qr.codewords + ec_bytes
    full_bit_string = "".join(f"{x:08b}" for x in final_message)
    
    print("\n--- GENERATING MATRIX ---")
    qr_mat = QRCodeMatrix()
    qr_mat.add_finders()
    qr_mat.place_data_bits(full_bit_string)

    mask_id = 0 # Checkerboard

    print(f"Applying Mask Pattern {mask_id}...")
    qr_mat.apply_mask(mask_id)
    qr_mat._place_format_info(mask_id, ec_level) # Write the ID into the grid
    qr_mat.print_grid()

if __name__ == "__main__":
    main()

