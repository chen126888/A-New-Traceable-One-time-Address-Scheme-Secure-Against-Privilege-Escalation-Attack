/****************************************************************************
 * File: python_api.h  
 * Desc: Python interface functions for Zhao et al. scheme
 *       Simple byte-based wrappers around core cryptographic functions
 ****************************************************************************/

#ifndef ZHAO_PYTHON_API_H
#define ZHAO_PYTHON_API_H

//----------------------------------------------
// Python Interface Functions
// These functions use byte arrays instead of OpenSSL types
// for easy integration with Python ctypes
//----------------------------------------------

/**
 * Python Interface: Generate key pair
 * @param public_key_out Buffer for public key (output)
 * @param private_key_out Buffer for private key (output)  
 * @param buf_size Size of each buffer
 */
void zhao_keygen_simple(unsigned char* public_key_out, unsigned char* private_key_out, int buf_size);

/**
 * Python Interface: Sign message using Zhao's signature scheme
 * @param message Message to sign (null-terminated string)
 * @param private_key_bytes Private key as bytes
 * @param signature_out Buffer for signature component (output)
 * @param hash_out Buffer for hash component (output)  
 * @param buf_size Size of output buffers
 */
void zhao_sign_simple(const char* message, const unsigned char* private_key_bytes,
                      unsigned char* signature_out, unsigned char* hash_out, int buf_size);

/**
 * Python Interface: Verify signature using Zhao's verification algorithm
 * @param message Message that was signed (null-terminated string)
 * @param public_key_bytes Signer's public key as bytes
 * @param signature_bytes Signature component as bytes
 * @param hash_bytes Hash component as bytes
 * @return 1 if signature is valid, 0 otherwise
 */
int zhao_verify_simple(const char* message, const unsigned char* public_key_bytes,
                       const unsigned char* signature_bytes, const unsigned char* hash_bytes);

/**
 * Python Interface: Hash arbitrary data to scalar
 * @param data Input data bytes
 * @param data_len Length of input data
 * @param hash_out Buffer for hash result (output)
 * @param buf_size Size of output buffer
 */
void zhao_hash_simple(const unsigned char* data, int data_len, 
                      unsigned char* hash_out, int buf_size);

/**
 * Python Interface: Performance test
 * @param iterations Number of test iterations
 * @param results Array to store performance results [4 doubles]
 *                results[0] = keygen_avg
 *                results[1] = sign_avg
 *                results[2] = verify_avg
 *                results[3] = hash_avg
 */
void zhao_performance_test_simple(int iterations, double* results);

/**
 * Python Interface: Get curve information
 * @param curve_name Buffer for curve name (output)
 * @param point_size Pointer to store point size (output)
 * @param scalar_size Pointer to store scalar size (output)  
 * @param buffer_size Pointer to store recommended buffer size (output)
 */
void zhao_get_curve_info(char* curve_name, int* point_size, int* scalar_size, int* buffer_size);

#endif /* ZHAO_PYTHON_API_H */