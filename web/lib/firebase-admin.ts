import { initializeApp, getApps, getApp, applicationDefault, type App } from 'firebase-admin/app';
import { getFirestore, type Firestore } from 'firebase-admin/firestore';
import { getAuth, type DecodedIdToken } from 'firebase-admin/auth';

let app: App | undefined;

function getAdminApp(): App {
  if (!app) {
    app = getApps().length === 0 ? initializeApp({ credential: applicationDefault() }) : getApp();
  }
  return app;
}

export function getAdminFirestore(): Firestore {
  return getFirestore(getAdminApp());
}

export async function verifyIdToken(token: string): Promise<DecodedIdToken> {
  return getAuth(getAdminApp()).verifyIdToken(token);
}
