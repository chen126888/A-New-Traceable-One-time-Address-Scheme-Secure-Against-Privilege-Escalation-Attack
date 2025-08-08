/****************************************************************************
 * File: python_api.h  
 * Desc: Python interface functions for CryptoNote2 scheme
 *       Simple byte-based wrappers around core cryptographic functions
 ****************************************************************************/

#ifndef CRYPTONOTE2_PYTHON_API_H
#define CRYPTONOTE2_PYTHON_API_H

//----------------------------------------------
// Python Interface Functions
// These functions use byte arrays instead of OpenSSL types
// for easy integration with Python ctypes
//----------------------------------------------

/**
 * Python Interface: Generate key pair
 * @param A_out Buffer for public key A (output)
 * @param B_out Buffer for public key B (output)  
 * @param a_out Buffer for private key a (output)
 * @param b_out Buffer for private key b (output)
 * @param buf_size Size of each buffer
 */
void cryptonote2_keygen_simple(unsigned char* A_out, unsigned char* B_out,
                               unsigned char* a_out, unsigned char* b_out, int buf_size);

/**
 * Python Interface: Generate one-time address
 * @param A_bytes Input public key A as bytes
 * @param B_bytes Input public key B as bytes
 * @param pk_one_out Buffer for generated one-time public key (output)
 * @param r_out Buffer for random point R (output)  
 * @param buf_size Size of output buffers
 */
void cryptonote2_addr_gen_simple(const unsigned char* A_bytes, const unsigned char* B_bytes,
                                 unsigned char* pk_one_out, unsigned char* r_out, int buf_size);

/**
 * Python Interface: Verify one-time address (Receiver Statistics)
 * @param pk_one_bytes One-time public key as bytes
 * @param r_bytes Random point R as bytes
 * @param a_bytes Private key a as bytes  
 * @param b_bytes Public key B as bytes
 * @return 1 if address belongs to receiver, 0 otherwise
 */
int cryptonote2_addr_verify_simple(const unsigned char* pk_one_bytes, const unsigned char* r_bytes,
                                   const unsigned char* a_bytes, const unsigned char* b_bytes);

/**
 * Python Interface: Generate one-time secret key
 * @param r_bytes Random point R as bytes
 * @param a_bytes Private key a as bytes
 * @param b_bytes Private key b as bytes
 * @param sk_out Buffer for one-time secret key (output)
 * @param buf_size Size of output buffer
 */
void cryptonote2_onetime_sk_gen_simple(const unsigned char* r_bytes, const unsigned char* a_bytes,
                                       const unsigned char* b_bytes, unsigned char* sk_out, int buf_size);

/**
 * Python Interface: Hash function H1 (point to scalar)
 * @param point_bytes Input elliptic curve point as bytes
 * @param hash_out Buffer for hash result (output)
 * @param buf_size Size of output buffer
 */
void cryptonote2_hash_simple(const unsigned char* point_bytes, unsigned char* hash_out, int buf_size);

/**
 * Python Interface: Hash arbitrary data to scalar
 * @param data Input data bytes
 * @param data_len Length of input data
 * @param hash_out Buffer for hash result (output)
 * @param buf_size Size of output buffer
 */
void cryptonote2_hash_data_simple(const unsigned char* data, int data_len, 
                                  unsigned char* hash_out, int buf_size);

/**
 * Python Interface: Performance test
 * @param iterations Number of test iterations
 * @param results Array to store performance results [4 doubles]
 *                results[0] = addr_gen_avg
 *                results[1] = addr_verify_avg
 *                results[2] = onetime_sk_avg  
 *                results[3] = h1_avg
 */
void cryptonote2_performance_test_simple(int iterations, double* results);

/**
 * Python Interface: Get curve information
 * @param curve_name Buffer for curve name (output)
 * @param point_size Pointer to store point size (output)
 * @param scalar_size Pointer to store scalar size (output)  
 * @param buffer_size Pointer to store recommended buffer size (output)
 */
void cryptonote2_get_curve_info(char* curve_name, int* point_size, int* scalar_size, int* buffer_size);

#endif /* CRYPTONOTE2_PYTHON_API_H */