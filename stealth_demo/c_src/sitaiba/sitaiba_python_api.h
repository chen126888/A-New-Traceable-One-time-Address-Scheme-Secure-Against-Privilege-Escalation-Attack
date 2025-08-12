/****************************************************************************
 * File: python_api.h  
 * Desc: Python API interface for SITAIBA scheme
 *       Provides simplified functions for Python/Flask integration
 ****************************************************************************/

#ifndef SITAIBA_PYTHON_API_H
#define SITAIBA_PYTHON_API_H

//----------------------------------------------
// Python Simple API Functions
//----------------------------------------------

/**
 * Initialize SITAIBA with parameter file
 * @param param_file Path to parameter file
 * @return 0 on success, non-zero on failure
 */
int sitaiba_init_simple(const char* param_file);

/**
 * Check if library is initialized
 * @return 1 if initialized, 0 otherwise
 */
int sitaiba_is_initialized_simple(void);

/**
 * Cleanup library resources
 */
void sitaiba_cleanup_simple(void);

/**
 * Reset performance counters
 */
void sitaiba_reset_performance_simple(void);

/**
 * Get element sizes
 * @return Size of G1 elements in bytes
 */
int sitaiba_element_size_G1_simple(void);

/**
 * Get element sizes  
 * @return Size of Zr elements in bytes
 */
int sitaiba_element_size_Zr_simple(void);

/**
 * Generate user key pair - simplified for Python
 * @param A_buf Buffer for public key A (output)
 * @param B_buf Buffer for public key B (output) 
 * @param a_buf Buffer for private key a (output)
 * @param b_buf Buffer for private key b (output)
 * @param buf_size Size of each buffer
 */
void sitaiba_keygen_simple(unsigned char* A_buf, unsigned char* B_buf,
                          unsigned char* a_buf, unsigned char* b_buf, int buf_size);

/**
 * Generate tracer key pair - simplified for Python
 * @param A_m_buf Buffer for tracer public key (output)
 * @param a_m_buf Buffer for tracer private key (output)
 * @param buf_size Size of each buffer
 */
void sitaiba_tracer_keygen_simple(unsigned char* A_m_buf, unsigned char* a_m_buf, int buf_size);

/**
 * Generate stealth address - simplified for Python
 * @param A_r_buf User public key A (input)
 * @param B_r_buf User public key B (input)
 * @param A_m_buf Manager public key (input) - can be NULL to use internal
 * @param addr_buf Generated address (output)
 * @param r1_buf Random element R1 (output)
 * @param r2_buf Random element R2 (output) 
 * @param buf_size Size of each buffer
 */
void sitaiba_addr_gen_simple(unsigned char* A_r_buf, unsigned char* B_r_buf, unsigned char* A_m_buf,
                            unsigned char* addr_buf, unsigned char* r1_buf, unsigned char* r2_buf,
                            int buf_size);

/**
 * Verify stealth address - simplified for Python
 * @param addr_buf Address to verify
 * @param r1_buf Random element R1
 * @param r2_buf Random element R2
 * @param A_r_buf User public key A  
 * @param B_r_buf User public key B
 * @param a_r_buf User private key a
 * @param A_m_buf Manager public key - can be NULL to use internal
 * @return 1 if valid, 0 otherwise
 */
int sitaiba_addr_recognize_simple(unsigned char* addr_buf, unsigned char* r1_buf, unsigned char* r2_buf,
                                  unsigned char* A_r_buf, unsigned char* B_r_buf, unsigned char* a_r_buf,
                                  unsigned char* A_m_buf);

/**
 * Fast recognize stealth address - simplified for Python
 * @param r1_buf Random element R1
 * @param r2_buf Random element R2  
 * @param A_r_buf User public key A
 * @param a_r_buf User private key a
 * @return 1 if recognized, 0 otherwise
 */
int sitaiba_addr_recognize_fast_simple(unsigned char* r1_buf, unsigned char* r2_buf,
                                       unsigned char* A_r_buf, unsigned char* a_r_buf);

/**
 * Generate one-time secret key - simplified for Python
 * @param r1_buf Random element R1 (input)
 * @param a_r_buf User private key a (input)
 * @param b_r_buf User private key b (input)
 * @param A_m_buf Manager public key (input) - can be NULL to use internal
 * @param dsk_buf One-time secret key (output)
 * @param buf_size Size of each buffer
 */
void sitaiba_onetime_skgen_simple(unsigned char* r1_buf, unsigned char* a_r_buf, unsigned char* b_r_buf,
                                 unsigned char* A_m_buf, unsigned char* dsk_buf, int buf_size);

/**
 * Trace identity from address - simplified for Python
 * @param addr_buf Address to trace (input)
 * @param r1_buf Random element R1 (input)
 * @param r2_buf Random element R2 (input)
 * @param a_m_buf Manager private key (input) - can be NULL to use internal
 * @param B_r_buf Recovered user public key B (output)
 * @param buf_size Size of each buffer
 */
void sitaiba_trace_simple(unsigned char* addr_buf, unsigned char* r1_buf, unsigned char* r2_buf,
                         unsigned char* a_m_buf, unsigned char* B_r_buf, int buf_size);

/**
 * Run performance test - simplified for Python
 * @param iterations Number of iterations
 * @param results Array to store results [addr_gen, addr_recognize, fast_recognize, onetime_sk, trace]
 */
void sitaiba_performance_test_simple(int iterations, double* results);

/**
 * Get tracer public key - simplified for Python
 * @param A_m_buf Buffer for tracer public key (output)
 * @param buf_size Size of buffer
 * @return 0 on success, -1 on failure
 */
int sitaiba_get_tracer_public_key_simple(unsigned char* A_m_buf, int buf_size);

#endif /* SITAIBA_PYTHON_API_H */