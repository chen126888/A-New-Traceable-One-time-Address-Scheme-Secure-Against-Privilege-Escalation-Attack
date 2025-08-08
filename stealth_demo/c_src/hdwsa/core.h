/****************************************************************************
 * File: core.h
 * Desc: Core cryptographic functions for HDWSA (Hierarchical Deterministic Wallet Signature Algorithm)
 * Uses: PBC library for pairing-based cryptography (same as My Stealth)
 ****************************************************************************/

#ifndef HDWSA_CORE_H
#define HDWSA_CORE_H

#include <pbc/pbc.h>

//----------------------------------------------
// Performance Statistics Structure
//----------------------------------------------
typedef struct {
    double keygen_avg;
    double sign_avg;
    double verify_avg;
    double derive_avg;
    double hash_avg;
    int operation_count;
} hdwsa_performance_t;

//----------------------------------------------
// HDWSA Key Structure
//----------------------------------------------
typedef struct {
    element_t master_secret;    // Master secret key
    element_t master_public;    // Master public key
    element_t chain_code;       // Chain code for derivation
    int depth;                  // Derivation depth
    unsigned char fingerprint[4]; // Parent key fingerprint
} hdwsa_key_t;

//----------------------------------------------
// Library Management Functions
//----------------------------------------------

/**
 * Initialize the HDWSA library with a parameter file
 * @param param_file Path to the PBC parameter file
 * @return 0 on success, -1 on failure
 */
int hdwsa_init(const char* param_file);

/**
 * Check if library is initialized
 * @return 1 if initialized, 0 otherwise
 */
int hdwsa_is_initialized(void);

/**
 * Cleanup library resources
 */
void hdwsa_cleanup(void);

/**
 * Reset performance counters
 */
void hdwsa_reset_performance(void);

/**
 * Get the current pairing for use in API functions
 * @return Pointer to the global pairing, NULL if not initialized
 */
pairing_t* hdwsa_get_pairing(void);

//----------------------------------------------
// Core Cryptographic Functions
//----------------------------------------------

/**
 * Generate master key pair from seed
 * @param master_key Master key structure (output)
 * @param seed Random seed for key generation
 * @param seed_len Length of seed
 */
void hdwsa_master_keygen(hdwsa_key_t* master_key, const unsigned char* seed, int seed_len);

/**
 * Derive child key from parent key
 * @param child_key Child key structure (output)
 * @param parent_key Parent key structure (input)
 * @param index Child key index
 * @param hardened Whether to use hardened derivation
 */
void hdwsa_derive_child_key(hdwsa_key_t* child_key, const hdwsa_key_t* parent_key, 
                           unsigned int index, int hardened);

/**
 * Generate simple key pair (non-hierarchical)
 * @param public_key Public key (output)
 * @param private_key Private key (output)
 */
void hdwsa_keygen(element_t public_key, element_t private_key);

/**
 * Sign a message using HDWSA signature scheme
 * @param signature Signature (output)
 * @param message Message to sign
 * @param msg_len Length of message
 * @param private_key Private key for signing
 */
void hdwsa_sign(element_t signature, const unsigned char* message, int msg_len, element_t private_key);

/**
 * Verify a signature using HDWSA verification algorithm
 * @param public_key Public key for verification
 * @param signature Signature to verify
 * @param message Original message
 * @param msg_len Length of message
 * @return 1 if signature is valid, 0 otherwise
 */
int hdwsa_verify(element_t public_key, element_t signature, 
                 const unsigned char* message, int msg_len);

//----------------------------------------------
// Hash Functions
//----------------------------------------------

/**
 * HDWSA hash function: bytes -> Zr element
 * @param hash_out Output hash element (output)
 * @param data Input data
 * @param len Length of input data
 */
void hdwsa_hash_to_zr(element_t hash_out, const unsigned char* data, int len);

/**
 * HDWSA hash function: bytes -> G1 element  
 * @param hash_out Output hash element (output)
 * @param data Input data
 * @param len Length of input data
 */
void hdwsa_hash_to_g1(element_t hash_out, const unsigned char* data, int len);

//----------------------------------------------
// Key Management Functions
//----------------------------------------------

/**
 * Initialize HDWSA key structure
 * @param key Key structure to initialize
 */
void hdwsa_key_init(hdwsa_key_t* key);

/**
 * Clear HDWSA key structure
 * @param key Key structure to clear
 */
void hdwsa_key_clear(hdwsa_key_t* key);

/**
 * Copy HDWSA key structure
 * @param dest Destination key structure
 * @param src Source key structure
 */
void hdwsa_key_copy(hdwsa_key_t* dest, const hdwsa_key_t* src);

//----------------------------------------------
// Performance and Utility Functions
//----------------------------------------------

/**
 * Get performance statistics
 * @param perf Performance structure to fill (output)
 */
void hdwsa_get_performance(hdwsa_performance_t* perf);

/**
 * Print performance statistics to stdout
 */
void hdwsa_print_performance(void);

/**
 * Run performance test
 * @param iterations Number of test iterations
 * @param results Array to store results [5 doubles: keygen, sign, verify, derive, hash]
 */
void hdwsa_performance_test(int iterations, double* results);

//----------------------------------------------
// Element Serialization Helpers
//----------------------------------------------

/**
 * Get the size needed for serializing a G1 element
 * @return Size in bytes, 0 if not initialized
 */
int hdwsa_element_size_G1(void);

/**
 * Get the size needed for serializing a Zr element
 * @return Size in bytes, 0 if not initialized
 */
int hdwsa_element_size_Zr(void);

/**
 * Serialize element to bytes
 * @param elem Element to serialize
 * @param buf Buffer to write to
 * @param buf_size Size of buffer
 * @return Number of bytes written, -1 on error
 */
int hdwsa_element_to_bytes(element_t elem, unsigned char* buf, int buf_size);

/**
 * Deserialize G1 element from bytes
 * @param elem Element to initialize and fill (output)
 * @param buf Buffer to read from
 * @param len Length of data
 * @return 0 on success, -1 on error
 */
int hdwsa_element_from_bytes_G1(element_t elem, const unsigned char* buf, int len);

/**
 * Deserialize Zr element from bytes
 * @param elem Element to initialize and fill (output)
 * @param buf Buffer to read from
 * @param len Length of data
 * @return 0 on success, -1 on error
 */
int hdwsa_element_from_bytes_Zr(element_t elem, const unsigned char* buf, int len);

#endif /* HDWSA_CORE_H */