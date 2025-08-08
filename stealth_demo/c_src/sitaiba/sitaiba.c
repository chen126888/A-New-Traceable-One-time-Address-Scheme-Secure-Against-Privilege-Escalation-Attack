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
                sumTrace=0,sumH1=0,sumH2=0;
    
 static const int RUN_COUNT = 100;

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
 
// hash_to_mpz() 與 timer_diff() 與 traceable_transaction.c 相同
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

void H2(element_t outZr, element_t inGT) {
    clock_t t1 = clock();
    unsigned char buf[2048];
    size_t len = element_length_in_bytes(inGT);
    element_to_bytes(buf, inGT);

    mpz_t tmpz; mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len, pairing->r);
    element_set_mpz(outZr, tmpz);
    mpz_clear(tmpz);
    clock_t t2 = clock();
    sumH2 += timer_diff(t1, t2);
}

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
 


void OnetimeAddrGen(element_t Addr, element_t R1, element_t R2,
                    element_t A_r, element_t B_r, element_t A_m) {
    clock_t t1 = clock();
    element_t r1, r2, r3, tmp;
    element_init_Zr(r1, pairing);
    element_init_Zr(r2, pairing);
    element_init_Zr(r3, pairing);
    element_init_GT(tmp, pairing);

    element_random(r1);
    element_pow_zn(R1, g, r1);

    element_t Ar_pow_r1;
    element_init_G1(Ar_pow_r1, pairing);
    element_pow_zn(Ar_pow_r1, A_r, r1);

    H1(r2, Ar_pow_r1);
    element_pow_zn(R2, A_r, r2);

    element_t eR2Am;
    element_init_GT(eR2Am, pairing);
    pairing_apply(eR2Am, R2, A_m, pairing);
    element_pow_zn(tmp, eR2Am, r1);
    H2(r3, tmp);

    element_t r3G, sum;
    element_init_G1(r3G, pairing);
    element_init_G1(sum, pairing);
    element_pow_zn(r3G, g, r3);

    element_mul(sum, r3G, R2);
    element_mul(Addr, sum, B_r);

    // 清除
    element_clear(r1); element_clear(r2); element_clear(r3);
    element_clear(tmp); element_clear(Ar_pow_r1); element_clear(eR2Am);
    element_clear(r3G); element_clear(sum);

    clock_t t2 = clock();
    sumAddrGen += timer_diff(t1, t2);
}

int AddressVerify(element_t Addr, element_t R1,element_t R2, element_t A_r, element_t B_r,
                  element_t A_m, element_t a_r) {
    clock_t t1 = clock();

    // Step 1: r2 = h1(a_r * R1)
    element_t R1_pow_a, r2Z;
    element_init_G1(R1_pow_a, pairing);
    element_init_Zr(r2Z, pairing);
    element_pow_zn(R1_pow_a, R1, a_r);
    H1(r2Z, R1_pow_a);

    // Step 2: R2 = r2 * A_r
    element_t R2_prime,r2a;
    element_init_G1(R2_prime, pairing);
    element_init_Zr(r2a, pairing);
    element_pow_zn(R2_prime, A_r, r2Z);
    element_mul(r2a,r2Z,a_r);

    // Step 3: r3 = H(e(R1, A_m)^r2) 
    element_t eR1Am, r3Z,tmp;
    element_init_GT(eR1Am, pairing);
    element_init_GT(tmp, pairing);
    element_init_Zr(r3Z, pairing);
    pairing_apply(eR1Am, R1, A_m, pairing);
    element_pow_zn(tmp, eR1Am, r2a);
    H2(r3Z, tmp);

    // Step 4: reconstruct Addr = r3 * G + R2 + B_r
    element_t r3G, sum, Addr_reconstructed;
    element_init_G1(r3G, pairing);
    element_init_G1(sum, pairing);
    element_init_G1(Addr_reconstructed, pairing);
    element_pow_zn(r3G, g, r3Z);
    element_mul(sum, r3G, R2);
    element_mul(Addr_reconstructed, sum, B_r);
    int eq1 = (element_cmp(R2_prime, R2) == 0);                
    int eq2 = (element_cmp(Addr_reconstructed, Addr) == 0);
    //printf("eq1: %d\n", eq1);
    //printf("eq2: %d\n", eq2);

    // cleanup
    element_clear(R1_pow_a); element_clear(r2Z);
    element_clear(r3Z); element_clear(r3G);
    element_clear(sum); element_clear(Addr_reconstructed);element_clear(tmp);

    clock_t t2 = clock();
    sumAddrVerify += timer_diff(t1, t2);
    return eq1&&eq2;
}

int accelerateAddrVerify(element_t R1, element_t R2,
                         element_t A_r, element_t a_r) {
    clock_t t1 = clock();

    // Step 1: r2 = h1(a_r * R1)
    element_t R1_pow_a, r2Z;
    element_init_G1(R1_pow_a, pairing);
    element_init_Zr(r2Z, pairing);
    element_pow_zn(R1_pow_a, R1, a_r);
    H1(r2Z, R1_pow_a);

    // Step 2: R2' = r2 * A_r
    element_t R2_prime;
    element_init_G1(R2_prime, pairing);
    element_pow_zn(R2_prime, A_r, r2Z);

    int eq = (element_cmp(R2_prime, R2) == 0);

    // cleanup
    element_clear(R1_pow_a); element_clear(r2Z); element_clear(R2_prime);

    clock_t t2 = clock();
    sumFastAddrVerify += timer_diff(t1, t2);
    return eq;
}


void OnetimeSKGen(element_t dsk, element_t R1, element_t a_r, element_t b_r,
                  element_t A_m) {
    clock_t t1 = clock();
    element_t r2, r3, eR1Am;
    element_init_Zr(r2, pairing);
    element_init_Zr(r3, pairing);
    element_init_GT(eR1Am, pairing);

    element_t R1_a,r2a;
    element_init_G1(R1_a, pairing);
    element_init_Zr(r2a, pairing);
    element_pow_zn(R1_a, R1, a_r);
    H1(r2, R1_a);

    pairing_apply(eR1Am, R1, A_m, pairing);
    element_mul(r2a, r2, a_r);
    element_pow_zn(eR1Am, eR1Am, r2a);

    H2(r3, eR1Am);

    element_add(dsk, r3, r2a);
    element_add(dsk, dsk, b_r);

    element_clear(r2); element_clear(r3); element_clear(eR1Am);
    element_clear(R1_a); element_clear(r2a); 
    clock_t t2 = clock();
    sumOnetimeSK += timer_diff(t1, t2);
}

void IdentityTracing(element_t Br, element_t Addr, element_t R1,
                     element_t R2, element_t a_m) {
    clock_t t1 = clock();
    element_t eR1R2, powed, r3;
    element_init_GT(eR1R2, pairing);
    element_init_GT(powed, pairing);
    element_init_Zr(r3, pairing);

    pairing_apply(eR1R2, R1, R2, pairing);
    element_pow_zn(powed, eR1R2, a_m);
    H2(r3, powed);

    element_t r3G, Addr_tmp, R2_inv;
    element_init_G1(r3G, pairing);
    element_init_G1(Addr_tmp, pairing);
    element_init_G1(R2_inv, pairing);

    // r3G = r3 * G
    element_pow_zn(r3G, g, r3);

    // Addr_tmp = Addr * (r3G)^-1
    element_invert(Addr_tmp, r3G);
    element_mul(Addr_tmp, Addr, Addr_tmp);

    // R2_inv = R2^-1
    element_invert(R2_inv, R2);

    // Br = Addr_tmp * R2^-1
    element_mul(Br, Addr_tmp, R2_inv);

    element_clear(eR1R2); element_clear(powed); element_clear(r3);
    element_clear(r3G); 

    clock_t t2 = clock();
    sumTrace += timer_diff(t1, t2);
}

void PrintAverageTimes() {
    printf("\n=== Average runtime over %d runs (ms) ===\n", RUN_COUNT);
    printf("OnetimeAddrGen:       %.3f ms\n", sumAddrGen        / RUN_COUNT);
    printf("AddressVerify:        %.3f ms\n", sumAddrVerify     / RUN_COUNT);
    printf("FastAddressVerify:    %.3f ms\n", sumFastAddrVerify / RUN_COUNT);
    printf("OnetimeSKGen:         %.3f ms\n", sumOnetimeSK      / RUN_COUNT);
    printf("IdentityTracing:      %.3f ms\n", sumTrace          / RUN_COUNT);
    printf("H1: %.3f ms\n", sumH1 / (4.0 * RUN_COUNT)); // 每次使用2次
    printf("H2: %.3f ms\n", sumH2 / (4.0 * RUN_COUNT)); // 每次使用2次
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <param_file>\n", argv[0]);
        return 1;
    }

     // Setup once
     Setup(argv[1]);
 
    // KeyGen for receiver
    element_t A_r, B_r, a_r, b_r;
    element_init_G1(A_r, pairing);
    element_init_G1(B_r, pairing);
    element_init_Zr(a_r, pairing);
    element_init_Zr(b_r, pairing);
    KeyGen(A_r, B_r, a_r, b_r);

    // KeyGen for manager
    element_t A_m, B_m, a_m, b_dummy;
    element_init_G1(A_m, pairing);
    element_init_G1(B_m, pairing);
    element_init_Zr(a_m, pairing);
    element_init_Zr(b_dummy, pairing);
    KeyGen(A_m, B_m, a_m, b_dummy); 

    for (int i = 0; i < RUN_COUNT; i++) {
        // ephemeral elements
        element_t Addr, R1, R2;
        element_init_G1(Addr, pairing);
        element_init_G1(R1, pairing);
        element_init_G1(R2, pairing);

        // === 1. Generate Addr ===
        OnetimeAddrGen(Addr, R1, R2, A_r, B_r, A_m);

        // === 2. Verify Full ===
        int ok1 = AddressVerify(Addr, R1, R2,A_r, B_r, A_m, a_r);
        if (!ok1) printf("Full Verify FAILED at %d\n", i);

        // === 3. Accelerated Verify ===
        int ok2 = accelerateAddrVerify(R1, R2, A_r, a_r);
        if (!ok2) printf("Fast Verify FAILED at %d\n", i);

        // === 4. Generate dsk ===
        element_t dsk;
        element_init_G1(dsk, pairing);
        OnetimeSKGen(dsk, R1, a_r, b_r, A_m);

        // === 5. Tracing ===
        element_t Br_recovered;
        element_init_G1(Br_recovered, pairing);
        IdentityTracing(Br_recovered, Addr, R1, R2, a_m);

        if (element_cmp(Br_recovered, B_r) != 0)
            printf("Tracing FAILED at %d\n", i);

        // cleanup
        element_clear(Addr);
        element_clear(R1);
        element_clear(R2);
        element_clear(dsk);
        element_clear(Br_recovered);
    }

    // output avg timing
    PrintAverageTimes();

    // cleanup
    element_clear(A_r); element_clear(B_r); element_clear(a_r); element_clear(b_r);
    element_clear(A_m); element_clear(B_m); element_clear(a_m); element_clear(b_dummy);
    element_clear(g);
    pairing_clear(pairing);
    return 0;
}
