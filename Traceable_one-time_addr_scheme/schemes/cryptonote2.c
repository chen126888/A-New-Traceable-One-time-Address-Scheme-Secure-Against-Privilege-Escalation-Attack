#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/ec.h>
#include <openssl/ecdsa.h>
#include <openssl/obj_mac.h>
#include <openssl/sha.h>
#include <openssl/bn.h>
#include <openssl/rand.h>
#include <openssl/evp.h>

#define LOOP 100

// Global variables
EC_GROUP *group;
EC_POINT *G;
BIGNUM *order;

double timer_diff(clock_t start, clock_t end) {
    return ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0;
}

double sumH1 = 0;
double sumGen = 0, sumStat = 0, sumSK = 0;

// H1: hash(EC_POINT) -> BIGNUM (Zr)
void H1(BIGNUM *outZr, EC_POINT *inG1, BN_CTX *ctx) {
    clock_t t1 = clock();
    
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    const EVP_MD *md = EVP_sha256();
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    
    EVP_DigestInit_ex(mdctx, md, NULL);
    
    // Convert EC_POINT to bytes
    size_t point_len = EC_POINT_point2oct(group, inG1, POINT_CONVERSION_COMPRESSED, NULL, 0, ctx);
    unsigned char *point_buf = OPENSSL_malloc(point_len);
    EC_POINT_point2oct(group, inG1, POINT_CONVERSION_COMPRESSED, point_buf, point_len, ctx);
    
    // Hash the point
    EVP_DigestUpdate(mdctx, point_buf, point_len);
    EVP_DigestFinal_ex(mdctx, hash, &hash_len);
    
    // Convert hash to BIGNUM and reduce modulo order
    BN_bin2bn(hash, hash_len, outZr);
    BN_mod(outZr, outZr, order, ctx);
    
    // Cleanup
    OPENSSL_free(point_buf);
    EVP_MD_CTX_free(mdctx);
    
    clock_t t2 = clock();
    sumH1 += timer_diff(t1, t2);
}

void Setup() {
    // Initialize curve (using secp256r1)
    group = EC_GROUP_new_by_curve_name(NID_X9_62_prime256v1);
    if (!group) {
        fprintf(stderr, "Failed to create EC group\n");
        exit(1);
    }
    
    // Get generator point
    const EC_POINT *generator = EC_GROUP_get0_generator(group);
    if (!generator) {
        fprintf(stderr, "Failed to get generator\n");
        exit(1);
    }
    G = EC_POINT_new(group);
    EC_POINT_copy(G, generator);
    
    // Get order of the group
    order = BN_new();
    if (!EC_GROUP_get_order(group, order, NULL)) {
        fprintf(stderr, "Failed to get group order\n");
        exit(1);
    }
}

void KeyGen(EC_POINT *A, EC_POINT *B, BIGNUM *a, BIGNUM *b, BN_CTX *ctx) {
    // Generate random private keys
    BN_rand_range(a, order);
    BN_rand_range(b, order);
    
    // Compute public keys: A = a*G, B = b*G
    EC_POINT_mul(group, A, NULL, G, a, ctx);
    EC_POINT_mul(group, B, NULL, G, b, ctx);
}

void OnetimeAddrGen(EC_POINT *PK_one, EC_POINT *R, EC_POINT *A, EC_POINT *B, BN_CTX *ctx) {
    clock_t t1 = clock();
    
    BIGNUM *r = BN_new();
    BIGNUM *r_out = BN_new();
    EC_POINT *temp = EC_POINT_new(group);
    EC_POINT *r_out_G = EC_POINT_new(group);
    
    // Generate random r
    BN_rand_range(r, order);
    
    // R = r * G
    EC_POINT_mul(group, R, NULL, G, r, ctx);
    
    // temp = r * A
    EC_POINT_mul(group, temp, NULL, A, r, ctx);
    
    // r_out = hash(r*A)
    H1(r_out, temp, ctx);
    
    // PK_one = r_out*G + B
    EC_POINT_mul(group, r_out_G, NULL, G, r_out, ctx);
    EC_POINT_add(group, PK_one, r_out_G, B, ctx);
    
    // Cleanup
    BN_free(r);
    BN_free(r_out);
    EC_POINT_free(temp);
    EC_POINT_free(r_out_G);
    
    clock_t t2 = clock();
    sumGen += timer_diff(t1, t2);
}

int ReceiverStatistics(EC_POINT *PK_one, EC_POINT *R, BIGNUM *a, EC_POINT *B, BN_CTX *ctx) {
    clock_t t1 = clock();
    
    BIGNUM *r_out = BN_new();
    EC_POINT *temp = EC_POINT_new(group);
    EC_POINT *r_out_G = EC_POINT_new(group);
    EC_POINT *check_PK = EC_POINT_new(group);
    
    // temp = a * R
    EC_POINT_mul(group, temp, NULL, R, a, ctx);
    
    // r_out = hash(a*R)
    H1(r_out, temp, ctx);
    
    // check_PK = r_out*G + B
    EC_POINT_mul(group, r_out_G, NULL, G, r_out, ctx);
    EC_POINT_add(group, check_PK, r_out_G, B, ctx);
    
    // Check if PK_one == check_PK
    int ok = (EC_POINT_cmp(group, PK_one, check_PK, ctx) == 0);
    
    // Cleanup
    BN_free(r_out);
    EC_POINT_free(temp);
    EC_POINT_free(r_out_G);
    EC_POINT_free(check_PK);
    
    clock_t t2 = clock();
    sumStat += timer_diff(t1, t2);
    
    return ok;
}

void OnetimeSKGen(BIGNUM *sk_ot, EC_POINT *R, BIGNUM *a, BIGNUM *b, BN_CTX *ctx) {
    clock_t t1 = clock();
    
    BIGNUM *r_out = BN_new();
    EC_POINT *temp = EC_POINT_new(group);
    
    // temp = a * R
    EC_POINT_mul(group, temp, NULL, R, a, ctx);
    
    // r_out = hash(a*R)
    H1(r_out, temp, ctx);
    
    // sk_ot = r_out + b
    BN_mod_add(sk_ot, r_out, b, order, ctx);
    
    // Cleanup
    BN_free(r_out);
    EC_POINT_free(temp);
    
    clock_t t2 = clock();
    sumSK += timer_diff(t1, t2);
}

void cleanup() {
    EC_POINT_free(G);
    EC_GROUP_free(group);
    BN_free(order);
}

int main() {
    Setup();
    
    BN_CTX *ctx = BN_CTX_new();
    
    // Initialize keys
    EC_POINT *A = EC_POINT_new(group);
    EC_POINT *B = EC_POINT_new(group);
    BIGNUM *a = BN_new();
    BIGNUM *b = BN_new();
    
    // Generate keys
    KeyGen(A, B, a, b, ctx);
    
    printf("Running %d iterations...\n", LOOP);
    
    for (int i = 0; i < LOOP; i++) {
        EC_POINT *PK_one = EC_POINT_new(group);
        EC_POINT *R = EC_POINT_new(group);
        BIGNUM *sk_ot = BN_new();
        
        // Run algorithms
        OnetimeAddrGen(PK_one, R, A, B, ctx);
        int result = ReceiverStatistics(PK_one, R, a, B, ctx);
        OnetimeSKGen(sk_ot, R, a, b, ctx);
        
        // Check correctness
        if (!result) {
            printf("FAIL at round %d\n", i);
        }
        
        // Cleanup round
        EC_POINT_free(PK_one);
        EC_POINT_free(R);
        BN_free(sk_ot);
    }
    
    // Print timing results
    printf("\n=== Performance Results ===\n");
    printf("Avg AddrGen Time     : %.3f ms\n", sumGen / LOOP);
    printf("Avg ReceiverStat Time: %.3f ms\n", sumStat / LOOP);
    printf("Avg OnetimeSKGen Time: %.3f ms\n", sumSK / LOOP);
    printf("Avg H1 Time: %.3f ms\n", sumH1 / (3*LOOP));
    
    // Cleanup
    EC_POINT_free(A);
    EC_POINT_free(B);
    BN_free(a);
    BN_free(b);
    BN_CTX_free(ctx);
    cleanup();
    
    return 0;
}