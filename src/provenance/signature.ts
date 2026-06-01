import { createSign, createVerify, generateKeyPairSync } from "node:crypto";

export function signBuffer(privateKeyPem: string, data: Buffer | string): string {
  const sign = createSign("RSA-SHA256");
  sign.update(data);
  sign.end();
  const sig = sign.sign(privateKeyPem);
  return sig.toString("base64");
}

export function verifyBuffer(publicKeyPem: string, data: Buffer | string, signatureB64: string): boolean {
  const verify = createVerify("RSA-SHA256");
  verify.update(data);
  verify.end();
  try {
    return verify.verify(publicKeyPem, Buffer.from(signatureB64, "base64"));
  } catch {
    return false;
  }
}

export function generateKeypair(): { publicKey: string; privateKey: string } {
  const { publicKey, privateKey } = generateKeyPairSync("rsa", {
    modulusLength: 2048,
    publicKeyEncoding: { type: "spki", format: "pem" },
    privateKeyEncoding: { type: "pkcs8", format: "pem" }
  });

  return { publicKey, privateKey };
}

export default { signBuffer, verifyBuffer, generateKeypair };
