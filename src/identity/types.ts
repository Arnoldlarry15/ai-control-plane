export type IdentityType = "human" | "ai" | "agent" | "org";

export interface IdentityCredentials {
  publicKeys?: string[];
  signerRefs?: string[];
  did?: string;
}

export interface IdentityRecord {
  id: string;
  type: IdentityType;
  label?: string;
  orgId?: string;
  credentials?: IdentityCredentials;
  trustAnchors?: string[];
  createdAt: string;
  metadata?: Record<string, any>;
}
