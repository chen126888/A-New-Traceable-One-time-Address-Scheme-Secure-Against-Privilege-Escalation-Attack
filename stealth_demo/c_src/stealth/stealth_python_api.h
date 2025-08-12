/****************************************************************************
 * File: python_api.h
 * Desc: Python interface functions for Traceable Anonymous Transaction Scheme
 *       Simple byte-based wrappers around core cryptographic functions
 ****************************************************************************/

#ifndef PYTHON_API_H
#define PYTHON_API_H

//----------------------------------------------
// Python Interface Functions
// These functions use byte arrays instead of PBC element_t types
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
void stealth_keygen_simple(unsigned char* A_out, unsigned char* B_out, 
                          unsigned char* a_out, unsigned char* b_out, int buf_size);

/**
 * Python Interface: Generate trace key
 * @param TK_out Buffer for trace public key (output)
 * @param k_out Buffer for trace private key (output)
 * @param buf_size Size of each buffer
 */
void stealth_tracekeygen_simple(unsigned char* TK_out, unsigned char* k_out, int buf_size);

/**
 * Python Interface: Generate address
 * @param A_bytes Input public key A as bytes
 * @param B_bytes Input public key B as bytes
 * @param TK_bytes Input trace public key as bytes
 * @param addr_out Buffer for generated address (output)
 * @param r1_out Buffer for R1 component (output)
 * @param r2_out Buffer for R2 component (output)
 * @param c_out Buffer for C component (output)
 * @param buf_size Size of output buffers
 */
void stealth_addr_gen_simple(const unsigned char* A_bytes, const unsigned char* B_bytes,
                            const unsigned char* TK_bytes,
                            unsigned char* addr_out, unsigned char* r1_out,
                            unsigned char* r2_out, unsigned char* c_out, int buf_size);

/**
 * Python Interface: Recognize address (fast version)
 * @param R1_bytes R1 component as bytes
 * @param B_bytes Public key B as bytes
 * @param A_bytes Public key A as bytes
 * @param C_bytes C component as bytes
 * @param a_bytes Private key a as bytes
 * @return 1 if recognized, 0 otherwise
 */
int stealth_addr_recognize_fast_simple(const unsigned char* R1_bytes, const unsigned char* B_bytes,
                                      const unsigned char* A_bytes, const unsigned char* C_bytes,
                                      const unsigned char* a_bytes);

/**
 * Python Interface: Recognize address (full version)
 * @param addr_bytes Address as bytes
 * @param R1_bytes R1 component as bytes
 * @param B_bytes Public key B as bytes
 * @param A_bytes Public key A as bytes
 * @param C_bytes C component as bytes
 * @param a_bytes Private key a as bytes
 * @param TK_bytes Trace public key as bytes
 * @return 1 if recognized, 0 otherwise
 */
int stealth_addr_recognize_simple(const unsigned char* addr_bytes, const unsigned char* R1_bytes,
                                 const unsigned char* B_bytes, const unsigned char* A_bytes,
                                 const unsigned char* C_bytes, const unsigned char* a_bytes,
                                 const unsigned char* TK_bytes);

/**
 * Python Interface: Generate one-time secret key (DSK)
 * @param addr_bytes Address as bytes
 * @param r1_bytes R1 component as bytes
 * @param a_bytes Private key a as bytes
 * @param b_bytes Private key b as bytes
 * @param dsk_out Buffer for one-time secret key (output)
 * @param buf_size Size of output buffer
 */
void stealth_dsk_gen_simple(const unsigned char* addr_bytes, const unsigned char* r1_bytes,
                           const unsigned char* a_bytes, const unsigned char* b_bytes,
                           unsigned char* dsk_out, int buf_size);

/**
 * Python Interface: Sign message
 * @param addr_bytes Address as bytes
 * @param dsk_bytes One-time secret key as bytes
 * @param message Message to sign (null-terminated string)
 * @param q_sigma_out Buffer for signature component Q (output)
 * @param h_out Buffer for hash component H (output)
 * @param buf_size Size of output buffers
 */
void stealth_sign_with_dsk_simple(const unsigned char* addr_bytes, const unsigned char* dsk_bytes,
                                 const char* message,
                                 unsigned char* q_sigma_out, unsigned char* h_out, int buf_size);

/**
 * Python Interface: Sign message (original version for compatibility)
 * @param addr_bytes Address as bytes
 * @param r1_bytes R1 component as bytes
 * @param a_bytes Private key a as bytes
 * @param b_bytes Private key b as bytes
 * @param message Message to sign (null-terminated string)
 * @param q_sigma_out Buffer for signature component Q (output)
 * @param h_out Buffer for hash component H (output)
 * @param dsk_out Buffer for one-time secret key (output)
 * @param buf_size Size of output buffers
 */
void stealth_sign_simple(const unsigned char* addr_bytes, const unsigned char* r1_bytes,
                        const unsigned char* a_bytes, const unsigned char* b_bytes,
                        const char* message,
                        unsigned char* q_sigma_out, unsigned char* h_out, 
                        unsigned char* dsk_out, int buf_size);

/**
 * Python Interface: Verify signature
 * @param addr_bytes Address as bytes
 * @param r2_bytes R2 component as bytes
 * @param c_bytes C component as bytes
 * @param message Message that was signed (null-terminated string)
 * @param h_bytes Hash component H as bytes
 * @param q_sigma_bytes Signature component Q as bytes
 * @return 1 if valid, 0 otherwise
 */
int stealth_verify_simple(const unsigned char* addr_bytes, const unsigned char* r2_bytes,
                         const unsigned char* c_bytes, const char* message,
                         const unsigned char* h_bytes, const unsigned char* q_sigma_bytes);

/**
 * Python Interface: Trace identity
 * @param addr_bytes Address as bytes
 * @param r1_bytes R1 component as bytes
 * @param r2_bytes R2 component as bytes
 * @param c_bytes C component as bytes
 * @param k_bytes Trace private key as bytes
 * @param b_recovered_out Buffer for recovered public key B (output)
 * @param buf_size Size of output buffer
 */
void stealth_trace_simple(const unsigned char* addr_bytes, const unsigned char* r1_bytes,
                         const unsigned char* r2_bytes, const unsigned char* c_bytes,
                         const unsigned char* k_bytes,
                         unsigned char* b_recovered_out, int buf_size);

/**
 * Python Interface: Performance test
 * @param iterations Number of test iterations
 * @param results Array to store performance results [7 doubles]
 *                results[0] = addr_gen_avg
 *                results[1] = addr_recognize_avg
 *                results[2] = fast_recognize_avg
 *                results[3] = onetime_sk_avg
 *                results[4] = sign_avg
 *                results[5] = verify_avg
 *                results[6] = trace_avg
 */
void stealth_performance_test_simple(int iterations, double* results);

#endif /* PYTHON_API_H */