/****************************************************************************
 * File: core.h
 * Desc: Core cryptographic functions for CryptoNote2 scheme
 * Uses: OpenSSL ECC (secp256r1 and other curves)
 ****************************************************************************/

#ifndef CRYPTONOTE2_CORE_H
#define CRYPTONOTE2_CORE_H

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
#define CRYPTONOTE2_MAX_BUFFER_SIZE 96  // Support up to secp521r1
#define CRYPTONOTE2_DEFAULT_BUFFER_SIZE 64  // Default for secp256r1
#define CRYPTONOTE2_MAX_POINT_SIZE 67   // secp521r1 compressed point
#define CRYPTONOTE2_MAX_SCALAR_SIZE 66  // secp521r1 scalar

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
    
} cryptonote2_context_t;

//----------------------------------------------
// Performance Statistics Structure  
//----------------------------------------------
typedef struct {
    double addr_gen_avg;
    double addr_verify_avg;
    double onetime_sk_avg;
    double h1_avg;
    int operation_count;
} cryptonote2_performance_t;

//----------------------------------------------
// Library Management Functions
//----------------------------------------------

/**
 * Initialize CryptoNote2 with curve configuration file
 * @param config_file Path to curve configuration file
 * @return 0 on success, -1 on failure
 */
int cryptonote2_init(const char* config_file);

/**
 * Check if library is initialized
 * @return 1 if initialized, 0 otherwise
 */
int cryptonote2_is_initialized(void);

/**
 * Cleanup library resources
 */
void cryptonote2_cleanup(void);

/**
 * Reset performance counters
 */
void cryptonote2_reset_performance(void);

/**
 * Get the current context for use in API functions
 * @return Pointer to the global context, NULL if not initialized
 */
cryptonote2_context_t* cryptonote2_get_context(void);

//----------------------------------------------
// Core Cryptographic Functions
//----------------------------------------------

/**
 * Generate a key pair (A, B, a, b) 
 * @param A Public key A (output)
 * @param B Public key B (output)
 * @param a Private key a (output)
 * @param b Private key b (output)
 * @param ctx BN context for computations
 */
void cryptonote2_keygen(EC_POINT *A, EC_POINT *B, BIGNUM *a, BIGNUM *b, BN_CTX *ctx);

/**
 * Generate one-time address
 * @param PK_one One-time public key (output)
 * @param R Random point R (output)
 * @param A Public key A (input)
 * @param B Public key B (input)  
 * @param ctx BN context for computations
 */
void cryptonote2_addr_gen(EC_POINT *PK_one, EC_POINT *R, EC_POINT *A, EC_POINT *B, BN_CTX *ctx);

/**
 * Verify/recognize one-time address (Receiver Statistics)
 * @param PK_one One-time public key to verify
 * @param R Random point R
 * @param a Private key a
 * @param B Public key B
 * @param ctx BN context for computations
 * @return 1 if address belongs to receiver, 0 otherwise
 */
int cryptonote2_addr_verify(EC_POINT *PK_one, EC_POINT *R, BIGNUM *a, EC_POINT *B, BN_CTX *ctx);

/**
 * Generate one-time secret key
 * @param sk_ot One-time secret key (output)
 * @param R Random point R
 * @param a Private key a
 * @param b Private key b
 * @param ctx BN context for computations
 */
void cryptonote2_onetime_sk_gen(BIGNUM *sk_ot, EC_POINT *R, BIGNUM *a, BIGNUM *b, BN_CTX *ctx);

//----------------------------------------------
// Hash Functions
//----------------------------------------------

/**
 * Hash function H1: EC_POINT -> BIGNUM
 * Maps elliptic curve point to scalar value
 * @param outZr Output scalar (output)
 * @param inG1 Input elliptic curve point
 * @param ctx BN context for computations
 */
void cryptonote2_H1(BIGNUM *outZr, EC_POINT *inG1, BN_CTX *ctx);

/**
 * General hash function: bytes -> BIGNUM
 * @param out_scalar Output scalar (output)
 * @param data Input data bytes
 * @param len Length of input data
 * @param ctx BN context for computations
 */
void cryptonote2_hash_bytes_to_scalar(BIGNUM *out_scalar, const unsigned char *data, int len, BN_CTX *ctx);

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
int cryptonote2_point_to_bytes(EC_POINT *point, unsigned char *buf, int buf_size);

/**
 * Convert bytes to EC_POINT
 * @param point Output elliptic curve point (must be initialized)
 * @param buf Input buffer
 * @param buf_len Length of input data
 * @return 0 on success, -1 on error
 */
int cryptonote2_point_from_bytes(EC_POINT *point, const unsigned char *buf, int buf_len);

/**
 * Convert BIGNUM scalar to bytes
 * @param scalar Input scalar
 * @param buf Output buffer
 * @param buf_size Size of output buffer  
 * @return Number of bytes written, -1 on error
 */
int cryptonote2_scalar_to_bytes(BIGNUM *scalar, unsigned char *buf, int buf_size);

/**
 * Convert bytes to BIGNUM scalar
 * @param scalar Output scalar (must be initialized)
 * @param buf Input buffer
 * @param buf_len Length of input data
 * @return 0 on success, -1 on error
 */
int cryptonote2_scalar_from_bytes(BIGNUM *scalar, const unsigned char *buf, int buf_len);

//----------------------------------------------
// Configuration Parser Functions
//----------------------------------------------

/**
 * Parse curve configuration file
 * @param config_file Path to configuration file
 * @param ctx Context to fill with parsed values
 * @return 0 on success, -1 on error
 */
int cryptonote2_parse_config(const char* config_file, cryptonote2_context_t* ctx);

/**
 * Get buffer sizes for current curve
 * @param point_size Pointer to store point size (can be NULL)
 * @param scalar_size Pointer to store scalar size (can be NULL)
 * @param buffer_size Pointer to store recommended buffer size (can be NULL)
 */
void cryptonote2_get_sizes(int* point_size, int* scalar_size, int* buffer_size);

//----------------------------------------------
// Performance and Utility Functions
//----------------------------------------------

/**
 * Get performance statistics
 * @param perf Performance structure to fill (output)
 */
void cryptonote2_get_performance(cryptonote2_performance_t* perf);

/**
 * Print performance statistics to stdout
 */
void cryptonote2_print_performance(void);

/**
 * Run performance test
 * @param iterations Number of test iterations
 * @param results Array to store results [4 doubles: addr_gen, addr_verify, onetime_sk, h1]
 */
void cryptonote2_performance_test(int iterations, double* results);

#endif /* CRYPTONOTE2_CORE_H */