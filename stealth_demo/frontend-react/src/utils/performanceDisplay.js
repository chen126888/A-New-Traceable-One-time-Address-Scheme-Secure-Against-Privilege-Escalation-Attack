export const getPerformanceTestDetails = (scheme, result, getFastestOperation, getSlowestOperation) => {
  if (!result) return '';

  const fastestOp = getFastestOperation(result);
  const slowestOp = getSlowestOperation(result);
  const commonHeader = `🏁 ${scheme.toUpperCase()} Scheme Performance Test Results - Test ${result.test_index}
⏰ Test Time: ${result.timestamp}
🔄 Iterations: ${result.iterations}
⚡ Total Test Duration: ${result.total_test_time}ms
📊 Average per Iteration: ${result.avg_per_iteration.toFixed(2)}ms
🎯 Scheme: ${scheme.toUpperCase()}`;

  if (scheme === 'sitaiba') {
    return `${commonHeader}\n\n📈 Detailed Performance Metrics (Average time per operation):\n\n🏠 Address Generation: ${result.addr_gen_ms}ms\n   ├─ Public key pair to stealth address\n   └─ Based on elliptic curve pairing\n\n🔍 Address Recognition: ${result.addr_recognize_ms}ms\n   ├─ Full recognition pairing computation\n   └─ Mathematical relationship verification\n\n⚡ Fast Address Recognition: ${result.fast_recognize_ms}ms\n   ├─ SITAIBA optimized recognition method\n   └─ ~${((result.addr_recognize_ms / result.fast_recognize_ms) || 1).toFixed(1)}x faster than full recognition\n\n🔐 One-time Secret Key Generation: ${result.onetime_sk_ms}ms\n   ├─ Derive DSK from address (Zr group)\n   └─ Used for identity tracing\n\n🔍 Identity Tracing: ${result.trace_ms}ms\n   ├─ Recover identity information from address\n   └─ Tracing authority operation\n\n📊 Performance Analysis:\n   Fastest Operation: ${fastestOp}\n   Slowest Operation: ${slowestOp}\n   Total Cycle Time: ${(result.addr_gen_ms + result.fast_recognize_ms + result.onetime_sk_ms + result.trace_ms).toFixed(3)}ms\n\n💡 SITAIBA Scheme Features:\n• Does not support message signing/verification\n• DSK is Zr group element (different from Stealth)\n• Focuses on address generation, recognition and tracing\n• Based on pairing-friendly elliptic curves`;
  }

  // Default to stealth
  return `${commonHeader}\n\n📈 Detailed Performance Metrics (Average time per operation):\n\n🏠 Address Generation: ${result.addr_gen_ms}ms\n   ├─ Key pair to stealth address\n   └─ Includes random element generation\n\n🔍 Address Recognition: ${result.addr_recognize_ms}ms\n   ├─ Full recognition pairing computation\n   └─ Cryptographic proof verification\n\n⚡ Fast Address Recognition: ${result.fast_recognize_ms}ms\n   ├─ Optimized recognition method\n   └─ ~${((result.addr_recognize_ms / result.fast_recognize_ms) || 1).toFixed(1)}x faster than full recognition\n\n🔐 One-time Secret Key Generation: ${result.onetime_sk_ms}ms\n   ├─ Derive DSK from address\n   └─ Required for signing operations\n\n✍️ Message Signing: ${result.sign_ms}ms\n   ├─ Cryptographic signature generation\n   └─ Includes random nonce generation\n\n✅ Signature Verification: ${result.sig_verify_ms}ms\n   ├─ Pairing verification\n   └─ Mathematical proof verification\n\n🔍 Identity Tracing: ${result.trace_ms}ms\n   ├─ Recover identity from address\n   └─ Tracing authority operation\n\n📊 Performance Analysis:\n   Fastest Operation: ${fastestOp}\n   Slowest Operation: ${slowestOp}\n   Total Cycle Time: ${(result.addr_gen_ms + result.fast_recognize_ms + result.onetime_sk_ms + result.sign_ms + result.sig_verify_ms + result.trace_ms).toFixed(3)}ms`;
};
