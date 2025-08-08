/****************************************************************************
 * File: core.h
 * Desc: Core cryptographic functions for Zhao et al. scheme
 * Uses: OpenSSL ECC (supports multiple elliptic curves)
 ****************************************************************************/

#ifndef ZHAO_CORE_H
#define ZHAO_CORE_H

#include <openssl/ec.h>
#include <openssl/ecdsa.h>
#include <openssl/obj_mac.h>
#include <openssl/sha.h>
#include <openssl/bn.h>
#include <openssl/rand.h>
#include <openssl/evp.h>

//----------------------------------------------
// Constants and Buffer Sizes
//----------------------------------------------
#define ZHAO_MAX_BUFFER_SIZE 96        // Support up to secp521r1
#define ZHAO_DEFAULT_BUFFER_SIZE 64    // Default for secp256r1
#define ZHAO_MAX_POINT_SIZE 67         // secp521r1 compressed point
#define ZHAO_MAX_SCALAR_SIZE 66        // secp521r1 scalar

//----------------------------------------------
// Global Context Structure
//----------------------------------------------
typedef struct {
    EC_GROUP *group;
    EC_POINT *G;          // Generator point
    BIGNUM *order;        // Group order
    int initialized;
    
    // Curve parameters from config
    int nid;              // OpenSSL curve NID
    int point_size;       // Point size in bytes
    int scalar_size;      // Scalar size in bytes
    int buffer_size;      // Buffer size for this curve
    char curve_name[32];  // Curve name
    char hash_alg[16];    // Hash algorithm (sha256, sha384, sha512)
    
} zhao_context_t;

//----------------------------------------------
// Performance Statistics Structure  
//----------------------------------------------
typedef struct {
    double keygen_avg;
    double sign_avg;
    double verify_avg;
    double hash_avg;
    int operation_count;
} zhao_performance_t;

//----------------------------------------------
// Library Management Functions
//----------------------------------------------

/**
 * Initialize Zhao scheme with curve configuration file
 * @param config_file Path to curve configuration file
 * @return 0 on success, -1 on failure
 */
int zhao_init(const char* config_file);

/**
 * Check if library is initialized
 * @return 1 if initialized, 0 otherwise
 */
int zhao_is_initialized(void);

/**
 * Cleanup library resources
 */
void zhao_cleanup(void);

/**
 * Reset performance counters
 */
void zhao_reset_performance(void);

/**
 * Get the current context for use in API functions
 * @return Pointer to the global context, NULL if not initialized
 */
zhao_context_t* zhao_get_context(void);

//----------------------------------------------
// Core Cryptographic Functions
//----------------------------------------------

/**
 * Generate a key pair (public_key, private_key)
 * @param public_key Public key (output)
 * @param private_key Private key (output)
 * @param ctx BN context for computations
 */
void zhao_keygen(EC_POINT *public_key, BIGNUM *private_key, BN_CTX *ctx);

/**
 * Sign a message using Zhao's signature scheme
 * @param signature Signature component (output)
 * @param hash_value Hash component (output)  
 * @param message Message to sign
 * @param msg_len Length of message
 * @param private_key Signer's private key
 * @param ctx BN context for computations
 */
void zhao_sign(EC_POINT *signature, BIGNUM *hash_value, const unsigned char* message, 
               int msg_len, BIGNUM *private_key, BN_CTX *ctx);

/**
 * Verify a signature using Zhao's verification algorithm
 * @param public_key Signer's public key
 * @param signature Signature component
 * @param hash_value Hash component
 * @param message Original message
 * @param msg_len Length of message
 * @param ctx BN context for computations
 * @return 1 if signature is valid, 0 otherwise
 */
int zhao_verify(EC_POINT *public_key, EC_POINT *signature, BIGNUM *hash_value,
                const unsigned char* message, int msg_len, BN_CTX *ctx);

//----------------------------------------------
// Hash Functions
//----------------------------------------------

/**
 * Hash function: bytes -> BIGNUM
 * Maps byte array to scalar value using Zhao's hash method
 * @param out_scalar Output scalar (output)
 * @param data Input data bytes
 * @param len Length of input data
 * @param ctx BN context for computations
 */
void zhao_hash_to_scalar(BIGNUM *out_scalar, const unsigned char *data, int len, BN_CTX *ctx);

/**
 * Hash function: EC_POINT -> BIGNUM  
 * Maps elliptic curve point to scalar value
 * @param out_scalar Output scalar (output)
 * @param point Input elliptic curve point
 * @param ctx BN context for computations
 */
void zhao_hash_point_to_scalar(BIGNUM *out_scalar, EC_POINT *point, BN_CTX *ctx);

//----------------------------------------------
// Serialization Helper Functions
//----------------------------------------------

/**
 * Convert EC_POINT to bytes (compressed format)
 * @param point Input elliptic curve point
 * @param buf Output buffer
 * @param buf_size Size of output buffer
 * @return Number of bytes written, -1 on error
 */
int zhao_point_to_bytes(EC_POINT *point, unsigned char *buf, int buf_size);

/**
 * Convert bytes to EC_POINT
 * @param point Output elliptic curve point (must be initialized)
 * @param buf Input buffer
 * @param buf_len Length of input data
 * @return 0 on success, -1 on error
 */
int zhao_point_from_bytes(EC_POINT *point, const unsigned char *buf, int buf_len);

/**
 * Convert BIGNUM scalar to bytes
 * @param scalar Input scalar
 * @param buf Output buffer
 * @param buf_size Size of output buffer  
 * @return Number of bytes written, -1 on error
 */
int zhao_scalar_to_bytes(BIGNUM *scalar, unsigned char *buf, int buf_size);

/**
 * Convert bytes to BIGNUM scalar
 * @param scalar Output scalar (must be initialized)
 * @param buf Input buffer
 * @param buf_len Length of input data
 * @return 0 on success, -1 on error
 */
int zhao_scalar_from_bytes(BIGNUM *scalar, const unsigned char *buf, int buf_len);

//----------------------------------------------
// Configuration Parser Functions
//----------------------------------------------

/**
 * Parse curve configuration file
 * @param config_file Path to configuration file
 * @param ctx Context to fill with parsed values
 * @return 0 on success, -1 on error
 */
int zhao_parse_config(const char* config_file, zhao_context_t* ctx);

/**
 * Get buffer sizes for current curve
 * @param point_size Pointer to store point size (can be NULL)
 * @param scalar_size Pointer to store scalar size (can be NULL)
 * @param buffer_size Pointer to store recommended buffer size (can be NULL)
 */
void zhao_get_sizes(int* point_size, int* scalar_size, int* buffer_size);

//----------------------------------------------
// Performance and Utility Functions
//----------------------------------------------

/**
 * Get performance statistics
 * @param perf Performance structure to fill (output)
 */
void zhao_get_performance(zhao_performance_t* perf);

/**
 * Print performance statistics to stdout
 */
void zhao_print_performance(void);

/**
 * Run performance test
 * @param iterations Number of test iterations
 * @param results Array to store results [4 doubles: keygen, sign, verify, hash]
 */
void zhao_performance_test(int iterations, double* results);

#endif /* ZHAO_CORE_H */