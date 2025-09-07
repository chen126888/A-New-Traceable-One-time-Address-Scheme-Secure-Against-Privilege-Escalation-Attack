/****************************************************************************
 * File: hdwsa_core.h
 * Desc: Core cryptographic functions for HDWSA Scheme
 *       (Hierarchical Deterministic Wallet Signature Algorithm)
 ****************************************************************************/

#ifndef HDWSA_CORE_H
#define HDWSA_CORE_H

#include <pbc/pbc.h>

//----------------------------------------------
// Performance Statistics Structure
//----------------------------------------------
typedef struct {
    double root_keygen_avg;
    double keypair_gen_avg;
    double addr_gen_avg;
    double addr_recognize_avg;
    double dsk_gen_avg;
    double sign_avg;
    double verify_avg;
    double h0_avg;
    double h1_avg;
    double h2_avg;
    double h3_avg;
    double h4_avg;
    int operation_count;
} hdwsa_performance_t;

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
 * Get performance statistics
 * @return Pointer to performance structure
 */
hdwsa_performance_t* hdwsa_get_performance(void);

/**
 * Get element sizes for G1 and Zr
 * @param g1_size Pointer to store G1 element size
 * @param zr_size Pointer to store Zr element size
 */
void hdwsa_get_element_sizes(size_t* g1_size, size_t* zr_size);

//----------------------------------------------
// Hash Functions
//----------------------------------------------

/**
 * H0: Hierarchical ID to G1 mapping
 * @param out Output element in G1
 * @param full_id Full hierarchical ID string (e.g., "id_0,id_1,id_2")
 */
void hdwsa_H0(unsigned char* out, const char* full_id);

/**
 * H1: G1 × G1 -> Zp mapping
 * @param out Output element in Zr
 * @param in1 First input element
 * @param in2 Second input element
 */
void hdwsa_H1(unsigned char* out, const unsigned char* in1, const unsigned char* in2);

/**
 * H2: G1 × G1 -> Zp mapping (different from H1)
 * @param out Output element in Zr
 * @param in1 First input element
 * @param in2 Second input element
 */
void hdwsa_H2(unsigned char* out, const unsigned char* in1, const unsigned char* in2);

/**
 * H3: G1 × G1 × G1 -> G1 mapping
 * @param out Output element in G1
 * @param in1 First input element
 * @param in2 Second input element
 * @param in3 Third input element
 */
void hdwsa_H3(unsigned char* out, const unsigned char* in1, const unsigned char* in2, const unsigned char* in3);

/**
 * H4: Signature hash function
 * @param out Output element in Zr
 * @param dvk_qr Derived verification key Qr component
 * @param dvk_qvk Derived verification key Qvk component  
 * @param msg Message to sign
 */
void hdwsa_H4(unsigned char* out, const unsigned char* dvk_qr, const unsigned char* dvk_qvk, const char* msg);

//----------------------------------------------
// System Setup Functions
//----------------------------------------------

/**
 * Generate root wallet keypair (system-level, done once)
 * @param A_out Root public key A (G1)
 * @param B_out Root public key B (G1) 
 * @param alpha_out Root private key alpha (Zr)
 * @param beta_out Root private key beta (Zr)
 * @return 0 on success, -1 on failure
 */
int hdwsa_root_keygen(unsigned char* A_out, unsigned char* B_out, 
                      unsigned char* alpha_out, unsigned char* beta_out);

//----------------------------------------------
// Key Management Functions
//----------------------------------------------

/**
 * Generate user keypair through wallet key delegation
 * @param A2_out User public key A2 (G1)
 * @param B2_out User public key B2 (G1)
 * @param alpha2_out User private key alpha2 (Zr)
 * @param beta2_out User private key beta2 (Zr)
 * @param alpha1_in Parent private key alpha1 (Zr)
 * @param beta1_in Parent private key beta1 (Zr)
 * @param full_id Full hierarchical ID string (e.g., "id_0,id_1,id_2")
 * @return 0 on success, -1 on failure
 */
int hdwsa_keypair_gen(unsigned char* A2_out, unsigned char* B2_out,
                      unsigned char* alpha2_out, unsigned char* beta2_out,
                      const unsigned char* alpha1_in, const unsigned char* beta1_in,
                      const char* full_id);

//----------------------------------------------
// Address Functions
//----------------------------------------------

/**
 * Generate address (derived verification key)
 * @param Qr_out Address component Qr (G1)
 * @param Qvk_out Address component Qvk (GT)
 * @param A_in Public key A (G1)
 * @param B_in Public key B (G1)
 * @return 0 on success, -1 on failure
 */
int hdwsa_addr_gen(unsigned char* Qr_out, unsigned char* Qvk_out,
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
int hdwsa_addr_recognize(const unsigned char* Qvk_in, const unsigned char* Qr_in,
                         const unsigned char* A_in, const unsigned char* B_in,
                         const unsigned char* beta_in);

//----------------------------------------------
// DSK Functions
//----------------------------------------------

/**
 * Generate derived signing key (DSK)
 * @param dsk_out Derived signing key (G1)
 * @param Qr_in Address component Qr (G1)
 * @param B_in Public key B (G1)
 * @param alpha_in Private key alpha (Zr)
 * @param beta_in Private key beta (Zr)
 * @return 0 on success, -1 on failure
 */
int hdwsa_dsk_gen(unsigned char* dsk_out,
                  const unsigned char* Qr_in, const unsigned char* B_in,
                  const unsigned char* alpha_in, const unsigned char* beta_in);

//----------------------------------------------
// Signature Functions
//----------------------------------------------

/**
 * Sign a message using DSK
 * @param h_out Signature component h (Zr)
 * @param Q_sigma_out Signature component Q_sigma (G1)
 * @param dsk_in Derived signing key (G1)
 * @param Qr_in Address component Qr (G1)
 * @param Qvk_in Address component Qvk (GT)
 * @param msg Message to sign
 * @return 0 on success, -1 on failure
 */
int hdwsa_sign(unsigned char* h_out, unsigned char* Q_sigma_out,
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
int hdwsa_verify(const unsigned char* h_in, const unsigned char* Q_sigma_in,
                 const unsigned char* Qr_in, const unsigned char* Qvk_in,
                 const char* msg);

//----------------------------------------------
// Performance Testing
//----------------------------------------------

/**
 * Run performance test
 * @param iterations Number of iterations to run
 * @return 0 on success, -1 on failure
 */
int hdwsa_performance_test(int iterations);

/**
 * Print performance statistics
 */
void hdwsa_print_performance(void);

#endif /* HDWSA_CORE_H */