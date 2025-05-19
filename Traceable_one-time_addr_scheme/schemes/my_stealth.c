/****************************************************************************
 * File: traceable_transaction.c
 * Desc: Traceable Anonymous Transaction Scheme using PBC + SHA256,
 *       now measuring OnetimeAddrGen / AddressVerify / OnetimeSKGen /
 *       Sign / Verify / IdentityTracing over 100 runs in ms.
 ****************************************************************************/

 #include <stdio.h>
 #include <stdlib.h>
 #include <string.h>
 #include <pbc/pbc.h>
 #include <pbc/pbc_test.h>
 #include <openssl/sha.h>
 #include <time.h>
 
 // Global variable
 pairing_t pairing;
 element_t g;
 
 // We only record times for these 6 functions:
    static double sumAddrGen=0, sumAddrVerify=0, sumFastAddrVerify=0, sumOnetimeSK=0,
                sumSign=0, sumVerify=0, sumTrace=0,sumH1=0,sumH2=0,sumH3=0,sumH4=0;
    
 static const int RUN_COUNT = 100;
 
 //----------------------------------------------
 // Timer helper
 //----------------------------------------------
 double timer_diff(clock_t start, clock_t end) {
     return ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0; // in ms
 }
 
 //----------------------------------------------
 // hash_to_mpz: do sha256 -> mpz mod r
 //----------------------------------------------
 void hash_to_mpz(mpz_t out, const unsigned char *data, size_t len, mpz_t mod) {
     unsigned char hash[SHA256_DIGEST_LENGTH];
     SHA256(data, len, hash);
     mpz_import(out, SHA256_DIGEST_LENGTH, 1, 1, 0, 0, hash);
     mpz_mod(out, out, mod);
 }
 
 //----------------------------------------------
 // H1, H2, H3 => produce element in G1 or Zr
 //----------------------------------------------
 void H1(element_t outZr, element_t inG1) {
     clock_t t1 = clock();
     unsigned char buf[1024];
     size_t len = element_length_in_bytes(inG1);
     element_to_bytes(buf, inG1);
 
     mpz_t tmpz; mpz_init(tmpz);
     hash_to_mpz(tmpz, buf, len, pairing->r);
 
     element_set_mpz(outZr, tmpz);
     mpz_clear(tmpz);
     clock_t t2 = clock();
     sumH1 += timer_diff(t1, t2);

 }
 
 void H2(element_t outG1, element_t inAny) {
     clock_t t1 = clock();
     unsigned char buf[1024];
     size_t len = element_length_in_bytes(inAny);
     element_to_bytes(buf, inAny);
 
     mpz_t tmpz; mpz_init(tmpz);
     hash_to_mpz(tmpz, buf, len, pairing->r);
 
     element_t z; element_init_Zr(z, pairing);
     element_set_mpz(z, tmpz);
 
     element_pow_zn(outG1, g, z);
 
     mpz_clear(tmpz);
     element_clear(z);
     clock_t t2 = clock();
     sumH2 += timer_diff(t1, t2);
 }
 
 void H3(element_t outG1, element_t inG1) {
     clock_t t1 = clock();
     unsigned char buf[1024];
     size_t len = element_length_in_bytes(inG1);
     element_to_bytes(buf, inG1);
 
     mpz_t tmpz; mpz_init(tmpz);
     hash_to_mpz(tmpz, buf, len, pairing->r);
 
     element_t z; element_init_Zr(z, pairing);
     element_set_mpz(z, tmpz);
 
     element_pow_zn(outG1, g, z);
 
     mpz_clear(tmpz);
     element_clear(z);
     clock_t t2 = clock();
     sumH3 += timer_diff(t1, t2);
 }
 
 //----------------------------------------------
 // H4: (G1, msg, G2) -> Zr
 //----------------------------------------------
 void H4(element_t outZr, element_t addr, const char* msg, element_t X) {
     clock_t t1 = clock();
     unsigned char buf[2048];
     unsigned char g1buf[512];
     unsigned char g2buf[512];
 
     size_t len1 = element_length_in_bytes(addr);
     size_t len2 = element_length_in_bytes(X);
     size_t msglen = strlen(msg);
 
     element_to_bytes(g1buf, addr);
     element_to_bytes(g2buf, X);
 
     memcpy(buf, g1buf, len1);
     memcpy(buf + len1, msg, msglen);
     memcpy(buf + len1 + msglen, g2buf, len2);
 
     mpz_t tmpz;
     mpz_init(tmpz);
     hash_to_mpz(tmpz, buf, len1 + msglen + len2, pairing->r);
 
     element_set_mpz(outZr, tmpz);
 
     mpz_clear(tmpz);
     clock_t t2 = clock();
     sumH4 += timer_diff(t1, t2);
 }
 
 //----------------------------------------------
 // Setup: do once, no measure
 //----------------------------------------------
 void Setup(const char* param_file) {
     // Use pbc_demo_pairing_init => param_file
     char *fake_argv[2];
     fake_argv[0] = "prog";
     fake_argv[1] = (char*)param_file;
     pbc_demo_pairing_init(pairing, 2, fake_argv);
 
     element_init_G1(g, pairing);
     element_random(g);
 }
 
 //----------------------------------------------
 // KeyGen: do once, no measure
 //----------------------------------------------
 void KeyGen(element_t A, element_t B, element_t aZ, element_t bZ) {
     element_random(aZ);
     element_random(bZ);
     element_pow_zn(A, g, aZ);
     element_pow_zn(B, g, bZ);
 }
 
 //----------------------------------------------
 // TraceKeyGen: do once, no measure
 //----------------------------------------------
 void TraceKeyGen(element_t TK, element_t kZ) {
     element_random(kZ);
     element_pow_zn(TK, g, kZ);
 }
 
 //----------------------------------------------
 // OnetimeAddrGen (time measured, sum in sumAddrGen)
 //----------------------------------------------
 void OnetimeAddrGen(
     element_t Addr,
     element_t R1,
     element_t R2,
     element_t C,
     element_t A_r,
     element_t B_r,
     element_t TK
 ) {
     clock_t t1 = clock();
 
     element_t rZ, r2Z; 
     element_init_Zr(rZ, pairing);
     element_init_Zr(r2Z, pairing);
 
     element_t R3; element_init_G1(R3, pairing);
 
     element_random(rZ);
     element_pow_zn(R1, g, rZ);
 
     element_t Ar_pow_r; element_init_G1(Ar_pow_r, pairing);
     element_pow_zn(Ar_pow_r, A_r, rZ);
 
     H1(r2Z, Ar_pow_r);
 
     element_pow_zn(R2, g, r2Z);
     element_pow_zn(C, B_r, r2Z);
 
     // e(R2, TK)
     element_t pairing_res, pairing_res_powr;
     element_init_GT(pairing_res, pairing);
     element_init_GT(pairing_res_powr, pairing);
 
     pairing_apply(pairing_res, R2, TK, pairing);
     element_pow_zn(pairing_res_powr, pairing_res, rZ);
     clock_t t2 = clock();
     sumAddrGen += timer_diff(t1, t2);
 
     H2(R3, pairing_res_powr);
     clock_t t3 = clock();
    
     // Addr = R3 * B_r * C
     element_mul(Addr, R3, B_r);
     element_mul(Addr, Addr, C);
 
     element_clear(rZ);
     element_clear(r2Z);
     element_clear(R3);
     element_clear(Ar_pow_r);
     element_clear(pairing_res);
     element_clear(pairing_res_powr);
 
     clock_t t4 = clock();
     sumAddrGen += timer_diff(t3, t4);
 }
 
 //----------------------------------------------
 // AddressVerify
 //----------------------------------------------
 int AddressVerify(element_t Addr, element_t R1, element_t B_r,
                   element_t A_r, element_t C, element_t aZ, element_t TK) {
     clock_t t1 = clock();
 
     element_t R1_pow_a, C_prime, R3_prime, Addr_prime;
     element_init_G1(R1_pow_a, pairing);
     element_init_G1(C_prime, pairing);
     element_init_G1(R3_prime, pairing);
     element_init_G1(Addr_prime, pairing);
 
     element_pow_zn(R1_pow_a, R1, aZ);
 
     element_t r2Z_prime;
     element_init_Zr(r2Z_prime, pairing);
     H1(r2Z_prime, R1_pow_a);
 
     element_pow_zn(C_prime, B_r, r2Z_prime);
 
     element_t pairing_res, pairing_res_r2Z;
     element_init_GT(pairing_res, pairing);
     element_init_GT(pairing_res_r2Z, pairing);
 
     pairing_apply(pairing_res, R1, TK, pairing);
     element_pow_zn(pairing_res_r2Z, pairing_res, r2Z_prime);

     clock_t t2 = clock();
     sumAddrVerify += timer_diff(t1, t2);

     H2(R3_prime, pairing_res_r2Z);
 
     clock_t t3 = clock();
     element_mul(Addr_prime, R3_prime, B_r);
     element_mul(Addr_prime, Addr_prime, C_prime);
 
     int eq = (element_cmp(Addr_prime, Addr) == 0);
 
     element_clear(R1_pow_a);
     element_clear(C_prime);
     element_clear(R3_prime);
     element_clear(Addr_prime);
     element_clear(r2Z_prime);
     element_clear(pairing_res);
     element_clear(pairing_res_r2Z);
 
     clock_t t4 = clock();
     sumAddrVerify += timer_diff(t3, t4);
 
     return eq;
 }

 int accelerateAddrVerify(
    element_t R1,       // input
    element_t B_r,      // input
    element_t A_r,      // input
    element_t C,        // input
    element_t aZ        // input (svk in Zr)
) {
    clock_t t1 = clock();

    // 1) r2' = H1( (R1)^aZ )
    element_t R1_pow_a;
    element_init_G1(R1_pow_a, pairing);
    element_pow_zn(R1_pow_a, R1, aZ);

    element_t r2Z_prime;
    element_init_Zr(r2Z_prime, pairing);
    H1(r2Z_prime, R1_pow_a);

    // 2) C' = B_r^(r2')
    element_t C_prime;
    element_init_G1(C_prime, pairing);
    element_pow_zn(C_prime, B_r, r2Z_prime);

    // 3) Compare with C
    int eq = (element_cmp(C_prime, C) == 0);

    // clear
    element_clear(R1_pow_a);
    element_clear(r2Z_prime);
    element_clear(C_prime);

    clock_t t2 = clock();    
    sumFastAddrVerify += timer_diff(t1, t2);

    return eq; // 1 if pass, 0 if fail
}
 //----------------------------------------------
 // OnetimeSKGen
 //----------------------------------------------
 void OnetimeSKGen(element_t dsk, element_t Addr, element_t R1,
                   element_t aZ, element_t bZ) {
     clock_t t1 = clock();
 
     element_t R1_pow_a; element_init_G1(R1_pow_a, pairing);
     element_pow_zn(R1_pow_a, R1, aZ);
 
     element_t r2Z; element_init_Zr(r2Z, pairing);
     H1(r2Z, R1_pow_a);
 
     element_t exp; element_init_Zr(exp, pairing);
     element_mul(exp, bZ, r2Z);
 
     element_t h3_addr; element_init_G1(h3_addr, pairing);
     clock_t t2 = clock();
     sumOnetimeSK += timer_diff(t1, t2);

     H3(h3_addr, Addr);
     clock_t t3 = clock();
 
     element_pow_zn(dsk, h3_addr, exp);
 
     element_clear(R1_pow_a);
     element_clear(r2Z);
     element_clear(exp);
     element_clear(h3_addr);
 
     clock_t t4 = clock();
     sumOnetimeSK += timer_diff(t3, t4);
 }
 
 //----------------------------------------------
 // Sign
 //----------------------------------------------
 void Sign(element_t Q_sigma, element_t hZ, element_t Addr, element_t dsk, const char* msg) {
     clock_t t1 = clock();
 
     element_t xZ; element_init_Zr(xZ, pairing);
     element_random(xZ);
 
     element_t gx; element_init_G1(gx, pairing);
     element_pow_zn(gx, g, xZ);
 
     element_t XGT; element_init_GT(XGT, pairing);
     pairing_apply(XGT, gx, g, pairing);
 
     H4(hZ, Addr, msg, XGT);
 
     element_t neg_hZ; element_init_Zr(neg_hZ, pairing);
     element_neg(neg_hZ, hZ);
 
     element_t dsk_inv_h; element_init_G1(dsk_inv_h, pairing);
     element_pow_zn(dsk_inv_h, dsk, neg_hZ);
 
     element_mul(Q_sigma, dsk_inv_h, gx);
 
     element_clear(xZ);
     element_clear(gx);
     element_clear(XGT);
     element_clear(neg_hZ);
     element_clear(dsk_inv_h);
 
     clock_t t2 = clock();
     sumSign += timer_diff(t1, t2);
 }
 
 //----------------------------------------------
 // Verify
 //----------------------------------------------
 int Verify(element_t Addr, element_t R2, element_t C,
            const char* msg, element_t hZ, element_t Q_sigma) {
     clock_t t1 = clock();
 
     element_t h3_addr; element_init_G1(h3_addr, pairing);
     clock_t t2 = clock();
     sumVerify += timer_diff(t1, t2);
 
     H3(h3_addr, Addr);
     clock_t t3 = clock();
 
     element_t pairing1, pairing2, pairing2_exp, prod;
     element_init_GT(pairing1, pairing);
     element_init_GT(pairing2, pairing);
     element_init_GT(pairing2_exp, pairing);
     element_init_GT(prod, pairing);
 
     pairing_apply(pairing1, Q_sigma, g, pairing);
     pairing_apply(pairing2, h3_addr, C, pairing);
     element_pow_zn(pairing2_exp, pairing2, hZ);
     element_mul(prod, pairing1, pairing2_exp);
 
     element_t hZ_prime; element_init_Zr(hZ_prime, pairing);
     H4(hZ_prime, Addr, msg, prod);
 
     int valid = (element_cmp(hZ, hZ_prime) == 0);
 
     element_clear(h3_addr);
     element_clear(pairing1);
     element_clear(pairing2);
     element_clear(pairing2_exp);
     element_clear(prod);
     element_clear(hZ_prime);
 
     clock_t t4 = clock();
     sumVerify += timer_diff(t3, t4);
 
     return valid;
 }
 
 //----------------------------------------------
 // IdentityTracing
 //----------------------------------------------
 void IdentityTracing(element_t B_r, element_t Addr, element_t R1, element_t R2, element_t C, element_t kZ) {
     clock_t t1 = clock();
 
     element_t pairing_res, pairing_powk, R3;
     element_init_GT(pairing_res, pairing);
     element_init_GT(pairing_powk, pairing);
     element_init_G1(R3, pairing);
 
     pairing_apply(pairing_res, R1, R2, pairing);
     element_pow_zn(pairing_powk, pairing_res, kZ);
     clock_t t2 = clock();
     sumTrace += timer_diff(t1, t2);
     H2(R3, pairing_powk);
     clock_t t3 = clock();
 
     element_t R3_inv, C_inv;
     element_init_G1(R3_inv, pairing);
     element_init_G1(C_inv, pairing);
 
     element_invert(R3_inv, R3);
     element_invert(C_inv, C);
 
     element_mul(B_r, Addr, R3_inv);
     element_mul(B_r, B_r, C_inv);
 
     element_clear(pairing_res);
     element_clear(pairing_powk);
     element_clear(R3);
     element_clear(R3_inv);
     element_clear(C_inv);
 
     clock_t t4 = clock();
     sumTrace += timer_diff(t3, t4);
 }
 
 //----------------------------------------------
 // Print average times (for the 6 funcs) in ms
 //----------------------------------------------
 void PrintAverageTimes() {
     printf("\n=== Average runtime over %d runs (ms) ===\n", RUN_COUNT);
     printf("OnetimeAddrGen:  %.3f ms\n", sumAddrGen   / RUN_COUNT);
     printf("AddressVerify:   %.3f ms\n", sumAddrVerify/ RUN_COUNT);
     printf("FastAddressVerify:   %.3f ms\n", sumFastAddrVerify/ RUN_COUNT);
     printf("OnetimeSKGen:    %.3f ms\n", sumOnetimeSK / RUN_COUNT);
     printf("Sign:            %.3f ms\n", sumSign      / RUN_COUNT);
     printf("Verify:          %.3f ms\n", sumVerify    / RUN_COUNT);
     printf("IdentityTracing: %.3f ms\n", sumTrace     / RUN_COUNT);
     printf("H1: %.3f ms\n", sumH1     / (4*RUN_COUNT));
     printf("H2: %.3f ms\n", sumH2     / (3*RUN_COUNT));
     printf("H3: %.3f ms\n", sumH3     / (2*RUN_COUNT));
     printf("H4: %.3f ms\n", sumH4     / (2*RUN_COUNT));

 }
 
 //----------------------------------------------
 // main
 //----------------------------------------------
 int main(int argc, char **argv) {
     if (argc < 2) {
         fprintf(stderr, "Usage: %s <param_file>\n", argv[0]);
         return 1;
     }
 
     // 1) Setup once
     Setup(argv[1]);
 
     // 2) KeyGen once
     element_t A, B, a, b;
     element_init_G1(A, pairing);
     element_init_G1(B, pairing);
     element_init_Zr(a, pairing);
     element_init_Zr(b, pairing);
     KeyGen(A, B, a, b);
 
     // 3) TraceKeyGen once
     element_t TK, k;
     element_init_G1(TK, pairing);
     element_init_Zr(k, pairing);
     TraceKeyGen(TK, k);
 
     // 4) Now do a loop for 100 times
     for(int i=0; i<RUN_COUNT; i++){
         // We create ephemeral R1,R2,C,Addr etc
         element_t Addr, R1, R2, C;
         element_init_G1(Addr, pairing);
         element_init_G1(R1, pairing);
         element_init_G1(R2, pairing);
         element_init_G1(C, pairing);
 
         // (A, B, TK, a, b, k) are from KeyGen / TraceKeyGen
         OnetimeAddrGen(Addr, R1, R2, C, A, B, TK);
 
         int ok = AddressVerify(Addr, R1, B, A, C, a, TK);
         int ok2= accelerateAddrVerify( R1, B, A, C, a);
         element_t dsk;
         element_init_G1(dsk, pairing);
         OnetimeSKGen(dsk, Addr, R1, a, b);
 
         const char* msg = "Test message";
         element_t Q_sigma, hZ;
         element_init_G1(Q_sigma, pairing);
         element_init_Zr(hZ, pairing);
 
         Sign(Q_sigma, hZ, Addr, dsk, msg);
 
         int valid = Verify(Addr, R2, C, msg, hZ, Q_sigma);
 
         element_t B_recovered;
         element_init_G1(B_recovered, pairing);
         IdentityTracing(B_recovered, Addr, R1, R2, C, k);
 
         // free ephemeral
         element_clear(Addr);
         element_clear(R1);
         element_clear(R2);
         element_clear(C);
         element_clear(dsk);
         element_clear(Q_sigma);
         element_clear(hZ);
         element_clear(B_recovered);
     }
 
     // show average times
     PrintAverageTimes();
 
     // final cleanup
     element_clear(A); element_clear(B);
     element_clear(a); element_clear(b);
     element_clear(TK); element_clear(k);
     element_clear(g);
     pairing_clear(pairing);
 
     return 0;
 }
 