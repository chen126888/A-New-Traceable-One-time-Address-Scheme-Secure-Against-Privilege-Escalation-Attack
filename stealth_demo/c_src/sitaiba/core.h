/****************************************************************************
 * File: core.h
 * Desc: Core cryptographic functions for Sitaiba et al. scheme
 * Uses: PBC library for pairing-based cryptography (similar to My Stealth)
 ****************************************************************************/

#ifndef SITAIBA_CORE_H
#define SITAIBA_CORE_H

#include <pbc/pbc.h>

//----------------------------------------------
// Performance Statistics Structure
//----------------------------------------------
typedef struct {
    double keygen_avg;
    double sign_avg;
    double verify_avg;
    double pairing_avg;
    double hash_avg;
    int operation_count;
} sitaiba_performance_t;

//----------------------------------------------
// Library Management Functions
//----------------------------------------------

/**
 * Initialize the Sitaiba library with a parameter file
 * @param param_file Path to the PBC parameter file
 * @return 0 on success, -1 on failure
 */
int sitaiba_init(const char* param_file);

/**
 * Check if library is initialized
 * @return 1 if initialized, 0 otherwise
 */
int sitaiba_is_initialized(void);

/**
 * Cleanup library resources
 */
void sitaiba_cleanup(void);

/**
 * Reset performance counters
 */
void sitaiba_reset_performance(void);

/**
 * Get the current pairing for use in API functions
 * @return Pointer to the global pairing, NULL if not initialized
 */
pairing_t* sitaiba_get_pairing(void);

//----------------------------------------------
// Core Cryptographic Functions
//----------------------------------------------

/**
 * Generate a key pair for Sitaiba scheme
 * @param public_key Public key (output)
 * @param private_key Private key (output)
 */
void sitaiba_keygen(element_t public_key, element_t private_key);

/**
 * Sign a message using Sitaiba's signature scheme
 * @param signature Signature (output)
 * @param message Message to sign
 * @param msg_len Length of message
 * @param private_key Private key for signing
 */
void sitaiba_sign(element_t signature, const unsigned char* message, int msg_len, element_t private_key);

/**
 * Verify a signature using Sitaiba's verification algorithm
 * @param public_key Public key for verification
 * @param signature Signature to verify
 * @param message Original message
 * @param msg_len Length of message
 * @return 1 if signature is valid, 0 otherwise
 */
int sitaiba_verify(element_t public_key, element_t signature, 
                   const unsigned char* message, int msg_len);

/**
 * Generate anonymous credentials (if supported by Sitaiba scheme)
 * @param credential Anonymous credential (output)
 * @param identity User identity
 * @param identity_len Length of identity
 * @param issuer_key Issuer's key
 */
void sitaiba_issue_credential(element_t credential, const unsigned char* identity, 
                             int identity_len, element_t issuer_key);

/**
 * Verify anonymous credential
 * @param credential Credential to verify
 * @param issuer_public_key Issuer's public key
 * @param identity User identity (may be hidden)
 * @param identity_len Length of identity
 * @return 1 if credential is valid, 0 otherwise
 */
int sitaiba_verify_credential(element_t credential, element_t issuer_public_key,
                             const unsigned char* identity, int identity_len);

//----------------------------------------------
// Hash Functions
//----------------------------------------------

/**
 * Sitaiba hash function: bytes -> Zr element
 * @param hash_out Output hash element (output)
 * @param data Input data
 * @param len Length of input data
 */
void sitaiba_hash_to_zr(element_t hash_out, const unsigned char* data, int len);

/**
 * Sitaiba hash function: bytes -> G1 element  
 * @param hash_out Output hash element (output)
 * @param data Input data
 * @param len Length of input data
 */
void sitaiba_hash_to_g1(element_t hash_out, const unsigned char* data, int len);

/**
 * Sitaiba hash function: bytes -> G2 element
 * @param hash_out Output hash element (output)
 * @param data Input data
 * @param len Length of input data
 */
void sitaiba_hash_to_g2(element_t hash_out, const unsigned char* data, int len);

//----------------------------------------------
// Pairing Operations (specific to Sitaiba)
//----------------------------------------------

/**
 * Compute pairing for Sitaiba verification
 * @param result Pairing result (output)
 * @param g1_elem Element from G1
 * @param g2_elem Element from G2
 */
void sitaiba_pairing_apply(element_t result, element_t g1_elem, element_t g2_elem);

/**
 * Batch pairing verification (if supported)
 * @param g1_array Array of G1 elements
 * @param g2_array Array of G2 elements
 * @param count Number of elements
 * @return 1 if batch verification succeeds, 0 otherwise
 */
int sitaiba_batch_verify(element_t* g1_array, element_t* g2_array, int count);

//----------------------------------------------
// Performance and Utility Functions
//----------------------------------------------

/**
 * Get performance statistics
 * @param perf Performance structure to fill (output)
 */
void sitaiba_get_performance(sitaiba_performance_t* perf);

/**
 * Print performance statistics to stdout
 */
void sitaiba_print_performance(void);

/**
 * Run performance test
 * @param iterations Number of test iterations
 * @param results Array to store results [5 doubles: keygen, sign, verify, pairing, hash]
 */
void sitaiba_performance_test(int iterations, double* results);

//----------------------------------------------
// Element Serialization Helpers
//----------------------------------------------

/**
 * Get the size needed for serializing a G1 element
 * @return Size in bytes, 0 if not initialized
 */
int sitaiba_element_size_G1(void);

/**
 * Get the size needed for serializing a G2 element
 * @return Size in bytes, 0 if not initialized
 */
int sitaiba_element_size_G2(void);

/**
 * Get the size needed for serializing a GT element
 * @return Size in bytes, 0 if not initialized
 */
int sitaiba_element_size_GT(void);

/**
 * Get the size needed for serializing a Zr element
 * @return Size in bytes, 0 if not initialized
 */
int sitaiba_element_size_Zr(void);

/**
 * Serialize element to bytes
 * @param elem Element to serialize
 * @param buf Buffer to write to
 * @param buf_size Size of buffer
 * @return Number of bytes written, -1 on error
 */
int sitaiba_element_to_bytes(element_t elem, unsigned char* buf, int buf_size);

/**
 * Deserialize G1 element from bytes
 * @param elem Element to initialize and fill (output)
 * @param buf Buffer to read from
 * @param len Length of data
 * @return 0 on success, -1 on error
 */
int sitaiba_element_from_bytes_G1(element_t elem, const unsigned char* buf, int len);

/**
 * Deserialize G2 element from bytes
 * @param elem Element to initialize and fill (output)
 * @param buf Buffer to read from
 * @param len Length of data
 * @return 0 on success, -1 on error
 */
int sitaiba_element_from_bytes_G2(element_t elem, const unsigned char* buf, int len);

/**
 * Deserialize GT element from bytes
 * @param elem Element to initialize and fill (output)
 * @param buf Buffer to read from
 * @param len Length of data
 * @return 0 on success, -1 on error
 */
int sitaiba_element_from_bytes_GT(element_t elem, const unsigned char* buf, int len);

/**
 * Deserialize Zr element from bytes
 * @param elem Element to initialize and fill (output)
 * @param buf Buffer to read from
 * @param len Length of data
 * @return 0 on success, -1 on error
 */
int sitaiba_element_from_bytes_Zr(element_t elem, const unsigned char* buf, int len);

#endif /* SITAIBA_CORE_H */