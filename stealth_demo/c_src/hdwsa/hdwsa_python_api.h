/****************************************************************************
 * File: hdwsa_python_api.h  
 * Desc: Python API interface for HDWSA scheme
 *       Provides simplified functions for Python/Flask integration
 ****************************************************************************/

#ifndef HDWSA_PYTHON_API_H
#define HDWSA_PYTHON_API_H

//----------------------------------------------
// Python Simple API Functions
//----------------------------------------------

/**
 * Initialize HDWSA with parameter file
 * @param param_file Path to parameter file
 * @return 0 on success, non-zero on failure
 */
int hdwsa_init_simple(const char* param_file);

/**
 * Check if library is initialized
 * @return 1 if initialized, 0 otherwise
 */
int hdwsa_is_initialized_simple(void);

/**
 * Cleanup library resources
 */
void hdwsa_cleanup_simple(void);

/**
 * Reset performance counters
 */
void hdwsa_reset_performance_simple(void);

/**
 * Get element sizes
 * @return Size of G1 elements in bytes
 */
int hdwsa_element_size_G1_simple(void);

/**
 * Get element sizes  
 * @return Size of Zr elements in bytes
 */
int hdwsa_element_size_Zr_simple(void);

/**
 * Get GT element size
 * @return Size of GT elements in bytes
 */
int hdwsa_element_size_GT_simple(void);

//----------------------------------------------
// Root System Functions
//----------------------------------------------

/**
 * Generate root wallet keypair (system setup)
 * @param A_out Buffer for root public key A (G1)
 * @param B_out Buffer for root public key B (G1)
 * @param alpha_out Buffer for root private key alpha (Zr)
 * @param beta_out Buffer for root private key beta (Zr)
 * @return 0 on success, non-zero on failure
 */
int hdwsa_root_keygen_simple(unsigned char* A_out, unsigned char* B_out,
                            unsigned char* alpha_out, unsigned char* beta_out);

//----------------------------------------------
// Key Management Functions
//----------------------------------------------

/**
 * Generate user keypair through hierarchical key derivation
 * @param A2_out Buffer for user public key A2 (G1)
 * @param B2_out Buffer for user public key B2 (G1)
 * @param alpha2_out Buffer for user private key alpha2 (Zr)
 * @param beta2_out Buffer for user private key beta2 (Zr)
 * @param alpha1_in Parent private key alpha1 (Zr)
 * @param beta1_in Parent private key beta1 (Zr)
 * @param full_id Full hierarchical ID string (e.g., "id_0,id_1,id_2")
 * @return 0 on success, non-zero on failure
 */
int hdwsa_keypair_gen_simple(unsigned char* A2_out, unsigned char* B2_out,
                            unsigned char* alpha2_out, unsigned char* beta2_out,
                            const unsigned char* alpha1_in, const unsigned char* beta1_in,
                            const char* full_id);

//----------------------------------------------
// Address Functions
//----------------------------------------------

/**
 * Generate address (derived verification key)
 * @param Qr_out Buffer for address component Qr (G1)
 * @param Qvk_out Buffer for address component Qvk (GT)
 * @param A_in Public key A (G1)
 * @param B_in Public key B (G1)
 * @return 0 on success, non-zero on failure
 */
int hdwsa_addr_gen_simple(unsigned char* Qr_out, unsigned char* Qvk_out,
                         const unsigned char* A_in, const unsigned char* B_in);

/**
 * Recognize/verify address ownership
 * @param Qvk_in Address component Qvk to check (GT)
 * @param Qr_in Address component Qr (G1)
 * @param A_in Public key A (G1)
 * @param B_in Public key B (G1)
 * @param beta_in Private key beta (Zr)
 * @return 1 if address is valid, 0 otherwise
 */
int hdwsa_addr_recognize_simple(const unsigned char* Qvk_in, const unsigned char* Qr_in,
                               const unsigned char* A_in, const unsigned char* B_in,
                               const unsigned char* beta_in);

//----------------------------------------------
// DSK Functions
//----------------------------------------------

/**
 * Generate derived signing key (DSK)
 * @param dsk_out Buffer for derived signing key (G1)
 * @param Qr_in Address component Qr (G1)
 * @param B_in Public key B (G1)
 * @param alpha_in Private key alpha (Zr)
 * @param beta_in Private key beta (Zr)
 * @return 0 on success, non-zero on failure
 */
int hdwsa_dsk_gen_simple(unsigned char* dsk_out,
                        const unsigned char* Qr_in, const unsigned char* B_in,
                        const unsigned char* alpha_in, const unsigned char* beta_in);

//----------------------------------------------
// Signature Functions
//----------------------------------------------

/**
 * Sign a message using DSK
 * @param h_out Buffer for signature component h (Zr)
 * @param Q_sigma_out Buffer for signature component Q_sigma (G1)
 * @param dsk_in Derived signing key (G1)
 * @param Qr_in Address component Qr (G1)
 * @param Qvk_in Address component Qvk (GT)
 * @param msg Message to sign
 * @return 0 on success, non-zero on failure
 */
int hdwsa_sign_simple(unsigned char* h_out, unsigned char* Q_sigma_out,
                     const unsigned char* dsk_in,
                     const unsigned char* Qr_in, const unsigned char* Qvk_in,
                     const char* msg);

/**
 * Verify a signature
 * @param h_in Signature component h (Zr)
 * @param Q_sigma_in Signature component Q_sigma (G1)
 * @param Qr_in Address component Qr (G1)
 * @param Qvk_in Address component Qvk (GT)
 * @param msg Original message
 * @return 1 if signature is valid, 0 otherwise
 */
int hdwsa_verify_simple(const unsigned char* h_in, const unsigned char* Q_sigma_in,
                       const unsigned char* Qr_in, const unsigned char* Qvk_in,
                       const char* msg);

//----------------------------------------------
// Performance Testing
//----------------------------------------------

/**
 * Run performance test
 * @param iterations Number of iterations to run
 * @return Number of successful iterations
 */
int hdwsa_performance_test_simple(int iterations);

/**
 * Print performance statistics
 */
void hdwsa_print_performance_simple(void);

/**
 * Get performance statistics as string
 * @param output Buffer to store performance string
 * @param buffer_size Size of output buffer
 * @return 0 on success, non-zero on failure
 */
int hdwsa_get_performance_string_simple(char* output, int buffer_size);

#endif /* HDWSA_PYTHON_API_H */