/****************************************************************************
 * File: python_api.h  
 * Desc: Python interface functions for HDWSA scheme
 *       Simple byte-based wrappers around core cryptographic functions
 ****************************************************************************/

#ifndef HDWSA_PYTHON_API_H
#define HDWSA_PYTHON_API_H

//----------------------------------------------
// Python Interface Functions
// These functions use byte arrays instead of PBC element_t types
// for easy integration with Python ctypes
//----------------------------------------------

/**
 * Python Interface: Generate key pair
 * @param public_key_out Buffer for public key (output)
 * @param private_key_out Buffer for private key (output)  
 * @param buf_size Size of each buffer
 */
void hdwsa_keygen_simple(unsigned char* public_key_out, unsigned char* private_key_out, int buf_size);

/**
 * Python Interface: Sign message using HDWSA signature scheme
 * @param message Message to sign (null-terminated string)
 * @param private_key_bytes Private key as bytes
 * @param signature_out Buffer for signature (output)
 * @param buf_size Size of output buffer
 */
void hdwsa_sign_simple(const char* message, const unsigned char* private_key_bytes,
                       unsigned char* signature_out, int buf_size);

/**
 * Python Interface: Verify signature using HDWSA verification algorithm
 * @param message Message that was signed (null-terminated string)
 * @param public_key_bytes Signer's public key as bytes
 * @param signature_bytes Signature as bytes
 * @return 1 if signature is valid, 0 otherwise
 */
int hdwsa_verify_simple(const char* message, const unsigned char* public_key_bytes,
                        const unsigned char* signature_bytes);

/**
 * Python Interface: Generate master key from seed
 * @param seed Random seed for key generation
 * @param seed_len Length of seed
 * @param master_secret_out Buffer for master secret key (output)
 * @param master_public_out Buffer for master public key (output)
 * @param chain_code_out Buffer for chain code (output)
 * @param buf_size Size of each buffer
 */
void hdwsa_master_keygen_simple(const unsigned char* seed, int seed_len,
                                unsigned char* master_secret_out, unsigned char* master_public_out,
                                unsigned char* chain_code_out, int buf_size);

/**
 * Python Interface: Derive child key from parent key
 * @param parent_secret_bytes Parent secret key as bytes
 * @param parent_public_bytes Parent public key as bytes  
 * @param parent_chain_bytes Parent chain code as bytes
 * @param index Child key index
 * @param hardened Whether to use hardened derivation (1 = yes, 0 = no)
 * @param child_secret_out Buffer for child secret key (output)
 * @param child_public_out Buffer for child public key (output)
 * @param child_chain_out Buffer for child chain code (output)
 * @param buf_size Size of each buffer
 */
void hdwsa_derive_child_simple(const unsigned char* parent_secret_bytes,
                               const unsigned char* parent_public_bytes,
                               const unsigned char* parent_chain_bytes,
                               unsigned int index, int hardened,
                               unsigned char* child_secret_out,
                               unsigned char* child_public_out,
                               unsigned char* child_chain_out, int buf_size);

/**
 * Python Interface: Hash arbitrary data to Zr element
 * @param data Input data bytes
 * @param data_len Length of input data
 * @param hash_out Buffer for hash result (output)
 * @param buf_size Size of output buffer
 */
void hdwsa_hash_simple(const unsigned char* data, int data_len, 
                       unsigned char* hash_out, int buf_size);

/**
 * Python Interface: Performance test
 * @param iterations Number of test iterations
 * @param results Array to store performance results [5 doubles]
 *                results[0] = keygen_avg
 *                results[1] = sign_avg
 *                results[2] = verify_avg
 *                results[3] = derive_avg
 *                results[4] = hash_avg
 */
void hdwsa_performance_test_simple(int iterations, double* results);

#endif /* HDWSA_PYTHON_API_H */