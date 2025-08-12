/****************************************************************************
 * File: sitaiba_core.h
 * Desc: Core cryptographic functions for SITAIBA Scheme
 *       (SIgnature-based TrAceable anonymIty using BilineAr mapping)
 ****************************************************************************/

#ifndef SITAIBA_CORE_H
#define SITAIBA_CORE_H

#include <pbc/pbc.h>

//----------------------------------------------
// Performance Statistics Structure
//----------------------------------------------
typedef struct {
    double addr_gen_avg;
    double addr_recognize_avg;
    double fast_recognize_avg;
    double onetime_sk_avg;
    double trace_avg;
    int operation_count;
} sitaiba_performance_t;

//----------------------------------------------
// Library Management Functions
//----------------------------------------------

/**
 * Initialize the SITAIBA library with a parameter file
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
 * Generate a key pair (A, B, a, b) for user
 * @param A Public key A (output)
 * @param B Public key B (output)
 * @param aZ Private key a (output)
 * @param bZ Private key b (output)
 */
void sitaiba_keygen(element_t A, element_t B, element_t aZ, element_t bZ);

/**
 * Generate tracer key pair (A_m, a_m) - called during init
 * @param A_m Tracer public key (output)
 * @param a_m Tracer private key (output)
 */
void sitaiba_tracer_keygen(element_t A_m, element_t a_m);

/**
 * Generate one-time address
 * @param Addr Generated address (output)
 * @param R1 Random element R1 (output)
 * @param R2 Random element R2 (output)
 * @param A_r User public key A
 * @param B_r User public key B
 * @param A_m Manager public key
 */
void sitaiba_addr_gen(element_t Addr, element_t R1, element_t R2,
                     element_t A_r, element_t B_r, element_t A_m);

/**
 * Recognize address (full version)
 * @param Addr Address to recognize
 * @param R1 Random element R1
 * @param R2 Random element R2
 * @param A_r User public key A
 * @param B_r User public key B
 * @param A_m Manager public key
 * @param a_r User private key a
 * @return 1 if recognized, 0 otherwise
 */
int sitaiba_addr_recognize(element_t Addr, element_t R1, element_t R2,
                          element_t A_r, element_t B_r, element_t A_m, element_t a_r);

/**
 * Fast address recognition (optimized)
 * @param R1 Random element R1
 * @param R2 Random element R2
 * @param A_r User public key A
 * @param a_r User private key a
 * @return 1 if recognized, 0 otherwise
 */
int sitaiba_addr_recognize_fast(element_t R1, element_t R2, element_t A_r, element_t a_r);

/**
 * Generate one-time secret key
 * @param dsk One-time secret key (output)
 * @param R1 Random element R1
 * @param a_r User private key a
 * @param b_r User private key b
 * @param A_m Manager public key
 */
void sitaiba_onetime_skgen(element_t dsk, element_t R1, element_t a_r, 
                          element_t b_r, element_t A_m);

/**
 * Trace identity from address
 * @param B_r Recovered user public key B (output)
 * @param Addr Address to trace
 * @param R1 Random element R1
 * @param R2 Random element R2
 * @param a_m Manager private key
 */
void sitaiba_trace(element_t B_r, element_t Addr, element_t R1, 
                  element_t R2, element_t a_m);

//----------------------------------------------
// Hash Functions (SITAIBA specific)
//----------------------------------------------

/**
 * Hash function H1: G1 -> Zr
 * @param outZr Output element in Zr (output)
 * @param inG1 Input element in G1
 */
void sitaiba_H1(element_t outZr, element_t inG1);

/**
 * Hash function H2: GT -> Zr
 * @param outZr Output element in Zr (output)
 * @param inGT Input element in GT
 */
void sitaiba_H2(element_t outZr, element_t inGT);

//----------------------------------------------
// Performance and Utility Functions
//----------------------------------------------

/**
 * Get performance statistics
 * @param perf Performance structure to fill (output)
 */
void sitaiba_get_performance(sitaiba_performance_t* perf);

//----------------------------------------------
// External variables for performance testing
//----------------------------------------------
extern int perf_counter;

/**
 * Print performance statistics to stdout
 */
void sitaiba_print_performance(void);

//----------------------------------------------
// Element Serialization Helpers
//----------------------------------------------

/**
 * Get the size needed for serializing a G1 element
 * @return Size in bytes, 0 if not initialized
 */
int sitaiba_element_size_G1(void);

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
 * Deserialize Zr element from bytes
 * @param elem Element to initialize and fill (output)
 * @param buf Buffer to read from
 * @param len Length of data
 * @return 0 on success, -1 on error
 */
int sitaiba_element_from_bytes_Zr(element_t elem, const unsigned char* buf, int len);

//----------------------------------------------
// Manager Key Access (for tracing)
//----------------------------------------------

/**
 * Get tracer public key (for external use)
 * @param A_m Tracer public key (output)
 * @return 0 on success, -1 if not initialized
 */
int sitaiba_get_tracer_public_key(element_t A_m);

/**
 * Get generator g (for external use)
 * @param g_out Generator g (output)
 * @return 0 on success, -1 if not initialized
 */
int sitaiba_get_generator(element_t g_out);

#endif /* SITAIBA_CORE_H */