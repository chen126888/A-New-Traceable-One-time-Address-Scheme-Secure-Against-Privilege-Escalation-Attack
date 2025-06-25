#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pbc/pbc.h>
#include <pbc/pbc_test.h>
#include <openssl/sha.h>
#include <time.h>

#define RUN_COUNT 100

pairing_t pairing;
element_t P; // generator in G1

double timer_diff(clock_t start, clock_t end) {
    return ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0;
}

static double sumDelegate = 0, sumVerifyKey = 0, sumCheck = 0, sumSignKey = 0, sumSign = 0, sumVerify = 0, sumH0 = 0, sumH1 = 0, sumH2 = 0, sumH3 = 0, sumH4 = 0;

void PrintAverageTimes() {
    printf("\n=== Average runtime over %d runs (ms) ===\n", RUN_COUNT);
    printf("WalletKeyDelegate:  %.3f ms\n", sumDelegate / RUN_COUNT);
    printf("VerifyKeyDerive:    %.3f ms\n", sumVerifyKey / RUN_COUNT);
    printf("VerifyKeyCheck:      %.3f ms\n", sumCheck / RUN_COUNT);
    printf("SignKeyDerive:      %.3f ms\n", sumSignKey / RUN_COUNT);
    printf("Sign:               %.3f ms\n", sumSign / RUN_COUNT);
    printf("Verify:             %.3f ms\n", sumVerify / RUN_COUNT);
    printf("H0:                 %.3f ms\n", sumH0 / RUN_COUNT);
    printf("H1:                 %.3f ms\n", sumH1 / (RUN_COUNT * 2));
    printf("H2:                 %.3f ms\n", sumH2 / RUN_COUNT);
    printf("H3:                 %.3f ms\n", sumH3 / (RUN_COUNT * 3));
    printf("H4:                 %.3f ms\n", sumH4 / (RUN_COUNT * 2));
}

void hash_to_mpz(mpz_t out, const unsigned char *data, size_t len, mpz_t mod) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(data, len, hash);
    mpz_import(out, SHA256_DIGEST_LENGTH, 1, 1, 0, 0, hash);
    mpz_mod(out, out, mod);
}

// H0: S_ID -> G1* (maps identity to G1)
void H0(element_t out, const char *id) {
    clock_t t1 = clock();
    mpz_t tmp;
    mpz_init(tmp);
    hash_to_mpz(tmp, (const unsigned char *)id, strlen(id), pairing->r);
    element_t zr;
    element_init_Zr(zr, pairing);
    element_set_mpz(zr, tmp);
    element_mul_zn(out, P, zr);
    element_clear(zr);
    mpz_clear(tmp);
    clock_t t2 = clock();
    sumH0 += timer_diff(t1, t2);
}

// H1: G1 × G1 -> Zp* (maps two G1 elements to Zp)
void H1(element_t out, element_t in1, element_t in2) {
    clock_t t1 = clock();
    unsigned char buf[2048];
    int len1 = element_length_in_bytes(in1);
    int len2 = element_length_in_bytes(in2);
    element_to_bytes(buf, in1);
    element_to_bytes(buf + len1, in2);
    
    mpz_t tmp;
    mpz_init(tmp);
    hash_to_mpz(tmp, buf, len1 + len2, pairing->r);
    element_set_mpz(out, tmp);
    mpz_clear(tmp);
    clock_t t2 = clock();
    sumH1 += timer_diff(t1, t2);
}

// H2: G1 × G1 -> Zp* (different from H1 by adding prefix)
void H2(element_t out, element_t in1, element_t in2) {
    clock_t t1 = clock();
    unsigned char buf[2048];
    // Add prefix to differentiate from H1
    buf[0] = 0x02; // H2 prefix
    int len1 = element_length_in_bytes(in1);
    int len2 = element_length_in_bytes(in2);
    element_to_bytes(buf + 1, in1);
    element_to_bytes(buf + 1 + len1, in2);
    
    mpz_t tmp;
    mpz_init(tmp);
    hash_to_mpz(tmp, buf, 1 + len1 + len2, pairing->r);
    element_set_mpz(out, tmp);
    mpz_clear(tmp);
    clock_t t2 = clock();
    sumH2 += timer_diff(t1, t2);
}

// H3: G1 × G1 × G1 -> G1* (maps three G1 elements to G1)
void H3(element_t out, element_t in1, element_t in2, element_t in3) {
    clock_t t1 = clock();
    unsigned char buf[3072];
    buf[0] = 0x03; // H3 prefix
    int len1 = element_length_in_bytes(in1);
    int len2 = element_length_in_bytes(in2);
    int len3 = element_length_in_bytes(in3);
    element_to_bytes(buf + 1, in1);
    element_to_bytes(buf + 1 + len1, in2);
    element_to_bytes(buf + 1 + len1 + len2, in3);
    
    mpz_t tmp;
    mpz_init(tmp);
    hash_to_mpz(tmp, buf, 1 + len1 + len2 + len3, pairing->r);
    element_t z;
    element_init_Zr(z, pairing);
    element_set_mpz(z, tmp);
    element_mul_zn(out, P, z);
    element_clear(z);
    mpz_clear(tmp);
    clock_t t2 = clock();
    sumH3 += timer_diff(t1, t2);
}

// H4: (G1 × G2) × M × G2 -> Zp* (for signature)
void H4(element_t out, element_t dvk_qr, element_t dvk_qvk, const char *msg) {
    clock_t t1 = clock();
    unsigned char buf[4096];
    buf[0] = 0x04; // H4 prefix
    int len1 = element_length_in_bytes(dvk_qr);
    int len2 = element_length_in_bytes(dvk_qvk);
    int lenm = strlen(msg);
    
    element_to_bytes(buf + 1, dvk_qr);
    element_to_bytes(buf + 1 + len1, dvk_qvk);
    memcpy(buf + 1 + len1 + len2, msg, lenm);
    
    mpz_t tmp;
    mpz_init(tmp);
    hash_to_mpz(tmp, buf, 1 + len1 + len2 + lenm, pairing->r);
    element_set_mpz(out, tmp);
    mpz_clear(tmp);
    clock_t t2 = clock();
    sumH4 += timer_diff(t1, t2);
}

void Setup(const char* param_file) {
    char *fake_argv[2];
    fake_argv[0] = "prog";
    fake_argv[1] = (char*)param_file;
    pbc_demo_pairing_init(pairing, 2, fake_argv);

    element_init_G1(P, pairing);
    element_random(P);
}

void RootWalletKeyGen(element_t A, element_t B, element_t alpha, element_t beta) {
    element_random(alpha);
    element_random(beta);
    element_mul_zn(A, P, alpha);
    element_mul_zn(B, P, beta);
}

void WalletKeyDelegate(
    element_t A2, 
    element_t B2, 
    element_t alpha2, 
    element_t beta2,
    element_t alpha1, 
    element_t beta1, 
    const char *id
) {
    clock_t t1 = clock();
    element_t QID, temp;
    element_init_G1(QID, pairing);
    element_init_G1(temp, pairing);
    clock_t t2 = clock();
    
    // Step 1: Compute Q_ID = H0(ID)
    H0(QID, id);
    
    clock_t t3 = clock();
    // Step 2: Compute α_ID = H1(Q_ID, α_{ID_(t-1)} * Q_ID)
    element_mul_zn(temp, QID, alpha1);
    clock_t t4 = clock();
    H1(alpha2, QID, temp);
    clock_t t5 = clock();
    
    // Step 3: Compute β_ID = H2(Q_ID, β_{ID_(t-1)} * Q_ID)
    element_mul_zn(temp, QID, beta1);
    clock_t t6 = clock();
    H2(beta2, QID, temp);
    clock_t t7 = clock();
    
    // Step 4: Compute public key components
    element_mul_zn(A2, P, alpha2);
    element_mul_zn(B2, P, beta2);
    
    element_clear(QID);
    element_clear(temp);
    clock_t t8 = clock();
    
    // Only count non-hash operations
    sumDelegate += timer_diff(t1, t2) + timer_diff(t3, t4) + timer_diff(t5, t6) + timer_diff(t7, t8);
}

void VerifyKeyDerive(
    element_t Qr, 
    element_t Qvk, 
    element_t A, 
    element_t B
) {
    clock_t t1 = clock();
    element_t r, rP, betaRp, h3, negA;
    element_init_Zr(r, pairing);
    element_init_G1(rP, pairing);
    element_init_G1(betaRp, pairing);
    element_init_G1(h3, pairing);
    element_init_G1(negA, pairing);
    
    // Step 1: Choose random r
    element_random(r);
    
    // Step 2: Compute Qr = r*P
    element_mul_zn(Qr, P, r);
    
    // For H3 computation, we need β_ID * r * P
    // Since we don't have β_ID directly, we compute r * B_ID (which equals β_ID * r * P)
    element_mul_zn(betaRp, B, r);
    clock_t t2 = clock();
    
    // Step 3: Compute H3(B_ID, Qr, β_ID * r * P)
    H3(h3, B, Qr, betaRp);
    
    clock_t t3 = clock();
    // Step 4: Compute Qvk = ê(H3(...), -A_ID)
    element_neg(negA, A);
    pairing_apply(Qvk, h3, negA, pairing);
    
    element_clear(r);
    element_clear(rP);
    element_clear(betaRp);
    element_clear(h3);
    element_clear(negA);
    clock_t t4 = clock();
    
    // Only count non-hash operations
    sumVerifyKey += timer_diff(t1, t2) + timer_diff(t3, t4);
}

int VerifyKeyCheck(
    element_t Qvk, 
    element_t Qr, 
    element_t A, 
    element_t B, 
    element_t beta
){
    clock_t t1 = clock();
    element_t betaQr, h3, echeck, negA;
    element_init_G1(betaQr, pairing);
    element_init_G1(h3, pairing);
    element_init_GT(echeck, pairing);
    element_init_G1(negA, pairing);
    
    // Compute β_ID * Qr
    element_mul_zn(betaQr, Qr, beta);
    clock_t t2 = clock();
    
    // Compute H3(B_ID, Qr, β_ID * Qr)
    H3(h3, B, Qr, betaQr);
    
    clock_t t3 = clock();
    // Compute ê(H3(...), -A_ID)
    element_neg(negA, A);
    pairing_apply(echeck, h3, negA, pairing);
    
    // Check if Qvk = ê(H3(...), -A_ID)
    int valid = (element_cmp(echeck, Qvk) == 0);
    
    element_clear(betaQr);
    element_clear(h3);
    element_clear(echeck);
    element_clear(negA);
    clock_t t4 = clock();
    
    // Only count non-hash operations
    sumCheck += timer_diff(t1, t2) + timer_diff(t3, t4);
    return valid;
}

void SignKeyDerive(
    element_t dsk,  
    element_t Qr, 
    element_t B, 
    element_t alpha, 
    element_t beta
) {
    clock_t t1 = clock();
    element_t betaQr, h3;
    element_init_G1(betaQr, pairing);
    element_init_G1(h3, pairing);
    
    // Compute β_ID * Qr
    element_mul_zn(betaQr, Qr, beta);
    clock_t t2 = clock();
    
    // Compute H3(B_ID, Qr, β_ID * Qr)
    H3(h3, B, Qr, betaQr);
    
    clock_t t3 = clock();
    // Compute dsk = α_ID * H3(...)
    element_mul_zn(dsk, h3, alpha);
    
    element_clear(betaQr);
    element_clear(h3);
    clock_t t4 = clock();
    
    // Only count non-hash operations
    sumSignKey += timer_diff(t1, t2) + timer_diff(t3, t4);
}

void Sign(
    element_t h,
    element_t Q_sigma, 
    element_t dsk, 
    element_t Qr, 
    element_t Qvk, 
    const char *msg
) {
    clock_t t1 = clock();
    element_t x, xP, eXP;
    element_init_Zr(x, pairing);
    element_init_G1(xP, pairing);
    element_init_GT(eXP, pairing);
    
    // Step 1: Choose random x
    element_random(x);
    
    // Step 2: Compute X = x*P
    element_mul_zn(xP, P, x);
    
    // Step 3: Compute ê(X, P) = ê(x*P, P)
    pairing_apply(eXP, xP, P, pairing);
    clock_t t2 = clock();
    
    // Step 4: Compute h = H4(dvk, m, ê(x*P, P))
    // Note: dvk = (Qr, Qvk), so we need to hash both components
    H4(h, Qr, Qvk, msg);
    
    clock_t t3 = clock();
    // Step 5: Compute Q_σ = h * dsk + x*P
    element_t hdsk;
    element_init_G1(hdsk, pairing);
    element_mul_zn(hdsk, dsk, h);
    element_add(Q_sigma, hdsk, xP);
    
    element_clear(x);
    element_clear(xP);
    element_clear(eXP);
    element_clear(hdsk);
    clock_t t4 = clock();
    
    // Only count non-hash operations
    sumSign += timer_diff(t1, t2) + timer_diff(t3, t4);
}

int Verify(
    element_t h, 
    element_t Q_sigma, 
    element_t Qr, 
    element_t Qvk, 
    const char *msg) {
    clock_t t1 = clock();
    element_t e1, e2, prod, hcheck;
    element_init_GT(e1, pairing);
    element_init_GT(e2, pairing);
    element_init_GT(prod, pairing);
    element_init_Zr(hcheck, pairing);
    
    // Step 1: Compute ê(Q_σ, P)
    pairing_apply(e1, Q_sigma, P, pairing);
    
    // Step 2: Compute (Q_vk)^h
    element_pow_zn(e2, Qvk, h);
    
    // Step 3: Compute ê(Q_σ, P) * (Q_vk)^h
    element_mul(prod, e1, e2);
    clock_t t2 = clock();
    
    // Step 4: Compute h' = H4(dvk, m, ê(Q_σ, P) * (Q_vk)^h)
    H4(hcheck, Qr, Qvk, msg);
    
    clock_t t3 = clock();
    // Step 5: Check if h = h'
    int valid = (element_cmp(h, hcheck) == 0);
    
    element_clear(e1);
    element_clear(e2);
    element_clear(prod);
    element_clear(hcheck);
    clock_t t4 = clock();
    
    // Only count non-hash operations
    sumVerify += timer_diff(t1, t2) + timer_diff(t3, t4);
    return valid;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <param_file>\n", argv[0]);
        return 1;
    }
    
    // 1) Setup once
    Setup(argv[1]);
    
    // 2) KeyGen once
    element_t A, B, alpha, beta;
    element_init_G1(A, pairing); 
    element_init_G1(B, pairing);
    element_init_Zr(alpha, pairing); 
    element_init_Zr(beta, pairing);
       
    RootWalletKeyGen(A, B, alpha, beta); 

    const char *msg = "hello world";
    
    for (int i = 0; i < RUN_COUNT; i++) {
        element_t A2, B2, alpha2, beta2, Qr, Qvk, dsk, h, Q_sigma;
        element_init_G1(A2, pairing);
        element_init_G1(B2, pairing);
        element_init_Zr(alpha2, pairing);
        element_init_Zr(beta2, pairing);
        element_init_G1(Qr, pairing);
        element_init_GT(Qvk, pairing);
        element_init_G1(dsk, pairing);
        element_init_Zr(h, pairing);
        element_init_G1(Q_sigma, pairing);

        char id_buf[64];
        sprintf(id_buf, "user_%d", i);

        // Execute the protocol
        WalletKeyDelegate(A2, B2, alpha2, beta2, alpha, beta, id_buf);
        VerifyKeyDerive(Qr, Qvk, A2, B2);

        int valid = VerifyKeyCheck(Qvk, Qr, A2, B2, beta2);
        if (!valid) {
            printf("[!] KeyCheck failed on run %d\n", i);
            continue;
        }

        SignKeyDerive(dsk, Qr, B2, alpha2, beta2);
        Sign(h, Q_sigma, dsk, Qr, Qvk, msg);
        int verify = Verify(h, Q_sigma, Qr, Qvk, msg);

        if (!verify) {
            printf("[!] Signature verification failed on run %d\n", i);
        }

        element_clear(A2);
        element_clear(B2);
        element_clear(alpha2);
        element_clear(beta2);
        element_clear(Qr);
        element_clear(Qvk);
        element_clear(dsk);
        element_clear(h);
        element_clear(Q_sigma);
    }

    PrintAverageTimes();

    element_clear(A);
    element_clear(B);
    element_clear(alpha);
    element_clear(beta);
    element_clear(P);
    pairing_clear(pairing);

    return 0;
}