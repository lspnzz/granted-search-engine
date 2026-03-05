import { createHash } from 'crypto';
import { getAdminFirestore } from './firebase-admin';
import { FieldValue } from 'firebase-admin/firestore';

const COLLECTION = 'query_usage';
const AUTHENTICATED_LIMIT = 9;
const UNAUTHENTICATED_LIMIT = 1;

interface UsageResult {
  allowed: boolean;
  remaining: number;
  isAuthenticated: boolean;
}

export async function checkAndIncrementUsage(
  userId: string | null,
  ip: string
): Promise<UsageResult> {
  const isAuthenticated = userId !== null;
  const limit = isAuthenticated ? AUTHENTICATED_LIMIT : UNAUTHENTICATED_LIMIT;
  const docId = isAuthenticated ? userId : createHash('sha256').update(ip).digest('hex');

  const db = getAdminFirestore();
  const docRef = db.collection(COLLECTION).doc(docId);

  return db.runTransaction(async (transaction) => {
    const doc = await transaction.get(docRef);
    const currentCount = doc.exists ? (doc.data()?.count ?? 0) : 0;

    if (currentCount >= limit) {
      return { allowed: false, remaining: 0, isAuthenticated };
    }

    if (doc.exists) {
      transaction.update(docRef, { count: FieldValue.increment(1), updatedAt: FieldValue.serverTimestamp() });
    } else {
      transaction.set(docRef, { count: 1, isAuthenticated, createdAt: FieldValue.serverTimestamp(), updatedAt: FieldValue.serverTimestamp() });
    }

    return { allowed: true, remaining: limit - currentCount - 1, isAuthenticated };
  });
}
