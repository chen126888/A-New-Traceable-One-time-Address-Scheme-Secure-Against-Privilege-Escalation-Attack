/****************************************************************************
 * File: stealth_core.h
 * Desc: Core cryptographic functions for Traceable Anonymous Transaction Scheme
 ****************************************************************************/

#ifndef STEALTH_CORE_H
#define STEALTH_CORE_H

#include <pbc/pbc.h>

//----------------------------------------------
// Performance Statistics Structure
//----------------------------------------------
typedef struct {
    double addr_gen_avg;
    double addr_recognize_avg;
    double fast_recognize_avg;
    double onetime_sk_avg;
    double sign_avg;
    double verify_avg;
    double trace_avg;
    int operation_count;
} stealth_performance_t;

//----------------------------------------------
// Library Management Functions
//----------------------------------------------

/**
 * Initialize the library with a parameter file
 * @param param_file Path to the PBC parameter file
 * @return 0 on success, -1 on failure
 */
int stealth_init(const char* param_file);

/**
 * Check if library is initialized
 * @return 1 if initialized, 0 otherwise
 */
int stealth_is_initialized(void);

/**
 * Cleanup library resources
 */
void stealth_cleanup(void);

/**
 * Reset performance counters
 */
void stealth_reset_performance(void);

/**
 * Performance counter (exposed for external access)
 */
extern int perf_counter;

/**
 * Get the current pairing for use in API functions
 * @return Pointer to the global pairing, NULL if not initialized
 */
pairing_t* stealth_get_pairing(void);

//----------------------------------------------
// Core Cryptographic Functions
//----------------------------------------------

/**
 * Generate a key pair (A, B, a, b)
 * @param A Public key A (output)
 * @param B Public key B (output)
 * @param aZ Private key a (output)
 * @param bZ Private key b (output)
 */
void stealth_keygen(element_t A, element_t B, element_t aZ, element_t bZ);

/**
 * Generate trace key (TK, k)
 * @param TK Trace public key (output)
 * @param kZ Trace private key (output)
 */
void stealth_tracekeygen(element_t TK, element_t kZ);

/**
 * Generate one-time address
 * @param Addr Generated address (output)
 * @param R1 Random element R1 (output)
 * @param R2 Random element R2 (output)
 * @param C Commitment C (output)
 * @param A_r Public key A
 * @param B_r Public key B
 * @param TK Trace public key
 */
void stealth_addr_gen(element_t Addr, element_t R1, element_t R2, element_t C,
                     element_t A_r, element_t B_r, element_t TK);

/**
 * Recognize address (full version)
 * @param Addr Address to recognize
 * @param R1 Random element R1
 * @param B_r Public key B
 * @param A_r Public key A
 * @param C Commitment C
 * @param aZ Private key a
 * @param TK Trace public key
 * @return 1 if recognized, 0 otherwise
 */
int stealth_addr_recognize(element_t Addr, element_t R1, element_t B_r,
                          element_t A_r, element_t C, element_t aZ, element_t TK);

/**
 * Fast address recognition
 * @param R1 Random element R1
 * @param B_r Public key B
 * @param A_r Public key A
 * @param C Commitment C
 * @param aZ Private key a
 * @return 1 if recognized, 0 otherwise
 */
int stealth_addr_recognize_fast(element_t R1, element_t B_r, element_t A_r, 
                               element_t C, element_t aZ);

/**
 * Generate one-time secret key
 * @param dsk One-time secret key (output)
 * @param Addr Address
 * @param R1 Random element R1
 * @param aZ Private key a
 * @param bZ Private key b
 */
void stealth_onetime_skgen(element_t dsk, element_t Addr, element_t R1,
                          element_t aZ, element_t bZ);

/**
 * Sign a message
 * @param Q_sigma Signature component (output)
 * @param hZ Hash value (output)
 * @param Addr Address
 * @param dsk One-time secret key
 * @param msg Message to sign
 */
void stealth_sign(element_t Q_sigma, element_t hZ, element_t Addr, 
                 element_t dsk, const char* msg);

/**
 * Verify a signature
 * @param Addr Address
 * @param R2 Random element R2
 * @param C Commitment C
 * @param msg Message
 * @param hZ Hash value
 * @param Q_sigma Signature component
 * @return 1 if valid, 0 otherwise
 */
int stealth_verify(element_t Addr, element_t R2, element_t C,
                  const char* msg, element_t hZ, element_t Q_sigma);

/**
 * Trace identity
 * @param B_r Recovered public key B (output)
 * @param Addr Address
 * @param R1 Random element R1
 * @param R2 Random element R2
 * @param C Commitment C
 * @param kZ Trace private key
 */
void stealth_trace(element_t B_r, element_t Addr, element_t R1, element_t R2, 
                  element_t C, element_t kZ);

//----------------------------------------------
// Performance and Utility Functions
//----------------------------------------------

/**
 * Get performance statistics
 * @param perf Performance structure to fill (output)
 */
void stealth_get_performance(stealth_performance_t* perf);

/**
 * Print performance statistics to stdout
 */
void stealth_print_performance(void);

//----------------------------------------------
// Element Serialization Helpers
//----------------------------------------------

/**
 * Get the size needed for serializing a G1 element
 * @return Size in bytes, 0 if not initialized
 */
int stealth_element_size_G1(void);

/**
 * Get the size needed for serializing a Zr element
 * @return Size in bytes, 0 if not initialized
 */
int stealth_element_size_Zr(void);

/**
 * Serialize element to bytes
 * @param elem Element to serialize
 * @param buf Buffer to write to
 * @param buf_size Size of buffer
 * @return Number of bytes written, -1 on error
 */
int stealth_element_to_bytes(element_t elem, unsigned char* buf, int buf_size);

/**
 * Deserialize G1 element from bytes
 * @param elem Element to initialize and fill (output)
 * @param buf Buffer to read from
 * @param len Length of data
 * @return 0 on success, -1 on error
 */
int stealth_element_from_bytes_G1(element_t elem, const unsigned char* buf, int len);

/**
 * Deserialize Zr element from bytes
 * @param elem Element to initialize and fill (output)
 * @param buf Buffer to read from
 * @param len Length of data
 * @return 0 on success, -1 on error
 */
int stealth_element_from_bytes_Zr(element_t elem, const unsigned char* buf, int len);

#endif /* STEALTH_CORE_H */